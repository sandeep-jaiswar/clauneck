# Specification: Expand Mathematics Domains (7 New Domains)

**Designer**: Claude Code (Sonnet 5)  
**Date**: 2026-09-15  
**Status**: DRAFT  
**Based on**: intent-expand-mathematics-domains.md  
**Target Build Phase**: /sdlc-build

---

## Overview

This specification details the implementation of 7 new mathematics domains (probability, PDE, vector calculus, sequences/series, graph theory, discrete math, numerical methods) for the clauneck platform. Each domain will follow the established Phase 1–4 architecture (function-dispatch solver pattern, @register discovery, externalized translator prompts, DRY/SOLID principles).

**Key architectural reuse**:
- Solver pattern: module-level operation functions + `_OPERATIONS` dict + `run_dispatch()` dispatch loop
- Registration: `@register("mathematics.<domain>")` decorator, auto-discovery via `registry.load_all()`
- Testing: correctness tests, determinism tests (solve twice → identical results), error-path tests
- Translator prompts: externalized `.txt` files in `translator-prompts/`, auto-loaded by Spring at startup
- Schema: add 7 domain enum entries to `schemas/model.schema.json`

**Scope**: Single coordinated phase, all 7 domains in parallel (batch orchestration with 7 agents, one per domain).

---

## Requirements

### Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|-------------------|
| REQ-F1 | **Probability Theory Domain** (`mathematics.probability`) | Domain solver class registered, 15+ operations (Bayes, expectations, distributions, stochastic processes), all operations produce deterministic results |
| REQ-F2 | **PDE Domain** (`mathematics.pde`) | Domain solver class registered, 12+ operations (heat, wave, Laplace equations, boundary conditions, method selection), supports both symbolic (SymPy) and numeric (SciPy) backends |
| REQ-F3 | **Vector Calculus Domain** (`mathematics.vector_calculus`) | Domain solver class registered, 18+ operations (grad, div, curl, directional derivative, Laplacian, line/surface/volume integrals, Green/Stokes/divergence theorems) in Cartesian/cylindrical/spherical coordinates |
| REQ-F4 | **Sequences & Series Domain** (`mathematics.sequences_series`) | Domain solver class registered, 16+ operations (convergence tests, power series, Taylor/Fourier series, generating functions), deterministic summation and evaluation |
| REQ-F5 | **Graph Theory Domain** (`mathematics.graph_theory`) | Domain solver class registered, 14+ operations (shortest path, MST, centrality, coloring, connectivity), adjacency matrix input/output |
| REQ-F6 | **Discrete Math Domain** (`mathematics.discrete_math`) | Domain solver class registered, 13+ operations (set operations, recurrence relations, inclusion-exclusion, Stirling/partition functions, Boolean algebra) |
| REQ-F7 | **Numerical Methods Domain** (`mathematics.numerical_methods`) | Domain solver class registered, 17+ operations (root-finding, interpolation, numerical derivatives/integrals, ODE/stiff system solvers) with configurable tolerance |
| REQ-F8 | **Schema Updated** | All 7 domain strings added to `domain` enum in `schemas/model.schema.json`; no schema logic changes |
| REQ-F9 | **Translator Prompts** | 7 `.txt` files created in `translator-prompts/`, each documenting domain purpose, 10–20 operations, input format, solver methods, worked example |
| REQ-F10 | **No Hardcoded Domain Lists** | Translator auto-discovers domains from prompt files (Phase 1 design); no Java code changes to add 7 new domains |
| REQ-F11 | **Integration with Physics/Chemistry** | Exemplary cross-domain tests: vector calculus + physics.electromagnetism, PDE + physics.thermodynamics, probability + chemistry.kinetics |

### Non-Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|-------------------|
| REQ-NF1 | **Determinism** | All 7 new solvers are pure functions; solve(model) twice → identical SolverResult dicts; 50+ determinism tests |
| REQ-NF2 | **DRY Code** | 100% of multi-equation dispatch uses shared `run_dispatch()` utility; zero duplicated equation parsing, quantity resolution, or dispatch logic across 7 solvers |
| REQ-NF3 | **SOLID Principles** | Single Responsibility: each solver handles one domain; Open/Closed: new ops add to dict, dispatch unchanged; no god objects; dependency inversion via base class SolverBase |
| REQ-NF4 | **Error Handling** | All invalid inputs → SolverResult(success=False, error="...") with clear message; no exceptions escape solver; edge cases (singular matrices, non-convergent series, disconnected graphs) handled gracefully |
| REQ-NF5 | **Comprehensive Testing** | 50+ new test files (6–8 per domain): correctness, determinism, error paths, edge cases, operation dispatch verification |
| REQ-NF6 | **Performance** | Each solver operation completes in <1 second for typical inputs; no pathological exponential behavior (e.g., exponential-time graph algorithm) without warning |
| REQ-NF7 | **Backward Compatibility** | No changes to existing 21 solvers or their tests; all Phase 1–5 tests pass unchanged; new domains are pure additions |
| REQ-NF8 | **Code Quality** | All code follows existing project conventions (CLAUDE.md); docstrings for all functions; type hints throughout; pytest passes with no warnings |
| REQ-NF9 | **Documentation** | Updated CLAUDE.md with new patterns (if any); updated `docs/architecture.md` with 7 new domains; translator prompts document all operations |

---

## Architecture & Design

### High-Level Architecture

```
User Natural Language (e.g., "Solve the heat equation")
    ↓ [Translator: Claude API + Spring controller]
Model JSON: {domain: "mathematics.pde", equations: [...], quantities: [...], solver: {...}}
    ↓ [Validator: schema + dimensional analysis (core module)]
Valid Model
    ↓ [Engine Router: GeneralSolver.solve(model)]
Domain-specific solver dispatch (via registry lookup)
    ↓ [Solver: e.g., PDESolver.solve(model)]
    ↓ [Function-dispatch loop: run_dispatch(model, quantities, operations)]
    ↓ [Operations: pure functions _heat_equation(), _laplace_solve(), etc.]
Result: SolverResult(success=True, summary={...})
    ↓ [Combine Model + Result + Metadata]
JSON response to client
```

### Module-Level Architecture

#### 1. **Engine Module** (`engine/app/solvers/`)

**New Solver Files** (one per domain):
- `probability.py` — Probability theory solver (15+ ops)
- `pde.py` — Partial differential equations solver (12+ ops)
- `vector_calculus.py` — Vector calculus solver (18+ ops)
- `sequences_series.py` — Sequences & series solver (16+ ops)
- `graph_theory.py` — Graph theory solver (14+ ops, requires NetworkX)
- `discrete_math.py` — Discrete mathematics solver (13+ ops)
- `numerical_methods.py` — Numerical methods solver (17+ ops)

**Shared Utilities** (`utils.py`):
- Existing helpers: `get_value()`, `get_vector()`, `get_matrix()`, `run_dispatch()`, etc.
- New helpers (if needed per domain):
  - `to_cylindrical()`, `to_spherical()` — coordinate transforms for vector calculus
  - `matrix_to_networkx()`, `networkx_to_matrix()` — graph representation conversions
  - (Others as discovered during implementation)

**Structure per Solver**:
```python
# Example: probability.py
from app.solvers.registry import register
from app.solvers.utils import run_dispatch, get_value, get_vector
from scipy import stats as scipy_stats
import sympy as sp

def _bayes_theorem(prior, likelihood, evidence) -> float:
    """Bayes' theorem: P(A|B) = P(B|A)*P(A) / P(B)"""
    # validation + computation
    return posterior

# ... 14 more operations ...

_OPERATIONS = {
    "bayes_theorem": _bayes_theorem,
    "expectation": _expectation,
    # ... etc
}

@register("mathematics.probability")
class ProbabilitySolver(SolverBase):
    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            return run_dispatch(model, {q.name: q for q in model.quantities}, _OPERATIONS)
        except ValueError as e:
            return SolverResult(success=False, error=str(e))
```

#### 2. **Web Module** (`web/src/main/resources/translator-prompts/`)

**New Translator Prompt Files** (one per domain):
- `mathematics.probability.txt`
- `mathematics.pde.txt`
- `mathematics.vector_calculus.txt`
- `mathematics.sequences_series.txt`
- `mathematics.graph_theory.txt`
- `mathematics.discrete_math.txt`
- `mathematics.numerical_methods.txt`

**Structure per Prompt**:
```
# Probability Theory (mathematics.probability)

## Domain Purpose
Model random events, distributions, and stochastic processes using Bayes' theorem,
conditional probability, and moment generating functions.

## Input Quantities
- `event_A`, `event_B`: probability values or labels
- `dataset`: array of samples
- `distribution`: name (e.g., "normal", "binomial", "poisson")
- `parameters`: parameters for distribution (mean, variance, shape, scale, etc.)

## Supported Operations (15+)
1. `bayes_theorem(prior, likelihood, evidence)` → posterior probability
2. `conditional_probability(joint, marginal)` → conditional prob
3. `joint_probability(p_a, p_b)` → joint (independent events)
4. `expectation(values, probabilities)` → E[X]
5. `variance(values, probabilities)` → Var[X]
... (10 more)

## Example Query
"Given P(disease)=0.01, P(test_positive|disease)=0.95, P(test_positive|healthy)=0.05,
what is P(disease|test_positive)?"

Expected Model JSON:
{
  "domain": "mathematics.probability",
  "equations": [
    {"lhs": "posterior", "rhs": "bayes_theorem(0.01, 0.95, 0.05*0.99 + 0.95*0.01)"}
  ],
  "quantities": [
    {"name": "prior", "value": 0.01, "isKnown": true, "siUnit": "dimensionless"},
    ...
  ]
}
```

No code changes to `ClaudeTranslator.java`; auto-discovery handles it (Phase 1).

#### 3. **Schema Module** (`schemas/model.schema.json`)

**Changes**:
```json
"domain": {
  "type": "string",
  "enum": [
    // Existing 21 domains
    "chemistry.acid_base_equilibrium",
    ...
    "physics.waves",
    // NEW: 7 math domains
    "mathematics.discrete_math",
    "mathematics.graph_theory",
    "mathematics.numerical_methods",
    "mathematics.pde",
    "mathematics.probability",
    "mathematics.sequences_series",
    "mathematics.vector_calculus"
  ]
}
```

No logic changes; purely adding enum values (alphabetical order per Phase 1 convention).

#### 4. **Core Module**

**No changes required.** Validation, dimensional analysis, and unit system already generic.

---

## Implementation Approach

### Phase Breakdown

#### **Phase 1: Design & Setup** (2–3 days, serial)
1. Finalize operation lists for all 7 domains (refine from intent)
2. Create skeleton solver files (class + @register decorator, empty _OPERATIONS dict)
3. Add 7 domain enum entries to schema
4. Create stub translator prompts (filenames only, minimal content)
5. Create test file stubs (imports, fixtures, placeholder tests)

**Deliverable**: Compiling code; all 7 domains registered but operations not implemented.

#### **Phase 2: Implementation** (5–7 days, parallel via batch)
**Launch 7 agents in parallel** (one per domain), each implementing:
1. **Operations**: 10–20 module-level functions (pure functions, validation + computation)
2. **Operations dict**: Register all functions in `_OPERATIONS`
3. **Solver class**: Implement `solve()` method using `run_dispatch()`
4. **Translator prompt**: Complete with all operations, examples, constraints
5. **Tests**: 6–8 test files per domain (correctness, determinism, error paths, edge cases)

**Per-domain breakdown**:

| Domain | Operations | Key Libraries | Test Cases | Notes |
|--------|-----------|---|---|---|
| **Probability** (15 ops) | Bayes, conditional prob, expectation, variance, distributions (normal, binomial, poisson, exponential), Markov chains, moment generating | SymPy, SciPy.stats | 8 test files: bayes, distributions, moments, markov chains | Distributions reuse SciPy; custom Bayes logic |
| **PDE** (12 ops) | Heat equation, wave equation, Laplace/Poisson, boundary conditions (Dirichlet/Neumann/Robin), method of characteristics, separation of variables, numeric (finite diff) | SymPy, SciPy.integrate.solve_ivp | 6 test files: heat 1D/2D, wave, Laplace, BC handling | Symbolic solutions via SymPy; numeric fallback to SciPy |
| **Vector Calculus** (18 ops) | Gradient, divergence, curl, directional derivative, Laplacian, line integral, surface integral, volume integral, Green/Stokes/divergence theorems, coordinate transforms (Cartesian/cylindrical/spherical) | SymPy, NumPy | 8 test files: grad/div/curl, integrals, theorems, coordinate transforms | Coordinate transforms add utility functions to utils.py |
| **Sequences/Series** (16 ops) | Arithmetic/geometric/harmonic series, convergence tests (ratio, root, integral, alternating), power series, Taylor/Maclaurin, Fourier series (sine, cosine, complex), generating functions | SymPy, NumPy | 7 test files: convergence, Taylor series, Fourier, generating functions | Fourier coefficients computed via SymPy integrals |
| **Graph Theory** (14 ops) | Adjacency matrix, connected components, bipartiteness, planarity, shortest path (Dijkstra, Bellman-Ford), APSP (Floyd-Warshall), MST (Prim, Kruskal), graph coloring, chromatic polynomial, centrality (degree, betweenness, closeness) | NetworkX, NumPy | 7 test files: shortest path, MST, connectivity, centrality, coloring | Requires NetworkX addition to `pyproject.toml` |
| **Discrete Math** (13 ops) | Set operations (union, intersection, complement, symmetric diff, power set), recurrence relations (1st/2nd order linear, non-homogeneous), inclusion-exclusion, partition/Stirling numbers, Boolean algebra | SymPy, NumPy | 6 test files: set ops, recurrences, combinatorics, Boolean logic | Recurrences solved via SymPy's `rsolve()` |
| **Numerical Methods** (17 ops) | Root-finding (Newton-Raphson, bisection, secant, Brent), polynomial interpolation (Lagrange, Newton), spline interpolation, finite difference (1st/2nd derivative, Richardson extrapolation), numerical integration (trapezoidal, Simpson, Gauss-Legendre), ODE (RK45, BDF), step control | SciPy.optimize, SciPy.interpolate, NumPy | 8 test files: root-finding, interpolation, differentiation, integration, ODE solvers | Reuses SciPy routines; wraps as first-class operations |

#### **Phase 3: Integration & Cross-Domain Testing** (2–3 days, serial)
1. Verify all 7 domains auto-discovered by registry
2. Test translator can route NL queries to each domain
3. Create exemplary cross-domain tests:
   - Vector calculus + physics.electromagnetism (curl(E) = -∂B/∂t)
   - PDE + physics.thermodynamics (heat diffusion)
   - Sequences/series + physics.waves (Fourier decomposition)
   - Probability + chemistry.kinetics (stochastic fluctuations)
   - Graph theory + chemistry (molecular networks)
4. Verify all 50+ tests pass; determinism verified
5. No regressions in existing 21 domains

#### **Phase 4: Documentation & Final Polish** (1–2 days, serial)
1. Update CLAUDE.md:
   - Add "Phase 6" section
   - Document any new utility patterns discovered (e.g., coordinate transforms)
   - Add 7 new domains to domain coverage list
   - Update extension points section
2. Update `docs/architecture.md`:
   - List all 28 domains
   - Document integration points (vector calculus ↔ electromagnetism, etc.)
   - Solver count summary
3. Final code review (linting, docstrings, type hints)
4. Create a demo end-to-end flow (e.g., translate "Solve heat equation..." → execute PDE solver → return results)

---

## Testing Strategy

### Test Structure per Domain

Each domain gets 6–8 test files (example for probability):

```python
# tests/test_probability.py (main correctness tests)
# tests/test_probability_distributions.py
# tests/test_probability_bayes.py
# tests/test_probability_markov.py
# tests/test_probability_determinism.py (determinism tests)
# tests/test_probability_errors.py (error-path tests)
# tests/test_probability_integration_chemistry.py (cross-domain: kinetics)
```

### Test Types

**1. Correctness Tests** (per-operation verification)
- Compare solver output against independently computed reference values
- Example: `bayes_theorem(0.01, 0.95, 0.0595)` → posterior ≈ 0.1597 (hand-calculated)
- Use existing library (SymPy, SciPy, NumPy) to verify

**2. Determinism Tests** (solve twice → identical results)
```python
def test_determinism_bayes():
    result1 = solver.solve(model)
    result2 = solver.solve(model)
    assert result1.summary == result2.summary  # byte-for-byte identical dicts
```

**3. Error-Path Tests** (invalid inputs → graceful error)
```python
def test_error_invalid_probability():
    # Create model with invalid probability (e.g., P(A) = 1.5)
    result = solver.solve(model)
    assert not result.success
    assert "probability must be in [0,1]" in result.error
```

**4. Edge-Case Tests** (boundary conditions)
- Singular matrices (graph theory, numerical methods)
- Non-convergent series (sequences/series)
- Disconnected graphs (graph theory)
- Zero variance (probability)

**5. Integration Tests** (cross-domain examples)
```python
def test_integration_vector_calculus_electromagnetism():
    # Compute curl(E) for given E field
    # Verify matches physics.electromagnetism ∂B/∂t
```

**6. Operation Dispatch Tests** (verify registry + @register)
```python
def test_dispatch_probability_operations():
    solver = registry.get("mathematics.probability")
    assert solver is not None
    # Verify all 15 operations registered
```

### Test Count Summary
- **Per domain**: 50+ total tests across 7 domains = ~7–8 tests per domain average
- **Types**: 40% correctness, 30% determinism, 20% error paths, 10% edge cases + integration

### CI/CD Integration
- Existing `.github/workflows/ci.yml` already runs `pytest engine/tests/`
- All 50+ new tests included automatically
- No CI changes needed (Phase 5 already set up)

---

## Technical Decisions

### 1. **Single Coordinated Phase vs. Phased Rollout**

**Decision**: Single phase, all 7 domains in parallel.

**Rationale**:
- All 7 share the same architecture (function-dispatch, @register, utils.py, test patterns)
- Coordinated implementation avoids rework and re-discovery of patterns per domain
- Batch orchestration with 7 parallel agents mitigates timeline risk
- If one domain hits blockers (e.g., NetworkX version conflict), others progress independently

**Trade-off**: Higher upfront complexity (7 parallel agents) vs. lower overall timeline and better code consistency.

### 2. **Symbolic vs. Numeric Backends**

**Decision**: Domain-specific (symbolic where possible, numeric fallback).

**Examples**:
- **PDE**: SymPy `dsolve()` for heat/wave/Laplace (closed-form when available); fall back to SciPy `solve_ivp()` for numeric
- **Sequences/Series**: SymPy for Taylor/power series; NumPy FFT for Fourier
- **Graph Theory**: NetworkX (fully numeric) + NumPy (matrix ops)

**Rationale**:
- Symbolic solutions are exact and educational (good for translator examples)
- Numeric fallback handles intractable cases
- Determinism preserved (fixed symbolic algorithms, no randomness except seeded in numeric fallback)

**Trade-off**: Symbolic ≈ slower but exact; numeric ≈ faster but approximate. Solver method configurable in Model.solver.method.

### 3. **NetworkX Dependency**

**Decision**: Add NetworkX 3.0+ to `engine/pyproject.toml`.

**Rationale**:
- Graph algorithms (shortest path, MST, centrality) are non-trivial to implement
- NetworkX is mature, well-tested, and deterministic
- Lighter than scipy.sparse for graph ops

**Trade-off**: New dependency (adds ~2 MB). Acceptable for significant feature (graph theory).

**Verification**: Test that NetworkX is deterministic (same input → same output).

### 4. **Coordinate Transform Utility Functions**

**Decision**: Add coordinate transform helpers to `utils.py` (Cartesian ↔ cylindrical ↔ spherical).

**Rationale**:
- Vector calculus operations (grad, div, curl) differ by coordinate system
- Reusable by vector_calculus.py and physics solvers
- Single source of truth for transforms (DRY)

**Alternative**: Duplicate transforms in each solver (rejected; violates DRY).

### 5. **Error Handling Strategy**

**Decision**: All errors → SolverResult(success=False, error="...") with clear message; no exceptions escape.

**Pattern** (per existing 21 solvers):
```python
@register("mathematics.probability")
class ProbabilitySolver(SolverBase):
    def solve(self, model: ScientificModel) -> SolverResult:
        try:
            # ... computation ...
            return SolverResult(success=True, summary={...})
        except ValueError as e:
            return SolverResult(success=False, error=str(e))
        except Exception as e:
            return SolverResult(success=False, error=f"Internal error: {e}")
```

**Rationale**: Consistent error surface; translator catches errors and returns 400 Bad Request to client.

### 6. **Determinism Guarantee**

**Decision**: All 7 new solvers are pure functions; determinism tests for all.

**Enforcement**:
- No global state, no side effects
- No randomness (use fixed seeds if stochastic needed)
- Numeric libraries (NumPy, SciPy) are deterministic given same inputs

**Verification**: 50+ determinism tests (solve twice → identical dicts).

**Risk**: Floating-point rounding differences across platforms. **Mitigation**: Test with ≈ tolerances (e.g., `assert abs(result1 - result2) < 1e-10`).

### 7. **Integration with Physics/Chemistry**

**Decision**: Loose coupling (math domains independent; physics/chemistry use as needed).

**Examples** (optional demos, not required):
- Vector calculus + physics.electromagnetism: compute curl(E) from given field
- PDE + physics.thermodynamics: solve heat diffusion on 1D rod
- Probability + chemistry.kinetics: compute reaction rate fluctuations

**Rationale**:
- Math domains are self-contained utilities
- Physics/chemistry don't hard-depend on new math domains (existing solvers still work)
- Cross-domain tests verify compatibility without breaking backward compat

### 8. **Operation Count: 10–20 per Domain**

**Decision**: 10–20 core operations per domain; not exhaustive.

**Rationale**:
- Covers 80/20 (most common use cases)
- Avoids feature creep ("implement all possible operations")
- Extensible: easy to add more later

**Per-domain targets** (from implementation approach table):
- Probability: 15 ops
- PDE: 12 ops
- Vector calculus: 18 ops
- Sequences/series: 16 ops
- Graph theory: 14 ops
- Discrete math: 13 ops
- Numerical methods: 17 ops

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| **SymPy performance** (symbolic solvers timeout on large inputs) | Phase 3 testing delays; users frustrated by slow PDE solver | Medium | Set configurable timeout (default 5s); fall back to numeric; document limitations in translator prompt |
| **NetworkX version conflicts** (incompatible with scipy/sympy versions) | Graph theory solver fails to import; phase 2 blocker for that domain | Low | Test compatibility matrix upfront; pin versions in pyproject.toml; use CI to verify |
| **Floating-point determinism** (numeric backends produce slightly different results on different architectures) | Determinism tests fail on some CI runners | Medium | Use relative tolerances (not exact equality) in determinism tests; document precision limits |
| **Translator prompts too vague** (Claude NL→JSON produces invalid Model JSON for complex queries) | Phase 3 integration testing catches errors; rework prompts | Medium | Iterative prompt refinement based on Phase 3 test failures; provide concrete examples in prompts |
| **Missing operation** (discover during testing that important operation is missing) | Minor timeline slip; quick add in Phase 2 or 3 | Low | Prioritize operations by frequency of use; can add more post-Phase 6 if needed |
| **Batch orchestration failures** (one or more parallel agents fail) | Phase 2 timeline slips; need sequential fallback | Medium | CI catches failures immediately; re-run failing agent; progress tracked in task tracking system |
| **CI test flakiness** (determinism tests fail intermittently due to floating-point) | Phase 4 delays; false confidence in non-determinism bug | Medium | Run determinism tests multiple times (e.g., 10x in CI); use statistical tolerance; log seed if stochastic |
| **Backward-compatibility regression** (new code breaks existing 21 solvers) | Phase 3 detects; need urgent fix | Low | Run full test suite (all 21 + 7) frequently; no changes to existing solver code; test isolation |

---

## Success Metrics

### Leading Indicators (during development)

| Metric | Target | How to Measure |
|--------|--------|---|
| Phase 2 completion | All 7 domain solvers implemented & core tests passing | CI green: 50+ tests pass |
| Determinism test pass rate | 100% | Determinism tests (10+ per domain) pass consistently |
| Cross-domain test coverage | ≥3 exemplary integration tests | Tests in test_*_integration_*.py files pass |
| Code review findings | <5 findings per domain | Code review tool (if available) runs without major issues |

### Lagging Indicators (post-merge)

| Metric | Target | How to Measure |
|--------|--------|---|
| All tests passing | 100% of 226 + 50 = 276 tests pass | CI green on main branch |
| No regressions | All 21 existing domain tests still pass | Baseline test run before/after merge |
| Translator routing | All 7 domains auto-discovered | Manual test: `/api/prototype` with query for each domain |
| Documentation completeness | CLAUDE.md + architecture.md updated, translator prompts complete | Peer review of docs |
| Code quality | No linter errors, type hints present, docstrings complete | `pylint`, `mypy` on engine/ (if added to CI) |

---

## Rollback Plan

### If Critical Issue Discovered

1. **During Phase 2** (parallel implementation):
   - Abort failing agent(s); revert those domain branches
   - Continue with successful domains (partial rollout)
   - Fallback: implement failures sequentially in Phase 3

2. **During Phase 3** (integration testing):
   - If cross-domain test fails (e.g., PDE + thermodynamics incompatible):
     - Revert integration test changes; keep solvers standalone
     - File issue for future refinement

3. **During Phase 4** (documentation):
   - If docs incomplete, merge with TODO notes
   - Complete docs in follow-up PR

4. **Post-merge** (if regression in production):
   - Option A: Temporarily disable problematic domain in translator (remove from enum)
   - Option B: Revert commit; hot-fix and re-land
   - Trigger post-mortem to identify root cause

### Emergency Revert
```bash
git revert <merge-commit-hash>
# or, if recent (safe):
git reset --hard HEAD~1
```

---

## Implementation Checklist (for Build Phase)

### Per-Domain Checklist

For each of the 7 domains, verify:

- [ ] Solver file created (`engine/app/solvers/<domain>.py`)
- [ ] @register decorator applied with correct domain string
- [ ] 10–20 module-level operation functions implemented
- [ ] _OPERATIONS dict complete with all operations
- [ ] solve() method delegates to run_dispatch()
- [ ] Error handling: all exceptions → SolverResult(success=False, ...)
- [ ] Translator prompt file created (`translator-prompts/mathematics.<domain>.txt`)
- [ ] Translator prompt documents all operations, examples, constraints
- [ ] 6–8 test files created (correctness, determinism, error paths, integration)
- [ ] All tests passing locally (`pytest engine/tests/test_<domain>*.py`)
- [ ] Determinism verified (solve twice → identical results)
- [ ] No regressions in existing tests

### Global Checklist

- [ ] Schema updated: all 7 domain strings added to `domain` enum (alphabetical order)
- [ ] All 7 domains auto-discovered by registry (verified via logger or manual test)
- [ ] Translator prompts auto-loaded by Spring (no code changes)
- [ ] Cross-domain integration tests passing (vector calculus + EM, PDE + thermo, etc.)
- [ ] CLAUDE.md updated (Phase 6 section, new patterns, domain list)
- [ ] `docs/architecture.md` updated (28 domains, integration points)
- [ ] Full test suite passes: `pytest engine/tests/` (~276 tests)
- [ ] No linter/type-check errors
- [ ] CI green (GitHub Actions)
- [ ] Commit message & PR description complete

---

## Estimated Timeline

| Phase | Duration | Owner | Deliverable |
|-------|----------|-------|-------------|
| Phase 1: Design & Setup | 2–3 days | Lead + Team | Skeleton code, schema update, stub prompts/tests |
| Phase 2: Implementation | 5–7 days | 7 parallel agents (Claude) | 7 complete solvers + 50+ tests |
| Phase 3: Integration | 2–3 days | Lead | Cross-domain tests, determinism verified, no regressions |
| Phase 4: Docs & Polish | 1–2 days | Lead | CLAUDE.md, architecture.md updated, end-to-end demo |
| **Total** | **~3 weeks** | | Merge-ready PR |

---

## Definition of Done

✅ This specification is complete and ready for Build phase when:

- [ ] Intent.md approved and committed
- [ ] Spec.md reviewed by team (this document)
- [ ] Clarifying questions answered
- [ ] No architectural blockers identified
- [ ] Ready to launch `/sdlc-build` with 7 parallel agents

---

## References

- **Intent**: `intent-expand-mathematics-domains.md`
- **Architecture**: `docs/architecture.md`, `docs/adr/0002-llm-translator-boundary.md`
- **Solver Pattern**: `engine/app/solvers/physics_thermodynamics.py` (example Phase 2 solver)
- **Test Pattern**: `engine/tests/test_statistics.py` (example test suite)
- **Utilities**: `engine/app/solvers/utils.py` (dispatch helpers)
- **Schema**: `schemas/model.schema.json`
- **Build Skill**: `/sdlc-build` (next phase)

---

**Next Step**: Review this spec.md. Once approved, proceed to `/sdlc-build` for implementation via batch orchestration (7 parallel agents, one per domain).
