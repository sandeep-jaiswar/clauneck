# Intent: Expand clauneck to Physics and Chemistry Domains (Phase 2)

**Author**: Sandeep Jaiswar  
**Date**: 2026-09-15  
**Timeline**: Next 12 months (through Q3 2026)  
**Status**: Planning Phase

---

## Problem Statement

clauneck currently solves **11 mathematical problem types** (algebra, calculus, linear algebra, statistics, trigonometry, number theory, geometry, optimization, complex numbers, ODE, physics.mechanics). While mathematically comprehensive, the platform cannot yet prototype scientific ideas in **physics (beyond mechanics)** or **chemistry**, severely limiting its utility for experimental feasibility modeling and theoretical exploration.

Users cannot describe:
- *"Will this chemical reaction reach equilibrium at these concentrations?"*
- *"What's the heat released in this combustion under these conditions?"*
- *"How does temperature affect reaction kinetics here?"*
- *"What's the voltage/current behavior in this electromagnetic circuit?"*
- *"How does temperature affect the wavelength distribution in thermal radiation?"*

This gap prevents clauneck from fulfilling its core mission: **enable anyone to prototype any scientific idea deterministically**.

---

## Goal

Make clauneck the **universal scientific prototyping platform** by systematically adding domain solvers across physics and chemistry. By end of 2026:

1. Expand from 11 mathematical domains to **21+ problem types**
2. Launch **5 new physics domains** (beyond mechanics)
3. Launch **5 new chemistry domains** to enable chemical feasibility modeling
4. Maintain **deterministic guarantees** across all new domains (byte-for-byte identical results)
5. Keep **schema backward-compatible** and follow **DRY/SOLID principles**
6. Enable end-to-end NL → Model → Result for all 10 new domains via translator layer

**Long-term vision**: clauneck should eventually know **all mathematics, physics, and chemistry** and enable users to prototype any scientific idea deterministically.

---

## Success Criteria

### Phase 2 (2026, Q4–Q3)

**Quantitative**:
- [ ] 5 physics domains implemented and passing golden-file determinism tests
- [ ] 5 chemistry domains implemented and passing golden-file determinism tests
- [ ] Schema extended with ≥10 new domain enum values (backward-compatible)
- [ ] 100% test coverage for each new domain (at least 2 real-world test cases per domain)
- [ ] Zero regressions: existing 11 math domains + 1 physics domain (mechanics) still pass all tests
- [ ] End-to-end: natural-language query → Model → SolverResult for ≥3 new domains via translator

**Qualitative**:
- [ ] Each domain has a dedicated solver class inheriting from `SolverBase`
- [ ] Each domain registered via `@register(domain)` decorator (no manual registry updates)
- [ ] Documentation updated: `docs/architecture.md`, CLAUDE.md, ADRs for new patterns
- [ ] Translator prompts generalized to handle new domains without hardcoding
- [ ] CI/CD validates all 21 domains on push/PR

**Determinism**:
- [ ] Each new domain passes 2+ golden-file comparison tests (SymPy/SciPy with pinned versions)
- [ ] Identical Model input → byte-for-byte identical results (verified via test harness)
- [ ] No random initialization or non-deterministic solver steps in any domain

---

## Scope: In/Out

### In Scope (Phase 2)

**Physics Domains** (5 new):
1. `physics.thermodynamics` — Energy, entropy, heat transfer, first/second laws, ideal gas law
2. `physics.waves` — Wave propagation, interference, resonance, Doppler effect, standing waves
3. `physics.electromagnetism` — Coulomb's law, electric/magnetic fields, circuits, Ohm's law, induction
4. `physics.simple_harmonic_motion` — Oscillators, pendulums, springs, damping, resonance
5. `physics.collisions` — Elastic/inelastic collisions, momentum conservation, center of mass, impulse

**Chemistry Domains** (5 new):
1. `chemistry.kinetics` — Reaction rates, rate laws, activation energy, Arrhenius equation, half-life
2. `chemistry.equilibrium` — Equilibrium constants, Le Chatelier's principle, concentration distributions
3. `chemistry.thermochemistry` — Enthalpy, Hess's law, calorimetry, standard heat of reaction
4. `chemistry.acid_base_equilibrium` — pH, pOH, buffer solutions, Henderson-Hasselbalch, titration curves
5. `chemistry.redox_reactions` — Redox balancing, electrode potentials, electrochemistry, Nernst equation

### Out of Scope (Phase 2)

- Organic chemistry (synthesis, reaction mechanisms) — too specialized for Phase 2
- Quantum mechanics / molecular orbital theory — requires specialized matrix handling
- Fluid dynamics / CFD — requires PDE solvers beyond ODE scope
- Phase equilibria / phase diagrams — requires experimental data + interpolation
- Spectroscopy / optical properties — requires quantum mechanics foundations
- Custom knowledge graphs or domain-specific heuristics — LLM translates, doesn't solve
- UI/UX improvements — solver correctness is priority
- Performance tuning or parallelization — correctness first

---

## Affected Modules

### Java / Spring Boot (web module)
- **No code changes** if translator + schema validation already generalize to new domains
- Optional: Add domain-specific prompt templates in `ClaudeTranslator` (e.g., different phrasing for kinetics vs. thermodynamics)
- Optional: Add logging/monitoring for new domain routing and success rates

### Python / FastAPI (engine module)
- **solvers/** directory:
  - Add `physics_thermodynamics.py` with `PhysicsThermodynamicsSolver` (register as `physics.thermodynamics`)
  - Add `physics_waves.py` → `PhysicsWavesSolver`
  - Add `physics_electromagnetism.py` → `PhysicsElectromagnetismSolver`
  - Add `physics_shm.py` → `PhysicsSimpleHarmonicMotionSolver`
  - Add `physics_collisions.py` → `PhysicsCollisionsSolver`
  - Add `chemistry_kinetics.py` → `ChemistryKineticsSolver`
  - Add `chemistry_equilibrium.py` → `ChemistryEquilibriumSolver`
  - Add `chemistry_thermochemistry.py` → `ChemistryThermochemistrySolver`
  - Add `chemistry_acid_base.py` → `ChemistryAcidBaseSolver`
  - Add `chemistry_redox.py` → `ChemistryRedoxSolver`
- **tests/** directory:
  - Add ≥2 test cases per domain (golden-file + determinism checks)
  - Extend test suite to validate schema extension
- **app/main.py** — No changes (registry auto-discovery handles new solvers automatically)
- **app/model.py** — May need to update Pydantic models if new solver configs are needed

### Schema (schemas/model.schema.json)
- Extend `domain` enum to include all 10 new domains:
  ```json
  "enum": [
    "physics.mechanics",
    "physics.thermodynamics",
    "physics.waves",
    "physics.electromagnetism",
    "physics.simple_harmonic_motion",
    "physics.collisions",
    "chemistry.kinetics",
    "chemistry.equilibrium",
    "chemistry.thermochemistry",
    "chemistry.acid_base_equilibrium",
    "chemistry.redox_reactions",
    "mathematics.algebra",
    ...rest of math domains...
  ]
  ```
- Ensure `quantities` schema handles all SI units for new domains (already flexible via `siUnit` string + `dimensionVector`)
- Ensure `solver` config schema is extensible for domain-specific parameters (rate law method for kinetics, collision type for collisions, etc.)
- **No breaking changes**: existing clients can still use old domains

### Documentation (docs/)
- Update `docs/architecture.md` with new domains, solver routing examples, and unit handling strategy
- Add ADR for physics/chemistry implementation patterns (e.g., how to handle units like mol/L, kJ/mol, J/K)
- Update CLAUDE.md with new build/test commands and solver registration pattern
- Add example queries and expected Model/Result for each new domain

---

## Dependencies

### Internal
- Existing `SolverBase` class (provides `solve()` contract)
- Existing `@register()` decorator and registry pattern (auto-discovery)
- Existing schema validation in web module (must extend cleanly)
- Existing translator layer (Claude API integration, Spring Boot plumbing)
- Python 3.10+ with SymPy, SciPy, NumPy (already pinned in engine)

### External
- **SymPy** (existing) — Symbolic math for algebra, calculus, thermodynamics, kinetics
- **SciPy** (existing) — Numeric ODE solver (kinetics, collisions), optimization (equilibrium)
- **NumPy** (existing) — Linear algebra utilities, array operations
- **Pydantic** (existing) — Schema validation
- **FastAPI** (existing) — API framework

### No New Dependencies Required
- All 10 domains solvable with SymPy + SciPy + NumPy ecosystem
- No external APIs or data files needed (deterministic computation only)
- Existing Anthropic SDK for translator

---

## Known Constraints

### Technical

1. **Determinism**: SymPy/SciPy must produce byte-for-byte identical results with pinned versions. All new solvers must pass golden-file tests.
2. **Schema Extensibility**: Each new domain may need solver-specific config params:
   - `chemistry.kinetics`: rate-law method (rate_law), order
   - `physics.collisions`: collision type (elastic/inelastic), is_1d
   - `physics.electromagnetism`: circuit_type (series/parallel)
   - Schema must remain backward-compatible (new fields optional, defaults provided)
3. **No Coupled PDEs in Phase 2**: ODE solvers handle single/multi-variable ODEs; PDEs (diffusion, heat equation) deferred to Phase 3.
4. **Unit System**: SI units only. Chemistry domains may use non-SI (mol, J/mol, M for molarity); must be convertible to SI or marked `dimensionless` with notes in quantity description.
5. **Translator Complexity**: Claude must understand domain-specific notation (e.g., K_eq for equilibrium constant, E_a for activation energy). Solver config must capture these clearly.

### Resource
- 1 developer (Sandeep) over 12 months
- No external research staff or domain experts required (problems are well-known physics/chemistry)
- Testing + documentation burden increases with 10 new domains

### Timeline
- **Q4 2025 (this month)**: Planning + Design phase, schema planning, spike on 1–2 domains
- **Q1–Q2 2026**: Implement 5 physics domains, deploy to production, gather feedback
- **Q3 2026**: Implement 5 chemistry domains, close Phase 2, prepare Phase 3 roadmap

---

## Background & Context

### Current State (Phase 1 Complete)
- **11 mathematical domains** working end-to-end (algebra, calculus, linear algebra, statistics, trigonometry, number theory, geometry, optimization, complex numbers, ODE)
- **1 physics domain** (physics.mechanics / projectile motion)
- **Vertical slice validated**: End-to-end flow (NL → Model → Solver → Result) proven with translator layer
- **Architecture stable**: Domain registry, solver pattern, schema validation proven
- **Production ready**: Spring Boot API gateway, FastAPI engine, CI/CD pipeline, Postman tests

### Why Phase 2 Now?
1. **Math + mechanics foundation complete**: 12 domains provide strong confidence in solver architecture and determinism strategy
2. **User demand**: Chemistry (kinetics, equilibrium) and physics (thermodynamics, waves) frequently requested
3. **Architectural confidence**: Schema extensibility proven; translator generalization working
4. **Market timing**: Positioning clauneck as comprehensive scientific tool requires coverage beyond mechanics

### Why This Order?
- **Physics first** (Q1–Q2 2026): Builds directly on existing mechanics solver, shares SciPy/SymPy infrastructure, lower mental model leap
- **Chemistry second** (Q3 2026): Larger conceptual shift (stoichiometry, equilibrium constants, rates); benefits from physics patterns established first

### Vision Trajectory
```
Phase 1 (Complete): Math + Physics.Mechanics (11 + 1 = 12 domains)
    ↓
Phase 2 (This Sprint): +5 Physics + 5 Chemistry (12 + 10 = 22 domains)
    ↓
Phase 3 (2027): +Organic Chemistry, Quantum, Spectroscopy, Materials Science (22 + N)
    ↓
Phase 4 (2027+): Full Coverage — "clauneck knows all science"
```

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Schema breaks on new domains | High | Add new enum values carefully; always extend, never delete; CI validates all 22 domains |
| Solver determinism fails for new physics/chemistry | High | Golden-file tests mandatory for each domain; SymPy/SciPy pinned strictly; test on multiple OS/Python versions |
| Translator prompts become domain-specific spaghetti | Medium | Generalize prompts in Design phase; use shared template with domain enum + field mappings |
| Performance degrades with larger solver set | Low | Registry is O(1); each solve() domain-specific, unaffected by total count; lazy-load if needed |
| Scope creep (e.g., add quantum mechanics mid-sprint) | High | Enforce Phase 2 boundary strictly via intent.md; defer out-of-scope to Phase 3 roadmap |
| Numerical stability in kinetics/collisions solvers | Medium | Thorough testing with edge cases (very small/large rate constants, high-speed collisions); choose stable ODE methods (RK45) |
| Natural-language ambiguity for new domains | Medium | Translator already proven; Design phase will create domain-specific example queries and translator guidance |

---

## Success Metrics (Lagging)

After Phase 2 closes (end Q3 2026):
1. **Coverage**: Can solve any problem in 22 domains (11 math + 1 physics.mechanics + 5 physics + 5 chemistry)
2. **Determinism**: 100% of 10 new solvers pass golden-file tests; zero regressions in existing domains
3. **Schema**: No breaking changes to existing clients; clean enum extension
4. **Test quality**: >90% code coverage on new solver modules; ≥2 real-world test cases per domain
5. **Translator**: End-to-end NL queries work for ≥50% of new domains (with tweaking, 100% achievable)
6. **User impact**: Documentation, examples, and Postman test suite for each domain; demo-able live prototype

---

## Next Artifact

Once intent-expand-physics-chemistry.md is approved, move to **Design phase** (`/sdlc design expand-physics-chemistry`):
- Detailed spec for each solver (input/output contract, test cases, edge cases)
- Schema finalization (all 10 new enum values, solver config params)
- Translator prompt templates for new domains
- Dependency verification (confirm SymPy/SciPy can handle all solvers)
- Risk mitigation plan (determinism strategy, golden-file approach, testing matrix)
- Build + deploy strategy (phased: 5 physics → 5 chemistry)

---

**Versioned**: Created 2026-09-15  
**Approval**: Awaiting review and merge to production  
**Owner**: Sandeep Jaiswar  
**Co-Authored-By**: Claude Haiku 4.5 <noreply@anthropic.com>
