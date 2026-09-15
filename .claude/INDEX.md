# Claude Code AI-Native SDLC System - Complete Index

**Status**: ✅ Production Ready  
**Last Updated**: 2026-09-15  
**Based On**: [AI-Native SDLC Playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook)

## 🚀 START HERE

**New to this system?** Start with one of these:

1. **In a hurry?** → Read `QUICK-START.md` (5 min)
2. **Need guidance?** → See `SKILL-SELECTOR.md` (2 min)
3. **Want full details?** → Read `SDLC-README.md` (10 min)
4. **Need overview?** → See `IMPLEMENTATION-SUMMARY.md` (5 min)

## 📋 Documentation Map

### Quick References
| File | Purpose | Read Time | Use When |
|------|---------|-----------|----------|
| `QUICK-START.md` | 5-step guide to first feature | 5 min | Starting your first feature |
| `SKILL-SELECTOR.md` | Decision tree for skill selection | 2 min | Choosing which skill to use |
| `IMPLEMENTATION-SUMMARY.md` | Overview of what was built | 5 min | Understanding the system |

### Comprehensive Guides
| File | Purpose | Audience | Details |
|------|---------|----------|---------|
| `SDLC-README.md` | Full workflow documentation | All developers | Complete workflow + principles + governance |
| `INDEX.md` | This file | All developers | Navigation and reference |

### Project Files
| File | Purpose | Update Frequency |
|------|---------|------------------|
| `CLAUDE.md` | Project conventions and patterns | During Build phase |
| `intent.md.template` | Template for Plan stage | Rarely (only if process changes) |
| `spec.md.template` | Template for Design stage | Rarely (only if process changes) |

## 🎯 Workflow Stages

### Stage 1: Plan - Capture Intent
**File**: `.claude/skills/sdlc-plan/SKILL.md`
**Key Template**: `intent.md.template`
**Use When**: Starting new feature or bug fix
**Output**: Versioned `intent.md` in git
**Time**: 2-4 hours from idea to committed artifact

### Stage 2: Design - Create Specification
**File**: `.claude/skills/sdlc-design/SKILL.md`
**Key Template**: `spec.md.template`
**Use When**: intent.md is approved
**Tool**: Claude Code `/plan mode` (interactive)
**Output**: Versioned `spec.md` in git
**Time**: 1-2 days for design iteration

### Stage 3: Build - Generate Code and Tests
**File**: `.claude/skills/sdlc-build/SKILL.md`
**Use When**: spec.md is approved
**Tool**: Claude Code `/plan mode` (default entry point)
**Output**: Code + tests + updated CLAUDE.md
**Time**: Varies by feature
**Features**: Supports parallel work with subagents

### Stage 4: Test - Continuous Evaluation
**File**: `.claude/skills/sdlc-test/SKILL.md`
**Use When**: During Build phase
**Tool**: `gradle build` and skill guidance
**Output**: Test results, coverage metrics
**Timing**: Continuous throughout Build
**Key Rule**: Tests must pass before commit

### Stage 6: Maintain - Monitor & Loop
**File**: `.claude/skills/sdlc-maintain/SKILL.md`
**Use When**: Feature deployed to production
**Output**: Metrics, incident reports, new intent.md for issues
**Timing**: Continuous monitoring
**Key Function**: Closes feedback loop → creates new intent.md → back to Plan

### ⏭️ Skip: Stage 5 Deploy (as requested)
Deploy stage is intentionally skipped in this implementation.
Your CI/CD pipeline handles deployment automatically.

## 🛠️ Reusable Skills

All skills follow **Single Responsibility** principle:

```
.claude/skills/
├── sdlc-orchestrator/     Meta skill - workflow overview
├── sdlc-plan/             Stage 1 - capture intent
├── sdlc-design/           Stage 2 - design solution
├── sdlc-build/            Stage 3 - implement code
├── sdlc-test/             Stage 4 - test continuously
└── sdlc-maintain/         Stage 6 - monitor production
```

Each skill:
- Has one clear purpose
- Is independent and reusable
- Reads input from previous stage's artifact
- Produces output for next stage
- Is version-controlled in git

## 📚 Templates & Artifacts

### Templates (for consistency)
- `intent.md.template` - Use for Plan stage
- `spec.md.template` - Use for Design stage

### Versioned Artifacts (committed to git)
- `intent.md` - Problem statement from Plan stage
- `spec.md` - Design from Design stage
- Code + tests - Implementation from Build stage
- `CLAUDE.md` - Updated with patterns from Build stage
- Skills - Reusable patterns created during Build
- Commits - Full audit trail of all decisions

## 🔄 Workflow Loops

### Normal Feature Loop
```
/sdlc-plan → intent.md (commit)
    ↓
/plan mode → spec.md (commit)
    ↓
/plan mode → code + tests (commit)
    ↓
gradle build (tests pass)
    ↓
PR review + merge
    ↓
/sdlc-maintain → monitor
```

### Issue/Fix Loop (from Maintain)
```
/sdlc-maintain → find issue
    ↓
/sdlc-plan → create new intent.md
    ↓
[Loop back to feature loop above]
```

## 💡 Key Design Principles

### Artifact-Driven
Each stage ends by committing; next stage begins by reading:
- Design reads intent.md
- Build reads spec.md
- Test runs the code
- Maintain creates new intent.md

### DRY (Don't Repeat Yourself)
- Templates standardize structure
- Skills encode reusable patterns
- CLAUDE.md is single source of truth
- Shared documentation centralized

### SOLID Principles
- **S**ingle Responsibility: Each skill does one thing
- **O**pen/Closed: Open for extension, closed for modification
- **L**iskov Substitution: Skills interchangeable as needed
- **I**nterface Segregation: Simple, focused interfaces
- **D**ependency Inversion: Depend on artifacts, not implementations

### Human-Centered
- Humans remain accountable for decisions
- AI handles automation and generation
- Critical gates have human review
- Full audit trail via git history

## 📊 Success Metrics

### Leading Indicators
- Time from idea to committed intent.md (target: hours)
- Time from intent.md to committed spec.md (target: 1-2 days)
- Test coverage percentage (target: >80%)
- Build failure rate (target: near zero)

### Lagging Indicators
- Production error rate (trend downward)
- Mean time to fix production issues (trend downward)
- Code review cycle time (trend shorter)
- Repeat incident rate (target: zero)

## 🚦 Decision Trees

### Which Documentation to Read?

```
Need to START?
  ├─ Busy? → QUICK-START.md
  ├─ Confused? → SKILL-SELECTOR.md
  ├─ Deep dive? → SDLC-README.md
  └─ Overview? → IMPLEMENTATION-SUMMARY.md

Implementing a FEATURE?
  ├─ Creating intent? → sdlc-plan/SKILL.md
  ├─ Designing? → sdlc-design/SKILL.md
  ├─ Building? → sdlc-build/SKILL.md
  ├─ Testing? → sdlc-test/SKILL.md
  └─ Monitoring? → sdlc-maintain/SKILL.md

Need TEMPLATES?
  ├─ Planning? → intent.md.template
  └─ Designing? → spec.md.template

Stuck?
  ├─ Don't know which skill? → SKILL-SELECTOR.md
  ├─ Workflow questions? → SDLC-README.md
  ├─ Quick answers? → QUICK-START.md
  └─ Still stuck? → Read all of SDLC-README.md
```

## 🔗 File Cross-References

### By Use Case

**New Feature Workflow**
1. Read: QUICK-START.md (5-step guide)
2. Use: sdlc-plan/SKILL.md
3. Use: sdlc-design/SKILL.md
4. Use: sdlc-build/SKILL.md
5. Use: sdlc-test/SKILL.md
6. Use: sdlc-maintain/SKILL.md

**Choosing Right Skill**
1. Read: SKILL-SELECTOR.md
2. Find matching scenario
3. Navigate to specific skill

**Understanding Architecture**
1. Read: SDLC-README.md
2. Review: Project structure section
3. Check: CLAUDE.md for conventions

**Troubleshooting**
1. Check: QUICK-START.md (Troubleshooting section)
2. Use: SKILL-SELECTOR.md for decision tree
3. Read: Specific skill's SKILL.md
4. Consult: SDLC-README.md (Governance/Metrics sections)

## 📖 Reading Paths

### Path 1: I Want to Build Something Now
1. `QUICK-START.md` (5 min)
2. `/sdlc-plan` (use skill)
3. `/plan mode` (interactive)
4. `gradle build`
5. Go!

### Path 2: I Want to Understand Everything
1. `IMPLEMENTATION-SUMMARY.md` (5 min)
2. `SDLC-README.md` (10 min)
3. `QUICK-START.md` (5 min)
4. Individual skill files as needed

### Path 3: I'm Confused - Help!
1. `SKILL-SELECTOR.md` (2 min)
2. Find your scenario
3. Navigate to specific skill
4. Read that skill's SKILL.md

### Path 4: I'm New to the Project
1. `CLAUDE.md` (conventions)
2. `QUICK-START.md` (workflow)
3. `SKILL-SELECTOR.md` (skills)
4. Start first feature

## 🎓 Learning Resources

**External**
- [AI-Native SDLC Playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook) - Full course
- [Claude Code Documentation](https://claude.ai/code) - Tools and features

**Internal**
- `CLAUDE.md` - Project-specific conventions
- `SDLC-README.md` - Full workflow guide
- Individual skill SKILL.md files - Detailed guidance per stage

## 🔧 Customization

### Extending the System

**Add a New Skill**
1. Create `.claude/skills/new-skill/SKILL.md`
2. Follow the template from existing skills
3. Document when skill triggers
4. Get team review
5. Commit to git

**Update CLAUDE.md**
1. During Build phase, if new patterns discovered
2. Document conventions found twice
3. Keep under 1 page
4. Commit changes

**Modify Templates**
1. Edit `intent.md.template` or `spec.md.template`
2. Ensure new structure makes sense
3. Notify team of changes
4. Commit to git

## 📞 Support & Help

**Still have questions?**
- Quick answers: `QUICK-START.md` (Troubleshooting section)
- Guidance: `SKILL-SELECTOR.md` (decision tree)
- Details: Specific skill's `SKILL.md`
- Full context: `SDLC-README.md`

**Found a problem?**
- Report through your team's issue system
- Reference which skill and file
- Include context about what you were trying

**Want to contribute?**
- Improvements to skills
- Better documentation
- New reusable patterns
- Follow PR process and get team review

## 📝 Version History

| Date | Change | Status |
|------|--------|--------|
| 2026-09-15 | Initial implementation | ✅ Complete |
| — | Future improvements | TBD |

---

**Quick Navigation**

- 🚀 [Quick Start](QUICK-START.md)
- 🎯 [Skill Selector](SKILL-SELECTOR.md)  
- 📖 [Full Guide](SDLC-README.md)
- 📋 [Summary](IMPLEMENTATION-SUMMARY.md)
- 🛠️ [Skills Directory](.claude/skills/)

**Start your first feature**: Read `QUICK-START.md` and use `/sdlc-plan` skill!
