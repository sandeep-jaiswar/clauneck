package com.clauneck.web.service;

import com.clauneck.core.model.Equation;
import com.clauneck.core.model.Model;
import com.clauneck.core.model.Quantity;
import com.clauneck.core.units.Dimension;
import com.clauneck.core.units.UnitRegistry;
import com.clauneck.core.validation.DimensionalAnalyzer;
import com.clauneck.web.dto.DimensionVector;
import com.clauneck.web.dto.ScientificModelDto;
import com.clauneck.web.exception.DimensionalMismatchException;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import org.springframework.stereotype.Service;

/**
 * Validates dimensional consistency of translated models.
 *
 * Converts ScientificModelDto (web layer) to core.Model and runs DimensionalAnalyzer
 * to catch dimensional inconsistencies before sending to the Python engine.
 */
@Service
public class DimensionalValidationService {

    private final DimensionalAnalyzer analyzer;

    public DimensionalValidationService(UnitRegistry unitRegistry) {
        this.analyzer = new DimensionalAnalyzer(unitRegistry);
    }

    /**
     * Validates a translated model for dimensional consistency.
     * Throws DimensionalMismatchException if validation fails.
     */
    public void validate(ScientificModelDto dto) {
        Model coreModel = toCoreModel(dto);
        DimensionalAnalyzer.ValidationResult result = analyzer.validate(coreModel);

        if (!result.isValid()) {
            throw new DimensionalMismatchException(result.getErrors());
        }
    }

    /**
     * Converts ScientificModelDto to core.Model for dimensional analysis.
     */
    private Model toCoreModel(ScientificModelDto dto) {
        Model.Builder builder = Model.builder(
                dto.getId() != null ? dto.getId() : "web-model",
                dto.getDomain() != null ? dto.getDomain() : "unknown");

        if (dto.getDescription() != null && !dto.getDescription().isBlank()) {
            builder.description(dto.getDescription());
        }

        // Convert quantities
        if (dto.getQuantities() != null) {
            for (com.clauneck.web.dto.Quantity dtoQty : dto.getQuantities()) {
                Quantity coreQty = toCoreQuantity(dtoQty);
                builder.quantity(coreQty);
            }
        }

        // Convert equations
        if (dto.getEquations() != null) {
            for (com.clauneck.web.dto.EquationDto dtoEq : dto.getEquations()) {
                Equation coreEq = toCoreEquation(dtoEq);
                builder.equation(coreEq);
            }
        }

        // Copy initial conditions
        if (dto.getInitialConditions() != null) {
            for (String key : dto.getInitialConditions().keySet()) {
                builder.initialCondition(key, dto.getInitialConditions().get(key));
            }
        }

        return builder.build();
    }

    /**
     * Converts web DTO Quantity to core Quantity.
     */
    private Quantity toCoreQuantity(com.clauneck.web.dto.Quantity dtoQty) {
        Optional<Object> value = dtoQty.getValue() != null
                ? Optional.of(dtoQty.getValue())
                : Optional.empty();

        Dimension dimension = toDimension(dtoQty.getDimensionVector());

        return new Quantity(
                dtoQty.getName(),
                value,
                dtoQty.getSiUnit() != null ? dtoQty.getSiUnit() : "dimensionless",
                dimension,
                dtoQty.isKnown(),
                dtoQty.getDescription() != null
                        ? Optional.of(dtoQty.getDescription())
                        : Optional.empty());
    }

    /**
     * Converts web DTO EquationDto to core Equation.
     */
    private Equation toCoreEquation(com.clauneck.web.dto.EquationDto dtoEq) {
        Equation.Type type = parseEquationType(dtoEq.getType());

        return new Equation(
                dtoEq.getLhs(),
                dtoEq.getRhs(),
                type,
                dtoEq.getDescription() != null
                        ? Optional.of(dtoEq.getDescription())
                        : Optional.empty());
    }

    /**
     * Converts web DTO DimensionVector to core Dimension.
     */
    private Dimension toDimension(DimensionVector dto) {
        if (dto == null) {
            return Dimension.DIMENSIONLESS;
        }

        return new Dimension(
                dto.getLength(),
                dto.getMass(),
                dto.getTime(),
                dto.getElectricCurrent(),
                dto.getTemperature(),
                dto.getAmountOfSubstance(),
                dto.getLuminousIntensity());
    }

    /**
     * Parses equation type from string ("algebraic", "ode", "pde", "constraint").
     */
    private Equation.Type parseEquationType(String typeStr) {
        if (typeStr == null || typeStr.isBlank()) {
            return Equation.Type.ALGEBRAIC;
        }

        try {
            return Equation.Type.fromSchemaValue(typeStr);
        } catch (IllegalArgumentException e) {
            // Default to ALGEBRAIC if type is unrecognized
            return Equation.Type.ALGEBRAIC;
        }
    }
}
