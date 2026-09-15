# ADR 0001: Polyglot Monorepo Architecture

## Status
**ACCEPTED**

## Context
Clauneck aims to be a deterministic, efficient scientific prototyping platform. Early planning identified that:

1. **Java excels at** structural validation, strong typing, schema management
2. **Python excels at** scientific computing (SymPy, NumPy, SciPy are mature, battle-tested)
3. **Forcing everything into one language** would sacrifice efficiency in both domains

The question: monorepo or multi-repo? Single language or polyglot?

## Decision
**Polyglot monorepo**: Single git repository with multiple language modules, each owned by the right tool for its job.

### Architecture
```
clauneck/
├── core/ (Java)           # UnitSystem, dimensional analysis, schema validation
├── engine-python/ (Python) # Symbolic + numeric solving (SymPy, SciPy)
├── web/ (Java)             # Spring Boot API gateway, LLM translation
├── schemas/ (JSON Schema)  # Shared contract across languages
└── Makefile                # Root orchestration
```

## Rationale

### Why Monorepo?
- **Single source of truth**: Schema lives in one place; no sync issues
- **Atomic commits**: Related changes across modules in one commit
- **Easier testing**: End-to-end tests in CI without cross-repo coordination
- **Simpler deployment**: One repo tag = one complete release

### Why Polyglot?
- **Use the best tool**: Don't force Python's mature solvers into Java; don't force Java's type system onto Python
- **Minimal bridges**: Schema validation (JSON) is the only interface; each module is internally independent
- **Precedent**: TensorFlow, PyTorch, and many enterprise platforms do this successfully

### Why Not Multi-Repo?
- Schema duplication and drift (Java Schema ≠ Python Schema = disaster)
- CI complexity (which repo's version is "current"?)
- Harder refactoring (schema changes require coordinated updates)

## Consequences

### Good
- Each module uses idiomatic tooling (Maven/Gradle for Java, Poetry/uv for Python)
- Solver efficiency: SymPy/SciPy run natively, not shoehorned into JVM
- Clean interfaces: HTTP + JSON schema, language-agnostic
- Parallelizable: Can develop Java gateway and Python solver independently

### Bad
- **Build complexity**: Developers need both JVM and Python installed locally
  - *Mitigation*: Makefile abstracts this; Docker for CI
- **Operational complexity**: Two runtime environments, two dependency management systems
  - *Mitigation*: Pinned lockfiles for both; clear Makefile targets
- **Onboarding**: New team members need to understand two ecosystems
  - *Mitigation*: CLAUDE.md documents patterns per module

## Alternatives Considered

### 1. All Java
- ✗ Would require porting or wrapping SymPy/SciPy (JNI/Jython)
- ✗ Significant performance loss; scientific libraries are C-native
- ✗ Determinism harder to guarantee (wrappers add layers)

### 2. All Python
- ✗ Loses strong typing benefits for schema validation
- ✗ Dependency hell (pip fragmentation, no equivalent to Maven Central)
- ✗ Harder to enforce architectural constraints in a service mesh

### 3. Multiple Repos (Java + Python separate)
- ✗ Schema duplication risk
- ✗ Versioning/coordination burden
- ✗ Slower CI/CD (two separate pipelines)

## Implementation Notes

### Schema as Contract
- `schemas/model.schema.json` is the single source of truth
- Java code validates Quantities, Equations against this schema at runtime
- Python code auto-generates Pydantic models from the same schema (future: via JSON Schema→Pydantic tool)
- Both sides reject invalid input; no silent fallbacks

### Build Orchestration
- Root `Makefile` provides unified targets: `make build`, `make test`
- Gradle runs for Java modules
- Poetry/uv runs for Python modules
- CI/CD (GitHub Actions) calls Makefile targets

### Deployment
- Python engine as a containerized microservice (FastAPI + uvicorn in Docker)
- Java web module as a Spring Boot jar
- Both deployed independently but as a unit (versioned together via git tags)

## Monitoring & Maintenance
- Watch dependency updates for both ecosystems
- Python lockfile (`poetry.lock` or `uv.lock`) committed to git
- Java: rely on Gradle's dependency resolution + periodic audit
- Schema changes require updates in both systems; PR process ensures this

## References
- [[0002-llm-translator-boundary]]
- `schemas/model.schema.json`
- `Makefile`
- `docs/architecture.md`
