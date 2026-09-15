---
name: sdlc-test
description: Continuous evaluation throughout implementation. Runs tests, generates coverage reports, and provides feedback to Build and Design phases.
---

# Stage 4: Test - Continuous Evaluation

This skill implements continuous testing throughout the Build phase, rather than treating testing as a gate at the end. Tests inform design decisions and catch issues early.

## What This Stage Does

**Implements continuous evaluation** that:
- Runs tests automatically after code changes
- Provides feedback to guide refinement
- Measures coverage and quality metrics
- Routes issues back to Build or Design as needed
- Integrates with CI/CD pipeline for automated checks

## How to Execute

### 1. Run Tests During Build

During implementation, test continuously:

```bash
# Run all tests across all modules
gradle test

# Run tests for specific module
gradle :core:test
gradle :web:test
gradle :api:test

# Run with coverage reporting (if configured)
gradle test --info

# Run before committing
gradle clean build   # Full clean build + tests
```

### 2. Test Strategy by Type

#### Unit Tests
- Test individual components in isolation
- Located in `src/test/java` next to source code
- Focus on business logic, edge cases, error handling
- Should run in seconds

```bash
gradle :core:test   # Unit tests for core module
```

#### Integration Tests
- Test interactions between modules
- Verify core → web and core → api dependencies
- May need test containers or embedded services
- Run in CI pipeline

```bash
gradle test         # Runs all tests including integration
```

#### End-to-End Tests
- Test complete workflows from user perspective
- Usually run against deployed service
- Slower but essential for critical paths
- Configured in web module for REST APIs

### 3. Continuous Evaluation Workflow

1. **Write test alongside code**
   - Test first or code + test together
   - Don't finish feature without tests
   - Coverage should be >80%

2. **Run tests after each commit**
   ```bash
   # Before committing
   gradle build    # Builds + runs all tests
   ```

3. **Fix failures immediately**
   - Don't accumulate broken tests
   - Failing tests block merge to main
   - Use plan mode to debug test failures

4. **Review coverage metrics**
   - Track coverage trend
   - Identify untested code paths
   - Add tests for critical paths

5. **Generate coverage report**
   ```bash
   gradle test --info
   # Look for coverage percentages in output
   ```

### 4. CI/CD Integration

Tests run automatically on:
- Push to `production` branch
- Pull requests to `production`
- Command: `gradle build --no-daemon`

CI pipeline (`.github/workflows/ci.yml`):
```yaml
- name: Build and Test
  run: gradle build --no-daemon
```

If CI fails:
1. Fix test failures in local branch
2. Commit fix
3. Push again
4. CI re-runs automatically

## Test Framework Setup

**Current Status**: Project is freshly scaffolded
- Add JUnit 5 for unit tests
- Add Mockito for mocking
- Add Testcontainers for integration tests (if needed)

### Add Test Dependencies

For **core** module (`core/build.gradle`):
```gradle
testImplementation 'org.junit.jupiter:junit-jupiter:5.9.0'
testImplementation 'org.mockito:mockito-core:5.0.0'
testImplementation 'org.mockito:mockito-junit-jupiter:5.0.0'
```

For **web** module (`web/build.gradle`):
```gradle
testImplementation 'org.springframework.boot:spring-boot-starter-test'
testImplementation 'org.junit.jupiter:junit-jupiter:5.9.0'
```

## Test Writing Guidelines

### Unit Test Example (core module)

```java
class MyServiceTest {
    @Test
    void testHappyPath() {
        MyService service = new MyService();
        Result result = service.doSomething("input");
        
        assertThat(result).isNotNull();
        assertThat(result.getValue()).isEqualTo("expected");
    }
    
    @Test
    void testEdgeCase() {
        MyService service = new MyService();
        assertThrows(IllegalArgumentException.class, 
            () -> service.doSomething(null));
    }
}
```

### Integration Test Example (web module)

```java
@SpringBootTest
class MyControllerTest {
    @Autowired
    TestRestTemplate restTemplate;
    
    @Test
    void testEndpoint() {
        ResponseEntity<String> response = 
            restTemplate.getForEntity("/api/endpoint", String.class);
        
        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.OK);
    }
}
```

## Governance

- **Artifact**: Test code, coverage reports, CI pipeline logs
- **Quality Gate**: All tests must pass before merge
- **Feedback Loop**: Test failures inform Build/Design refinement
- **Audit Trail**: Test history in git shows quality evolution

## Success Metrics

**Leading Indicators**:
- Test execution time (should be <5 min for all tests)
- Code coverage % (aim for >80%)
- Tests added per commit

**Lagging Indicators**:
- Defects found in testing vs. production
- Rework needed due to test failures
- Time to fix test failures

## Continuous Feedback Loop

Test results inform the workflow:

```
Code Implementation
    ↓
/sdlc-test runs tests
    ↓
Tests Pass? 
    ├─ YES → Continue to next feature or PR review
    └─ NO → Failures inform Build phase refinement
                ↓
            Fix code or tests
                ↓
            Re-run tests (loop)
                ↓
            If design issue → inform Design phase
                ↓
            Update spec.md if needed
```

## Common Test Issues & Solutions

| Issue | Solution |
|-------|----------|
| Tests timeout | Check for infinite loops, external service calls |
| Flaky tests | Reduce external dependencies, use mocks |
| Low coverage | Identify untested paths, add targeted tests |
| Test runs slow | Move to integration test tier, parallelize unit tests |
| Mocking issues | Check Mockito setup, verify spy/mock distinction |

## Integration with Build Phase

During `/sdlc-build`:
1. Generate tests alongside code
2. Run `gradle build` frequently (every commit)
3. Keep build passing
4. Fix test failures immediately
5. Don't move forward with broken tests

## Next Steps

After successful testing:
1. Merge to main branch (if tests pass in CI)
2. Monitor in Maintain phase via metrics
3. If issues found → create new intent.md
4. Loop back to Plan phase

---

**Prerequisites**: Code generated in Build phase with tests

**Infrastructure Needed**:
- Gradle test runner
- Test frameworks (JUnit, Mockito, etc.)
- CI/CD pipeline (.github/workflows/ci.yml)
- Coverage reporting tools

**Key Principle**: Testing is continuous, not gated:
- Test early and often
- Tests inform design decisions
- Failures halt progress (intentionally)
- Coverage metrics guide implementation
- CI ensures quality at merge time
