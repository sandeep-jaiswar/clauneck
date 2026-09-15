---
name: sdlc-build
description: Build phase using Claude Code plan mode. Generates code and tests from spec.md, maintains CLAUDE.md with patterns, commits artifacts, and supports parallel implementation with subagents.
---

# Stage 3: Build - Implementation with Plan Mode

This skill guides the Build phase where Claude generates code and tests according to the spec.md specification. Plan mode is the default entry point for maximum automation and interactive refinement.

## What This Stage Does

**Generates production-ready code and tests** while:
- Following architectural patterns from spec.md
- Maintaining and updating CLAUDE.md with new patterns
- Creating reusable skills for repeated patterns
- Supporting parallel implementation with subagents
- Keeping comprehensive commit history (audit trail)

## How to Execute

### 1. Start with Plan Mode (Default Entry Point)

```bash
# In Claude Code, open the repo and reference the approved spec.md
# /plan "Implement feature from spec.md"
```

Plan mode enables:
- Interactive refinement of generated code
- Immediate testing and feedback
- Quick pivots if needed
- Comprehensive decision tracking

### 2. Core Build Workflow

1. **Reference the spec.md**
   - Understand requirements and architecture
   - Identify which modules to change (core, web, api)
   - Note implementation phases

2. **Generate code per spec**
   - Create classes, interfaces, endpoints
   - Follow conventions in CLAUDE.md
   - Implement per the architectural design

3. **Generate tests alongside code**
   - Unit tests for business logic
   - Integration tests for module interactions
   - E2E tests for user workflows

4. **Update CLAUDE.md**
   - Document new patterns discovered
   - Add build/test/lint commands if new
   - Record conventions for this feature
   - Keep under 1 page (remove stale info)

5. **Create skills for repeated patterns** (if applicable)
   - Write skill in `.claude/skills/<name>/SKILL.md`
   - Use when pattern must be applied consistently
   - Helps future implementations follow same pattern

6. **Commit code in logical chunks**
   ```bash
   git commit -m "feat: [feature-name] - brief description
   
   - What was implemented
   - Why this approach
   - How it fits spec.md requirements"
   ```

7. **Run tests and build**
   ```bash
   gradle build          # All modules
   gradle :core:test     # Specific module
   ```

8. **Create PR for review**
   - Reference spec.md and approved intent.md
   - Include test results
   - Highlight any deviations from spec
   - Use code-review skill for quality checks

### 3. Parallel Implementation (Subagents)

For larger features, parallelize work:

```
# Main agent handles core module changes
/plan "Implement core models and services from spec"

# Subagent handles web module changes
@agent "Implement web endpoints and controllers from spec"

# Another subagent handles API changes
@agent "Implement API interfaces and adapters from spec"

# Main agent integrates and runs full test suite
/plan "Integrate subagent work and verify all tests pass"
```

Subagents:
- Work independently on different modules
- Read spec.md for coordination
- Commit to same repo (mainbranch)
- Main agent integrates results

## Build Phase Principles

### 1. Tests and Code Together
- Don't write code then tests
- Interleave test and code generation
- Tests guide the design

### 2. Update CLAUDE.md Continuously
- Add new patterns as discovered
- Document conventions before next developer sees them
- Remove outdated info
- Keep it under 1 page for agent context

### 3. Create Skills for Reusable Patterns
Use skills when:
- A pattern must be applied consistently
- Multiple features will use the same approach
- Organization has a policy to enforce

Example: If all REST endpoints need the same security checks:
```
.claude/skills/secure-api/SKILL.md
```

### 4. Commit Strategically
- Logical units (one feature per commit ideally)
- Meaningful commit messages with "why"
- Reference spec.md and intent.md
- Keep diff reviewable (not 5000-line commits)

### 5. Follow Existing Conventions
- Check CLAUDE.md before starting
- Use existing patterns from codebase
- Don't create new patterns without documenting
- Prefer consistency over personal preference

## Gradle Build Details for clauneck

**Project Structure**:
- `core/` - Base library (Guava dependency)
- `web/` - Spring Boot REST APIs (depends on core)
- `api/` - API module (depends on core)

**Build Commands**:
```bash
gradle build              # Build all modules + tests
gradle build -x test      # Build without tests
gradle :core:test         # Test specific module
gradle :web:build         # Build specific module
gradle clean              # Clean artifacts
```

**Dependencies**:
- Java 21
- Spring Boot 3.2.2 (web module)
- Guava 31.1-jre (core module)
- Add test frameworks as needed (JUnit, Mockito)

## CLAUDE.md Update Template

When updating CLAUDE.md during Build, include:

```markdown
## [Feature Name] Implementation

### New Build Commands
- gradle :[module]:build   # Build this module

### Conventions
- [Convention 1]: [Description]
- [Convention 2]: [Description]

### New Dependencies Added
- [Dependency]: [Version] - [Reason]

### Architecture Pattern
- [Pattern Name]: [When to use]

### Things Claude Gets Wrong (for this feature)
- ❌ Don't do this
- ✅ Do this instead
```

## Commit Message Format

```
<type>: <feature-name> - <short description>

<detailed explanation of what was implemented>

Relates to spec.md: <feature-name>
Relates to intent.md: <feature-name>

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `test`, `docs`, `style`, `chore`

## Governance

- **Artifact**: Committed code, tests, and updated CLAUDE.md
- **Audit Trail**: Git history shows all decisions
- **Quality Gate**: Tests pass before merge
- **Code Review**: Use /code-review skill before PR

## Success Metrics

**Leading Indicator**: Build time per feature
- How long from approved spec.md to PR ready?
- Should decrease as patterns are reused

**Lagging Indicator**: Test coverage and defect rate
- Code coverage from test suite
- Defects found in production vs. testing phase

## Common Issues & Solutions

| Issue | Root Cause | Solution |
|-------|-----------|----------|
| Code doesn't match spec | Spec not clear | Revise plan mode questions about spec |
| Tests are fragile | Testing strategy issues | Reference spec.md testing section |
| Can't build after commit | Missing CLAUDE.md updates | Update CLAUDE.md with new commands |
| Repeated mistakes in code | New pattern not documented | Add pattern to CLAUDE.md |

## Next Steps

After Build phase:
1. Run `/sdlc-test` for continuous evaluation
2. Address test failures
3. Get code review via /code-review
4. Merge to main
5. Transition to Maintain phase

---

**Prerequisites**: Approved and committed spec.md

**Infrastructure Needed**:
- Claude Code with plan mode
- Gradle 4.4.1
- Java 21
- Approved spec.md and intent.md
- Updated CLAUDE.md

**Key Principle**: Build phase is where AI acceleration happens:
- Plan mode for interactive development
- Parallel subagents for modularity
- Continuous CLAUDE.md updates to capture patterns
- Comprehensive commit history as audit trail
- Tests guide implementation alongside code
