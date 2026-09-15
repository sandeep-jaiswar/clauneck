---
name: sdlc-maintain
description: Monitor production metrics and close the feedback loop. Routes issues back to planning cycle and maintains CLAUDE.md with lessons learned.
---

# Stage 6: Maintain - Closing the Loop

This skill monitors production deployments and routes insights back into the planning cycle, creating a continuous feedback loop. Issues discovered in production become new intent.md entries that restart the workflow.

## What This Stage Does

**Maintains deployed features** by:
- Monitoring production metrics and health
- Capturing incidents and issues
- Analyzing root causes
- Creating new intent.md for problems found
- Updating CLAUDE.md with lessons learned
- Feeding feedback back to Planning stage

## How to Execute

### 1. Monitor Production Metrics

Set up monitoring for deployed features:

**Key Metrics to Track**:
- Error rates and exceptions
- Performance/latency
- Feature usage (if applicable)
- User-reported issues
- Test coverage (regression risk)

**Tools**:
- Application logs
- Metrics dashboards (Grafana, CloudWatch, etc.)
- Error tracking (Sentry, DataDog, etc.)
- User feedback channels

### 2. Incident Response Workflow

When an issue is detected:

```
Incident Detected
    ↓
Classify Severity
    ├─ Critical → Immediate fix
    ├─ High → Fix in next sprint
    └─ Low → Backlog for future work
    ↓
Diagnose Root Cause
    ├─ Code bug → Create fix PR
    ├─ Design issue → Create new intent.md
    └─ Infrastructure → Route to ops team
    ↓
Create intent.md for issue
    (Link to incident record)
    ↓
Assign to team
    ↓
Loop back to Plan → Design → Build → Test
```

### 3. Create Issue Intent.md

For problems found in production, create a new `intent.md`:

```markdown
# Intent: Fix [Issue Name]

**Date**: 2026-09-15
**Author**: [Who discovered issue]
**Incident Link**: [Monitoring/ticketing URL]

## Problem Statement

[Description of the issue from monitoring/customer reports]

## Observed Behavior

- What's happening in production?
- Impact on users
- Frequency of occurrence

## Expected Behavior

- How should the feature work?
- What's the correct behavior?

## Root Cause Analysis

- What's the underlying cause?
- Is it code, design, or infrastructure?
- How did testing miss this?

## Immediate Mitigation

- Temporary workaround if needed
- Should we rollback?

## Affected Modules

- [ ] core
- [ ] web
- [ ] api

## Fix Strategy

- Quick fix or redesign?
- Testing improvements needed?

## Prevention

- How to prevent this in future?
- What should CLAUDE.md say?
- New test cases needed?
```

### 4. Update CLAUDE.md with Lessons

For each issue, update CLAUDE.md:

```markdown
## Lesson from [Incident Name]

**Issue**: [Brief description]  
**Root Cause**: [Why it happened]  
**Prevention**: What to watch for

### Things Claude Gets Wrong (updated)
- ❌ This mistake led to [incident]
- ✅ Do this instead to prevent it
```

### 5. Track Metrics Over Time

**Create or update a MAINTAIN.md** file to track:

```markdown
# Maintenance Metrics - clauneck

## Production Health
- Last week error rate: [X%]
- Last week avg latency: [Xms]
- Uptime: [X%]

## Issues by Category
- Code bugs fixed: [N]
- Design changes: [N]
- Infrastructure: [N]

## Test Coverage
- Overall: [X%]
- Improved by: [X%] from last period

## Lessons Learned
- [Issue 1]: Root cause and fix
- [Issue 2]: Root cause and fix

## Trends
- Incident rate: [Trending up/down/stable]
- Mean time to resolution: [X hours]
- Prevention success rate: [X%]
```

## Governance

- **Artifact**: Incident records, fix PRs, updated intent.md files
- **Feedback Loop**: Issues → new intent.md → Design → Build → Testing
- **Audit Trail**: All incidents tracked in git history
- **Learning**: CLAUDE.md updated with lessons

## Success Metrics

**Leading Indicators**:
- Time from incident detection to fix deployment
- % of incidents with root cause analysis
- % of lessons incorporated into CLAUDE.md

**Lagging Indicators**:
- Repeat incident rate (same issue twice?)
- Production error rate (trending?)
- Customer-reported issues (trending down?)
- Mean time to resolution (MTTR)

## Integration with Full Workflow

The Maintain phase completes the loop:

```
/sdlc-plan (new feature)
    ↓
/sdlc-design
    ↓
/sdlc-build
    ↓
/sdlc-test
    ↓
Deploy to production
    ↓
/sdlc-maintain (monitor)
    ↓
Issue found?
    ├─ YES → Create new intent.md
    │   └─ Loop back to /sdlc-plan
    └─ NO → Continue monitoring
```

## Common Maintenance Tasks

### Daily
- Check error rates and dashboards
- Review new incidents
- Respond to critical issues

### Weekly
- Update maintenance metrics
- Review incident trends
- Plan fixes for backlog issues

### Monthly
- Analyze patterns (what keeps breaking?)
- Update CLAUDE.md with trends
- Retrospective on incident response

### Quarterly
- Major lessons review
- Update deployment strategy if needed
- Plan preventive improvements

## Prevention Best Practices

### In Build Phase
- Follow existing patterns (check CLAUDE.md)
- Don't skip test coverage
- Add edge case tests

### In Test Phase
- Run production-like tests
- Test error scenarios
- Load/stress testing for critical paths

### In Maintain Phase
- Monitor before issues escalate
- Quick root cause analysis
- Share learnings with team

## Handling Different Issue Types

| Issue Type | Response | Next Steps |
|-----------|----------|-----------|
| **Code Bug** | Fix immediately | PR with test, update CLAUDE.md |
| **Design Issue** | Assess impact | May need redesign (new intent.md) |
| **Performance** | Investigate cause | Optimize or refactor, add tests |
| **Security** | Critical priority | Audit, fix, security review |
| **Infrastructure** | Route to ops | May not require code change |

## Creating Skills from Lessons

If similar issues occur repeatedly, create a skill:

```
.claude/skills/prevent-[issue]/SKILL.md
```

Example: If null pointer exceptions keep happening:

```markdown
---
name: prevent-null-pointers
description: Prevent null pointer exceptions in clauneck
---

# Prevention: Null Pointer Exceptions

When working with potentially null values:
1. Always null-check before use
2. Prefer Optional<T> for Java
3. Use @NonNull annotations
4. Write tests for null cases
```

## Next Steps

Continuous cycle:
1. Monitor production continuously
2. Detect issues early
3. Create intent.md for problems
4. Fix via Plan → Design → Build → Test cycle
5. Deploy fix
6. Resume monitoring
7. Update CLAUDE.md with lessons

---

**Prerequisites**: Deployed feature in production

**Infrastructure Needed**:
- Monitoring/alerting system
- Metrics dashboard
- Error tracking tool
- Incident management system
- Communication channels for alerts

**Key Principle**: Maintain phase closes the loop:
- Production insights inform future development
- Issues become intent.md entries
- Lessons captured in CLAUDE.md
- Prevention > Reaction
- Continuous improvement cycle
