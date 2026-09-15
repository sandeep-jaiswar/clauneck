# Specification: Translator Layer (NL → Model JSON)

**Author**: Claude Haiku 4.5 + sandeep-jaiswar  
**Date**: 2026-09-16  
**Status**: DRAFT (awaiting technical review)  
**Implements**: intent.md (translator layer)  
**Timeline**: Sept 16-19, 2026

---

## Overview

This specification details the implementation of **Layer 2: Translator** in the Clauneck architecture. The translator converts natural language scientific queries into schema-validated Model JSON using Claude API, enabling end-to-end NL→Results workflows.

**Scope**: Physics.mechanics domain (projectile motion) with strict schema validation, configurable Claude model, and clear error handling.

**Outcome**: Users can query the system in plain English and receive deterministic computational results without manually writing JSON.

---

## Requirements

### Functional Requirements

| ID | Requirement | Acceptance Criteria |
|----|-------------|-------------------|
| **FR1** | Accept natural language query | `POST /api/prototype` accepts JSON with `query` field (string, 1-1000 chars) |
| **FR2** | Translate NL to Model JSON | Claude produces valid `ScientificModel` matching `schemas/model.schema.json` |
| **FR3** | Strict schema validation | Invalid JSON is rejected with 400 error + specific validation message |
| **FR4** | Return deterministic result | Model is sent to engine `/api/solve`, response includes both Model and SolverResult |
| **FR5** | Domain routing | `physics.mechanics` queries routed to ProjectileMotionSolver; other domains return 501 |
| **FR6** | Error clarity | All rejection reasons (invalid NL, schema violation, domain unsupported) are logged and returned to client |
| **FR7** | Configurable LLM model | Claude model selected via `CLAUDE_MODEL` env var (default: `claude-haiku-4-5`) |
| **FR8** | Input validation | Reject queries that are ambiguous, nonsensical, or outside domain scope with helpful error message |

### Non-Functional Requirements

| ID | Requirement | Target | Rationale |
|----|-------------|--------|-----------|
| **NFR1** | Latency | < 5s (including Claude API) | Interactive feel; Claude adds ~1-2s per request |
| **NFR2** | Availability | Graceful degradation if Claude API down | Return 503 with retry guidance, not 500 crash |
| **NFR3** | Security | API key in environment variable, never logged | Prevent credential leaks in logs/responses |
| **NFR4** | Maintainability | Prompt and schema constraints documented in code | Future developers can iterate on translator logic |
| **NFR5** | Testability | Unit tests for translate logic, integration tests for full stack | Enables regression testing and model validation |

---

## Architecture & Design

### High-Level Flow

```
Client Request
    ↓
┌─────────────────────────────────────────────────────────────┐
│ POST /api/prototype                                          │
│ { "query": "Ball at 20 m/s, 45°, mass 0.5kg, drag 0.1" }   │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ PrototypeController (Spring REST)                            │
│ • Validate input format                                      │
│ • Extract query string                                       │
│ • Route to ClaudeTranslator                                  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ ClaudeTranslator (Service)                                   │
│ • Build system prompt (physics.mechanics, schema constraints)│
│ • Call Claude API (model from CLAUDE_MODEL env)              │
│ • Parse JSON response                                        │
│ • Validate against JsonSchema                                │
│ • Return Model or ValidationException                        │
└─────────────────────────────────────────────────────────────┘
    ↓ (if valid)
┌─────────────────────────────────────────────────────────────┐
│ EngineClient (HTTP client to localhost:8001)                 │
│ • POST /api/solve with Model JSON                            │
│ • Receive PrototypeResponse (Model + SolverResult)           │
│ • Return combined response to client                         │
└─────────────────────────────────────────────────────────────┘
    ↓ (if invalid)
┌─────────────────────────────────────────────────────────────┐
│ ValidationException Handler (ControllerAdvice)               │
│ • Extract validation errors                                  │
│ • Return 400 with error details + suggestion                 │
│ • Log for monitoring                                         │
└─────────────────────────────────────────────────────────────┘
    ↓
Client Response (200 or 400 with details)
```

### Module Changes

#### **web** Module Changes

**New Classes**:

1. **`com.clauneck.web.api.dto.PrototypeRequest`**
   ```java
   public class PrototypeRequest {
       private String query;  // Natural language query (required, 1-1000 chars)
       // Optional overrides for power-users
       private Map<String, Double> parameterOverrides;  // e.g., {"mass": 1.0}
   }
   ```

2. **`com.clauneck.web.api.dto.PrototypeResponse`**
   ```java
   public class PrototypeResponse {
       private ScientificModel model;       // Echoed input model
       private SolverResult result;         // Result from engine
       private String message;              // Status message
   }
   ```

3. **`com.clauneck.web.api.PrototypeController`** (REST endpoint)
   ```java
   @RestController
   @RequestMapping("/api/prototype")
   public class PrototypeController {
       @PostMapping
       public PrototypeResponse prototype(@RequestBody PrototypeRequest request)
           throws TranslationException, EngineException { ... }
   }
   ```

4. **`com.clauneck.web.service.ClaudeTranslator`** (Main translator logic)
   ```java
   @Service
   public class ClaudeTranslator {
       // Build domain-specific prompts
       private String buildPrompt(String query) { ... }
       
       // Call Claude API with retry logic
       private String callClaudeAPI(String prompt) throws TranslationException { ... }
       
       // Translate NL query → Model JSON
       public ScientificModel translate(String query) 
           throws TranslationException, ValidationException { ... }
       
       // Validate JSON against schema
       private void validateSchema(ScientificModel model) throws ValidationException { ... }
   }
   ```

5. **`com.clauneck.web.client.EngineClient`** (HTTP client to engine microservice)
   ```java
   @Service
   public class EngineClient {
       private final RestTemplate restTemplate;
       private static final String ENGINE_URL = "http://localhost:8001/api/solve";
       
       public PrototypeResponse solve(ScientificModel model) throws EngineException { ... }
   }
   ```

6. **`com.clauneck.web.exception.TranslationException`**
   ```java
   public class TranslationException extends RuntimeException { ... }
   ```

7. **`com.clauneck.web.exception.PrototypeExceptionHandler`** (Global exception handling)
   ```java
   @RestControllerAdvice
   public class PrototypeExceptionHandler {
       @ExceptionHandler(TranslationException.class)
       public ResponseEntity<?> handleTranslationError(TranslationException e) { ... }
       
       @ExceptionHandler(ValidationException.class)
       public ResponseEntity<?> handleValidationError(ValidationException e) { ... }
   }
   ```

**Modified Files**:

1. **`build.gradle`** - Add dependencies:
   ```gradle
   dependencies {
       // Existing
       implementation project(':core')
       implementation 'org.springframework.boot:spring-boot-starter-web:3.2.2'
       
       // New: Anthropic SDK
       implementation 'com.anthropic:sdk:0.1.0'  // (or latest)
       
       // JSON Schema validation
       implementation 'com.networknt:json-schema-validator:1.0.88'
       
       // HTTP client (already included via Spring)
       implementation 'org.springframework.boot:spring-boot-starter-webflux'
   }
   ```

2. **`src/main/resources/application.yml`** - Add configuration:
   ```yaml
   clauneck:
     translator:
       model: ${CLAUDE_MODEL:claude-haiku-4-5}
       timeout-seconds: 30
       max-retries: 2
     engine:
       url: http://localhost:8001
       timeout-seconds: 30
   ```

**Configuration**:

- **Environment Variables**:
  - `ANTHROPIC_API_KEY`: Claude API authentication (required at runtime)
  - `CLAUDE_MODEL`: Model selection (default: `claude-haiku-4-5`)
  - `CLAUNECK_ENGINE_URL`: Engine service URL (default: `http://localhost:8001`)

#### **core** Module Changes

**No changes**. The `DimensionalAnalyzer` and schema validation already exist. Translator will reuse validation logic via the engine's `/api/solve` endpoint (engine does validation before solving).

#### **engine** Module Changes

**No changes**. The Python engine already validates Model JSON against schema and rejects invalid inputs.

---

## Implementation Approach

### Phase 1: Foundation (Dev Day 1-2)

**Goal**: Get basic NL→JSON translation working with schema validation

**Tasks**:
1. **Dependencies & Configuration**
   - Add Anthropic SDK + Jackson to `build.gradle`
   - Create `application.yml` with Claude model configuration
   - Add `ANTHROPIC_API_KEY` to local `.env` / CI secrets

2. **Data Models**
   - Create `PrototypeRequest`, `PrototypeResponse` DTOs
   - Create custom exceptions (`TranslationException`, `ValidationException`)

3. **Core Translator Logic**
   - Implement `ClaudeTranslator.translate()`:
     - Build prompt (see Prompt Design below)
     - Call Anthropic SDK with structured output constraints
     - Parse and validate JSON response
     - Return `ScientificModel` or throw exception

4. **Schema Validator**
   - Implement `ClaudeTranslator.validateSchema()`:
     - Load `schemas/model.schema.json`
     - Use `json-schema-validator` library
     - Return validation errors or pass

5. **Tests (Unit)**
   - Test prompt generation (mocked Claude API)
   - Test schema validation with valid/invalid JSON
   - Test error handling

**Acceptance**: `translate()` method works with mocked API responses; validates schema correctly.

---

### Phase 2: Controller & Engine Integration (Dev Day 2-3)

**Goal**: Wire translator into REST endpoint and engine pipeline

**Tasks**:
1. **Controller**
   - Implement `PrototypeController.prototype()`:
     - Validate input format
     - Call `ClaudeTranslator.translate()`
     - Handle exceptions (return 400/503 with clear errors)

2. **Engine Client**
   - Implement `EngineClient.solve()`:
     - POST model JSON to `http://localhost:8001/api/solve`
     - Parse `PrototypeResponse` from engine
     - Return to controller

3. **Exception Handler**
   - Implement global `PrototypeExceptionHandler`:
     - Catch `TranslationException` → 400 with details
     - Catch `ValidationException` → 400 with schema errors
     - Catch `EngineException` → 502/503 with guidance

4. **Integration Tests**
   - Full E2E: NL query → Model JSON → Engine result → Client response
   - Test with known projectile motion queries

5. **Documentation**
   - Add comments to `ClaudeTranslator` explaining prompt design
   - Document configuration options in README

**Acceptance**: `POST /api/prototype` works end-to-end; returns deterministic results for projectile motion queries.

---

### Phase 3: Polish & Deployment (Dev Day 3-4)

**Goal**: Solidify, test edge cases, prepare for demo

**Tasks**:
1. **Error Handling Edge Cases**
   - Ambiguous queries (e.g., "tell me about physics")
   - Out-of-domain queries (e.g., chemistry)
   - Malformed NL (e.g., gibberish)
   - Engine timeout/unavailability

2. **Performance Optimization**
   - Measure end-to-end latency
   - Consider schema validation caching
   - Ensure Claude API call is efficient (compact prompt)

3. **Monitoring & Logging**
   - Log all translator requests (query, model used, validation result)
   - Log Claude API responses (for debugging)
   - Metrics: success rate, latency distribution

4. **Demo Readiness**
   - Test with 5-10 projectile motion queries
   - Verify determinism (same query → same result)
   - Show error handling (invalid query → helpful error)

5. **PR & Documentation**
   - Update CLAUDE.md with new patterns (translator layer, Claude SDK usage)
   - Document environment setup for Claude API key
   - Add troubleshooting guide (common Claude failures)

**Acceptance**: System is production-ready for limited demo; one-page runbook for ops.

---

## Prompt Design (Critical Component)

The Claude prompt is the "specification" the LLM uses to produce valid Model JSON. It must be:
- **Specific**: Domain constraints (physics.mechanics only)
- **Complete**: All required schema fields listed
- **Constrained**: Limits on values (SI units only, dimensionless for certain fields)
- **Examples**: Show desired JSON structure

### System Prompt (Constant)

```
You are a scientific model translator for the Clauneck platform.

Your role: Convert natural language physics problems into structured Model JSON.

CRITICAL CONSTRAINTS:
1. Output ONLY valid JSON matching the schema below. No preamble, no explanation.
2. Domain: ONLY physics.mechanics (projectile motion). Reject other domains.
3. All quantities must use SI units (m, kg, s, m/s, m/s^2, etc.).
4. Include drag_coeff only if user mentions drag, air resistance, or friction.
5. Default values:
   - g (gravity): 9.81 m/s^2
   - angle: 45 degrees (if not specified)
   - mass: 1.0 kg (if not specified)
   - drag_coeff: 0.0 (if not mentioned)

SCHEMA STRUCTURE (required fields):
{
  "id": "unique_identifier",
  "domain": "physics.mechanics",
  "description": "Human-readable description",
  "quantities": [
    {"name": "v0", "value": <number>, "siUnit": "m/s", "isKnown": true},
    {"name": "angle", "value": <degrees>, "siUnit": "deg", "isKnown": true},
    {"name": "mass", "value": <kg>, "siUnit": "kg", "isKnown": true},
    {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
    {"name": "drag_coeff", "value": <coefficient>, "siUnit": "dimensionless", "isKnown": true}
  ],
  "equations": [
    {
      "lhs": "d2x/dt2",
      "rhs": "-drag_coeff * vx * sqrt(vx^2 + vy^2) / mass",
      "type": "ode",
      "description": "Horizontal acceleration with drag"
    },
    {
      "lhs": "d2y/dt2",
      "rhs": "-g - drag_coeff * vy * sqrt(vx^2 + vy^2) / mass",
      "type": "ode",
      "description": "Vertical acceleration with gravity and drag"
    }
  ],
  "initialConditions": {
    "v0": <number>,
    "angle": <degrees>,
    "mass": <kg>,
    "g": 9.81,
    "drag_coeff": <coefficient>
  },
  "solver": {
    "method": "RK45",
    "tolerance": 1e-6,
    "maxSteps": 10000,
    "timeSpan": {"start": 0, "end": 5.0, "numPoints": 5000}
  },
  "metadata": {
    "source": "llm_translator",
    "originalQuery": "<user's exact query>"
  }
}

VALIDATION RULES:
- v0 > 0 (positive velocity)
- angle: 0–90 degrees (launching angle, not negative)
- mass > 0
- g > 0
- drag_coeff >= 0

If the query is ambiguous, nonsensical, or outside physics.mechanics, output this JSON error:
{
  "error": "true",
  "reason": "Explanation of why this query cannot be translated",
  "suggestion": "What the user should ask instead"
}
```

### User Prompt (Dynamic)

```
Translate this physics query into Model JSON:

"{USER_QUERY}"

Output ONLY the JSON. No explanation.
```

### Example Interaction

**User Query**: "Ball at 20 m/s, 45°, mass 0.5kg, drag coefficient 0.1"

**Claude Output** (valid):
```json
{
  "id": "projectile_001_20250916",
  "domain": "physics.mechanics",
  "description": "Ball launch at 20 m/s at 45 degrees with 0.5 kg mass and 0.1 drag coefficient",
  "quantities": [
    {"name": "v0", "value": 20.0, "siUnit": "m/s", "isKnown": true},
    {"name": "angle", "value": 45.0, "siUnit": "deg", "isKnown": true},
    {"name": "mass", "value": 0.5, "siUnit": "kg", "isKnown": true},
    {"name": "g", "value": 9.81, "siUnit": "m/s^2", "isKnown": true},
    {"name": "drag_coeff", "value": 0.1, "siUnit": "dimensionless", "isKnown": true}
  ],
  "equations": [...],
  "initialConditions": {...},
  "solver": {...},
  "metadata": {"source": "llm_translator", "originalQuery": "Ball at 20 m/s, 45°, mass 0.5kg, drag coefficient 0.1"}
}
```

---

## Testing Strategy

### Unit Tests (Phase 1)

**`TranslatorServiceTest`** (Mocked Claude API):
- `testTranslateValidQuery_ReturnsModel()` — Mock Claude, parse JSON, assert fields
- `testTranslateInvalidJSON_ThrowsValidationException()` — Claude returns malformed JSON
- `testTranslateNonPhysicsDomain_ReturnsErrorModel()` — Query about chemistry
- `testSchemaValidation_RejectsInvalidUnits()` — Missing siUnit field
- `testSchemaValidation_AcceptsValidModel()` — Full valid model

**`PromptGeneratorTest`**:
- `testPromptIncludesConstraints()` — System prompt has domain/unit constraints
- `testPromptIncludesSchema()` — User sees expected JSON structure

### Integration Tests (Phase 2)

**`PrototypeControllerTest`** (Real Spring context, mocked Claude API):
- `testPostPrototype_ValidQuery_Returns200()` — Full controller path
- `testPostPrototype_InvalidQuery_Returns400()` — Error handling
- `testPostPrototype_InvalidJSON_Returns400()` — Validation failure

**`EngineIntegrationTest`** (With engine running on :8001):
- `testFullStack_ProjectileMotion_Returns7_5m()` — End-to-end: NL → JSON → solver result
- `testFullStack_DifferentQueries_AllValid()` — Multiple projectile queries
- `testDeterminism_SameQuery_SameResult()` — Run twice, compare results

### Error Scenario Tests

**`ErrorHandlingTest`**:
- `testEngineTimeout_Returns503()` — Engine down
- `testClaudeAPITimeout_Returns503()` — Claude API down
- `testAmbiguousQuery_Returns400WithSuggestion()` — "Tell me about physics"
- `testOutOfDomainQuery_Returns400()` — Chemistry question

---

## Technical Decisions

### Decision 1: Claude Model Selection (Configurable, Default Haiku)

**Chosen**: Environment variable `CLAUDE_MODEL` with default `claude-haiku-4-5`

**Rationale**:
- **Haiku** (default): Fast (~0.5s/request), cheap, sufficient for structured projectile motion
- **Sonnet**: Better for complex/ambiguous queries, 2-3x slower
- **Opus**: Highest reasoning, overkill for this slice

**Trade-offs**:
- Haiku sometimes fails on ambiguous inputs → mitigated by strict prompts
- Alternative: Hard-code to Sonnet for reliability → higher latency/cost

**How to Change**: `CLAUDE_MODEL=claude-3-5-sonnet` at runtime

---

### Decision 2: Strict Schema Validation (No Auto-Repair)

**Chosen**: Reject invalid JSON with clear error message, no attempt to fix

**Rationale**:
- Determinism: Fixed input should always produce same model
- Safety: Invalid models should not reach solver (fail fast)
- Debugging: User can see exactly what went wrong

**Trade-offs**:
- User experience: Errors are strict, but also clear
- Alternative: Auto-repair common mistakes (missing fields, typos) → harder to test, less deterministic
- Alternative: Permissive acceptance → validation errors found later (bad UX)

---

### Decision 3: Engine Client Over Direct Integration

**Chosen**: Call engine via HTTP (`EngineClient`) over direct Python subprocess

**Rationale**:
- Clean separation: Web and engine are independent services
- Scalability: Engine can run on different machine
- Reliability: Engine can restart without restarting web
- Testability: Can mock or test engine separately

**Trade-offs**:
- Latency: HTTP adds ~10-50ms roundtrip
- Complexity: Extra service to manage
- Alternative: Direct subprocess call → tighter coupling, harder to scale

---

### Decision 4: REST over gRPC for Translator Endpoint

**Chosen**: REST (`POST /api/prototype`)

**Rationale**:
- Accessibility: Easy to call from any client (curl, JavaScript, etc.)
- Consistency: Matches engine's REST API
- Development speed: No need for .proto files

**Trade-offs**:
- Performance: HTTP slower than gRPC (not critical for <5s latency)
- Alternative: gRPC → better for high-throughput, overkill for this slice

---

### Decision 5: Schema Validation Library

**Chosen**: `com.networknt:json-schema-validator` (Java library)

**Rationale**:
- Standards-compliant: Supports JSON Schema Draft 7
- Active maintenance: Well-used in Java ecosystem
- No external service needed: Validation happens in-process

**Trade-offs**:
- Dependency: Adds one JAR to classpath
- Alternative: Manual validation → error-prone, code duplication

---

## Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| **Claude API returns invalid JSON** | Medium | High | Strict prompt + JSON schema validation + retry logic (2 attempts) |
| **Claude API unavailable** | Low | High | Return 503, log error, retry with backoff |
| **Slow latency (>5s)** | Low | Medium | Use Haiku by default, monitor latency, can upgrade to Sonnet if needed |
| **Ambiguous user queries confuse Claude** | Medium | Low | Return clear error message suggesting how to rephrase |
| **Out-of-domain queries (chemistry)** | Medium | Low | Explicit domain check in prompt, reject with suggestion |
| **Engine microservice down** | Low | High | Graceful HTTP error, guide user to start engine |
| **API key leaked in logs** | Low | Critical | Never log API key, mask in error messages |
| **Schema changes break translator** | Low | Medium | Keep prompt in sync with schema (testing + documentation) |

---

## Success Metrics

### Launch Criteria (Must-Have)
- ✓ `POST /api/prototype` accepts NL query
- ✓ Returns valid `PrototypeResponse` (Model + SolverResult)
- ✓ Determinism verified (same query → same result)
- ✓ Error handling is clear (400/503 with helpful message)
- ✓ Unit + integration tests pass

### Quality Metrics (Track Over Time)
- **Correctness**: % of NL queries that produce valid Model JSON (target: >95%)
- **Latency**: p50 <2s, p99 <5s (excluding network jitter)
- **Reliability**: Uptime when Claude API is available (target: >99%)
- **User Satisfaction**: Queries that don't need rephrasing (target: >90%)

### Demo Success Criteria
- End-to-end demo: "Ball at 20 m/s, 45°, mass 0.5 kg" → 7.52m range (matches known result)
- Error demo: "Tell me about chemistry" → clear "unsupported domain" message
- Determinism demo: Same query twice → byte-identical results

---

## Rollback Plan

If translator implementation is incomplete or blocked:

1. **Day 3 Checkpoint**: Evaluate whether controller + engine integration is working
2. **If Blocked**: Fall back to manual model JSON submission (users POST JSON directly to `/api/solve`)
3. **Partial Deploy**: Release translator for projectile motion only, mark other domains as unsupported
4. **Communication**: Notify team of delay, document known limitations

**Do NOT**:
- Ship incomplete translator (partial NL support)
- Ship without schema validation (risk of invalid models)
- Ship without error handling (unhelpful errors)

---

## Dependencies & Build

### New Dependencies (to add to `web/build.gradle`)

```gradle
// Anthropic SDK for Claude API
implementation 'com.anthropic:sdk:0.1.0'

// JSON Schema validation
implementation 'com.networknt:json-schema-validator:1.0.88'

// Existing (should already be present)
implementation 'org.springframework.boot:spring-boot-starter-web:3.2.2'
implementation 'org.springframework.boot:spring-boot-starter-webflux'
implementation project(':core')
```

### Environment Setup

**Local Development**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..." # Your Anthropic API key
export CLAUDE_MODEL="claude-haiku-4-5"  # Optional, defaults to Haiku
export CLAUNECK_ENGINE_URL="http://localhost:8001"  # Engine service

# Start engine on port 8001
cd engine && python -m uvicorn app.main:app --port 8001

# In another terminal, start web on port 8080
gradle :web:bootRun
```

**CI/CD**:
- Add `ANTHROPIC_API_KEY` secret to GitHub Actions
- Update `.github/workflows/ci.yml` to set env vars before `gradle build`

---

## Communication & Handoff

### Stakeholder Updates
- **Product Owner**: Weekly status (intent → design → build → launch)
- **Team**: Daily standup on blockers
- **Demo Audience**: End of week, show NL→Results demo

### Documentation (Before Merge)
- **README**: How to set up Claude API key, run web service
- **CLAUDE.md**: New translator patterns, extend with future domains
- **Code Comments**: Explain prompt design, validation constraints
- **GitHub Wiki**: Troubleshooting guide for common Claude failures

---

## Future Extensions (Out of Scope)

Once this slice ships, consider:
1. **Additional Domains**: Chemistry.kinetics (reaction rates), Thermodynamics
2. **Advanced Error Recovery**: Fuzzy matching, auto-repair of LLM output
3. **User Feedback Loop**: Log rejected queries, improve prompt over time
4. **Caching**: Memoize common queries (deterministic, safe)
5. **Async API**: Long-running solver jobs (for complex multi-domain models)
6. **Frontend**: Web UI for natural language input + results visualization

---

## Appendix: API Contracts

### Request/Response Examples

**Request**:
```json
POST /api/prototype
{
  "query": "Ball at 20 m/s, 45°, mass 0.5kg, drag coefficient 0.1"
}
```

**Response (200 OK)**:
```json
{
  "model": {
    "id": "projectile_001",
    "domain": "physics.mechanics",
    "quantities": [...],
    "equations": [...],
    "solver": {"method": "RK45", "tolerance": 1e-8, ...},
    "metadata": {"source": "llm_translator", "originalQuery": "..."}
  },
  "result": {
    "success": true,
    "message": "Projectile motion solved successfully",
    "summary": {
      "max_range": 7.515369,
      "max_height": 3.205008,
      "flight_time": 1.588318
    },
    "trajectory": {
      "t": [...],
      "x": [...],
      "y": [...],
      "vx": [...],
      "vy": [...]
    }
  },
  "message": "OK"
}
```

**Response (400 Bad Request — Invalid Query)**:
```json
{
  "error": "TRANSLATION_FAILED",
  "message": "Could not translate query: ambiguous input",
  "details": "Query mentions 'chemistry' but only physics.mechanics is supported",
  "suggestion": "Try: 'Ball at 10 m/s, 30° angle, 1 kg mass'",
  "timestamp": "2026-09-16T13:00:00Z"
}
```

**Response (503 Service Unavailable — Claude API Down)**:
```json
{
  "error": "SERVICE_UNAVAILABLE",
  "message": "Claude API is temporarily unavailable",
  "details": "Connection timeout after 30 seconds",
  "suggestion": "Please retry in a few moments",
  "timestamp": "2026-09-16T13:00:00Z"
}
```

---

**Next Step**: Move to `/sdlc-build` phase to implement this specification.

**Sign-Off**: Awaiting technical review and team approval before Build phase begins.
