# ADR 0002: LLM as Translator Only — Determinism Boundary

## Status
**ACCEPTED**

## Context
The original vision: "understand scientific information" + "deterministic, optimized" system.

These seem contradictory at first: LLMs are non-deterministic (temperature > 0, token sampling), but determinism is a hard requirement.

How do we square this circle?

## Decision
**LLM translates natural language → schema-validated Model; all computation is 100% deterministic downstream.**

### Architecture
```
User Input (NL)
    ↓
[Translator: Claude + schema validation]  ← LLM boundary
    ↓
Scientific Model (JSON, schema-validated)
    ↓
[Validator, Solver, Results]              ← 100% deterministic
    ↓
Results (byte-for-byte reproducible)
```

The LLM's job: map fuzzy human intent onto a formal, structured Model.  
The solver's job: execute that Model deterministically.

## Rationale

### What "Deterministic" Means Here
- Same Model input → same output (to numeric precision)
- No randomness in computation path
- Reproducible: run twice, get byte-identical results
- **Not** deterministic: LLM translation (may rephrase, retry validation, etc.)

### Why This Works
1. **LLM never touches computation**
   - No ML models evaluating equations
   - No neural networks in the solver
   - No probabilistic physics

2. **Model is the contract**
   - LLM produces a Model (JSON)
   - Validated against schema before solver sees it
   - Solver has no wiggle room: given Model X, it runs algorithm Y deterministically

3. **Audit trail**
   - Every result includes the Model that produced it
   - User can see exactly what was computed
   - Reproducibility guaranteed by replaying the Model

### Practical Example
```
User: "Ball at 20 m/s, 45°, 0.5kg, drag 0.1 — how far?"

LLM (may be non-deterministic):
  First try: v0=20, angle=45, mass=0.5, drag=0.1
  Validates? ✓ → Return Model
  
  (OR) Validates? ✗ → Retry, refine quantities
  
Second user with same query:
  LLM might rephrase, reorder quantities, but produces
  same structural Model (schema-validated)
  
Same Model → Solver runs it identically
  → Same trajectory, same summary
```

## Consequences

### Good
- **Determinism guarantee**: Results are reproducible
- **Explainability**: Model is human-readable; user sees what was computed
- **Auditability**: Every decision traceable to a Model structure
- **Testability**: Golden-file tests work (fixed input → fixed output)
- **Extensibility**: Solver doesn't need to know about natural language

### Bad
- **Two stages of interpretation**: LLM translates; user may have to refine
  - *Mitigation*: Good validation error messages guide user
  - *Mitigation*: Retry with feedback loop (not in first slice)
- **Schema complexity**: Model must be expressive enough for all domains
  - *Mitigation*: Extensible schema; domain-specific fields added over time

## Alternatives Considered

### 1. End-to-end LLM (LLM runs the solver)
- ✗ Non-deterministic
- ✗ Can't guarantee correctness of computation
- ✗ No audit trail
- ✓ Simple

### 2. Hybrid: LLM in the solver
- ✗ Loses determinism
- ✗ Slow (ML inference per solve)
- ✗ Impossible to debug: "Why does it give this answer?"

### 3. No LLM: Pure manual Model entry
- ✓ Deterministic
- ✗ Defeats "understand scientific information" goal
- ✗ Steep learning curve (user must write formal Model)

## Implementation Notes

### Schema Validation
- `schemas/model.schema.json` is the hard boundary
- Invalid Models are rejected; LLM retries or returns error
- No coercion or defaults; explicit is required

### LLM Integration
- Use Claude's structured output / tool-use mode
- Constrain output to Model schema
- Validate response before returning to user
- Store original query in Model.metadata for audit trail

### Solver Determinism
- All RNG seeded (if any) to fixed values
- Solver method, tolerance, time span explicit in Model
- Dependencies pinned via lockfile
- No wall-clock time or external state in computation

### Testing
- Unit tests: Dimension arithmetic, unit parsing (no LLM involved)
- Integration tests: Model → validated Model (schema checks)
- End-to-end tests: Model → deterministic results (golden files)
- Determinism tests: Run twice, compare byte-for-byte

## Monitoring & Maintenance
- Track LLM translation errors (validation failures)
- If schema changes, update both LLM prompt and validation logic
- Monitor solver precision (if results start drifting, check dependencies/config)

## References
- [[0001-polyglot-monorepo]]
- `schemas/model.schema.json`
- `app/solver.py` (deterministic solve path)
- `app/main.py` (endpoint that echoes Model in response)

---

## Summary
The system achieves both goals — "AI understands" and "deterministic" — by drawing a clear boundary: LLM produces a formal Model, and everything downstream is pure, deterministic computation. This makes the system auditable, reproducible, and trustworthy for scientific use.
