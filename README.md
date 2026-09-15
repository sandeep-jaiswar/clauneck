# Clauneck

> A deterministic, efficient, and intelligent scientific prototyping platform for modeling, validating, and solving math, physics, and chemistry problems.

## Overview

**Clauneck** turns natural language scientific ideas into validated, solved models. Users describe an experiment or formula in plain English; the system automatically translates it to a formal model, validates dimensional consistency, solves it symbolically and numerically, and returns deterministic results.

```
Your Idea (Natural Language)
    ↓
Translator (Claude + Schema)
    ↓
Scientific Model (JSON)
    ↓
Validator (Dimensional Analysis)
    ↓
Solver (SymPy + SciPy)
    ↓
Results (Trajectory, Summary)
```

**Key guarantee**: Identical input → identical output (deterministic, byte-for-byte reproducible).

## Features

- 🧠 **Natural Language Input**: Describe your problem in English; no math syntax required
- ✅ **Automatic Validation**: Dimensional analysis catches errors before computation
- 🔢 **Deterministic Solving**: SymPy symbolic + SciPy numeric solvers with pinned dependencies
- 📋 **Schema-Driven**: Single JSON Schema contract shared between Java and Python, no duplication
- 🏗️ **Polyglot Architecture**: Java (translation, validation) + Python (computation)
- 🚀 **Microservice-Ready**: REST API endpoints for each layer; FastAPI engine runs as persistent service
- 📐 **Physics-Ready**: Supports SI units, dimensional vectors, ODE systems, constraints

## Quick Start

### Prerequisites

- **Java 21** ([download](https://www.oracle.com/java/technologies/downloads/))
- **Python 3.10+**
- **Make** (optional, but recommended)

### 1. Clone and Setup

```bash
git clone <repo>
cd clauneck

# Set up Python environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd engine && pip install -e ".[dev]"
cd ..

# Set environment (required for LLM translation)
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 2. Build Everything

```bash
# Using Make (recommended)
make build

# Or manually:
./gradlew build                              # Build Java modules
cd engine && pip install -e .                # Install Python engine
```

### 3. Run the Platform

```bash
# Terminal 1: Start the Python engine
make run
# Or: cd engine && python -m uvicorn app.main:app --port 8001

# Terminal 2: Start the Spring Boot API gateway (when ready)
./gradlew :web:bootRun
# Runs on http://localhost:8080
```

### 4. Test

```bash
make test

# Or individually:
./gradlew build              # Java tests included
cd engine && pytest tests/    # Python tests
```

## Architecture

### Five-Layer Stack

| Layer | Component | Tech | Role |
|-------|-----------|------|------|
| **1** | Schema | JSON Schema | Language-agnostic contract |
| **2** | Translator | Spring Boot + Claude | Natural language → Model |
| **3** | Validator | Java Core | Dimensional analysis + consistency |
| **4** | Solver | Python Engine (SymPy, SciPy) | Deterministic computation |
| **5** | Gateway | Spring Boot API | Orchestrate full pipeline |

### Modules

- **`core/`** (Java): Unit system, dimensional analysis, model representation
- **`web/`** (Java): Spring Boot API, translator client, engine orchestration
- **`engine/`** (Python): FastAPI solver service (symbolic + numeric)
- **`schemas/`** (JSON Schema): Shared contract for Model (Java ↔ Python)
- **`docs/`**: Architecture deep-dive, ADRs, examples

### REST Endpoints

```
POST /api/prototype          # Gateway: natural language → model + results
POST /api/solve              # Engine: model → trajectories + summary
```

## Vertical Slice: Projectile Motion

End-to-end example showing all five layers working together.

**Input**: *"I launch a ball at 20 m/s at 45°, mass 0.5kg, drag coefficient 0.1 — how far does it go?"*

**Output**:
```json
{
  "model": {
    "id": "projectile-1",
    "domain": "physics.mechanics",
    "quantities": [...],
    "equations": [...]
  },
  "result": {
    "success": true,
    "trajectory": {
      "t": [0, 0.01, ..., 3.5],
      "x": [0, ..., 32.5],
      "y": [0, ..., 0]
    },
    "summary": {
      "max_range": 32.5,
      "max_height": 8.2,
      "flight_time": 3.5
    }
  }
}
```

Test it:
```bash
cd engine && python -m pytest tests/test_projectile.py -v
```

## Environment Variables

```bash
ANTHROPIC_API_KEY          # Required: Claude API key for translation layer
CLAUDE_MODEL              # Optional: model to use (default: claude-haiku-4-5)
CLAUNECK_ENGINE_URL       # Optional: engine service URL (default: http://localhost:8001)
```

See `.env.example` for template.

## Project Structure

```
clauneck/
├── schemas/
│   └── model.schema.json           # Shared JSON Schema contract
├── core/                           # Java: units + dimensional analysis
│   ├── src/main/java/com/clauneck/core/
│   │   ├── units/                  # UnitSystem, Dimension, UnitRegistry
│   │   ├── model/                  # Scientific model classes
│   │   └── validation/             # DimensionalAnalyzer
│   └── build.gradle
├── engine/                         # Python: SymPy + SciPy solver
│   ├── app/
│   │   ├── main.py                 # FastAPI service
│   │   ├── solver.py               # Numeric/symbolic solvers
│   │   └── model.py                # Pydantic models from schema
│   ├── tests/
│   │   └── test_projectile.py      # Golden-file determinism tests
│   └── pyproject.toml
├── web/                            # Java: Spring Boot API gateway
│   └── build.gradle
├── docs/
│   ├── architecture.md             # Full system design (read this next!)
│   └── adr/                        # Architecture Decision Records
├── Makefile                        # Root orchestration
├── CLAUDE.md                       # Project conventions + AI-native SDLC
└── README.md                       # This file
```

## Build Commands

```bash
# Full workflow (Make)
make build                          # Build all (Gradle + Python)
make test                           # Test all
make clean                          # Clean artifacts
make run                            # Start engine service

# Java (Gradle)
./gradlew build                     # Build all modules + run tests
./gradlew build -x test             # Build without tests
./gradlew :core:build               # Build core module only
./gradlew :core:test                # Test core module
./gradlew :web:bootRun              # Start Spring Boot server

# Python (Engine)
cd engine && pip install -e .       # Install with dependencies
cd engine && pip install -e ".[dev]" # Install with dev/test deps
cd engine && pytest tests/ -v       # Run tests with verbose output
cd engine && python -m uvicorn app.main:app --port 8001  # Start server
```

## Technology Stack

| Component | Tech | Version |
|-----------|------|---------|
| **Language (Core/Web)** | Java | 21 |
| **Framework (Core/Web)** | Spring Boot | 3.2.2 |
| **Testing (Java)** | JUnit 5 | 5.x |
| **Language (Engine)** | Python | 3.10+ |
| **Solver (Symbolic)** | SymPy | Latest (pinned) |
| **Solver (Numeric)** | SciPy | Latest (pinned) |
| **API (Engine)** | FastAPI | Latest (pinned) |
| **Schema** | JSON Schema | Draft 2020-12 |
| **CI/CD** | GitHub Actions | - |

## Design Principles

1. **Determinism First**: Identical input always produces identical output
2. **Schema-Driven**: Single source of truth (JSON Schema) for both Java and Python
3. **LLM Translation Only**: Claude generates models, never touches computation
4. **Layer Separation**: Each layer has one responsibility; swap implementations without breaking contracts
5. **Test-Driven**: Unit tests, integration tests, determinism tests, golden-file tests

## Key Decisions

See [Architecture Decision Records](docs/adr/) for detailed rationale:

- **0001-polyglot-monorepo.md**: Why Java + Python in one repo
- **0002-llm-translator-boundary.md**: Why LLM is only for translation, not solving

## Determinism Guarantee

Clauneck ensures reproducibility at every level:

- **Schema validation**: No silent coercion; explicit is required
- **Dependency pinning**: All versions locked via lockfiles
- **Explicit configuration**: Solver method, tolerance, time span specified in Model
- **Golden-file tests**: Solve twice, verify byte-for-byte match
- **No randomness**: All solvers use deterministic algorithms with fixed seeds

## Next Steps

- 📖 Read [Architecture Guide](docs/architecture.md) for a deep dive
- 🧪 Try the [Projectile Motion Example](engine/tests/test_projectile.py)
- 🔧 Extend with a [New Domain](docs/architecture.md#new-domains)
- 🚀 Deploy using [CI/CD Pipeline](.github/workflows/ci.yml)

## Contributing

This project follows the **AI-Native SDLC** workflow:

1. **Plan**: Define requirements (`/sdlc plan`)
2. **Design**: Create specifications (`/sdlc design`)
3. **Build**: Implement with AI assistance (`/sdlc build`)
4. **Test**: Continuous evaluation (`/sdlc test`)
5. **Maintain**: Monitor and iterate (`/sdlc maintain`)

See [CLAUDE.md](CLAUDE.md) for project conventions, build patterns, and AI workflow details.

## License

(Add your license here)

## Support & Feedback

- 📚 [Full Architecture Docs](docs/architecture.md)
- 🏗️ [Development Guide](CLAUDE.md)
- 🐛 Report issues on GitHub
- 💡 See [ADRs](docs/adr/) for design rationale

---

**Built with determinism, clarity, and scientific rigor.** 🔬
