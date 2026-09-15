package com.clauneck.core.model;

import static org.junit.Assert.*;

import com.clauneck.core.units.Dimension;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jdk8.Jdk8Module;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;
import java.util.Optional;
import org.junit.Before;
import org.junit.Test;

public class ModelSerializationTest {
  private ObjectMapper objectMapper;

  @Before
  public void setUp() {
    objectMapper = new ObjectMapper()
        .registerModule(new Jdk8Module())
        .registerModule(new JavaTimeModule());
  }

  @Test
  public void testSchemaPropertyAndEnumMappingsRoundTrip() throws Exception {
    Model model = Model.builder("mapping", "mathematics.general")
        .quantity(Quantity.builder("current")
            .value(1)
            .siUnit("A")
            .dimension(Dimension.CURRENT_DIMENSION)
            .build())
        .equation(Equation.builder()
            .lhs("current")
            .rhs("current")
            .type(Equation.Type.ALGEBRAIC)
            .build())
        .initialCondition("current", 1)
        .solverConfig(SolverConfig.builder()
            .method(SolverConfig.Method.SOLVE_IVP)
            .tolerance(1e-6)
            .timeSpan(new SolverConfig.TimeSpan(0, 1, Optional.of(10)))
            .build())
        .build();

    JsonNode json = objectMapper.readTree(objectMapper.writeValueAsString(model));

    assertTrue(json.has("solver"));
    assertFalse(json.has("solverConfig"));
    assertEquals("solve_ivp", json.at("/solver/method").asText());
    assertEquals("algebraic", json.at("/equations/0/type").asText());
    assertEquals(1.0, json.at("/initialConditions/values/current").asDouble(), 0.0);
    assertTrue(json.at("/quantities/0").has("dimensionVector"));
    assertFalse(json.at("/quantities/0").has("dimension"));
    assertEquals(1.0,
        json.at("/quantities/0/dimensionVector/electricCurrent").asDouble(), 0.0);

    Model roundTripped = objectMapper.treeToValue(json, Model.class);
    assertEquals(SolverConfig.Method.SOLVE_IVP, roundTripped.getSolverConfig().getMethod());
    assertEquals(Equation.Type.ALGEBRAIC, roundTripped.getEquations().get(0).getType());
    assertEquals(Dimension.CURRENT_DIMENSION,
        roundTripped.getQuantities().get(0).getDimension());
    assertEquals(1.0, roundTripped.getInitialConditions().get("current"), 0.0);
  }

  @Test(expected = com.fasterxml.jackson.databind.JsonMappingException.class)
  public void testMissingRequiredSolverIsRejected() throws Exception {
    objectMapper.readValue(
        "{\"id\":\"missing-solver\",\"domain\":\"mathematics.general\","
            + "\"quantities\":[],\"equations\":[]}",
        Model.class);
  }
}
