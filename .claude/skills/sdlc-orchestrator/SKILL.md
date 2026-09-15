---
name: sdlc-orchestrator
description: AI-Native SDLC workflow orchestrator. Use to start any phase of the development lifecycle (Plan, Design, Build, Test, Maintain). Skips Deploy phase.
---

# AI-Native SDLC Workflow Orchestrator

This skill guides you through the AI-Native SDLC workflow for clauneck. Each stage produces versioned artifacts that feed into the next stage, creating an audit trail.

## Available Commands

### /sdlc-plan
**Capture project intent as machine-readable requirements**
- Input: Problem description or feature request
- Output: `intent.md` (versioned, committed)
- Next Stage: Design (spec.md creation)

### /sdlc-design  
**Create detailed specifications from intent**
- Input: Approved `intent.md` file reference
- Output: `spec.md` with architecture and implementation approach
- Next Stage: Build (code generation with plan mode)

### /sdlc-build
**Generate code and tests using Claude Code plan mode**
- Input: Approved `spec.md` file reference
- Output: Code, tests, updated `CLAUDE.md`, and optional skills
- Next Stage: Test (continuous evaluation)

### /sdlc-test
**Run continuous evaluations throughout implementation**
- Input: Module to test (core, web, api)
- Output: Test results, coverage metrics, feedback for design
- Next Stage: Refinement or Maintain

### /sdlc-maintain
**Monitor metrics and close the feedback loop**
- Input: Production metrics or incident report
- Output: Metrics summary, new `intent.md` for issues discovered
- Next Stage: Plan (loop back to start)

## Workflow Example

```
User describes problem
    ↓
/sdlc-plan creates intent.md
    ↓
Product owner reviews and approves intent.md (git commit)
    ↓
/sdlc-design creates spec.md
    ↓
Team reviews spec.md (git commit)
    ↓
/sdlc-build generates code using plan mode
    ↓
/sdlc-test runs continuous evaluations
    ↓
PR merges (code becomes artifact)
    ↓
/sdlc-maintain monitors and provides feedback
    ↓
Loop continues or new /sdlc-plan starts
```

## Key Artifacts

- **intent.md** - Problem statement, goals, constraints (Plan stage)
- **spec.md** - Detailed design, architecture, implementation approach (Design stage)
- **Code + Tests** - Generated via plan mode, maintains CLAUDE.md (Build stage)
- **Test Results** - Coverage, metrics, evaluation feedback (Test stage)
- **Metrics + Incidents** - Production monitoring data (Maintain stage)

## Principles

1. **Artifact-Driven**: Each stage ends by committing; next stage begins by reading
2. **Continuous Evaluation**: Test throughout, not just at boundaries
3. **Encoded Standards**: Use skills to maintain organizational patterns
4. **Human Accountability**: Humans responsible for decisions; AI handles automation
5. **Version Control**: All artifacts versioned in Git with full audit trail

## Quick Start

1. Start with `/sdlc-plan "Your feature or problem description"`
2. Review and commit the generated `intent.md`
3. Move to design phase: `/sdlc-design` or use the specific `/sdlc-design` skill
4. Follow the workflow through each stage

---

**Reference**: Based on [AI-Native SDLC Playbook](https://academy.claude.com/courses/ai-native-sdlc-playbook)
