# Intent: Expand Mathematics Domains (7 New Domains)

**Author**: sandeep-jaiswar  
**Date**: 2026-09-15  
**Status**: DRAFT  
**Tracking Issue**: (none yet)

---

## Problem Statement

The clauneck system currently covers **10 core math domains**, but is missing higher-order branches that directly complement existing **physics and chemistry solvers**. This limits the platform's ability to model complex phenomena requiring:

- **Probability & stochastic processes** (needed by kinetics, equilibrium, statistical mechanics)
- **Partial differential equations** (heat/wave/Laplace equations in thermodynamics, electromagnetism, waves)
- **Vector calculus** (gradient/divergence/curl in electromagnetism, wave propagation)
- **Sequences & series** (Fourier analysis in waves, power series solutions)
- **Graph theory** (network analysis, chemical bonding pathways, reaction networks)
- **Discrete mathematics** (recurrence relations, combinatorial chemistry)
- **Numerical methods** (first-class solvers for stiff systems, interpolation)

**Pain Point**: Users must model these phenomena indirectly or defer to external tools. The platform cannot solve complete problems in thermodynamics, electromagnetism, and kinetics that require probabilistic or differential-geometric reasoning.

**Why Now**: Phases 1–4 completed 21 domains with proven architecture (function-dispatch solver pattern, auto-discovery via @register, externalized translator prompts). Phase 5 regression-tested all 21. Adding 7 more domains leverages existing patterns with minimal architectural innovation — pure horizontal expansion using established DRY principles.

---

## Goals

1. **Completeness** - Add 7 mathematically rigorous domains (probability, PDE, vector calculus, sequences/series, graph theory, discrete math, numerical methods) to fill gaps in physics/chemistry modeling
2. **Coherence** - Each new domain explicitly complements 1–3 existing physics/chemistry domains (no orphaned math)
3. **Scale with elegance** - Reuse all Phase 1–4 patterns: function-dispatch architecture, @register discovery, externalized translator prompts, 226+ test suite model
4. **Comprehensive coverage** - 10–20 core operations per domain (not toy/stub implementations); include real SymPy/NumPy/SciPy implementations
5. **Deterministic & testable** - All solvers pure functions; results reproducible byte-for-byte; determinism tests for all 7 domains (50+ new tests)
6. **DRY & SOLID** - Reuse shared helpers (`app/solvers/utils.py`); no duplicated dispatch logic; each solver has single responsibility; fail fast with clear errors

---

## Success Criteria

- [ ] **All 7 domains implemented** - One registered solver class per domain (@register decorator), each with 10–20 operations
- [ ] **Schema updated** - All 7 domain strings added to `schemas/model.schema.json` enum (no stubs)
- [ ] **Translator prompts** - One `.txt` file per domain in `web/src/main/resources/translator-prompts/` (externalized, not hardcoded)
- [ ] **Comprehensive tests** - 50+ new test files covering: correctness, determinism (solve twice → identical results), error paths, operation dispatch, edge cases
- [ ] **Integration verified** - Vector calculus operations called by physics.electromagnetism tests; PDE solver used by thermodynamics examples; probability distributions by kinetics tests
- [ ] **DRY compliance** - No duplicated dispatch code; 100% of multi-equation logic uses shared `run_dispatch` utility; all file-based helpers in `utils.py`
- [ ] **Documentation** - Each domain's translator prompt documents 10–20 operations, input/output format, solver method, worked example
- [ ] **End-to-end demo** - Complex model (e.g., coupled PDE + probability initial condition, or Fourier series + wave physics) solved end-to-end through translator → engine
- [ ] **CI green** - All tests pass; no regressions in existing 11 + 10 = 21 domains

---

## Scope

### In Scope

#### New Domains (7)
1. **Probability Theory** (`mathematics.probability`)
   - Bayes' theorem, joint/conditional/marginal probability
   - Expectation, variance, covariance, moment generating functions
   - Common distributions (binomial, poisson, normal, exponential, etc.)
   - Markov chains, basic stochastic processes
   - ~15 operations

2. **Partial Differential Equations** (`mathematics.pde`)
   - Heat equation (1D/2D, transient/steady-state)
   - Wave equation (1D/2D, d'Alembert solution)
   - Laplace/Poisson equation
   - Method of characteristics, separation of variables
   - Boundary conditions: Dirichlet, Neumann, Robin, periodic
   - Numeric solver (finite difference, finite element for simple cases)
   - ~12 operations

3. **Vector Calculus** (`mathematics.vector_calculus`)
   - Gradient, divergence, curl (in Cartesian/cylindrical/spherical coords)
   - Directional derivative, Laplacian
   - Line integrals, surface integrals, volume integrals
   - Green's theorem, Stokes' theorem, divergence theorem
   - Vector field operations (dot product, cross product in 3D)
   - ~18 operations

4. **Sequences & Series** (`mathematics.sequences_series`)
   - Arithmetic, geometric, harmonic series; sums
   - Convergence tests (ratio, root, integral, alternating series)
   - Power series, Taylor series, Maclaurin series
   - Fourier series (sine, cosine, complex exponential)
   - Generating functions
   - ~16 operations

5. **Graph Theory** (`mathematics.graph_theory`)
   - Graph construction, adjacency/incidence matrices
   - Connected components, bipartiteness, planarity
   - Shortest path (Dijkstra, Bellman-Ford), all-pairs shortest paths
   - Minimum spanning tree (Prim, Kruskal)
   - Graph coloring, chromatic polynomial
   - Centrality measures (betweenness, closeness, degree)
   - ~14 operations

6. **Discrete Mathematics** (`mathematics.discrete_math`)
   - Set operations (union, intersection, complement, symmetric diff, power set)
   - Recurrence relations (first/second order linear, non-homogeneous)
   - Inclusion-exclusion principle
   - Partition functions, Stirling numbers
   - Boolean algebra, logical operators
   - ~13 operations

7. **Numerical Methods** (`mathematics.numerical_methods`)
   - Root-finding: Newton-Raphson, bisection, secant, Brent's method
   - Interpolation: polynomial (Lagrange, Newton), spline
   - Numerical differentiation (finite differences, Richardson extrapolation)
   - Numerical integration (trapezoidal, Simpson, Gauss-Legendre)
   - ODE systems (RK45, BDF for stiff), step size control
   - ~17 operations

#### Existing Integration Points
- **Translator layer** (`web/...ClaudeTranslator.java`) — already auto-discovers domains from prompt files; no code changes needed (Phase 1 design)
- **Schema** (`schemas/model.schema.json`) — add 7 enum entries; validation unchanged
- **Test infrastructure** — existing `pytest` patterns in `engine/tests/test_*.py`; no new harness needed

### Out of Scope (Future)

- **Advanced PDE solvers** (spectral methods, mesh generation, FEM libraries)
- **Probabilistic graphical models** (Bayesian networks, hidden Markov models beyond basic stochastic)
- **Advanced numerical stability analysis** (condition numbers, perturbation bounds)
- **Symbolic geometry** (differential forms, tensor calculus)
- **Machine learning integrations** (regression as a solver option, neural nets)
- **Parallel computing** (GPU acceleration, distributed solvers)
- **Language bindings** (Python API, Julia integration)
- **Frontend UI** for visualization (phase out of `/batch` scope)

---

## Affected Modules

| Module | Change | Reason |
|--------|--------|--------|
| **engine** | Add 7 solver files (`app/solvers/probability.py`, `pde.py`, `vector_calculus.py`, `sequences_series.py`, `graph_theory.py`, `discrete_math.py`, `numerical_methods.py`) | Core domain implementations |
| **engine** | Add 50+ test files (`tests/test_probability*.py`, `test_pde*.py`, etc.) | Correctness, determinism, error paths, integration |
| **engine** | No changes to `utils.py` except minor: add helpers if `vector_calculus` or others need unique utilities (e.g., coordinate transforms) | Minimize code duplication; reuse existing dispatch |
| **web** | Add 7 translator prompt files (`web/src/main/resources/translator-prompts/mathematics.*.txt`) | Domain-specific Claude prompts (no code) |
| **schemas** | Add 7 domain strings to `domain` enum in `schemas/model.schema.json` | Contract update; no logic change |
| **core** | No changes | Validation layer already generic |
| **docs** | Update `CLAUDE.md`, `docs/adr/`, `docs/architecture.md` | Reflect Phase 6 completion, 7 new domains, integration points |

---

## Dependencies

### Internal
- **engine/app/solvers/utils.py** — dispatch helpers, quantity getters, helper functions for all 7 new solvers
- **engine/app/solvers/registry.py** — @register decorator (unchanged; auto-discovery)
- **core** module — dimensional analysis, schema validation (unchanged)
- **web** module — translator auto-loads prompts from classpath (unchanged; Phase 1)

### External (Python)
- **SymPy** (≥1.12) — probability distributions, PDEs (symbolic), series analysis, graph algorithms
- **NumPy** (≥1.24) — numerical methods, matrix operations, FFT for Fourier
- **SciPy** (≥1.10) — optimize.root_scalar, optimize.brentq, interpolate.CubicSpline, integrate.quad, solve_ivp for PDE numerics
- **NetworkX** (≥3.0) — graph algorithms, centrality, shortest path (not in current dependencies; add to `engine/pyproject.toml`)

### External (Java)
- **Spring Boot 3.2.2** (existing)
- **Gradle 8.10** (existing)

### Build & Test
- **pytest** (≥7.0) — all 50+ new test files
- **CI/CD** — existing `.github/workflows/ci.yml` (no changes needed; just runs `pytest engine/tests/`)

---

## Known Constraints

### Technical
1. **Symbolic vs. Numeric Trade-off**
   - PDE, sequences/series favor symbolic (SymPy) when closed-form exists; fall back to numeric (SciPy)
   - Numerical methods are explicitly numeric
   - Probability theory uses SymPy for symbolic distributions, NumPy/SciPy for evaluation
   - Trade-off: symbolic solutions slower but more general; numeric solutions fast but approximate

2. **Graph Representation**
   - User specifies adjacency matrix or edge list in Model JSON
   - NetworkX used internally; results serialized back to matrix form
   - No native graph plot output (out of scope)

3. **Integration Point Coupling**
   - Vector calculus ↔ physics.electromagnetism: user may want `curl(E) = -∂B/∂t` from Maxwell equations
   - PDE ↔ physics.thermodynamics: heat diffusion equation solver
   - Probability ↔ chemistry.kinetics: rate laws + stochastic fluctuations
   - These are *optional* user-facing demos; solvers work independently (loose coupling)

4. **Determinism Guarantee**
   - All 7 new solvers are pure functions (no hidden state, randomness, or global side effects)
   - Numerical methods use fixed random seeds if stochasticity needed (e.g., Monte Carlo integration); configurable via Model.solver.randomSeed
   - Determinism tests: solve(model) twice → identical summary dicts (same as existing 21 domains)

5. **Error Handling**
   - Invalid inputs → SolverResult(success=False, error="...") with clear message
   - No exceptions escape solver; translator catches and returns 400 Bad Request
   - Edge cases (singular matrices, non-convergent series, disconnected graphs) handled gracefully

### Timeline
- **Design phase** (sdlc-design): 2–3 days (spec.md, operation lists, test skeleton)
- **Implementation** (batch with 7 workers, one per domain): 5–7 days
- **Integration testing**: 2–3 days (cross-domain tests, physics/chemistry integration)
- **Documentation & final review**: 2 days
- **Total**: ~3 weeks (assuming 1 developer + Claude Code pair programming)

### Resource
- 1 developer (Sandeep) + Claude Code (batch orchestration)
- Local testing (ports 8080 for web, 8001 for engine)
- Python environment with SymPy/NumPy/SciPy/NetworkX
- No external compute (all runs locally or in CI)

---

## Background & Context

### Why These 7 Domains?

From Phase 5 audit:
- **Probability** — distributions exist in `statistics.py` (normal, binomial, poisson pdf/cdf), but general probability theory (Bayes, expectations, stochastic processes) missing
- **PDE** — ODE solver exists (`ode_general.py`); PDEs needed for physics.waves/thermodynamics (heat, wave, Laplace equations)
- **Vector calculus** — required by physics.electromagnetism (Maxwell equations); distinct from `calculus.py` (single-variable) and `linear_algebra.py` (no derivatives)
- **Sequences/series** — Fourier series ties directly to `physics.waves`; power series solutions for ODEs and PDEs
- **Graph theory** — reaction networks (chemistry), molecule connectivity (chemistry), network analysis (general)
- **Discrete math** — recurrence relations (population dynamics, Fibonacci kinetics), set operations, combinatorics (beyond nPr/nCr in `number_theory.py`)
- **Numerical methods** — stiff ODE solvers, interpolation, root-finding as first-class ops (not buried in solver internals)

### Architectural Principles

**DRY (Don't Repeat Yourself)**:
- All 7 solvers use `run_dispatch(model, quantities, operations)` from `utils.py` (established in Phase 1)
- No duplicated equation parsing, quantity resolution, or error handling
- Shared coordinate transform helpers for vector calculus, FFT wrappers for Fourier series

**SOLID**:
- **Single Responsibility**: Each solver handles one domain; utilities handle shared concerns (dispatch, quantity lookup)
- **Open/Closed**: New operations add to `_OPERATIONS` dict; dispatch logic unchanged
- **Liskov Substitution**: All solvers inherit `SolverBase`; signatures interchangeable
- **Interface Segregation**: Solver methods only return what's needed (SolverResult); no god objects
- **Dependency Inversion**: Solvers depend on abstractions (SolverBase, utils), not concrete implementations

**Configurable & Scalable**:
- **Model-driven**: All configuration via Model JSON (domain, equations, solver method, tolerances)
- **Extensible prompts**: New domain = new `.txt` file in `translator-prompts/` (Phase 1 design)
- **Auto-discovery**: @register decorator + registry.load_all(); no hardcoded domain lists
- **Test templates**: Reuse `test_algebra.py` structure (correctness, determinism, error paths) for all 7

### Vertical Integration

User journey after Phase 6:
```
Natural Language (e.g., "Solve the heat equation on [0,1] with initial condition u(x,0)=sin(πx)")
    ↓ [Translator: Claude NL→JSON]
Model JSON: {domain: "mathematics.pde", equations: [...], quantities: [...], solver: {...}}
    ↓ [Validator: schema + dimension checking]
Dimensionally consistent, schema-valid model
    ↓ [Solver Engine: PDE solver dispatches on RHS, calls heat_equation(L, T, method, bc)]
Numeric solution: temperature profile u(x, t) at time steps
    ↓ [Summarize]
JSON result with convergence info, solution summary, metadata
```

This end-to-end flow is not possible today without PDE + vector calculus + sequences/series.

### Why Single Phase?

**Advantage**: All 7 share architecture (dispatch, @register, Phase 1 patterns), so coordinated implementation avoids rework. Phased rollout would re-discover patterns per domain.

**Risk mitigation**: Each domain is independent; if one hits blockers (e.g., NetworkX version conflict), it doesn't block others. Batch orchestration (7 parallel agents) mitigates timeline risk.

---

## Implementation Sketch (Out of Scope for Intent, But Noted)

Each domain follows the established 3-file pattern:

1. **Solver class** (`engine/app/solvers/<domain>.py`)
   ```python
   from app.solvers.registry import register
   from app.solvers.utils import run_dispatch, get_value, get_vector, etc.
   
   @register("mathematics.<domain>")
   class <Domain>Solver(SolverBase):
       def solve(self, model: ScientificModel) -> SolverResult:
           try:
               operations = {...}  # 10–20 ops, e.g., {"diff": _diff, "integrate": _integrate, ...}
               return run_dispatch(model, model.quantities, operations)
           except ValueError as e:
               return SolverResult(success=False, error=str(e))
   ```

2. **Tests** (`engine/tests/test_<domain>.py` + supporting files)
   - Correctness tests: verify against independently computed reference values
   - Determinism tests: solve(model) twice → identical summary
   - Error-path tests: invalid inputs → SolverResult(success=False, error=...)
   - Integration tests: solver called by physics/chemistry domain tests

3. **Translator prompt** (`web/src/main/resources/translator-prompts/mathematics.<domain>.txt`)
   - Domain name, purpose, input quantities, supported operations, solver methods, worked example

---

## Success Timeline

| Phase | Date Range | Milestone | Owner |
|-------|------------|-----------|-------|
| **1. Clarify** | 2026-09-15 | Intent.md drafted, approved by team | Sandeep |
| **2. Design** | 2026-09-16 to 2026-09-18 | Spec.md (operation lists, test skeleton, integration points) | Claude + Sandeep |
| **3. Implement** | 2026-09-19 to 2026-09-28 | 7 parallel solver implementations (batch, one agent per domain) | Claude (agents) |
| **4. Test & Integrate** | 2026-09-29 to 2026-10-02 | 50+ tests green, cross-domain integration verified | Claude + Sandeep |
| **5. Docs & Demo** | 2026-10-03 to 2026-10-04 | CLAUDE.md, ADR, end-to-end demo (e.g., PDE from NL) | Sandeep |
| **6. Review & Merge** | 2026-10-05+ | PR review, merge to production | Sandeep |

---

## Questions for Product Owner / Reviewers

1. **PDE scope**: Should we include 1D only or 2D/3D? (1D is SymPy-friendly; 2D/3D requires numeric grid, more complex)
2. **Graph representation**: Should adjacency matrix be dense (square matrix) or sparse (edge list)? (Affects numeric library choice)
3. **Probability distributions**: Reuse SciPy's frozen distributions or build custom Pydantic wrappers? (Custom = more control but more code)
4. **Numerical method tolerances**: User-configurable (Model.solver.tolerance) or domain-specific defaults? (Configurable is more flexible but complex)
5. **Integration with physics**: Should PDE solver automatically apply boundary conditions from physics.thermodynamics? Or keep math domain decoupled? (Decoupled = simpler, but less "automatic")

---

## References

- **Phase 5 audit**: `/home/sandeep/.claude/plans/flickering-twirling-haven.md` (math domain gap analysis)
- **Architecture**: `docs/architecture.md` + `docs/adr/0002-llm-translator-boundary.md`
- **Schema**: `schemas/model.schema.json`
- **Phase 1 patterns**: `engine/app/solvers/utils.py` (run_dispatch, shared helpers)
- **Existing solvers**: `engine/app/solvers/{algebra,calculus,statistics,ode_general}.py` (examples of 10–20 op structure)
- **Test patterns**: `engine/tests/test_{algebra,statistics,ode_general}.py` (correctness, determinism, error-path tests)
- **CLAUDE.md**: Extension points, determinism guarantee, test strategy

---

**Next Step**: Proceed to `/sdlc-design` to create detailed spec.md with per-domain operation lists, integration signatures, test skeleton, and worker instructions for batch orchestration.
