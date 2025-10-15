# Quality Gate Escalation Procedures

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Escalation workflows for quality gate overrides and blocked PR resolution

---

## Overview

This document defines the escalation procedures for resolving blocked PRs when quality gate failures prevent merge. The escalation system balances code quality enforcement with business agility through structured approval workflows.

**Escalation Levels:**
1. **Level 1**: Self-service override (non-critical checks)
2. **Level 2**: Tech lead approval (architectural/testing exceptions)
3. **Level 3**: Security team review (security check overrides)
4. **Level 4**: Emergency override (production incidents)

---

## Table of Contents

1. [Escalation Decision Tree](#escalation-decision-tree)
2. [Level 1: Self-Service Override](#level-1-self-service-override)
3. [Level 2: Tech Lead Approval](#level-2-tech-lead-approval)
4. [Level 3: Security Team Review](#level-3-security-team-review)
5. [Level 4: Emergency Override](#level-4-emergency-override)
6. [Notification Templates](#notification-templates)
7. [Response Time SLAs](#response-time-slas)
8. [Audit and Compliance](#audit-and-compliance)

---

## Escalation Decision Tree

```
PR Blocked by Quality Gate
        ↓
Is it a SECURITY check failure?
    YES → Level 3 (Security Team Review)
    NO  → ↓
        
Is it a BREAKING CHANGE check failure?
    YES → Can you update CHANGELOG.md?
        YES → Fix and re-run checks
        NO  → Level 2 (Tech Lead Approval)
    NO  → ↓
        
Is it an ARCHITECTURE/TESTING check failure?
    YES → Do you have valid justification?
        YES → Level 1 (Self-Service Override)
        NO  → Level 2 (Tech Lead Approval)
    NO  → ↓
        
Is this a PRODUCTION INCIDENT?
    YES → Level 4 (Emergency Override)
    NO  → Level 1 or Level 2
```

---

## Level 1: Self-Service Override

### Applicable Checks

**Architecture Checks:**
- `layer-separation`
- `dependency-injection`
- `async-patterns`

**Testing Checks:**
- `new-functions-tests`
- `bug-fix-regression`

**Performance Checks:**
- `n-plus-one`
- `database-indexes`
- `algorithm-complexity`

**Documentation Checks:**
- `docstring-coverage`

### Process

**Timeframe:** Immediate (no approval required)

**Steps:**

1. **Verify Check is Overridable**
   - Review list of available override checks in PR comment
   - Confirm check is not security-related or breaking change

2. **Prepare Justification (50+ characters)**
   - Explain why override is necessary
   - Describe mitigation or planned remediation
   - Reference tickets if temporary workaround

3. **Post Override Command**
   ```
   @coderabbitai ignore <check-name> --reason "Your detailed justification here"
   ```

4. **CodeRabbit Processes Override**
   - Validates justification length
   - Logs override to audit trail
   - Marks check as `[IGNORED]` in review
   - Unblocks PR merge

### Example

```markdown
@coderabbitai ignore layer-separation --reason "Temporary direct database call in controller to work around bug TECH-789 in repository layer. Scheduled for proper refactoring in sprint 24 (ticket TECH-790). Risk is low - only affects internal admin panel, not customer-facing API."
```

### Validation

✅ **Accepted if:**
- Justification >= 50 characters
- Check is in allowed override list
- Justification is substantive (not generic)

❌ **Rejected if:**
- Justification too short
- Generic justification ("it's fine", "trust me")
- Check is security-related
- Check is not available for override

---

## Level 2: Tech Lead Approval

### Applicable Situations

**Architectural Deviations:**
- Violating layered architecture with business justification
- Using anti-patterns with documented reason
- Technical debt with planned remediation

**Test Coverage Exceptions:**
- New functions without tests (legacy integration)
- Missing regression tests (time-sensitive hotfix)

**Business-Justified Exceptions:**
- Customer demo deadline
- Contractual obligation
- Critical business opportunity

### Process

**Timeframe:** 4-hour SLA during business hours (9am-6pm Pacific)

**Steps:**

1. **Developer Initiates Escalation**
   - Mention `@kellerai/tech-leads` in PR comment
   - Provide business justification template (see below)

2. **Tech Lead Reviews**
   - Assess technical risk
   - Evaluate business impact
   - Consider alternatives
   - Review remediation plan

3. **Tech Lead Decision**
   - **Approved:** Posts override command with tech lead justification
   - **Conditional:** Requests changes or additional context
   - **Rejected:** Provides guidance on proper fix

4. **Logging**
   - Override logged with tech lead as authorizer
   - Business justification captured
   - Remediation plan documented

### Business Justification Template

```markdown
@kellerai/tech-leads - Escalation request for tech lead override approval

**Check Failed:** <check-name>
**PR:** #<number> - <title>

**Business Justification:**
<Why is this merge urgent? What is the business impact of delay?>

**Technical Context:**
<What is the check failure? Why can't it be fixed immediately?>

**Remediation Plan:**
- Follow-up ticket: <TICKET-ID>
- Scheduled for: <Sprint/Date>
- Temporary workaround: <Description>
- Risk assessment: <Low/Medium/High - with reasoning>

**Impact of Delay:**
<What happens if we wait to fix this properly?>

**Approval Request:**
Tech lead override approval requested for <check-name> with plan to remediate in <timeframe>.
```

### Example

```markdown
@kellerai/tech-leads - Escalation request for tech lead override approval

**Check Failed:** layer-separation
**PR:** #456 - feat(orders): add expedited shipping option

**Business Justification:**
Major enterprise customer (Acme Corp - $2M ARR) requires expedited shipping by EOD Friday for contract renewal demo. Missing this deadline risks losing the renewal.

**Technical Context:**
Need direct database call in controller to bypass caching bug in repository layer (TECH-789). Proper fix requires refactoring repository caching mechanism (estimated 2 days).

**Remediation Plan:**
- Follow-up ticket: TECH-790 "Refactor order repository caching"
- Scheduled for: Sprint 24 (starts Monday)
- Temporary workaround: Direct DB call with explicit transaction handling
- Risk assessment: LOW - only affects new expedited shipping feature, not existing order processing

**Impact of Delay:**
- Cannot demo expedited shipping to Acme Corp on Friday
- Risk losing $2M ARR contract renewal
- Competitor offering similar feature

**Approval Request:**
Tech lead override approval requested for layer-separation with plan to remediate in Sprint 24 (5 business days).
```

### Tech Lead Approval

```markdown
**TECH LEAD APPROVAL**

Reviewed escalation request for PR #456.

**Decision:** APPROVED

**Reasoning:**
- Business justification is valid (customer demo, contract renewal)
- Technical risk is acceptable (isolated to new feature, not existing functionality)
- Remediation plan is concrete (ticket created, timeline defined)
- Temporary workaround includes proper safeguards (explicit transaction handling)

**Conditions:**
1. Add TODO comment with TECH-790 reference at direct DB call
2. Include rollback plan in deployment notes
3. Monitor new feature for issues during demo period
4. Complete TECH-790 remediation before next release

@coderabbitai ignore layer-separation --reason "TECH LEAD APPROVED: Temporary direct database call for expedited shipping feature. Business justification: Acme Corp $2M contract renewal demo (deadline Friday). Technical debt tracked in TECH-790, scheduled for Sprint 24 remediation. Risk: LOW - isolated new feature. Approved by @tech-lead-name"

**Approval Timestamp:** 2025-10-14 14:30 PST
**Approver:** @tech-lead-name
```

### Response Time SLA

**Business Hours (9am-6pm Pacific):**
- **Target:** 2 hours
- **Maximum:** 4 hours

**After Hours / Weekends:**
- Use emergency override process (Level 4)
- Or wait for next business day

**Escalation:**
If no response within SLA, mention `@kellerai/engineering-leadership`

---

## Level 3: Security Team Review

### Applicable Situations

**Security Check Overrides Only:**
- `hardcoded-credentials`
- `sql-injection`
- `sensitive-data-logging`
- `unsafe-deserialization`

**Typical False Positives:**
- Test data from vendor documentation
- Public API keys (publishable, not secret)
- Logging patterns that appear sensitive but aren't
- Safe deserialization patterns (known-safe types)

### Process

**Timeframe:** 1 business day (8 hours during business hours)

**Steps:**

1. **Developer Provides Security Analysis**
   - Mention `@kellerai/security-team`
   - Use security review template (see below)
   - Provide complete context and evidence

2. **Security Team Reviews**
   - Validate claim of false positive
   - Assess actual security risk
   - Consider alternative implementations
   - Consult external references if needed

3. **Security Team Decision**
   - **Approved:** Override granted with security team justification
   - **Alternative Required:** Provides secure implementation guidance
   - **Rejected:** Confirms genuine security issue, must be fixed

4. **Logging**
   - All security overrides logged separately
   - Quarterly security override review
   - Patterns inform false positive reduction

### Security Review Template

```markdown
@kellerai/security-team - Security check false positive review request

**Check:** <check-name>
**Severity:** <critical/high/medium/low>
**File:** `<file-path>:<line-number>`

**Flagged Code:**
```<language>
<exact code that was flagged>
```

**Security Analysis:**
<Why this is not a genuine security vulnerability>

**Evidence:**
<Links to documentation, vendor guidelines, security research>

**Context:**
<Where is this code used? What data flows through it?>

**Alternative Considered:**
<What alternatives did you evaluate? Why is this approach necessary?>

**Risk Assessment:**
<What is the actual security risk, if any?>

**Request:**
Override approval for this specific instance. <Explain if pattern should be generally allowed>
```

### Example: Test API Key

```markdown
@kellerai/security-team - Security check false positive review request

**Check:** hardcoded-credentials
**Severity:** critical
**File:** `tests/integration/payment/stripe_fixtures.py:23`

**Flagged Code:**
```python
STRIPE_TEST_PUBLISHABLE_KEY = "pk_test_51Hqz..." # Stripe test publishable key
```

**Security Analysis:**
This is a Stripe test mode publishable key (pk_test_*), NOT a secret key. Publishable keys are designed to be public and safe to commit to version control.

**Evidence:**
- Stripe Official Docs: https://stripe.com/docs/keys#test-live-modes
  > "Publishable keys are meant to be public and can be safely included in client-side code."
- Key prefix: `pk_test_` indicates TEST publishable key (not production, not secret)
- Stripe dashboard shows this key has rate limits and cannot charge real cards

**Context:**
Used exclusively in test fixtures for integration tests. Never used in production code. Test suite requires consistent key for reproducible test data.

**Alternative Considered:**
- Environment variable: Adds complexity to test setup without security benefit
- Generated per test: Would break test fixture determinism
- Mock: Already using mocks for actual API calls; this is just the fixture data

**Risk Assessment:**
Zero security risk. This is public test data by design. Even if leaked, can only interact with Stripe test mode which has no real monetary value.

**Request:**
Override approval for Stripe test publishable keys (pk_test_*) in test fixtures. Consider adding pattern to allow test publishable keys globally.
```

### Security Team Response

```markdown
**SECURITY TEAM REVIEW COMPLETE**

**Decision:** APPROVED

**Analysis:**
Reviewed security check flagging Stripe test publishable key. Confirmed this is a false positive:

1. ✅ Key type is `pk_test_*` (publishable, test mode)
2. ✅ Stripe documentation confirms publishable keys are safe to commit
3. ✅ Located in test fixtures directory, not production code
4. ✅ Test mode keys have no access to production data or real charges
5. ✅ Rate-limited by Stripe, cannot be abused

**Recommendation:**
Approve override for this specific instance. Additionally, updating security check to allow pattern:
- `pk_test_*` in `tests/**` directories
- Reduces false positives while maintaining security for genuine secret keys (`sk_*`)

@coderabbitai ignore hardcoded-credentials --reason "SECURITY TEAM APPROVED: Stripe test publishable key (pk_test_*) in test fixtures. False positive confirmed - publishable keys are safe to commit per Stripe documentation. No security risk. Approved by @security-team-member"

**Follow-up Action:**
Created ticket SEC-123 to refine hardcoded-credentials check to exclude test publishable keys in test directories.

**Approval Timestamp:** 2025-10-14 15:45 PST
**Reviewer:** @security-team-member
```

### Response Time SLA

**Business Hours:**
- **Target:** 4 hours
- **Maximum:** 8 hours (1 business day)

**After Hours:**
- Next business day
- For production incidents, escalate to Level 4 (Emergency)

---

## Level 4: Emergency Override

### Applicable Situations

**Production Incidents Only:**
- System outage affecting customers
- Data integrity issue requiring immediate fix
- Security vulnerability exploitation in progress
- Critical bug causing revenue loss

**NOT for:**
- Feature deadlines (use Level 2)
- Demo pressure (use Level 2)
- "Urgent" without customer impact
- Developer convenience

### Process

**Timeframe:** Immediate (incident response SLA applies)

**Steps:**

1. **Declare Incident**
   - Use on-call process to declare incident
   - Create incident ticket (INCIDENT-XXX)
   - Notify incident commander

2. **Create Hotfix PR**
   - Prefix PR title with `[INCIDENT-XXX]`
   - Include incident ticket link in description
   - Tag as `priority:critical`

3. **Request Emergency Override**
   - Mention `@kellerai/admins` in PR comment
   - Reference incident ticket
   - Describe urgency and customer impact

4. **Admin Grants Override**
   - Admin provides blanket override for all checks
   - Override references incident ticket
   - Post-incident review required

5. **Merge Immediately**
   - Deploy hotfix to production
   - Monitor for stability
   - Continue incident resolution

6. **Post-Incident Review (Within 24 hours)**
   - Review what checks failed
   - Assess if failures were genuine issues
   - Create follow-up tickets for proper fixes
   - Document in incident report

### Emergency Override Template

```markdown
🚨 **EMERGENCY OVERRIDE REQUEST** 🚨

**Incident:** INCIDENT-<number>
**Severity:** <SEV-1/SEV-2>
**Impact:** <Customer impact description>
**PR:** #<number> - [INCIDENT-XXX] <title>

**Situation:**
<Brief description of production issue>

**Customer Impact:**
- Affected users: <number/percentage>
- Business impact: <revenue loss, SLA breach, etc.>
- Duration: <how long has this been ongoing>

**Hotfix Description:**
<What does this PR fix>

**Quality Gate Failures:**
<List of check failures - will be addressed in post-incident>

**Justification for Emergency Override:**
<Why can't we wait to fix quality issues properly>

**Post-Incident Commitment:**
- Post-incident review scheduled: <date/time>
- Follow-up tickets will be created for quality issues
- Proper fixes will be implemented: <timeline>

@kellerai/admins - Emergency override requested for production incident INCIDENT-<number>
```

### Admin Emergency Override

```markdown
**🚨 EMERGENCY OVERRIDE GRANTED 🚨**

**Incident:** INCIDENT-789
**Severity:** SEV-1 (Production Outage)
**Authorized By:** @admin-name
**Timestamp:** 2025-10-14 02:15 PST

**Authorization:**
Emergency override approved for production incident. All quality gate checks temporarily bypassed for this critical hotfix.

@coderabbitai ignore all-checks --reason "EMERGENCY OVERRIDE - INCIDENT-789: Production outage affecting 80% of users. Payment processing down. Customer impact: ~$50K/hour revenue loss. Quality gate checks bypassed for immediate hotfix deployment. POST-INCIDENT REVIEW REQUIRED within 24 hours. Follow-up tickets will be created for any genuine quality issues. Authorized by @admin-name at 2025-10-14 02:15 PST."

**Required Follow-up:**
1. ✅ Deploy hotfix immediately
2. ⏳ Post-incident review scheduled: 2025-10-15 10:00am PST
3. ⏳ Create follow-up tickets for quality gate failures
4. ⏳ Document in incident report: INCIDENT-789
5. ⏳ Notify engineering leadership of override usage

**Merge authorized - deploy immediately**
```

### Post-Incident Review Process

**Within 24 Hours of Incident Resolution:**

1. **Review Quality Gate Failures**
   - List all checks that failed
   - Categorize: genuine issues vs false positives
   - Assess security implications

2. **Create Follow-up Tickets**
   - For each genuine quality issue
   - Prioritize based on severity
   - Assign to appropriate team members

3. **Document in Incident Report**
   - Why emergency override was necessary
   - What quality checks failed
   - Follow-up remediation plan
   - Lessons learned

4. **Update Runbooks**
   - If incident type could recur
   - Add to troubleshooting guides
   - Update monitoring/alerts

### Emergency Override Audit

**Logged to:**
- Incident tracking system
- Quality gate audit trail
- Engineering leadership reports

**Reviewed:**
- Quarterly by engineering leadership
- Patterns indicating need for runbook updates
- Patterns indicating need for better monitoring

---

## Notification Templates

### Level 2: Tech Lead Escalation Notification

**Sent to:** @kellerai/tech-leads (Slack, GitHub notification)

```
🔔 Tech Lead Override Request

PR #456: feat(orders): add expedited shipping option
Requested by: @developer-name
Check failed: layer-separation

Business justification:
Enterprise customer demo (Acme Corp - $2M ARR) - deadline Friday

Action required: Review and approve/reject within 4 hours
Link: [View PR](#) | [Review Request](#)
```

### Level 3: Security Team Escalation Notification

**Sent to:** @kellerai/security-team (Slack, PagerDuty)

```
🔒 Security Override Review Requested

PR #789: fix(api): update authentication endpoint
Requested by: @developer-name
Check failed: hardcoded-credentials (CRITICAL)

Claimed false positive: Stripe test publishable key in fixtures

Action required: Security review within 8 business hours
Link: [View PR](#) | [Security Analysis](#)
Priority: High
```

### Level 4: Emergency Override Notification

**Sent to:** @kellerai/admins, @kellerai/engineering-leadership (PagerDuty, Slack, SMS)

```
🚨 EMERGENCY OVERRIDE REQUESTED 🚨

Incident: INCIDENT-789 (SEV-1)
PR #1234: [INCIDENT-789] hotfix: restore payment processing
Requested by: @on-call-engineer

Customer Impact:
- 80% of users affected
- Payment processing down
- Revenue loss: ~$50K/hour

Action required: IMMEDIATE admin override approval
Link: [View PR](#) | [Incident Details](#)
```

---

## Response Time SLAs

### Summary Table

| Level | Check Type | Target Response | Max Response | Escalation Path |
|-------|-----------|----------------|--------------|-----------------|
| 1 | Self-Service | Immediate | N/A | N/A |
| 2 | Tech Lead | 2 hours | 4 hours | Engineering Leadership |
| 3 | Security Team | 4 hours | 8 hours | Security Leadership |
| 4 | Emergency | Immediate | 15 minutes | CTO/VP Engineering |

### Business Hours

**Defined as:** 9:00am - 6:00pm Pacific Time, Monday-Friday (excluding holidays)

**SLA Application:**
- Level 2: 4-hour SLA applies during business hours
- Level 3: 8-hour SLA applies during business hours
- After hours: Next business day (unless emergency)

### After Hours / Weekends

**Process:**
1. If truly urgent, escalate to Level 4 (Emergency)
2. Otherwise, wait for next business day
3. For time-sensitive business needs, provide advance notice to tech leads

---

## Audit and Compliance

### Override Logging

**All overrides logged to:** `.coderabbit-overrides.log`

**Log Entry Format:**
```json
{
  "timestamp": "2025-10-14T14:30:00Z",
  "level": 2,
  "check_name": "layer-separation",
  "pr_number": 456,
  "pr_title": "feat(orders): add expedited shipping option",
  "requested_by": "developer-name",
  "requested_at": "2025-10-14T14:15:00Z",
  "approved_by": "tech-lead-name",
  "approved_at": "2025-10-14T14:30:00Z",
  "approval_duration": "PT15M",
  "justification": "TECH LEAD APPROVED: Temporary direct database call...",
  "business_justification": "Acme Corp $2M contract renewal demo",
  "remediation_ticket": "TECH-790",
  "incident_reference": null
}
```

**Timestamp Field Specifications:**
- `requested_at`: ISO 8601 UTC timestamp when override was initially requested
- `approved_at`: ISO 8601 UTC timestamp when override was approved
- `approval_duration`: ISO 8601 duration format (e.g., "PT15M" = 15 minutes, "PT2H30M" = 2.5 hours)
- All timestamps must use UTC timezone (Z suffix) for consistency

### Weekly Override Report

**Recipients:** Engineering leadership, tech leads  
**Frequency:** Monday mornings

**Contents:**
- Total overrides by level (L1, L2, L3, L4)
- Override trends (increasing/decreasing)
- Most frequently overridden checks
- Emergency override usage (should be rare)
- Recommendations for pattern refinement

### Quarterly Security Review

**Process:**
1. Security team reviews all Level 3 overrides
2. Identify patterns in false positives
3. Propose check refinements to reduce false positives
4. Update security standards based on learnings
5. Report to security steering committee

### Annual Escalation Analysis

**Purpose:** Optimize escalation workflows

**Analysis:**
- Response time adherence to SLAs
- Escalation volume trends
- Developer satisfaction with process
- Bottlenecks and improvement opportunities

---

## Summary

This escalation framework provides:

✅ **Clear escalation paths** for different types of quality gate failures  
✅ **Defined response time SLAs** for each escalation level  
✅ **Structured templates** for escalation requests and approvals  
✅ **Audit trail** for compliance and pattern analysis  
✅ **Balance** between code quality and business agility  
✅ **Emergency procedures** for production incidents  

**Key Principles:**
- Self-service for common cases (reduce friction)
- Expert review for complex cases (maintain quality)
- Emergency path for incidents (support business continuity)
- Complete audit trail (enable compliance and learning)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Platform Engineering  
**Status:** Active
