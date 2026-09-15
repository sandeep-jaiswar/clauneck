package com.clauneck.web.dto;

import com.fasterxml.jackson.annotation.JsonInclude;
import com.fasterxml.jackson.annotation.JsonProperty;

@JsonInclude(JsonInclude.Include.NON_NULL)
public class Quantity {

    private String name;
    private String description;
    private Object value;
    private String siUnit;
    private DimensionVector dimensionVector;

    // Jackson strips "is" from boolean getter names by default (isKnown() -> "known"),
    // which would silently rename this field on the wire. Pin it explicitly so it
    // stays "isKnown" to match schemas/model.schema.json and engine/app/model.py.
    @JsonProperty("isKnown")
    private boolean isKnown;

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public String getDescription() {
        return description;
    }

    public void setDescription(String description) {
        this.description = description;
    }

    public Object getValue() {
        return value;
    }

    public void setValue(Object value) {
        this.value = value;
    }

    public String getSiUnit() {
        return siUnit;
    }

    public void setSiUnit(String siUnit) {
        this.siUnit = siUnit;
    }

    public DimensionVector getDimensionVector() {
        return dimensionVector;
    }

    public void setDimensionVector(DimensionVector dimensionVector) {
        this.dimensionVector = dimensionVector;
    }

    @JsonProperty("isKnown")
    public boolean isKnown() {
        return isKnown;
    }

    @JsonProperty("isKnown")
    public void setKnown(boolean known) {
        isKnown = known;
    }
}
