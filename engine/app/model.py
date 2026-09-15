"""
Pydantic models for scientific prototyping engine.
Maps to schemas/model.schema.json — same contract across Java and Python.
"""
from typing import Optional, Dict, List, Union
from pydantic import BaseModel, model_validator
from enum import Enum


class EquationType(str, Enum):
    ALGEBRAIC = "algebraic"
    ODE = "ode"
    PDE = "pde"
    CONSTRAINT = "constraint"


class SolverMethod(str, Enum):
    RK45 = "RK45"
    RK23 = "RK23"
    DOP853 = "DOP853"
    SOLVE_IVP = "solve_ivp"
    ODEINT = "odeint"
    SYMBOLIC_SOLVE = "symbolic_solve"
    FSOLVE = "fsolve"


class DimensionVector(BaseModel):
    """Fundamental dimensional exponents [L, M, T, I, Θ, N, J]"""
    length: float = 0.0
    mass: float = 0.0
    time: float = 0.0
    electricCurrent: float = 0.0
    temperature: float = 0.0
    amountOfSubstance: float = 0.0
    luminousIntensity: float = 0.0


class Quantity(BaseModel):
    name: str
    description: Optional[str] = None
    value: Optional[Union[float, List[float], List[List[float]]]] = None
    siUnit: str
    dimensionVector: Optional[DimensionVector] = None
    isKnown: bool

    @model_validator(mode="after")
    def known_status_matches_value(self):
        if self.isKnown != (self.value is not None):
            raise ValueError("isKnown must be true exactly when value is present")
        return self


class Equation(BaseModel):
    lhs: str
    rhs: str
    type: EquationType = EquationType.ALGEBRAIC
    description: Optional[str] = None


class TimeSpan(BaseModel):
    start: float
    end: float
    numPoints: Optional[int] = None


class Solver(BaseModel):
    method: SolverMethod
    tolerance: float
    timeSpan: Optional[TimeSpan] = None


class Metadata(BaseModel):
    createdAt: Optional[str] = None
    source: str = "manual"
    originalQuery: Optional[str] = None
    validationErrors: Optional[List[str]] = []


class ScientificModel(BaseModel):
    """Complete scientific model for prototyping."""
    id: str
    domain: str
    description: Optional[str] = None
    quantities: List[Quantity]
    equations: List[Equation]
    initialConditions: Optional[Dict[str, float]] = {}
    boundaryConditions: Optional[List[Dict]] = []
    solver: Solver
    metadata: Optional[Metadata] = None


class SolverResult(BaseModel):
    """Result from solving a model."""
    success: bool
    message: str
    trajectory: Optional[Dict[str, List[float]]] = None
    summary: Optional[Dict[str, float]] = None
    error: Optional[str] = None


class PrototypeResponse(BaseModel):
    """Complete response with model and results."""
    model: ScientificModel
    result: SolverResult
