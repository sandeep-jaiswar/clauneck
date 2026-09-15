package com.clauneck.web.service;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import com.clauneck.web.dto.EquationDto;
import com.clauneck.web.dto.MetadataDto;
import com.clauneck.web.dto.Quantity;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.dto.SolverConfigDto;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

class SchemaValidatorTest {

    private SchemaValidator validator;

    @BeforeEach
    void setUp() {
        validator = new SchemaValidator(new ObjectMapper());
        validator.loadSchema();
    }

    private ScientificModelDto validModel() {
        ScientificModelDto model = new ScientificModelDto();
        model.setId("projectile_001");
        model.setDomain("physics.mechanics");
        model.setDescription("Ball at 20 m/s, 45 degrees");

        Quantity v0 = new Quantity();
        v0.setName("v0");
        v0.setValue(20.0);
        v0.setSiUnit("m/s");
        v0.setKnown(true);
        model.setQuantities(List.of(v0));

        EquationDto eq = new EquationDto();
        eq.setLhs("d2x/dt2");
        eq.setRhs("-g");
        eq.setType("ode");
        model.setEquations(List.of(eq));

        model.setInitialConditions(java.util.Map.of("v0", 20.0));

        com.clauneck.web.dto.TimeSpanDto timeSpan = new com.clauneck.web.dto.TimeSpanDto();
        timeSpan.setStart(0.0);
        timeSpan.setEnd(5.0);
        timeSpan.setNumPoints(5000);

        SolverConfigDto solver = new SolverConfigDto();
        solver.setMethod("RK45");
        solver.setTolerance(1e-6);
        solver.setTimeSpan(timeSpan);
        model.setSolver(solver);

        MetadataDto metadata = new MetadataDto();
        metadata.setSource("llm_translator");
        model.setMetadata(metadata);

        return model;
    }

    @Test
    void validModelPassesWithNoErrors() {
        List<String> errors = validator.validate(validModel());
        assertTrue(errors.isEmpty(), "Expected no validation errors, got: " + errors);
    }

    @Test
    void missingRequiredFieldFails() {
        ScientificModelDto model = validModel();
        model.setId(null);

        List<String> errors = validator.validate(model);
        assertFalse(errors.isEmpty(), "Expected validation errors for missing 'id'");
    }

    @Test
    void badDomainEnumValueFails() {
        ScientificModelDto model = validModel();
        model.setDomain("chemistry.wizardry");

        List<String> errors = validator.validate(model);
        assertFalse(errors.isEmpty(), "Expected validation errors for invalid domain enum value");
    }

    @Test
    void flatInitialConditionsDoesNotTripSchemaDrift() {
        // The known schema/engine drift (nested {time,values} vs flat map) must not
        // cause a false-positive rejection of an otherwise-valid model.
        ScientificModelDto model = validModel();
        model.setInitialConditions(java.util.Map.of("v0", 20.0, "angle", 45.0, "mass", 0.5));

        List<String> errors = validator.validate(model);
        assertTrue(errors.isEmpty(), "Flat initialConditions should not fail validation, got: " + errors);
    }
}
