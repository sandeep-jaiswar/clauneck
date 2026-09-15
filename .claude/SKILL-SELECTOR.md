# Skill Selector Guide

Use this guide to quickly find the right skill for your task. Follow DRY and SOLID principles.

## Which Skill Do I Need?

### ❓ I'm not sure where to start
→ **Use**: `/sdlc-orchestrator`

The orchestrator gives you an overview of the entire workflow and explains which skill to use next.

---

### 💡 I have a new idea or problem to solve
→ **Use**: `/sdlc-plan`

**When to use**:
- Starting a new feature
- Reporting a bug that needs fixing
- Incident discovered in production
- New requirement from stakeholders

**What it does**:
- Asks clarifying questions about the problem
- Captures goals and success criteria
- Identifies scope and constraints
- Produces `intent.md`

**Example**:
```
Claude: "We need user authentication"
→ /sdlc-plan creates intent.md
→ You commit intent.md
```

**Next**: Review the generated intent.md, then move to Design

---

### ✏️ I have an approved intent.md and need to design the solution
→ **Use**: `/plan "Design feature from intent.md"` (Plan Mode)

**When to use**:
- intent.md is approved and committed
- Ready to design architecture
- Need to make design decisions
- Building consensus on approach

**What it does**:
- Creates detailed spec.md
- Documents architecture decisions
- Identifies module changes needed
- Specifies testing approach
- Uses interactive plan mode for iteration

**Example**:
```
/plan "Design the user auth feature from intent.md"
→ Claude generates spec.md interactively
→ You iterate on architecture
→ You commit spec.md when ready
```

**Next**: Get team review, then move to Build

---

### 🔨 I have an approved spec.md and need to implement it
→ **Use**: `/plan "Implement feature from spec.md"` (Plan Mode)

**When to use**:
- spec.md is approved and committed
- Ready to write code and tests
- Need guidance on implementation
- Building features

**What it does**:
- Generates code for each module
- Writes tests alongside code
- Updates CLAUDE.md with patterns
- Creates reusable skills if needed
- Commits in logical chunks

**Example**:
```
/plan "Implement the user auth feature from spec.md"
→ Claude generates code + tests
→ Tests run as you go
→ You commit regularly
→ CLAUDE.md gets updated with patterns
```

**Next**: Run tests (see Testing below)

---

### ✅ My code is generated. How do I test it?
→ **Use**: `/sdlc-test`

**When to use**:
- After code generation in Build phase
- Continuously during implementation
- Before committing code
- Need to debug test failures

**What it does**:
- Runs unit, integration, E2E tests
- Generates coverage reports
- Identifies gaps
- Provides feedback for refinement

**Example**:
```
gradle build              # Run all tests
gradle :core:test         # Test specific module
# Tests failing? Use /plan to debug
/plan "Debug the failing test"
```

**Next**: Fix failures, then commit code

---

### 📊 My feature is deployed. How do I monitor it?
→ **Use**: `/sdlc-maintain`

**When to use**:
- Feature is in production
- Monitoring metrics and health
- Issue discovered in production
- Creating action items from incidents

**What it does**:
- Reviews production metrics
- Captures incidents
- Analyzes root causes
- Creates new intent.md for issues
- Updates CLAUDE.md with lessons

**Example**:
```
/sdlc-maintain
→ Review error rates, latency
→ Find auth endpoint is slow
→ Create intent.md: "Fix auth performance"
→ Loop back to /sdlc-plan
```

**Next**: If issues found, create new intent.md and loop back to Plan

---

## Decision Tree

```
                        What do I need?
                              |
                ______________|_____________
               |              |            |
           Not sure?      Have an idea?  Already designing/
               |              |           building/testing?
               |              |                 |
               v              v                 |
            Use:           Use:         ________|________
          sdlc-           sdlc-plan      |              |
        orchestrator                   Designing or   Testing or
                                       Building?      Monitoring?
                                          |              |
                                          v              v
                                    Use /plan mode   Use next
                                                    appropriate
                                    Design:         skill:
                                    spec.md         
                                                    Testing:
                                    Build:          sdlc-test
                                    Code + tests
                                                    Monitoring:
                                                    sdlc-maintain
                                                    
                                                    Issues found?
                                                    Loop back to
                                                    sdlc-plan
```

---

## By Current Stage

### 📋 Planning Stage
| Question | Skill | Output |
|----------|-------|--------|
| Got a new idea? | `/sdlc-plan` | intent.md |
| Is intent approved? | Move to Design | — |

### ✏️ Design Stage
| Question | Skill | Output |
|----------|-------|--------|
| Ready to design? | `/plan mode` | spec.md |
| Is spec approved? | Move to Build | — |

### 🔨 Build Stage
| Question | Skill | Output |
|----------|-------|--------|
| Ready to implement? | `/plan mode` | Code + tests |
| Tests passing? | `/sdlc-test` | Test results |
| All features done? | Move to Maintain | — |

### 📊 Maintain Stage
| Question | Skill | Output |
|----------|-------|--------|
| Monitoring production? | `/sdlc-maintain` | Metrics |
| Found an issue? | `/sdlc-plan` | New intent.md |

---

## By File Type

### When You See...

**intent.md** (exists, not approved)
→ Review and approve it
→ Then use `/plan mode` for design

**spec.md** (exists, not approved)
→ Review and approve it
→ Then use `/plan mode` for implementation

**Code with failing tests**
→ Use `/sdlc-test`
→ Or use `/plan "Debug the failing test"`
→ Fix and re-run

**Production issue**
→ Use `/sdlc-maintain`
→ Create new intent.md
→ Loop back to `/sdlc-plan`

---

## By Error/Blocker

### I don't understand the workflow
→ Read `.claude/SDLC-README.md`
→ Or use `/sdlc-orchestrator` skill

### I'm stuck in plan mode
→ What are you trying to do?
- Designing? Keep going, `/plan mode` is correct
- Building? Keep going, `/plan mode` is correct
- Stuck? Use `/plan "Help me with [specific problem]"`

### Tests are failing
→ Don't ignore them
→ Option 1: Use `/plan "Debug the failing test"`
→ Option 2: Review test code and fix
→ Tests must pass before commit

### Not sure what to do next
→ Check the workflow diagram in QUICK-START.md
→ Or use `/sdlc-orchestrator`

### Want to automate a pattern
→ Create a skill in `.claude/skills/new-skill/SKILL.md`
→ Document when it triggers
→ Team reviews and approves

---

## SOLID Principles Reminder

Each skill has **Single Responsibility**:

- `sdlc-plan` - Captures intent (no design, no code)
- `sdlc-design` - Designs solution (no implementation yet)
- `sdlc-build` - Implements from spec (generates code + tests)
- `sdlc-test` - Validates implementation (runs tests)
- `sdlc-maintain` - Monitors production (finds issues)

They are **Loosely Coupled** - each reads the artifact from the previous stage:

- Design reads intent.md
- Build reads spec.md
- Test runs the code
- Maintain monitors the deployed code
- Maintain creates new intent.md for issues

They are **Composable** - use them in sequence or standalone:

```
Typical flow:
sdlc-plan → /plan design → /plan build → sdlc-test → sdlc-maintain

Standalone:
- Just need design? → /plan mode directly
- Just testing? → gradle build or sdlc-test
- Just monitoring? → sdlc-maintain
```

---

## Quick Reference Card

```
Start Here          | Use This         | Get This
--------------------|-----------------|-------------
New idea            | /sdlc-plan       | intent.md
Approved intent.md  | /plan mode       | spec.md
Approved spec.md    | /plan mode       | Code+tests
Code generated      | /sdlc-test       | Test results
In production       | /sdlc-maintain   | Metrics
Issue in prod       | /sdlc-plan       | New intent.md
```

---

**Still not sure?** Use `/sdlc-orchestrator` for guidance.

**Want details?** Read the specific skill's SKILL.md file (e.g., `.claude/skills/sdlc-plan/SKILL.md`).

**Need full context?** See `.claude/SDLC-README.md`.
