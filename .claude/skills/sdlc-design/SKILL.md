---
name: sdlc-design
description: Convert intent.md into detailed specifications. Creates spec.md with architecture, design decisions, and implementation approach for the Build phase.
---

# Stage 2: Design - Requirements and Specification

This skill converts an approved `intent.md` into a detailed `spec.md` that guides the Build phase. The designer compresses requirements and design decisions into one interactive working session with Claude.

## What This Stage Does

Transforms high-level intent into **detailed specification** that includes:
- Functional and non-functional requirements
- Architecture and design decisions
- Module-by-module changes (core, web, api)
- Implementation approach and phases
- Testing strategy
- Technical decision rationale
- Risk identification and mitigation
- Success metrics

## How to Execute

### 1. Use Claude Code Plan Mode (Recommended)

Start with plan mode for interactive design session:
```bash
# In Claude Code, open the repo and reference the approved intent.md
# /plan "Design the feature from intent.md"
```

Plan mode lets you:
- Ask clarifying questions interactively
- Iterate on architecture together
- Build consensus before coding starts
- Document decisions as you make them

### 2. Design Workflow

1. **Read the approved intent.md**
   - Understand problem, goals, scope, constraints
   - Identify affected modules and dependencies

2. **Explore the codebase**
   - Understand current architecture (core, web, api modules)
   - Review existing patterns in CLAUDE.md
   - Check build.gradle for dependencies

3. **Create spec.md using the template**
   - Overview: Brief description of what will be built and why
   - Requirements: Functional and non-functional specs
   - Architecture: High-level design approach
   - Module Changes: Specific changes per module
   - Implementation Approach: Step-by-step phases
   - Testing Strategy: Unit, integration, E2E approaches
   - Technical Decisions: Rationale for design choices
   - Risks & Mitigations: Identify and plan for risks
   - Success Metrics: How to measure if it worked

4. **Document decision rationale**
   - Why this approach over alternatives?
   - What are the tradeoffs?
   - How does it fit existing architecture?

5. **Review and iterate**
   - Get feedback from team
   - Refine architecture if needed
   - Ensure feasibility

6. **Commit to version control**
   ```bash
   git add spec.md
   git commit -m "design: [feature-name]

   [Brief description of design approach]"
   ```

7. **Get team review approval**
   - Technical lead reviews design
   - Architecture decisions are sound?
   - Correct module dependencies?
   - Tests align with requirements?
   - Merge indicates readiness for Build

## Spec.md Structure Reference

### High-Level Sections

1. **Overview** - What's being built and why (1-2 paragraphs)

2. **Requirements**
   - Functional Requirements (REQ-1, REQ-2, etc. with acceptance criteria)
   - Non-Functional Requirements (performance, security, scalability, maintainability)

3. **Architecture & Design**
   - High-level architecture diagram/description
   - Module changes for: core, web, api
   - Design patterns used

4. **Implementation Approach**
   - Phase-by-phase breakdown
   - Which tasks go in which phase
   - Testing strategy for each phase

5. **Technical Decisions**
   - Why this choice?
   - Alternatives considered?
   - What are the tradeoffs?

6. **Risks & Mitigations**
   - Identify risks by impact
   - Plan mitigation for each

7. **Success Metrics**
   - How to measure if feature works
   - How to measure quality

8. **Rollback Plan** - What if things go wrong?

## Governance

- **Artifact**: Committed spec.md with designer as author
- **Approval**: Technical lead/architect review
- **Decision Record**: Git history of spec.md changes
- **Changes**: Updates to spec.md are reviewed like code

## Principles

1. **Plan Mode First**: Use Claude Code plan mode for interactive, iterative design
2. **Write for Build Phase**: Spec.md should be detailed enough to guide implementation
3. **Update CLAUDE.md**: Document new patterns discovered during design
4. **Keep Rationale**: Record why decisions were made (helps future readers)

## Success Metrics

**Leading Indicator**: Time from intent.md approval to spec.md commit
- Should be 1-2 days for moderate features

**Lagging Indicator**: Spec.md drift during Build
- Few changes to spec.md after Build starts = clear specifications
- Many changes = requirements weren't well understood

## Mistakes to Avoid

- ❌ Writing spec without plan mode (use interactive design)
- ❌ Over-specifying details that Build phase will figure out
- ❌ Under-specifying enough to guide Build phase
- ❌ Ignoring existing patterns (check CLAUDE.md for conventions)
- ❌ Forgetting to update CLAUDE.md with new patterns

## Next Steps

Once spec.md is committed and approved:
1. Move to Build phase
2. Use `/sdlc-build` to implement the specification
3. Build phase generates code and tests using plan mode
4. Maintain spec.md as source of truth for implementation

---

**Prerequisites**: Approved and committed intent.md

**Infrastructure Needed**:
- Claude Code with plan mode
- Approved intent.md from Plan stage
- Existing CLAUDE.md for architecture context
- spec.md template

**Key Principle**: Design phase bridges intent and implementation by:
- Making architecture decisions explicit
- Documenting rationale for future reference
- Creating shared understanding before Build starts
- Using plan mode for interactive, iterative refinement
