package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;

/**
 * "type" is kept as a raw String ("algebraic"/"ode"/"pde"/"constraint") rather
 * than a Java enum to avoid fighting casing mismatches against
 * schemas/model.schema.json and engine/app/model.py's EquationType, both of
 * which use lowercase values. SchemaValidator enforces the allowed set.
 */
@JsonInclude(JsonInclude.Include.NON_NULL)
public class EquationDto {

    private String lhs;
    private String rhs;
    private String type = "algebraic";
    private String description;

    public String getLhs() {
        return lhs;
    }

    public void setLhs(String lhs) {
        this.lhs = lhs;
    }

    public String getRhs() {
        return rhs;
    }

    public void setRhs(String rhs) {
        this.rhs = rhs;
    }

    public String getType() {
        return type;
    }

    public void setType(String type) {
        this.type = type;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }
}
