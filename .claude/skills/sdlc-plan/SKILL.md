---
name: sdlc-plan
description: Capture project intent for features or fixes. Creates machine-readable, version-controlled intent.md files that initiate the development workflow.
---

# Stage 1: Plan - Capture Intent

This skill helps capture the intent for a new feature or fix. The output is a versioned `intent.md` file that serves as the starting artifact for the AI-Native SDLC workflow.

## What This Stage Does

Converts user ideas, feature requests, or incidents into **machine-readable and human-readable intent.md** files that:
- Synthesize pain points and requirements
- Define scope, goals, and success criteria
- Document constraints and dependencies
- Create an audit trail (author, timestamp, git history)

## How to Execute

1. **Describe the problem** to Claude in your own words
   - What can't you do today? What's broken?
   - Who is affected?
   - What would better look like?

2. **Brainstorm until concrete**
   - Claude will ask clarifying questions about scope, users, constraints
   - Iteratively refine the idea

3. **Generate intent.md**
   - Claude writes the result using the project's intent.md template
   - Structure covers: problem, goals, success criteria, scope, affected modules, dependencies, constraints

4. **Review and correct**
   - Review the generated intent.md for accuracy
   - Make corrections if Claude misunderstood something
   - Ensure goals and success criteria are measurable

5. **Commit to version control**
   ```bash
   git add intent.md
   git commit -m "plan: [feature-name]

   [Brief description of what this intent captures]"
   ```

6. **Get product owner approval**
   - Product owner reviews the committed intent.md
   - Approves or requests changes via PR review
   - Merge indicates acceptance and triggers Design stage

## Template Reference

The intent.md template includes sections for:
- **Problem Statement** - What problem are we solving and why?
- **Goals** - What should be achieved?
- **Success Criteria** - How will we measure success?
- **Scope** - What's in/out of scope?
- **Affected Modules** - Which modules are impacted? (core, web, api)
- **Dependencies** - External or internal dependencies?
- **Known Constraints** - Technical, timeline, resource constraints?
- **Background & Context** - Why was this requested?

## Governance

- **Evidence**: The committed intent.md with author, timestamp, and full git history
- **Approval**: Product owner's merge or close decision
- **Audit Trail**: Git history shows who requested what and when

## Success Metrics

**Leading Indicator**: Time from first conversation to committed intent.md
- Traditional SDLC: multi-week refinement cycle
- AI-Native SDLC: should be hours

**Lagging Indicator**: Survival rate of intent.md files
- % of intent.md accepted into Design stage
- Fewer changes to intent.md after spec.md is created = clearer requirements

## Next Steps

Once intent.md is committed and approved:
1. Move to Design phase
2. Use `/sdlc-design` to create detailed spec.md
3. Designer compresses requirements into implementation approach
4. Spec.md guides the Build phase

---

**Prerequisites**: None. Start here with any new feature or fix.

**Infrastructure Needed**:
- Claude access (claude.ai, Claude Code, or Cowork)
- Shared intent.md template in the repo
- Version-controlled home for intent artifacts (e.g., `intent/` folder in repo)

**Key Principle**: Intent capture is fast (hours, not weeks) because:
- The originator describes it in their own terms
- Claude asks the analytical questions
- The artifact is immediately consumable by Design phase
- Handoff is via versioned file, not person-to-person
