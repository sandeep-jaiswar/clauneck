# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**clauneck** is a scientific prototyping platform: deterministic, efficient, smart, configurable. Users describe math/physics/chemistry ideas; the system models, validates, and solves them.

**Architecture**: Polyglot monorepo (Java + Python) with LLM translation boundary + deterministic computation.

### Modules
- **core** (Java): UnitSystem, dimensional analysis, schema validation
- **web** (Java, Spring Boot 3.2.2): API gateway, translator layer, engine orchestration
- **engine** (Python, FastAPI): Symbolic + numeric solving (SymPy, SciPy)
- **api** (Java): Reserved for future use
- **schemas**: JSON Schema contract shared across Java + Python

### Technology Stack
- **Java**: 21, Gradle (wrapper pinned to 8.10), Spring Boot 3.2.2, JUnit 5
- **Python**: 3.10+, FastAPI, SymPy, NumPy, SciPy
- **Schema**: JSON Schema (schemas/model.schema.json)
- **CI/CD**: GitHub Actions (on push/PR to production)
- **HTTP Client**: RestTemplate (Spring Boot), direct Anthropic API calls

### Key Design Decisions
See `docs/adr/` for full rationale:
- **0001-polyglot-monorepo**: Why two languages + one repo
- **0002-llm-translator-boundary**: Why LLM is only for translation, not computation

## Build and Development Commands

### Unified (Root Makefile)
```bash
make build                # Build all (Gradle + Python)
make test                 # Test all (Gradle + Python)
make run                  # Start engine FastAPI service
make clean                # Clean all build artifacts
```

### Java / Gradle
Use the included Gradle Wrapper (Java 21 required):
```bash
./gradlew build              # Build all Java modules and run tests
./gradlew build -x test      # Build without running tests
./gradlew clean              # Clean (.gradle, build/)
./gradlew :core:test         # Test core module (dimensional analysis, unit system)
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
cd engine && python -m pytest tests/ -v                    # Run projectile motion tests
cd engine && python -m uvicorn app.main:app --port 8001    # Start FastAPI service
```

### Polyglot Notes
- Gradle and Poetry/uv manage dependencies independently
- Schema (JSON) is the contract; both sides validate against it
- `Makefile` provides one entry point for common tasks
- CI runs both `gradle build` and `pytest` (see `.github/workflows/ci.yml`)

## Project Structure

```
clauneck/
├── schemas/
│   └── model.schema.json              # Shared contract (Java + Python)
├── core/                              # Java: units, dimensions, validation
│   ├── src/main/java/.../
│   │   ├── units/                    # Dimension, Unit, UnitRegistry
│   │   ├── model/                    # Model, Quantity, Equation, SolverConfig
│   │   └── validation/               # DimensionalAnalyzer
│   ├── src/test/java/.../            # Dimension, Unit, Analyzer tests
│   └── build.gradle
├── engine/                           # Python: SymPy + SciPy solver
│   ├── app/
│   │   ├── main.py                  # FastAPI /api/solve endpoint
│   │   ├── model.py                 # Pydantic models (from schema)
│   │   └── solver.py                # ProjectileMotionSolver, GeneralSolver
│   ├── tests/
│   │   └── test_projectile.py       # Determinism + correctness tests
│   └── pyproject.toml               # Dependencies + build config
├── web/                              # Java: Spring Boot API gateway (to be completed)
│   └── build.gradle
├── api/                              # Reserved for future use
│   └── build.gradle
├── docs/
│   ├── architecture.md              # Full system design
│   └── adr/                         # Decision records
│       ├── 0001-polyglot-monorepo.md
│       └── 0002-llm-translator-boundary.md
├── Makefile                         # Root orchestration (build, test, run, clean)
├── CLAUDE.md                        # This file
├── build.gradle                     # Root Gradle config
├── settings.gradle                  # Gradle module definitions
└── .github/workflows/ci.yml         # CI (to be updated for Python)
```

**Core Directories (Java)**
- `core/src/main/java/com/clauneck/core/units/`: SI units, dimensional analysis
- `core/src/main/java/com/clauneck/core/model/`: Scientific model representation
- `core/src/main/java/com/clauneck/core/validation/`: Schema validation

**Engine (Python)**
- `engine/app/solver.py`: ProjectileMotionSolver (vertical slice), GeneralSolver (extensible)
- `engine/app/model.py`: Pydantic models matching JSON Schema

**Documentation**
- `docs/architecture.md`: System overview, layers, vertical slice example
- `docs/adr/`: Architecture Decision Records (polyglot, LLM boundary, determinism)

## Dependencies and Relationships

- **web** → **core** (web depends on core)
- **api** → **core** (api depends on core)
- **core** has no internal dependencies
- **web** and **api** are independent of each other (can run separately)

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on:
- Push to `production` branch
- Pull requests targeting `production` branch

Command: `gradle build --no-daemon`

## AI-Native SDLC Workflow

This project follows the **AI-Native SDLC** approach for continuous, AI-assisted development with human oversight. Each stage produces versioned artifacts that feed into the next stage, creating an audit trail.

### Workflow Stages (Skip Deploy)

**1. Plan** - Capture project intent as machine-readable requirements
- Command: `/sdlc plan <description>`
- Output: `intent.md` (versioned, committed)
- Responsibility: Define what needs to be built and why

**2. Design** - Compress requirements into detailed specifications
- Command: `/sdlc design <feature>`
- Output: `spec.md` (versioned, committed)
- Tool: Claude Code plan mode for interactive design sessions
- Responsibility: How the feature will be implemented

**3. Build** - Generate code and tests through AI with plan mode
- Command: `/sdlc build <feature>`
- Output: Code, tests, updated `CLAUDE.md`, skills
- Tool: Claude Code plan mode as default entry point
- Responsibility: Maintain `CLAUDE.md` and skills for institutional knowledge

**4. Test** - Continuous evaluation throughout implementation
- Command: `/sdlc test <module>`
- Output: Test results, coverage reports
- Integration: Runs in CI pipeline automatically
- Responsibility: Catch issues early, inform design decisions

**5. Maintain** - Monitor production and close the loop
- Command: `/sdlc maintain`
- Output: Metrics, incident reports, updated `intent.md`
- Responsibility: Route issues back to planning cycle

### Core Principles

- **Artifact-Driven**: Each stage ends by committing an artifact; next stage begins by reading it
- **Continuous Evaluation**: Test throughout, not just at stage boundaries
- **Encoded Standards**: Use reusable skills to maintain organizational patterns
- **Human Accountability**: Humans responsible for decisions; AI handles automation

### Skill Templates

All skills follow these patterns:

**plan.md** - Captures user intent for features/fixes
**spec.md** - Detailed design and implementation approach  
**CLAUDE.md** - Updated with new patterns, dependencies, commands
**skills/** - Reusable skills for this project

### Development Workflow (Typical)

```bash
# 1. Start with planning
/sdlc plan "Add user authentication to web module"

# 2. Design the feature
/sdlc design "user-authentication"

# 3. Build with plan mode (automatic starting point)
/sdlc build "user-authentication"

# 4. Run tests continuously
/sdlc test web

# 5. Monitor and collect feedback
/sdlc maintain
```

## Architecture Layers

### Layer 1: Schema (`schemas/model.schema.json`)
Language-agnostic JSON Schema for scientific models. Both Java and Python validate against this — no duplication.

### Layer 2: Translator (web module, implemented)
- `com.clauneck.web.service.ClaudeTranslator`: builds domain-specific prompt, calls Anthropic API directly via `RestTemplate`, parses/validates JSON
- `com.clauneck.web.service.SchemaValidator`: validates against `schemas/model.schema.json` using `com.networknt:json-schema-validator`
- `com.clauneck.web.api.PrototypeController`: REST endpoint `POST /api/prototype` (accepts natural-language query, returns Model + SolverResult)
- Configuration: `clauneck.translator.*` in `application.yml`, driven by `ANTHROPIC_API_KEY` / `CLAUDE_MODEL` / `CLAUNECK_ENGINE_URL` env vars
- Key: LLM never touches computation, only translation

### Layer 3: Validator (core module)
- `DimensionalAnalyzer`: unit parsing, dimensional consistency
- `UnitRegistry`: SI units, conversion factors
- Runs before solver; catches nonsense early

### Layer 4: Compute Engine (engine)
- `ProjectileMotionSolver`: vertical slice (end-to-end proof)
- `GeneralSolver`: extensible routing by domain
- Deterministic: SymPy + SciPy with pinned versions, explicit solver config
- Exposed as FastAPI microservice (`POST /api/solve`)

### Layer 5: API Gateway (web module, implemented)
- `com.clauneck.web.api.PrototypeController` orchestrates: translator → engine
- `com.clauneck.web.client.EngineClient`: POSTs to `${clauneck.engine.url}/api/solve`
- Returns complete response: Model + SolverResult
- Endpoint: `POST /api/prototype`
- Error handling via `com.clauneck.web.exception.PrototypeExceptionHandler`: maps to 400/501/502/503

## Determinism & Reproducibility

**Guarantee**: Identical Model → identical results (byte-for-byte, to numeric precision).

### Implementation
- Schema validation: no silent coercion
- Dependency pinning: `poetry.lock` for Python, Gradle lock for Java
- Solver config explicit: method, tolerance, time span all in Model
- Golden-file tests: same input run twice → compare trajectories

### Testing Strategy
- Unit: Dimension arithmetic, UnitRegistry parsing
- Integration: Model validation, dimensional analysis
- End-to-end: Full solve path (Model → trajectory)
- Determinism: Run solver twice, compare byte-for-byte

## Extension Points

### New Domains
1. Add domain to `domain` enum in schema
2. Create specialized solver in `engine/app/solver.py` (e.g., `ChemicalKineticsSolver`)
3. Update `GeneralSolver.solve()` to route to it
4. Add tests to `engine/tests/`

### New Quantities / Constants
1. Add to schema if new fundamental type
2. Register in `core/UnitRegistry` (SI units)
3. Document in `docs/architecture.md`

### Custom LLM Prompts
- Not in this slice (to be added in translator layer)
- Will be constrained to schema + knowledge base

## Notes for Future Development

- **Vertical slice complete**: Projectile motion (physics.mechanics) works end-to-end, including the translator layer — `POST /api/prototype` takes a natural-language query and returns Model + SolverResult
- **Next slice**: Second domain (chemistry.kinetics) to validate schema generalization
- **CI/CD update needed**: Add Python test stage and `ANTHROPIC_API_KEY` secret to `.github/workflows/ci.yml` once engine stabilizes; use `./gradlew` (not system `gradle`)
- **Performance**: Engine runs as persistent FastAPI service (not per-request) to avoid startup overhead; translator uses configurable Haiku by default for latency
- **Follow-up**: Review schema completeness (all valid enum values, constraint coverage) and add more test domains
- **Maintain `CLAUDE.md`**: Update when new patterns emerge or build commands change
- **Skills**: Stored in `.claude/skills/`; add domain-specific patterns as they're discovered
