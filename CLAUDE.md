# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**clauneck** is a scientific prototyping platform: deterministic, efficient, smart, configurable. Users describe math/physics/chemistry ideas; the system models, validates, and solves them.

**Architecture**: Polyglot monorepo (Java + Python) with LLM translation boundary + deterministic computation.

### Domain Coverage (33 total: 28 implemented + 5 planned)

**Mathematics** (17 domains, all implemented):
- algebra, calculus, complex_numbers, discrete_math, geometry, graph_theory, linear_algebra, number_theory, numerical_methods, ode, optimization, pde, probability, sequences_series, statistics, trigonometry, vector_calculus

**Physics** (11 domains: 6 implemented + 5 planned):
- **Implemented**: mechanics, thermodynamics, waves, electromagnetism, simple_harmonic_motion, collisions
- **Planned**: fluid_mechanics, optics, quantum_mechanics, rotational_dynamics, special_relativity

**Chemistry** (5 domains, all implemented):
- kinetics, equilibrium, thermochemistry, acid_base_equilibrium, redox_reactions

### Modules
- **core** (Java): UnitSystem, dimensional analysis, schema validation
- **web** (Java, Spring Boot 3.2.2): API gateway, translator layer (Claude LLM), engine orchestration
- **engine** (Python, FastAPI): Symbolic + numeric solving (SymPy, SciPy, NumPy)
- **schemas**: JSON Schema contract shared across Java + Python
- **web/src/main/resources/translator-prompts/**: 28 domain-specific prompt fragments (one .txt file per implemented domain)

### Technology Stack
- **Java**: 21, Gradle (wrapper pinned to 8.10), Spring Boot 3.2.2, JUnit 5
- **Python**: 3.10+, FastAPI, SymPy, NumPy, SciPy
- **Schema**: JSON Schema (schemas/model.schema.json)
- **CI/CD**: GitHub Actions (on push/PR to production)

### Key Design Decisions
See `docs/adr/` for full rationale:
- **0001-polyglot-monorepo**: Why two languages + one repo
- **0002-llm-translator-boundary**: Why LLM is only for translation, not computation
- **0003-domain-prompt-externalization** (Phase 1): Externalize translator prompts to `translator-prompts/*.txt` to eliminate hardcoded domain lists

## Build and Development Commands

### Unified (Root Makefile)
```bash
make build                # Build all (Gradle + Python)
make test                 # Test all (Gradle + Python)
make run                  # Start engine FastAPI service
make clean                # Clean all build artifacts
```

### Java / Gradle
```bash
./gradlew build              # Build all Java modules and run tests
./gradlew build -x test      # Build without running tests
./gradlew clean              # Clean (.gradle, build/)
./gradlew :core:test         # Test core module
./gradlew :web:test          # Test web module (translator, engine client, controller)
./gradlew :web:bootRun       # Start the Spring Boot API gateway on :8080 (requires ANTHROPIC_API_KEY)
./gradlew tasks              # List all available tasks
```

Environment setup for translator layer:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."  # Required for Claude API calls
export CLAUDE_MODEL="claude-haiku-4-5"  # Optional, defaults to Haiku
export CLAUNECK_ENGINE_URL="http://localhost:8001"  # Optional, defaults to localhost:8001
```

### Python / Engine
```bash
cd engine && python -m pip install -e .                    # Install engine + deps
cd engine && python -m pip install -e ".[dev]"             # Install with test deps
cd engine && python -m pytest tests/ -v                    # Run all solver tests (556 tests)
cd engine && python -m pytest tests/test_physics_thermodynamics.py -v  # Test single domain
cd engine && python -m uvicorn app.main:app --port 8001    # Start FastAPI service
```

### Polyglot Notes
- Gradle and pip manage dependencies independently
- Schema (JSON) is the contract; both sides validate against it
- `Makefile` provides one entry point for common tasks
- CI runs both `gradle build` and `pytest` (see `.github/workflows/ci.yml`)

## Project Structure

```
clauneck/
├── schemas/
│   └── model.schema.json              # Shared contract (Java + Python)
├── core/                              # Java: units, dimensions, validation
├── engine/                            # Python: SymPy + SciPy solver
│   ├── app/
│   │   ├── main.py                  # FastAPI /api/solve endpoint
│   │   ├── model.py                 # Pydantic models (from schema)
│   │   ├── solver.py                # GeneralSolver (routes by domain)
│   │   └── solvers/
│   │       ├── base.py              # SolverBase ABC
│   │       ├── registry.py          # @register decorator + auto-discovery
│   │       ├── utils.py             # Shared DRY helpers (run_dispatch, get_value, etc.)
│   │       ├── physics_*.py         # 6 physics solvers (21 files total)
│   │       ├── chemistry_*.py       # 5 chemistry solvers
│   │       └── mathematics_*.py     # 10 math solvers
│   ├── tests/
│   │   └── test_*.py                # 556 tests (determinism + correctness + error paths)
│   └── pyproject.toml               # Dependencies + build config
├── web/                              # Java: Spring Boot API gateway
│   ├── src/main/java/com/clauneck/web/
│   │   ├── api/PrototypeController.java       # REST endpoint /api/prototype
│   │   ├── service/ClaudeTranslator.java      # LLM translation (loads prompts from resources)
│   │   ├── service/SchemaValidator.java       # JSON-schema validation
│   │   ├── exception/                        # Error handling (401/502/503/etc)
│   │   └── client/EngineClient.java          # HTTP client to Python engine
│   ├── src/main/resources/translator-prompts/  # 21 .txt files (one per domain)
│   └── build.gradle
├── docs/
│   ├── architecture.md              # System design + patterns
│   └── adr/                         # Architecture Decision Records
├── Makefile                         # Root orchestration
├── CLAUDE.md                        # This file
├── build.gradle                     # Root Gradle config
├── settings.gradle                  # Gradle module definitions
└── .github/workflows/ci.yml         # CI pipeline
```

## Solver Architecture

### Engine Pattern: Function-Dispatch + run_dispatch

All solvers follow the **function-dispatch pattern** via `app/solvers/utils.py::run_dispatch`:

1. **Define operations** as module-level functions (not methods)
   ```python
   def _ideal_gas_pressure(n, R, T, V):
       if V <= 0: raise ValueError("V > 0")
       return n * R * T / V
   
   _OPERATIONS = {"ideal_gas_pressure": _ideal_gas_pressure, ...}
   ```

2. **Dispatch via equations**: solver parses each equation.rhs as `func_name(arg1, arg2, ...)`

3. **Core DRY helper** (`run_dispatch`):
   - Parse equation.rhs → (func_name, [arg_strs])
   - Resolve arguments (literals or quantity names)
   - Call _OPERATIONS[func_name](*args)
   - Accumulate results in summary dict

**Why this pattern:**
- **Zero code duplication** across 21 solvers (shared run_dispatch)
- **Error handling standardized** (ValueError → error string in SolverResult)
- **Deterministic** (pure functions, no randomness)
- **Extensible** (add new operation = add function + register in dict)

### Solver Classes (all registered via `@register` decorator)

Auto-discovery via `registry.load_all()` in `app.main`. No manual wiring.

**Physics solvers** (5 new + 1 existing mechanics):
- `physics.thermodynamics`: ideal gas, work, heat, Carnot, entropy
- `physics.waves`: wave speed, Doppler, standing waves, beats
- `physics.electromagnetism`: Coulomb, circuits, capacitors, magnetic force
- `physics.simple_harmonic_motion`: springs, pendulums, damping, SHM position
- `physics.collisions`: elastic/inelastic, momentum, CoR, impulse

**Chemistry solvers** (5 new):
- `chemistry.kinetics`: rate laws (0/1/2-order), half-life, Arrhenius
- `chemistry.equilibrium`: Q, K, Le Chatelier direction
- `chemistry.thermochemistry`: Hess, ΔH_rxn, calorimetry, bond energy
- `chemistry.acid_base_equilibrium`: pH, pOH, Henderson-Hasselbalch, Ka/pKa, weak acid, titration
- `chemistry.redox_reactions`: E_cell, Nernst, ΔG, K from E°

**Math solvers** (10 existing, unchanged):
- algebra, calculus, complex_numbers, geometry, linear_algebra, number_theory, ode, optimization, statistics, trigonometry

### Shared Helpers (`app/solvers/utils.py`)

Used by all 10 new solvers (Phase 2+ only; original 11 have local helpers for backward-compat):

- **`get_value(quantities, name, ic)`**: scalar lookup (ic takes precedence)
- **`get_optional_value(..., default)`**: scalar with fallback
- **`get_vector(quantities, name)`**: 1D array extraction
- **`get_matrix(quantities, name)`**: 2D array extraction
- **`to_radians(value, si_unit)`**: angle conversion (deg/rad)
- **`parse_call(expr)`**: parse `func_name(arg1, arg2, ...)` → (func_name, [args])
- **`resolve_arg(arg, quantities)`**: literal or quantity name → value
- **`run_dispatch(model, quantities, operations)`**: multi-equation dispatch loop (the DRY core)

### Testing Strategy

Each domain has ≥2 test files:
- **Correctness tests** (2+): verify against independently computed reference values
- **Determinism tests** (1+): solve(model) twice → identical summary dict
- **Error-path tests** (1+): invalid inputs → SolverResult(success=False, error=...)
- **Routing tests** (1): GeneralSolver().solve(model) reaches correct solver

Total: 556 passing tests (1 pre-existing flaky ODE test excluded).

## Translator Layer (Java)

### ClaudeTranslator Service

**Before Phase 1**: Hardcoded domain logic in 3 places (SYSTEM_PROMPT, SUPPORTED_DOMAINS, UnsupportedDomainException)  
**After Phase 1+**: Single source of truth via `translator-prompts/*.txt` files

**How it works**:
1. At startup, load all `.txt` files from `classpath:translator-prompts/`
2. Filename (minus `.txt`) = domain string (e.g., `physics.mechanics.txt` → `physics.mechanics`)
3. File content = domain-specific prompt fragment
4. `SUPPORTED_DOMAINS = TreeMap keys` (alphabetical order, unmodifiable)
5. `SYSTEM_PROMPT = preamble + all domain fragments + footer`

**Adding a new domain**:
1. Create `web/src/main/resources/translator-prompts/<domain>.txt`
2. Commit
3. Done! Translator auto-discovers on next restart.

### Prompt Fragments

Each `.txt` file documents:
- Domain name and purpose
- Input quantities (names, units)
- Supported operations (function dispatch list)
- Solver method recommendation
- Example query

See `translator-prompts/*.txt` for current examples.

## Determinism & Reproducibility

**Guarantee**: Identical Model input → identical results (byte-for-byte, to numeric precision).

### Implementation
- Schema validation: no silent coercion
- Dependency pinning: `pyproject.toml` (≥ versions, no lockfile yet)
- Solver config explicit: method, tolerance, time span all in Model
- Determinism tests: solve(model) twice, compare summaries (35+ such tests)
- No randomness: pure functions, no unseeded generators

### Known Gaps
- No Python lockfile (only `>=` versions) – future improvement
- ODE solver `test_coupled_ode_oscillatory` is flaky (numerical issue, not code issue)

## Translator Prompt Externalization (Phase 1 ADR)

**Problem**: 3-way domain list duplication (SYSTEM_PROMPT, SUPPORTED_DOMAINS, UnsupportedDomainException) made scope expansion error-prone.

**Solution**: 
- Extract each domain's prompt paragraph into `translator-prompts/<domain>.txt`
- Load at startup via Spring's `ClassPathResource` + `Files.list()`
- Derive `SUPPORTED_DOMAINS` from filenames
- Update `UnsupportedDomainException` to accept dynamic domain list

**Benefits**:
- Single edit point: add file → automatic translator support
- Schema enum stays in sync with prompts
- New domains require no Java code changes
- Alphabetical ordering natural (TreeMap)

## Extension Points

### New Domains

1. **Write Python solver** in `engine/app/solvers/<domain>.py`:
   ```python
   from app.solvers.registry import register
   
   @register("new.domain")
   class NewDomainSolver(SolverBase):
       def solve(self, model): ...
   ```

2. **Write tests** in `engine/tests/test_new_domain.py` (330+ test pattern)

3. **Add translator prompt** in `web/src/main/resources/translator-prompts/new.domain.txt`

4. **Update schema** (if needed): extend `domain` enum (normally just add file, schema already has all 21)

5. **Commit**: auto-discovery handles the rest

### New Quantities / Constants

1. Add to schema if new fundamental type
2. Register in `core/UnitRegistry` (SI units)
3. Document in `docs/architecture.md`

## Notes for Future Development

- **Phase 0 (complete)**: Trust & Hygiene — added correctness/determinism/error-path tests for all 9 untested domains. 556 passing tests. Added Python test stage to CI, lockfile for determinism.
- **Phase 1 (complete)**: Domain Coverage — implemented all 5 missing physics domains (rotational_dynamics, optics, fluid_mechanics, quantum_mechanics, special_relativity) with tests and prompts. 735 passing tests total. **All 33 schema domains now implemented.**
- **Phase 2 (complete)**: Wire the dormant DimensionalAnalyzer into the live request path. Created `DimensionalMismatchException` + `DimensionalValidationService` mapping layer. All requests now validated for dimensional consistency before reaching engine. Exception handler returns 400 on mismatch with clear error details.
- **Phase 3 (next)**: Centralized knowledge base of constants (Planck, Avogadro, c, etc.) for translator + solvers.
- **Phase 4 (future)**: Demo Web UI with live plots, CSV export.
- **Phase 5 (future)**: SQLite-backed prototype history/gallery.
- **Performance**: Engine runs as persistent FastAPI service; translator uses Haiku (cost/latency optimized)
- **Maintain CLAUDE.md**: Update when new patterns emerge

## Commits & History

All phases committed separately with detailed messages:
- **Phase 1**: Bug fix + shared helpers + translator generalization (1 commit)
- **Phase 2**: 5 physics solvers (1 commit)
- **Phase 3**: 5 chemistry solvers (1 commit)
- **Phase 4**: Schema + translator prompts (1 commit)
- **Phase 5**: Docs + final tests (this commit)

## Contact & Questions

For architecture questions, see `docs/architecture.md` and `docs/adr/`.
For implementation patterns, see this file + `engine/app/solvers/utils.py`.
For test patterns, see `engine/tests/test_*.py` (especially `test_statistics.py`).
