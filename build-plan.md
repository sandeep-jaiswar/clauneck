# Build Plan: Translator Layer (NL → Model JSON)

**Status**: Approved, ready for implementation
**Implements**: `spec.md` (translator layer)
**Author**: Claude (plan mode) + sandeep-jaiswar

---

## Context

`spec.md` (approved, committed) designs the translator layer: a Spring Boot endpoint `POST /api/prototype` that takes a natural-language physics query, calls Claude to produce schema-shaped Model JSON, validates it, forwards it to the already-working Python engine (`/api/solve` on :8001), and returns the combined Model + SolverResult. This closes the loop on the vertical slice — currently users must hand-write JSON (as was done manually for the "ball at 20 m/s" demo earlier this session).

During plan-mode research, three facts emerged that `spec.md` didn't anticipate and that materially change the implementation:

1. **`com.anthropic:sdk:0.1.0` is not a verified Maven artifact.** No lockfile/version-catalog anywhere confirms it exists. **Resolved (user-approved):** call the Anthropic Messages API directly via HTTP (`RestTemplate`, `POST https://api.anthropic.com/v1/messages`) instead of a third-party SDK.
2. **System Gradle is genuinely 4.4.1** (verified via the actual `gradle-launcher-4.4.1.jar`, not a fake banner) — released 2017, incompatible with the Spring Boot Gradle plugin (needs Gradle 7.5+), which `web/build.gradle` currently lacks entirely (only `id 'java'`). **Resolved (user-approved):** add a Gradle Wrapper pinned to Gradle 8.10, scoped to this repo only. Network access to `services.gradle.org` is confirmed working (tested, got a valid 307 redirect to GitHub releases).
3. **`web/` is a completely empty scaffold** — no `src/`, no Spring Boot main class, no config. Everything below is new.

Additionally, a smaller but real discrepancy: `schemas/model.schema.json` declares `initialConditions` as a nested `{time, values: {...}}` object, but `engine/app/model.py` (the actual, already-tested, live `/api/solve` consumer) declares it as a **flat** `Dict[str, float]` — confirmed working in the earlier manual engine test this session. Per `spec.md`'s own constraint ("engine: No changes"), the translator's DTOs must match the engine's real accepted shape (flat map), not the stricter literal schema.json nesting. Document this pre-existing drift in a code comment rather than silently ignoring it or touching `schemas/`/`engine/`.

`core` module's `Model`/`Quantity`/`Equation`/`SolverConfig` classes exist and are reusable, but have enum-casing mismatches against the schema/engine contract (`Equation.Type.ODE` vs `"ode"`, etc.) and the `initialConditions` shape mismatch above. Rather than force-fitting into `core.model.*` (which `spec.md` says gets "no changes" anyway), the translator uses its own DTOs in `web`, matching `engine/app/model.py` field-for-field, and validates structurally via `com.networknt:json-schema-validator` against `schemas/model.schema.json` for everything the schema and engine agree on.

## Scope for this build session

Implements `spec.md` Phase 1 (Foundation) + Phase 2 (Integration) in full: a working, tested, end-to-end `POST /api/prototype`. From Phase 3 (Polish), includes error-edge-case handling, logging, and the CLAUDE.md update (cheap and load-bearing for correctness); defers advanced metrics/monitoring instrumentation as noted follow-up work, since it's not required to demonstrate or ship the feature.

## Key technical decisions (already made, do not re-litigate)

- **Claude API client**: direct HTTP via `RestTemplate`, not an SDK.
- **Gradle**: use a wrapper pinned to Gradle 8.10 (`./gradlew`), not the system `gradle` (4.4.1). Generate via `gradle wrapper --gradle-version 8.10` using the existing old system `gradle` (the built-in `wrapper` task works fine on old Gradle).
- **Engine HTTP client**: also `RestTemplate` (same bean, reused for both Claude and engine calls) — no WebClient/webflux dependency needed.
- **DTOs**: web-module-local classes mirroring `engine/app/model.py` exactly (flat `initialConditions`), not `core.model.*`.
- **Validation**: `com.networknt:json-schema-validator` against `schemas/model.schema.json` (classpath-referenced from the shared `schemas/` dir via a `sourceSets` tweak — no file duplication), with the known `initialConditions` shape drift documented and worked around.
- **Domain scope**: `physics.mechanics` only. Non-matching domain → `UnsupportedDomainException` → HTTP 501 (per spec FR5). Claude's own explicit decline (`{"error": true, ...}`) → `TranslationException` → HTTP 400. Malformed/unparseable Claude output → retry up to `max-retries`, then 400. Schema-invalid model → `ModelValidationException` → 400. Engine unreachable/timeout → `EngineException` → 502.
- **Testing**: JUnit 5 + Mockito via `spring-boot-starter-test` (test-scope only; `core` module's existing JUnit 4 tests are untouched/out of scope). All translator/engine-client unit and integration tests mock `RestTemplate` — no real network calls in the test suite.

## Files to create/modify

### Build infrastructure
- `gradle/wrapper/gradle-wrapper.properties`, `gradlew`, `gradlew.bat`, `gradle/wrapper/gradle-wrapper.jar` — generated via `gradle wrapper --gradle-version 8.10`.
- `web/build.gradle` (rewrite): add `id 'org.springframework.boot' version '3.2.2'` + `id 'io.spring.dependency-management' version '1.1.4'`, `java { sourceCompatibility = JavaVersion.VERSION_21 }`, dependencies on `spring-boot-starter-web`, `com.networknt:json-schema-validator:1.0.88`, `spring-boot-starter-test` (test scope), `tasks.named('test') { useJUnitPlatform() }`, and a `sourceSets` addition so `../schemas/model.schema.json` is on the classpath.
- `.env.example` (repo root): documents `ANTHROPIC_API_KEY`, `CLAUDE_MODEL` (default `claude-haiku-4-5`), `CLAUNECK_ENGINE_URL` (default `http://localhost:8001`).

### Application source (`web/src/main/java/com/clauneck/web/`)
- `ClauneckWebApplication.java` — `@SpringBootApplication` main class.
- `config/TranslatorProperties.java`, `config/EngineProperties.java` — `@ConfigurationProperties` bound to `application.yml`.
- `config/RestTemplateConfig.java` — one `RestTemplate` bean with explicit connect/read timeouts.
- `dto/` — `Quantity`, `DimensionVector`, `EquationDto`, `TimeSpanDto`, `SolverConfigDto`, `MetadataDto`, `ScientificModelDto` (mirrors `engine/app/model.py`, flat `initialConditions`), `SolverResultDto`, `PrototypeRequest`, `PrototypeResponse`, `ErrorResponse`.
- `exception/` — `TranslationException` (→400), `UnsupportedDomainException` (→501), `ModelValidationException` (→400), `EngineException` (→502), plus `PrototypeExceptionHandler` (`@RestControllerAdvice`) mapping each to the `ErrorResponse` shape from `spec.md`'s API contract appendix.
- `service/SchemaValidator.java` — loads `schemas/model.schema.json` from the classpath, validates a Jackson `JsonNode`, documents/works around the `initialConditions` drift.
- `service/ClaudeTranslator.java` — builds the system+user prompt (from `spec.md`'s "Prompt Design" section: physics.mechanics only, SI units, required fields, default values), POSTs to the Anthropic Messages API via `RestTemplate` with `x-api-key`/`anthropic-version` headers, parses the response, retries up to `max-retries` on transient I/O failure or unparseable JSON, detects Claude's `{"error": true, ...}` decline → `TranslationException`, detects `domain != "physics.mechanics"` → `UnsupportedDomainException`, runs `SchemaValidator`, sets `metadata.source="llm_translator"` and `metadata.originalQuery` server-side (per ADR 0002's audit-trail requirement).
- `client/EngineClient.java` — POSTs the validated `ScientificModelDto` to `${clauneck.engine.url}/api/solve` via the same `RestTemplate`, maps connection/timeout failures to `EngineException`.
- `api/PrototypeController.java` — `POST /api/prototype`, orchestrates translator → engine client → `PrototypeResponse`.
- `resources/application.yml` — `server.port: 8080`, `clauneck.translator.*` / `clauneck.engine.*` keys (env-var driven with defaults), basic logging config.

### Tests (`web/src/test/java/com/clauneck/web/`)
- `service/ClaudeTranslatorTest.java` — Mockito-mocked `RestTemplate`; covers valid translation, Claude decline JSON, malformed JSON + retry exhaustion, unsupported domain, schema-invalid model.
- `service/SchemaValidatorTest.java` — valid model passes; missing required field / bad enum value fails.
- `client/EngineClientTest.java` — mocked `RestTemplate`; success path and connection-failure → `EngineException`.
- `api/PrototypeControllerTest.java` — `@WebMvcTest` + `@MockBean` translator/engine client; asserts status codes (200/400/501/502) and response shape for each scenario from `spec.md`'s API contract appendix.

### Documentation
- `CLAUDE.md` update: add `./gradlew :web:bootRun` / `./gradlew :web:test` commands, note the Gradle-wrapper-vs-system-Gradle distinction, document `ANTHROPIC_API_KEY`/`CLAUDE_MODEL` env vars, correct the stale "Gradle 4.4.1" line, note the known `initialConditions` schema/engine drift as follow-up.

## Execution order

1. Generate Gradle wrapper (`gradle wrapper --gradle-version 8.10`) using the existing system `gradle`; verify `./gradlew -v` reports 8.10.
2. Rewrite `web/build.gradle`; run `./gradlew :web:build` (no source yet) to confirm the Spring Boot plugin + dependency-management resolve correctly over network. **Checkpoint**: if this fails, stop and report rather than proceeding blind.
3. Scaffold main application class + config + `application.yml`.
4. DTOs → exceptions → `SchemaValidator` (+test) → `ClaudeTranslator` (+test) → `EngineClient` (+test) → `PrototypeController` (+test), committing in logical chunks (roughly one commit per component group), per commit message format in `.claude/skills/sdlc-build/SKILL.md`.
5. Run full `./gradlew :web:test`.
6. Live smoke test: start the Python engine (`cd engine && python -m uvicorn app.main:app --port 8001`, or reuse the venv at `/tmp/clauneck_venv` created earlier this session if present), start `./gradlew :web:bootRun`, and if `ANTHROPIC_API_KEY` is available in the environment, run the actual "Ball at 20 m/s, 45°, mass 0.5kg, drag coefficient 0.1" query through `POST /api/prototype` end-to-end and compare against the known-good result (range ≈ 7.515369 m, height ≈ 3.205008 m, flight time ≈ 1.588318 s) established earlier this session. If no API key is available, report that live verification was skipped and why — do not fabricate a result.
7. Update `CLAUDE.md`, final commit.

## Verification

- `./gradlew :web:test` — all unit/integration tests green (no real network calls; Claude and engine calls are mocked).
- `./gradlew build` — full multi-module build still succeeds (core unaffected).
- Live curl smoke test against `POST /api/prototype` (engine + web both running locally), comparing to the deterministic baseline already established this session.

## Explicitly out of scope (do not implement)

- Any domain other than `physics.mechanics`.
- Auto-repair of invalid LLM output.
- Authentication, rate limiting, caching.
- Frontend UI.
- Fixing the `schemas/model.schema.json` vs `engine/app/model.py` `initialConditions` drift (note it, don't fix it — fixing it means touching `engine/` or `schemas/`, both explicitly "no changes" per spec.md).
- Advanced metrics/observability tooling (structured logging is enough for this slice).
