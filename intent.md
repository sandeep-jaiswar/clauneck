# Intent: Implement Translator Layer for NL → Model JSON

**Author**: sandeep-jaiswar  
**Date**: 2026-09-15  
**Status**: DRAFT  
**Tracking Issue**: (none yet)

---

## Problem Statement

Currently, users must manually construct JSON models matching `schemas/model.schema.json` to use the Clauneck engine. This is a barrier to adoption: scientists describe problems in natural language (e.g., "Ball at 20 m/s, 45°, mass 0.5kg, drag 0.1"), but must learn JSON schema details to interact with the system.

**Pain Point**: Manual JSON construction is error-prone, time-consuming, and not scalable.

**Why Now**: The deterministic solver engine (Layer 4) is complete and proven. The validator (Layer 3) is working. The translator is the bottleneck blocking end-to-end natural-language-to-results flow.

---

## Goals

1. **Enable NL queries** - Accept natural language descriptions and convert to valid Model JSON
2. **Strict safety** - Ensure all outputs conform to schema; reject ambiguous or invalid inputs
3. **Domain-focused** - Focus on physics.mechanics (projectile motion) as the first and only supported domain
4. **Fast path** - Implement and integrate within one week using minimal but solid scope
5. **Configurable** - Allow switching Claude models via environment variable (default: Haiku for speed/cost)

---

## Success Criteria

- [ ] **Functional**: NL query → valid Model JSON → deterministic solver result (end-to-end)
- [ ] **Schema-Compliant**: 100% of translator outputs pass `model.schema.json` validation
- [ ] **Tested**: Unit tests for NL→JSON + integration tests for full stack
- [ ] **Configurable**: Model selection via `CLAUDE_MODEL` env var (default: claude-haiku-4-5)
- [ ] **Error Handling**: Invalid/ambiguous queries rejected with clear error messages (not silent failures)
- [ ] **Documented**: Translator logic, prompts, and constraints documented in code
- [ ] **Endpoint Live**: `POST /api/prototype` accepts NL + returns Model+Result

---

## Scope

### In Scope
- Translator controller in `web` module (Spring Boot)
- Natural language → Model JSON conversion using Claude API
- Strict schema validation + rejection of invalid outputs
- Support for physics.mechanics domain (projectile motion with/without drag)
- Basic test suite (unit + integration)
- Environment-based model configuration

### Out of Scope (Future Slices)
- Support for other domains (thermodynamics, chemistry, math)
- Advanced error recovery (e.g., fuzzy matching, auto-repair of LLM output)
- User authentication/rate limiting
- Caching or memoization of queries
- Frontend UI for natural language input
- Batch processing or async endpoints

---

## Affected Modules

| Module | Change | Reason |
|--------|--------|--------|
| **web** | Add `TranslatorController` + `ClaudeTranslator` service | New translator endpoint + LLM integration |
| **core** | No changes | Validation layer already exists |
| **engine** | No changes | Solver engine unchanged |
| **schemas** | No changes | Schema is the contract; translator conforms to it |

---

## Dependencies

### Internal
- `core` module for dimensional analysis + schema validation
- `engine` module for solver integration (already running on port 8001)

### External
- **Claude API** (Anthropic)
  - Models: claude-3-5-haiku (default), claude-3-5-sonnet, claude-opus-4
  - Requires API key in environment (`ANTHROPIC_API_KEY`)
  - Rate limits: standard tier (~100K tokens/min)

### Build & Runtime
- Spring Boot 3.2.2 (already in place)
- Gradle 4.4.1 (already in place)
- Java 21 (already in place)
- Jackson or similar JSON parsing (for response handling)

---

## Known Constraints

### Technical
1. **Schema Strictness**: Translator must produce 100% schema-compliant JSON. No partial/malformed models accepted.
2. **Domain Limitation**: Phase 1 supports only `physics.mechanics`. Other domains return 501 "Not Implemented".
3. **Determinism**: The translator itself is non-deterministic (LLM output varies). But once Model JSON is produced, solver is deterministic.
4. **Token Budget**: Default Haiku model ~4K context. Projectile motion descriptions fit easily; complex multi-domain problems may require Sonnet.

### Timeline
- **Deadline**: End of week (2026-09-19)
- **Dev Time**: ~3 days
- **Testing/Integration**: ~1 day
- **Contingency**: Switch to simpler domain-specific parsing if Claude integration hits blockers

### Resource
- 1 developer (Sandeep)
- Claude Code for implementation (pair programming with AI)
- Local testing (port 8080 for web, port 8001 for engine)

---

## Background & Context

### Architecture Rationale
From `CLAUDE.md` and `docs/adr/0002-llm-translator-boundary.md`:
- LLM is constrained to translation only (NL → structured schema)
- Computation stays deterministic (SymPy + SciPy)
- Clear separation: LLM doesn't touch math, only schema mapping

### Vertical Slice Success
The projectile motion solver works end-to-end (determinism verified, range=7.52m). Translator unblocks the human-facing entry point.

### Why This Matters
Once translator is live, the full system is:
```
Natural Language
    ↓ [Translator: Claude API]
Schema-Validated Model JSON
    ↓ [Validator: Core module]
Dimension checks + routing
    ↓ [Solver: Engine microservice]
Deterministic result (trajectory + summary)
```

This demo-able flow is powerful for attracting collaborators and users.

---

## Implementation Sketch (Out of Scope for Intent, But Noted)

1. **Controller** (`web/src/.../api/PrototypeController.java`)
   - `POST /api/prototype` → accept NL query + optional overrides
   - Route to TranslatorService

2. **TranslatorService** (`web/src/.../service/ClaudeTranslator.java`)
   - Build Claude prompt (domain-specific, schema constraints)
   - Call Claude API (configurable model)
   - Validate JSON output against schema
   - Reject if invalid; return error + suggestion

3. **Schema Validator** (reuse from `core`)
   - Already exists; pass Model JSON through it
   - Return validation errors to caller

4. **Integration**
   - Call engine `/api/solve` to compute result
   - Return combined response: Model + Solver Result

---

## Success Timeline

| Date | Milestone | Owner |
|------|-----------|-------|
| 2026-09-15 | Intent.md drafted & committed | Sandeep |
| 2026-09-16 | Design spec.md complete | Claude + Sandeep |
| 2026-09-17 | Core translator implementation | Claude + Sandeep |
| 2026-09-18 | Integration testing + bug fixes | Sandeep |
| 2026-09-19 | End-to-end demo + documentation | Claude + Sandeep |
| 2026-09-20 | PR review + merge (if approved) | Sandeep |

---

## Questions for Product Owner / Reviewers

1. Should the translator support partial/incomplete models (e.g., user specifies v0 and angle, we infer mass/g from defaults)?
2. Should we accept alternate unit systems (e.g., feet/pounds) and auto-convert to SI?
3. What's the expected latency SLA for `/api/prototype`? (Claude API adds ~1-2s per request)
4. Should rejected queries (invalid LLM output) be logged for future training/improvement?

---

## References

- Architecture: `docs/architecture.md` (Layer 2: Translator)
- ADR: `docs/adr/0002-llm-translator-boundary.md`
- Schema: `schemas/model.schema.json`
- Previous Demo: Projectile motion solver verified deterministic (7.52m range)
- CLAUDE.md: Extension points, build commands, CI/CD integration notes

---

**Next Step**: Proceed to `/sdlc-design` to create detailed spec.md with implementation approach.
