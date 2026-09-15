# AI-Native SDLC for clauneck

This directory contains reusable skills and utilities implementing the **AI-Native SDLC workflow** for the clauneck project. The workflow automates handoffs between development stages while maintaining human oversight at critical gates.

## Quick Start

### New Feature Workflow

1. **Capture Intent** (`/sdlc-plan`)
   ```bash
   # Describe your feature or problem
   # Claude will create intent.md
   # Commit when ready: git add intent.md && git commit
   ```

2. **Design** (`/sdlc-design`)
   ```bash
   # Use plan mode for interactive design
   # /plan "Design the feature from intent.md"
   # Commit spec.md when complete
   ```

3. **Build** (`/sdlc-build`)
   ```bash
   # Use plan mode to generate code
   # /plan "Implement feature from spec.md"
   # Commit code and update CLAUDE.md
   ```

4. **Test** (`/sdlc-test`)
   ```bash
   # Run tests continuously
   gradle build
   # Tests must pass before merge
   ```

5. **Maintain** (`/sdlc-maintain`)
   ```bash
   # Monitor production
   # Create new intent.md if issues found
   # Loop back to Plan phase
   ```

## Available Skills

### sdlc-orchestrator
**Meta skill** - Overview of the entire workflow and available commands.
- Use when: Starting a new phase or need workflow reference
- Produces: Guidance for which skill to use next

### sdlc-plan
**Stage 1: Plan** - Capture project intent and requirements
- Input: Problem description or feature idea
- Output: `intent.md` (versioned, committed)
- Time: ~2-4 hours from idea to committed intent.md
- Next: Design phase

**Key Questions Claude Asks**:
- Who is affected by this?
- What does success look like?
- Are there constraints?
- What's out of scope?

### sdlc-design
**Stage 2: Design** - Create detailed specifications
- Input: Approved `intent.md`
- Output: `spec.md` with architecture and implementation approach
- Time: ~1-2 days for design iteration
- Tool: Use Claude Code **plan mode** for interactive session
- Next: Build phase

**Design Includes**:
- Requirements (functional and non-functional)
- Architecture decisions
- Module-by-module changes
- Implementation phases
- Testing strategy
- Risk identification

### sdlc-build
**Stage 3: Build** - Generate code and tests using plan mode
- Input: Approved `spec.md`
- Output: Code, tests, updated `CLAUDE.md`, optional skills
- Time: Varies by feature complexity
- Tool: **Claude Code plan mode** as default starting point
- Supports: Parallel implementation via subagents
- Next: Test phase

**Build Activities**:
- Generate code per spec.md
- Write tests alongside code
- Update CLAUDE.md with new patterns
- Create reusable skills if applicable
- Commit in logical chunks

### sdlc-test
**Stage 4: Test** - Continuous evaluation throughout implementation
- Input: Code from Build phase
- Output: Test results, coverage metrics, feedback
- Timing: Run continuously during Build
- Integration: Automatic in CI/CD pipeline
- Next: Maintain phase (or refinement in Build)

**Testing Levels**:
- Unit tests: Individual components
- Integration tests: Module interactions
- End-to-end tests: Complete workflows

### sdlc-maintain
**Stage 6: Maintain** - Monitor production and close the loop
- Input: Deployed feature, production metrics
- Output: Incident records, updated `intent.md`, lessons in `CLAUDE.md`
- Timing: Continuous monitoring
- Next: Plan phase (if issues found)

**Maintain Activities**:
- Monitor metrics and health
- Capture and classify incidents
- Root cause analysis
- Create new intent.md for problems
- Update CLAUDE.md with lessons

## Project Artifacts

### Versioned Artifacts (Committed to Git)

- **intent.md** - Problem statement, goals, constraints
- **spec.md** - Detailed design, architecture, implementation approach
- **Code + Tests** - Generated implementation
- **CLAUDE.md** - Updated with new patterns and conventions
- **Skills** - Reusable patterns in `.claude/skills/<name>/`
- **PR/Commit History** - Audit trail of decisions

### Transient Artifacts (Plan Mode Sessions)

- Design decisions and rationale (captured in spec.md)
- Implementation iterations (visible in git commits)
- Test outputs (in CI logs)

## DRY and SOLID Principles Implementation

### DRY (Don't Repeat Yourself)

- **Templates**: `intent.md.template`, `spec.md.template` provide consistent structure
- **Skills**: Reusable patterns captured in `.claude/skills/` directory
- **CLAUDE.md**: Single source of truth for conventions and commands
- **Shared Documentation**: This README, skill documentation

### SOLID Principles

1. **Single Responsibility**
   - Each skill has one clear purpose
   - sdlc-plan: Capture intent only
   - sdlc-design: Design only
   - sdlc-build: Implementation only
   - sdlc-test: Testing only
   - sdlc-maintain: Monitoring only

2. **Open/Closed**
   - Skills are open for extension (can add new skills)
   - But closed for modification (update via PRs)
   - CLAUDE.md is closed to prevent drift

3. **Liskov Substitution**
   - Each skill can be used independently
   - Skills compose together in predictable ways
   - Swappable based on team needs

4. **Interface Segregation**
   - Simple CLI interface: `/sdlc-<stage>`
   - Each skill has focused input/output
   - No unnecessary complexity per skill

5. **Dependency Inversion**
   - Skills depend on artifacts (intent.md, spec.md)
   - Not on specific implementation details
   - Loosely coupled workflow

## Directory Structure

```
.claude/
├── SDLC-README.md                 # This file
├── skills/
│   ├── SKILL.md                   # Main orchestrator skill
│   ├── sdlc-plan/SKILL.md          # Plan stage skill
│   ├── sdlc-design/SKILL.md        # Design stage skill
│   ├── sdlc-build/SKILL.md         # Build stage skill
│   ├── sdlc-test/SKILL.md          # Test stage skill
│   └── sdlc-maintain/SKILL.md      # Maintain stage skill
└── helpers/
    └── (Future utility scripts)

Project Root:
├── CLAUDE.md                      # Project conventions (UPDATED)
├── intent.md.template             # Plan stage template
├── spec.md.template               # Design stage template
└── intent/                        # Directory for intent.md files
```

## Workflow Example: Adding User Authentication

### Stage 1: Plan (2 hours)
```bash
# User describes the need
# Claude generates intent.md

git add intent.md
git commit -m "plan: add-user-authentication

Captures need to add user authentication to web module"
```

### Stage 2: Design (1 day)
```bash
# /plan "Design user authentication from intent.md"
# Interactive design session creates spec.md

git add spec.md
git commit -m "design: add-user-authentication

Architecture: JWT-based auth with Spring Security"
```

### Stage 3: Build (2-3 days)
```bash
# /plan "Implement user auth from spec.md"
# Parallel work possible:
# - Main: Spring Security config
# - Subagent 1: User controller
# - Subagent 2: JWT token service
# - Main: Integration and testing

git add src/ CLAUDE.md .claude/skills/
git commit -m "feat: add-user-authentication

- Implemented JWT-based authentication
- Spring Security configuration
- User registration and login endpoints
- Comprehensive test coverage"
```

### Stage 4: Test
```bash
# Run during Build phase
gradle build          # All tests pass
# Tests inform implementation decisions
```

### Stage 5: Maintain
```bash
# Monitor auth endpoints
# If issues found: create new intent.md
# Loop back to Plan phase
```

## Key Concepts

### Artifact-Driven Workflow

Each stage **ends** by committing an artifact to git, and the next stage **begins** by reading it:

```
Plan ends:     commit intent.md
Design begins: read intent.md
Design ends:   commit spec.md
Build begins:  read spec.md
Build ends:    commit code + updated CLAUDE.md
Test begins:   run tests on code
Maintain:      monitor code in production
              create new intent.md if issues
```

### Plan Mode as Default

Claude Code **plan mode** is the recommended entry point for:
- Interactive design sessions (sdlc-design)
- Implementation work (sdlc-build)
- Complex debugging (sdlc-test failures)

Plan mode enables:
- Iterative refinement
- Immediate feedback
- Comprehensive decision tracking
- Easy pivots if direction changes

### Continuous Evaluation

Testing isn't a gate:
- Tests run during Build, not after
- Test failures inform code changes immediately
- Coverage metrics guide implementation
- CI/CD enforces quality at merge

### Parallel Implementation

Large features can use subagents:
- Main agent: Core module changes
- Subagent 1: Web module changes
- Subagent 2: API module changes
- Main agent: Integration and verification

## Common Patterns

### When to Create a New Skill

Create a skill when:
- A pattern will be used in multiple features
- Organization policy must be enforced consistently
- Best practice should be applied uniformly

Example: If all endpoints need the same security checks, create `sdlc-secure-api/SKILL.md`.

### When to Update CLAUDE.md

Update CLAUDE.md when:
- New build/test commands are introduced
- New conventions are established
- Common mistakes are discovered twice
- Keep under 1 page (remove stale info)

### When to Loop Back to Plan

Create new intent.md if:
- Production issue discovered (Maintain phase)
- Major design flaw found (Build phase)
- Requirement changes (anytime)
- New initiative requested

## Governance & Audit Trail

The AI-Native SDLC provides built-in governance:

1. **Git History** - Complete audit trail of all decisions
2. **Versioned Artifacts** - intent.md, spec.md, code, CLAUDE.md all versioned
3. **Human Approval Gates** - Product owner (Plan), Architect (Design), Reviewer (Build)
4. **Skill Enforcement** - Organization policies automated in skills
5. **Metrics Tracking** - Production monitoring in Maintain phase

## Team Setup

### Roles
- **Product Owner**: Approves intent.md, defines requirements
- **Architect/Designer**: Approves spec.md, makes design decisions
- **Engineers**: Implement via Build phase, maintain CLAUDE.md
- **QA/Tester**: Configure and monitor tests
- **Operations**: Monitor production for Maintain phase

### Access Control
- All team members can read/run skills
- Designated owners update skills when policies change
- CLAUDE.md changes reviewed like code
- intent.md written by originators, approved by product owner

## References

- **Course**: [AI-Native SDLC Playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook)
- **Project CLAUDE.md**: `CLAUDE.md` (updated with SDLC workflow)
- **Templates**: `intent.md.template`, `spec.md.template`

---

**Questions?** Check the specific skill documentation (e.g., `sdlc-plan/SKILL.md`) for detailed guidance on each phase.

**Getting Started?** Begin with `/sdlc-plan` to capture your first feature.
