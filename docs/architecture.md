# Clauneck Architecture: Scientific Prototyping Platform

**Status**: Vertical slice complete (projectile motion example)  
**Date**: 2026-09-15  
**Vision**: Deterministic, optimized, efficient, smart, and configurable platform for rapid scientific prototyping across math, physics, chemistry, and other domains.

## Overview

Clauneck is a **monorepo, polyglot** platform where users describe a scientific idea in natural language, the system translates it into a formal model, validates it, solves it, and returns deterministic results.

```
User's Idea (NL)
    ↓
[Translator: LLM + Schema validation]
    ↓
Scientific Model (JSON)
    ↓
[Validator: Dimensional analysis]
    ↓
[Compute Engine: Symbolic + Numeric]
    ↓
Results (Trajectory, Summary)
```

**Key property**: All computation downstream of translation is deterministic — identical Model in always produces identical output out.

---

## Architecture Layers

### Layer 1: Schema (`schemas/model.schema.json`)

Language-agnostic JSON Schema defining the complete Model contract:

- **Metadata**: ID, domain (e.g., `physics.mechanics`), description, audit trail
- **Quantities**: Variables, constants, unknowns with SI units and dimensional vectors
- **Equations**: Symbolic equations and constraints (algebraic, ODE, PDE, constraint)
- **Initial/Boundary Conditions**: Starting values for integration
- **Solver Config**: Numeric method (RK45, RK23, etc.), tolerance, time span

Both Java and Python validate against this schema — no duplication, single source of truth.

### Layer 2: Translator (Spring Boot `web` module)

**Responsibility**: Convert natural language → validated Model JSON

- Takes user input: *"I launch a ball at 20 m/s at 45°, mass 0.5kg, drag coefficient 0.1 — how far does it go?"*
- Calls Claude (structured output mode, constrained to schema)
- Validates result against `schemas/model.schema.json`
- Returns resolved Model + any issues
- **Important**: LLM never touches computation; it only produces a Model structure

REST endpoint: `POST /api/prototype` (to be implemented)

### Layer 3: Validator (Java `core` module)

**Responsibility**: Dimensional analysis and consistency checking

Components:
- **`UnitRegistry`**: Parses unit strings ("m/s", "kg*m/s^2") → Dimension vectors
- **`Dimension`**: Dimensional arithmetic (multiply, divide, power)
- **`DimensionalAnalyzer`**: Validates all quantities have consistent units, equations reference known variables

Runs before solver is invoked; catches nonsense early.

### Layer 4: Compute Engine (Python `engine` module)

**Responsibility**: Deterministic solving via SymPy (symbolic) + SciPy (numeric)

- **Input**: Validated ScientificModel (Pydantic models matching schema)
- **Processing**:
  - Parse equations symbolically
  - Set up ODE/algebraic system
  - Integrate numerically (e.g., `solve_ivp` with user-specified method/tolerance)
- **Output**: Trajectory, summary statistics
- **Deployment**: Persistent FastAPI service (not per-request subprocess) for efficiency
- **Determinism**: Dependencies pinned via lockfile; solver method/tolerance explicit; no unseeded randomness

REST endpoint: `POST /api/solve` (returns `PrototypeResponse`)

### Layer 5: API Gateway (Spring Boot `web` module)

**Responsibility**: Orchestrate the full pipeline

- Accept user query (NL string)
- Call Translator layer (Claude)
- Call Validator layer (dimensional check)
- Call Compute Engine layer (solve)
- Return complete response: Model + Results

---

## Directory Layout

```
clauneck/
├── schemas/
│   └── model.schema.json           # Shared contract (Java + Python)
├── core/
│   ├── src/main/java/
│   │   └── com/clauneck/core/
│   │       ├── units/              # UnitSystem, Dimension, Unit, UnitRegistry
│   │       ├── model/              # Model, Quantity, Equation, Solver config
│   │       └── validation/          # DimensionalAnalyzer
│   └── build.gradle                # JUnit 5 for tests
├── engine/
│   ├── app/
│   │   ├── main.py                 # FastAPI app + /api/solve endpoint
│   │   ├── model.py                # Pydantic models (from schema)
│   │   └── solver.py               # Numeric/symbolic solver (SymPy, SciPy)
│   ├── tests/
│   │   └── test_projectile.py      # Projectile motion unit + golden tests
│   └── pyproject.toml              # Dependencies (sympy, scipy, fastapi, etc.)
├── web/
│   ├── src/main/java/
│   │   └── com/clauneck/web/
│   │       ├── api/                # PrototypeController
│   │       ├── translator/         # ClaudeTranslatorClient
│   │       └── engine/             # EngineClient (HTTP calls to engine)
│   └── build.gradle                # Spring Boot 3.2.2
├── api/
│   └── build.gradle                # (unchanged; for future use)
├── docs/
│   ├── architecture.md             # This file
│   └── adr/
│       ├── 0001-polyglot-monorepo.md
│       └── 0002-llm-translator-boundary.md
├── Makefile                        # Root orchestration: make build, make test, make run
├── CLAUDE.md                       # (updated) Project conventions + new engine section
└── settings.gradle                 # Includes: core, web, api
```

---

## Vertical Slice: Projectile Motion

**Proof-of-concept**: End-to-end demonstration of all layers.

### Example: "I launch a ball at 20 m/s at 45°, mass 0.5kg, drag coefficient 0.1"

#### Step 1: Translate (LLM)
```
Input: "I launch a ball at 20 m/s at 45°, mass 0.5kg, drag coefficient 0.1 — how far does it go?"

Output (Model JSON):
{
  "id": "projectile-1",
  "domain": "physics.mechanics",
  "quantities": [
    {"name": "v0", "value": 20, "siUnit": "m/s", "isKnown": true},
    {"name": "angle", "value": 45, "siUnit": "deg", "isKnown": true},
    {"name": "mass", "value": 0.5, "siUnit": "kg", "isKnown": true},
    {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
    {"name": "drag_coeff", "value": 0.1, "siUnit": "dimensionless", "isKnown": true}
  ],
  "equations": [
    {
      "lhs": "d2x/dt2",
      "rhs": "-drag_coeff * vx * |v| / mass"
    },
    {
      "lhs": "d2y/dt2", 
      "rhs": "-g - drag_coeff * vy * |v| / mass"
    }
  ],
  "solver": {
    "method": "RK45",
    "tolerance": 1e-6,
    "timeSpan": {"start": 0, "end": 5, "numPoints": 500}
  }
}
```

#### Step 2: Validate (Dimensional Analysis)
- v0: "m/s" → Dimension(L=1, T=-1) ✓
- angle: "rad" → Dimensionless ✓
- mass: "kg" → Dimension(M=1) ✓
- g: "m/s^2" → Dimension(L=1, T=-2) ✓
- All equations reference known variables ✓

#### Step 3: Solve (Python Engine)
```python
# ODE system:
# dx/dt = vx
# dy/dt = vy
# dvx/dt = -0.1 * vx * sqrt(vx^2 + vy^2) / 0.5
# dvy/dt = -9.81 - 0.1 * vy * sqrt(vx^2 + vy^2) / 0.5

# Solve via RK45, tolerance 1e-6
# Output: trajectory points + summary
```

#### Step 4: Return Results
```json
{
  "model": { ... (echo the model) },
  "result": {
    "success": true,
    "trajectory": {
      "t": [0, 0.01, ..., 3.5],
      "x": [0, ..., 32.5],
      "y": [0, ..., 0],
      ...
    },
    "summary": {
      "max_range": 32.5,
      "max_height": 8.2,
      "flight_time": 3.5
    }
  }
}
```

---

## Determinism & Reproducibility

**Guarantee**: Identical Model input → identical (byte-for-byte) output.

### Implementation
1. **Schema validation**: No silent coercion or defaults; explicit is required
2. **Dependency pinning**: `pyproject.toml` + lockfile pin all versions
3. **Deterministic algorithms**: RK45/RK23 solvers with fixed seed (if any randomness introduced)
4. **Explicit config**: Solver method, tolerance, time span all specified in Model, never inferred
5. **Golden-file tests**: Fixed Model → verify output byte-for-byte (run twice, should match)

### Testing
- Unit tests for Dimension arithmetic, UnitRegistry parsing
- Integration tests for DimensionalAnalyzer + Model validation
- End-to-end tests for full solve path (Model → trajectory)
- Determinism tests: solve twice, compare trajectories and summaries

---

## Future Extensions

### Generalize Schema
- Extend `domain` enum to include `chemistry.kinetics`, `mathematics.general`, etc.
- Add domain-specific quantity types and equation patterns

### Knowledge Base
- Build a curated library of constants (Planck's constant, Avogadro's number, etc.)
- Formula library: kinematic equations, reaction-rate laws, thermodynamic relations
- Both Translator and Validator reference the KB

### Second Domain Module
- Implement `chemistry.kinetics` solver (coupled reaction-rate ODEs)
- Validate that schema + architecture generalize

### UI / Notebook Interface
- Web UI: input natural language, see model + plots interactively
- Export trajectories to CSV, plots to PNG

### Performance Solver
- For large ODE systems, bridge to Rust or Julia via sidecar service
- Keep same REST/HTTP contract, swap backend solver

### CI/CD Integration
- Add Python module to GitHub Actions
- Separate test stages: `gradle test` + `pytest`
- Coverage reports for both Java and Python

---

## Build & Test Commands

See `Makefile` for full orchestration:

```bash
make build      # gradle build + python setup
make test       # gradle test + pytest
make clean      # clean all artifacts
make run        # start engine FastAPI service
```

Individual commands:
```bash
gradle :core:build              # Build core module
gradle :core:test               # Test core module
cd engine && pytest      # Test Python engine
cd engine && python -m uvicorn app.main:app --port 8001  # Run engine
```

---

## References

- **Schema Contract**: `schemas/model.schema.json`
- **AI-Native SDLC**: `.claude/SDLC-README.md`
- **Decisions**: See ADRs in `docs/adr/`

---

## Next Steps (Not This Slice)

1. Implement Translator layer (Claude API integration in Spring Boot)
2. Implement PrototypeController + EngineClient to orchestrate pipeline
3. Test full end-to-end flow locally
4. Add chemistry.kinetics domain (second vertical slice)
5. Extend schema + knowledge base for generalizable domains
