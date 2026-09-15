# Quick Start: AI-Native SDLC for clauneck

Get started with the AI-Native SDLC workflow in 5 steps.

## 1️⃣ Your First Feature

### Capture the Idea

**Start here**: Use `/sdlc-plan` skill

```
Describe your feature or problem to Claude:
- "Add user authentication to the web module"
- "Fix the payment processing bug"
- "Improve API performance"
```

Claude will ask clarifying questions like:
- Who needs this?
- What does success look like?
- Are there constraints?

**Output**: An `intent.md` file is generated

### Commit Your Intent

```bash
# Review the generated intent.md
# Make corrections if needed

git add intent.md
git commit -m "plan: feature-name

Brief description of what this intent captures"
```

---

## 2️⃣ Design Phase

### Start Interactive Design

**Use**: Claude Code **plan mode**

```
# In Claude Code, run:
/plan "Design the feature from intent.md"
```

Claude will:
- Ask about architecture
- Discuss module changes needed
- Identify design patterns
- Create a detailed spec.md

### Commit Your Specification

```bash
git add spec.md
git commit -m "design: feature-name

Architecture: brief description of design approach"
```

---

## 3️⃣ Implementation Phase

### Generate Code with Plan Mode

**Use**: Claude Code **plan mode** (recommended)

```
# In Claude Code, run:
/plan "Implement feature from spec.md"
```

Claude will:
- Generate code for each module (core, web, api)
- Write tests alongside code
- Update CLAUDE.md with new patterns
- Commit in logical chunks

### Keep Tests Passing

```bash
# Run tests frequently during implementation
gradle build

# Build must pass before committing
# Tests failing? Fix immediately (don't ignore)
```

### Commit Your Work

```bash
git commit -m "feat: feature-name - brief description

- What was implemented
- Why this approach
- How it satisfies spec.md"
```

---

## 4️⃣ Testing & Verification

### Run Tests

**Use**: `/sdlc-test` skill

```bash
# During implementation (part of Build)
gradle build          # All modules + tests
gradle :core:test     # Specific module
gradle test --info    # With coverage info
```

**Key Rules**:
- Tests must pass before merge
- Coverage should be >80%
- Test failures are NOT ignored

### CI/CD Automatic

Tests also run automatically in:
- `.github/workflows/ci.yml`
- Runs on push/PR to `production` branch
- Command: `gradle build --no-daemon`

---

## 5️⃣ Monitor Production (Maintain Phase)

### Track Metrics

**Use**: `/sdlc-maintain` skill

```bash
# Monitor your deployed feature
# Check: error rates, latency, usage

# If you find an issue:
# Create a new intent.md and loop back to step 1
```

---

## File Reference

### Templates

Create new features from templates:
- `intent.md.template` - Use for planning
- `spec.md.template` - Use for design

### Project Files (Updated for SDLC)

- `CLAUDE.md` - Project conventions and patterns
- `.claude/SDLC-README.md` - Full workflow documentation
- `.claude/skills/` - All available skills

---

## Workflow in One Picture

```
💡 IDEA
  ↓
📋 /sdlc-plan → intent.md (commit)
  ↓
✏️ /plan mode → spec.md (commit)
  ↓
🔨 /plan mode → Code + Tests + CLAUDE.md (commit)
  ↓
✅ /sdlc-test → gradle build (PASS)
  ↓
📦 Merge to main (automatic CI runs)
  ↓
📊 /sdlc-maintain → Monitor production
  ↓
❓ Issue found?
  └─> Create new intent.md → Loop back to 📋
```

---

## Common Commands

### Start New Feature
```bash
# Describe your idea to Claude using /sdlc-plan skill
# Reference the orchestrator skill for guidance
```

### Use Plan Mode for Interactive Development
```bash
# In Claude Code:
/plan "Design/implement based on spec.md or intent.md"
```

### Run Tests
```bash
gradle build              # All tests
gradle :core:test         # Core module
gradle :web:build         # Web module
```

### Commit Work
```bash
git add .
git commit -m "feat: name - description"
```

### Check CI Status
```bash
# .github/workflows/ci.yml runs automatically
# Check GitHub Actions tab for status
```

---

## Troubleshooting

### "Tests are failing"
```bash
# 1. Don't commit failing tests
# 2. Use plan mode to debug
# 3. /plan "Debug the failing test"
# 4. Fix and re-run
# 5. Then commit
```

### "I'm not sure about the architecture"
```bash
# Use /plan mode with spec.md visible
# /plan "Review and refine architecture for module X"
# Iterate until clear
```

### "What conventions should I follow?"
```bash
# Read CLAUDE.md - it's your source of truth
# It documents:
# - Build commands
# - Conventions
# - Architecture patterns
# - Common mistakes
```

### "How do I create a reusable skill?"
```bash
# See .claude/skills/ directory
# Skills are for patterns that repeat
# Example: All endpoints need X check
# Create: .claude/skills/enforce-x/SKILL.md
```

---

## Next Steps

1. **Now**: Read `.claude/SDLC-README.md` for full documentation
2. **Next**: Start your first feature with `/sdlc-plan`
3. **Then**: Design with `/plan "Design from intent.md"`
4. **Build**: Implement with `/plan "Implement from spec.md"`
5. **Test**: Run `gradle build` to verify
6. **Deploy**: Merge to main (CI runs automatically)
7. **Maintain**: Monitor with `/sdlc-maintain`

---

## Skills Available

| Skill | Purpose | Input | Output |
|-------|---------|-------|--------|
| sdlc-orchestrator | Workflow overview | Question | Guidance |
| sdlc-plan | Capture intent | Problem desc | intent.md |
| sdlc-design | Design phase | intent.md | spec.md |
| sdlc-build | Implementation | spec.md | Code + tests |
| sdlc-test | Testing | Code | Test results |
| sdlc-maintain | Production monitor | Metrics | Issues/lessons |

---

**Ready?** Start with `/sdlc-plan "Your feature or problem description"`

**Questions?** See `.claude/SDLC-README.md` for detailed guidance on each skill.
