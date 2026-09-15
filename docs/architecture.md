# Clauneck Architecture: Scientific Prototyping Platform

**Status**: All 21 domains implemented + operational (Phase 4 complete)  
**Date**: 2026-09-15  
**Vision**: Deterministic, universal scientific prototyping across math, physics, chemistry, and beyond.

## Overview

Clauneck is a **monorepo, polyglot** platform where users describe a scientific idea in natural language, the system translates it into a formal model, validates it, solves it deterministically, and returns results.

```
User's Idea (NL)
    ↓
[Translator: LLM + dynamic prompts (ClaudeTranslator)]
    ↓
Scientific Model (JSON, validated against schema)
    ↓
[Engine: 21 domain-specific solvers via registry auto-discovery]
    ↓
Results (Trajectory, Summary, deterministic byte-for-byte identical)
```

**Key property**: All computation downstream of translation is deterministic — identical Model in always produces identical output out.

---

## Domain Coverage

**21 total domains** (all operational as of Phase 4):

| Category | Count | Domains |
|----------|-------|---------|
| **Mathematics** | 10 | algebra, calculus, complex_numbers, geometry, linear_algebra, number_theory, ode, optimization, statistics, trigonometry |
| **Physics** | 6 | mechanics (existing), thermodynamics, waves, electromagnetism, simple_harmonic_motion, collisions |
| **Chemistry** | 5 | kinetics, equilibrium, thermochemistry, acid_base_equilibrium, redox_reactions |
| **Total** | **21** | All auto-discovered via `@register` decorator + registry |

All 21 domains accessible via `/api/prototype` (LLM translator) and `/api/solve` (direct engine).

---

## Architecture Layers

### Layer 1: Schema (`schemas/model.schema.json`)

Language-agnostic JSON Schema defining the complete Model contract:

- **Metadata**: ID, domain (21-element enum), description, audit trail
- **Quantities**: Variables, constants, unknowns with SI units and dimensional vectors
- **Equations**: Symbolic equations and constraints (algebraic, ODE, PDE, constraint)
- **Initial/Boundary Conditions**: Starting values for integration
- **Solver Config**: Numeric method (RK45, RK23, etc.), tolerance, time span

**Single source of truth**: Both Java and Python validate against this schema.

### Layer 2: Translator (Spring Boot `web` module)

**Responsibility**: Convert natural language → validated Model JSON

- Takes user input: *"Ideal gas pressure with n=1 mol, R=8.314, T=300K, V=0.024 m³"*
- Calls Claude (structured output mode, constrained to schema)
- Validates result against `schemas/model.schema.json`
- Returns resolved Model + any issues
- **Important**: LLM never touches computation; it only produces a Model structure

**Translator Prompt Generalization (Phase 1)**:
- Prompts externalized to `web/src/main/resources/translator-prompts/<domain>.txt` (21 files)
- `SUPPORTED_DOMAINS` derived from filenames (single source of truth)
- Adding a new domain = create 1 file + commit (no Java code changes needed)

REST endpoint: `POST /api/prototype`

### Layer 3: Validator (Java `core` module)

**Responsibility**: Dimensional analysis and consistency checking

Components:
- **`UnitRegistry`**: Parses unit strings ("m/s", "kg*m/s^2") → Dimension vectors
- **`Dimension`**: Dimensional arithmetic (multiply, divide, power)
- **`DimensionalAnalyzer`**: Validates all quantities have consistent units, equations reference known variables

Runs before solver is invoked; catches nonsense early.

### Layer 4: Compute Engine (Python `engine` module)

**Responsibility**: Deterministic solving via domain-specific solvers

- **Input**: Validated ScientificModel (Pydantic models matching schema)
- **Architecture**: 
  - `GeneralSolver.solve(model)` → look up domain-specific solver via registry
  - Each solver inherits from `SolverBase` and implements `solve(model) → SolverResult`
  - Auto-discovery via `@register(domain)` decorator + `pkgutil.iter_modules`
- **Solver Pattern** (DRY via `app/solvers/utils.py`):
  - All 21 solvers follow **function-dispatch** pattern
  - Core helper `run_dispatch(model, quantities, operations_dict)` handles:
    - Parse equation.rhs as `func_name(arg1, arg2, ...)`
    - Resolve arguments (quantity names or numeric literals)
    - Call `operations[func_name](*args)`
    - Accumulate results in summary dict
  - Each solver provides dict of operation functions
- **Output**: Trajectory (optional), summary statistics, deterministic guarantee
- **Deployment**: Persistent FastAPI service (not per-request) for efficiency
- **Determinism**: Pinned dependencies, explicit solver config, no unseeded randomness

REST endpoint: `POST /api/solve`

### Layer 5: API Gateway (Spring Boot `web` module)

**Responsibility**: Orchestrate the full pipeline

- Accept user query (NL string)
- Call Translator layer (Claude)
- Call Validator layer (dimensional check, domain-specific validation)
- Call Compute Engine layer (solve)
- Return complete response: Model + Results

REST endpoint: `POST /api/prototype`

---

## Solver Dispatch & DRY Pattern

### How Solver Discovery Works

1. **Registry initialization** (`app/solvers/registry.py`):
   - `load_all()` uses `pkgutil.iter_modules` to find all `.py` files in `app/solvers/`
   - Each file imports, triggering `@register(domain)` decorators
   - Populates global dict `_SOLVERS: Dict[str, Type[SolverBase]]`

2. **Routing** (`app/solver.py`):
   - `GeneralSolver.solve(model)` calls `registry.get_solver(model.domain)`
   - Instantiates `solver_cls()` and calls `.solve(model)`
   - Returns `SolverResult`

3. **No manual wiring**: Add a new domain solver → auto-discovered on next startup

### Function-Dispatch Pattern (All 21 Solvers)

**Example: Chemistry Kinetics**

```python
def _first_order_concentration(A0: float, k: float, t: float) -> float:
    return float(A0 * np.exp(-k * t))

def _first_order_half_life(k: float) -> float:
    if k <= 0: raise ValueError("k > 0")
    return float(np.log(2) / k)

_OPERATIONS = {
    "first_order_concentration": _first_order_concentration,
    "first_order_half_life": _first_order_half_life,
    ...
}

@register("chemistry.kinetics")
class ChemistryKineticsSolver(SolverBase):
    def solve(self, model):
        quantities = {q.name: q for q in model.quantities}
        summary = run_dispatch(model, quantities, _OPERATIONS)
        return SolverResult(success=True, ..., summary=summary)
```

**User provides model with equations like**:
- `{"lhs": "[A]_t", "rhs": "first_order_concentration(A0, k, t)"}`

**`run_dispatch` does**:
1. Parse `first_order_concentration(A0, k, t)` → ("first_order_concentration", ["A0", "k", "t"])
2. Resolve args: ["A0", "k", "t"] → [0.1, 0.05, 10.0]
3. Call `_first_order_concentration(0.1, 0.05, 10.0)`
4. Store result in `summary["[A]_t"]`

**Benefits**:
- **Zero code duplication**: `run_dispatch` shared across all solvers
- **Standardized error handling**: ValueError → SolverResult(error=...)
- **Deterministic**: Pure functions, no state
- **Extensible**: Add operation = add function + dict entry

---

## Vertical Slice: Ideal Gas Law (Physics Thermodynamics)

**Example**: "Ideal gas pressure with n=1 mol, R=8.314, T=300K, V=0.024 m³"

### Step 1: Translate (LLM)
```
Input: "Ideal gas pressure with n=1, R=8.314, T=300, V=0.024"

Output (Model JSON):
{
  "id": "thermo-1",
  "domain": "physics.thermodynamics",
  "quantities": [
    {"name": "n", "value": 1.0, "siUnit": "mol", "isKnown": true},
    {"name": "R", "value": 8.314, "siUnit": "J/(mol*K)", "isKnown": true},
    {"name": "T", "value": 300.0, "siUnit": "K", "isKnown": true},
    {"name": "V", "value": 0.024, "siUnit": "m^3", "isKnown": true}
  ],
  "equations": [
    {"lhs": "P", "rhs": "ideal_gas_pressure(n, R, T, V)", "type": "algebraic"}
  ],
  "solver": {"method": "SYMBOLIC_SOLVE", "tolerance": 1e-6}
}
```

### Step 2: Validate
- All quantities present, positive, finite ✓
- Solver method valid ✓
- Domain enum includes `physics.thermodynamics` ✓

### Step 3: Solve (Python Engine)
```python
# Locate solver via registry
solver_cls = registry.get_solver("physics.thermodynamics")
solver = solver_cls()

# run_dispatch orchestrates:
quantities = {"n": Quantity(...), "R": Quantity(...), ...}
summary = run_dispatch(model, quantities, {
    "ideal_gas_pressure": _ideal_gas_pressure,
    ...
})

# _ideal_gas_pressure(1.0, 8.314, 300.0, 0.024)
# = 1 * 8.314 * 300 / 0.024
# = 103925 Pa
```

### Step 4: Return Results
```json
{
  "model": { ... (echo the model) },
  "result": {
    "success": true,
    "message": "Thermodynamics solved successfully",
    "summary": {
      "P": 103925.0
    }
  }
}
```

---

## Determinism & Reproducibility

**Guarantee**: Identical Model input → identical (byte-for-byte) output.

### Implementation
1. **Schema validation**: No silent coercion or defaults; explicit is required
2. **Dependency pinning**: `pyproject.toml` specifies ≥ versions (full lockfile pending)
3. **Deterministic algorithms**: RK45/RK23 solvers with explicit method/tolerance (no random seeds)
4. **Explicit config**: Solver method, tolerance, time span all specified in Model, never inferred
5. **Golden-file tests**: Fixed Model → run twice, assert identical summary (226 such tests)

### Testing
- Unit tests for Dimension arithmetic, UnitRegistry parsing
- Integration tests for DimensionalAnalyzer + Model validation
- End-to-end tests for full solve path (Model → trajectory)
- Determinism tests: solve twice, compare trajectories and summaries (≥1 per domain)
- Error-path tests: invalid inputs → proper SolverResult(success=False, error=...) (≥1 per domain)

**Current status**: 226 passing tests (1 pre-existing flaky ODE test excluded)

---

## Future Extensions

### Phase 5+ Roadmap

1. **Enhanced Chemistry** (Phase 3):
   - Organic synthesis mechanisms
   - Electrochemistry details
   - Phase diagrams

2. **Quantum Mechanics** (Phase 4):
   - Particle in a box
   - Hydrogen atom
   - Molecular orbitals

3. **Advanced Physics** (Phase 4):
   - Fluid dynamics (PDEs)
   - Relativity
   - Quantum field theory

4. **Knowledge Base**:
   - Curated library of constants (Planck, Avogadro, etc.)
   - Formula library (kinematic, thermodynamic, etc.)
   - Both Translator and Validator reference KB

5. **UI / Notebook Interface**:
   - Web UI: input NL, see model + plots interactively
   - Export trajectories to CSV, plots to PNG
   - Jupyter integration

6. **Performance Solver**:
   - For large ODE systems, bridge to Rust or Julia via sidecar
   - Keep same REST/HTTP contract, swap backend

7. **CI/CD Integration**:
   - Add Python test stage to GitHub Actions
   - Coverage reports for both Java and Python
   - Multi-OS testing (Linux, macOS, Windows)

---

## Build & Test Commands

See `Makefile` for full orchestration:

```bash
make build      # gradle build + python setup
make test       # gradle test + pytest (226 tests)
make clean      # clean all artifacts
make run        # start engine FastAPI service
```

Individual commands:
```bash
gradle :core:build              # Build core module
gradle :core:test               # Test core module
gradle :web:test                # Test web module
cd engine && pytest              # Test Python engine (226 tests)
cd engine && python -m uvicorn app.main:app --port 8001  # Run engine
```

---

## References

- **Schema Contract**: `schemas/model.schema.json`
- **Solver Registry**: `engine/app/solvers/registry.py`
- **Translator Prompts**: `web/src/main/resources/translator-prompts/` (21 files)
- **Test Examples**: `engine/tests/test_*.py` (226 total)
- **Decisions**: See ADRs in `docs/adr/`
- **CLAUDE.md**: Project patterns and conventions

---

**Last updated**: Phase 4 complete (schema + translator prompts for all 21 domains)
