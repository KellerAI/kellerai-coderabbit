# Request Changes Workflow - Quality Gate Enforcement

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Configuration and usage guide for automated PR blocking via CodeRabbit request changes workflow

---

## Overview

The Request Changes Workflow automatically blocks PR merges when critical quality gate failures are detected. This enforcement mechanism integrates CodeRabbit reviews with GitHub status checks to prevent non-compliant code from reaching production.

**Key Features:**
- ✅ Automated PR blocking for critical failures (security, breaking changes)
- ✅ GitHub status check integration for merge prevention
- ✅ Clear remediation guidance in PR comments
- ✅ Override mechanism with justification requirements
- ✅ Automatic retry for transient failures
- ✅ Team notification and escalation procedures

---

## Table of Contents

1. [How It Works](#how-it-works)
2. [GitHub Status Check Integration](#github-status-check-integration)
3. [Critical vs Warning Mode Checks](#critical-vs-warning-mode-checks)
4. [Automatic Retry Mechanism](#automatic-retry-mechanism)
5. [Developer Workflow](#developer-workflow)
6. [Override Process](#override-process)
7. [Escalation Procedures](#escalation-procedures)
8. [Branch Protection Setup](#branch-protection-setup)
9. [Monitoring and Compliance](#monitoring-and-compliance)
10. [Troubleshooting](#troubleshooting)

---

## How It Works

### Workflow Sequence

```
1. Developer creates/updates PR
   ↓
2. CodeRabbit analyzes code changes
   ↓
3. Quality checks execute (error mode for critical checks)
   ↓
4. If CRITICAL failure detected:
   ├─→ CodeRabbit posts "Request Changes" review
   ├─→ GitHub status check set to "failure"
   ├─→ Merge button blocked
   ├─→ Notification posted with remediation guidance
   └─→ Developer must fix or request override
   ↓
5. Developer fixes issue and pushes
   ↓
6. CodeRabbit re-evaluates automatically
   ↓
7. If checks pass:
   ├─→ CodeRabbit approves PR
   ├─→ GitHub status check set to "success"
   └─→ Merge button enabled
```

### Configuration

**File:** `.coderabbit.yaml`

```yaml
reviews:
  # ENABLED: Request changes workflow blocks PRs with critical failures
  request_changes_workflow: true

quality_checks:
  # ENFORCED: Error mode blocks merge via GitHub status checks
  mode: error
  
  # Critical checks (always error mode)
  custom_checks:
    security:
      enabled: true
      mode: error  # Blocks merge
      retry_on_transient_failure: true
      max_retries: 3
    
    breaking_changes:
      enabled: true
      mode: error  # Blocks merge
      retry_on_transient_failure: true
      max_retries: 3
```

---

## GitHub Status Check Integration

### Status Check Context

**Name:** `CodeRabbit Quality Gates`

**States:**
- ✅ **success**: All quality gates passed
- ❌ **failure**: One or more critical failures detected
- ⏳ **pending**: Checks in progress

### GitHub Actions Workflow

**File:** `.github/workflows/quality-gate-status.yml`

**Triggers:**
- PR opened
- PR synchronized (new commits pushed)
- PR reopened
- CodeRabbit review submitted

**Jobs:**
1. **quality-gate-enforcement**: Runs quality checks and creates status
2. **check-coderabbit-approval**: Verifies CodeRabbit review state

**Artifacts:**
- Quality check results (JSON)
- Detailed failure reports
- Retention: 30 days

### Integration with Branch Protection

The GitHub status check can be added to branch protection rules to enforce quality gates at the repository level.

**Setup:**
1. Go to repository Settings → Branches
2. Edit branch protection rule for `main`
3. Enable "Require status checks to pass before merging"
4. Add required status check: `CodeRabbit Quality Gates`
5. Enable "Require branches to be up to date before merging"

---

## Critical vs Warning Mode Checks

### Error Mode (Blocks Merge)

**When Used:**
- Security vulnerabilities (hardcoded credentials, SQL injection, etc.)
- Breaking changes without documentation
- PR title format violations

**Behavior:**
- ❌ CodeRabbit requests changes
- ❌ GitHub status check fails
- ❌ Merge button disabled
- 📧 Team notification sent

**Checks in Error Mode:**
```yaml
- hardcoded-credentials (CRITICAL)
- sql-injection (CRITICAL)
- sensitive-data-logging (HIGH)
- unsafe-deserialization (CRITICAL)
- api-signature-changes (HIGH)
- removed-public-methods (CRITICAL)
- pr-title-format (ENFORCED)
```

### Warning Mode (Allows Merge)

**When Used:**
- Architecture suggestions
- Performance recommendations
- Documentation completeness
- Code organization

**Behavior:**
- ⚠️ CodeRabbit posts review comments
- ✅ GitHub status check passes (with warnings)
- ✅ Merge button enabled
- 📊 Warnings logged for metrics

**Checks in Warning Mode:**
```yaml
- docstring-coverage (85% threshold)
- layer-separation (architectural)
- dependency-injection (pattern enforcement)
- async-patterns (best practice)
- n-plus-one (performance)
- database-indexes (optimization)
- algorithm-complexity (efficiency)
```

---

## Automatic Retry Mechanism

### Transient Failure Handling

**Purpose:** Prevent false positives from temporary issues (network errors, API rate limits, service outages)

**Configuration:**
```yaml
custom_checks:
  security:
    retry_on_transient_failure: true
    max_retries: 3
    retry_delay_seconds: 5
    backoff_multiplier: 2  # Exponential backoff
```

**Retry Logic:**
1. Initial check fails with transient error (network timeout, 5xx error)
2. Wait 5 seconds
3. Retry attempt 1
4. If fails, wait 10 seconds (backoff)
5. Retry attempt 2
6. If fails, wait 20 seconds (backoff)
7. Retry attempt 3
8. If still fails, report as genuine failure

**Transient Error Types:**
- Network timeouts
- HTTP 5xx errors (server issues)
- API rate limit errors (429)
- Temporary service unavailability

**Non-Transient Errors (No Retry):**
- Code quality violations
- Security vulnerabilities
- Breaking changes

---

## Developer Workflow

### When PR is Blocked

**Step 1: Review Failure Details**

Check the PR for:
- ❌ "Changes requested" review from CodeRabbit
- ❌ Failed "CodeRabbit Quality Gates" status check
- 📝 Detailed comment with remediation guidance

**Example Comment:**
```markdown
## ⚠️ Quality Gate Failure - Merge Blocked

This PR has been blocked due to 2 critical quality gate failure(s).

### Failed Checks
- **hardcoded-credentials** (critical): Hardcoded API key detected in config.py:42
- **sql-injection** (critical): Potential SQL injection in user_service.py:156

### Next Steps
1. Review failed checks above
2. Fix issues according to remediation guidance
3. Push changes (CodeRabbit will automatically re-evaluate)
4. Request override if false positive (see below)
```

**Step 2: Fix Issues**

Address each failure:

```python
# ❌ BEFORE (hardcoded credential)
API_KEY = "sk_live_abc123xyz"

# ✅ AFTER (environment variable)
import os
API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise ValueError("API_KEY environment variable not set")
```

```python
# ❌ BEFORE (SQL injection)
query = f"SELECT * FROM users WHERE email = '{email}'"
cursor.execute(query)

# ✅ AFTER (parameterized query)
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))
```

**Step 3: Push Fixes**

```bash
git add .
git commit -m "fix: address quality gate failures"
git push
```

**Step 4: Automatic Re-evaluation**

- CodeRabbit automatically re-runs checks on new commits
- GitHub Actions workflow re-executes
- If checks pass:
  - ✅ Status check updates to "success"
  - ✅ Merge button enabled
  - ✅ CodeRabbit approves PR

---

## Override Process

### When to Use Overrides

**Valid Reasons:**
- False positive detection
- Test data or fixtures (not production code)
- Legacy code with documented exceptions
- Approved architectural deviation

**Invalid Reasons:**
- "I don't have time to fix this"
- "It works on my machine"
- "We'll fix it later"
- No justification provided

### Override Command Syntax

**Format:**
```
@coderabbitai ignore <check-name> --reason "Detailed justification (minimum 50 characters)"
```

**Examples:**

✅ **Good Override:**
```
@coderabbitai ignore hardcoded-credentials --reason "Public test API key from Stripe documentation used exclusively in test fixtures. Not a security risk as it's rate-limited and cannot access production data."
```

❌ **Bad Override:**
```
@coderabbitai ignore hardcoded-credentials --reason "It's fine"
```
(Rejected: Justification too short and lacks detail)

### Available Override Checks

**Architectural Checks** (Tech lead approval recommended):
- `layer-separation`
- `dependency-injection`
- `async-patterns`

**Testing Checks** (Tech lead approval recommended):
- `new-functions-tests`
- `bug-fix-regression`

**Performance Checks** (Context-dependent):
- `n-plus-one`
- `database-indexes`
- `algorithm-complexity`

**Documentation Checks**:
- `docstring-coverage`

### Non-Overridable Checks

**Always Enforced (No Override Allowed):**
- ❌ `hardcoded-credentials`
- ❌ `sql-injection`
- ❌ `sensitive-data-logging`
- ❌ `unsafe-deserialization`
- ❌ `api-signature-changes` (must update CHANGELOG)
- ❌ `removed-public-methods` (must update CHANGELOG)
- ❌ `pr-title-format`

**Rationale:** Critical security and compliance requirements

### Elevated Permission Overrides

**Security Checks** require elevated permissions:

**Authorized Roles:**
- @kellerai/security-team
- @kellerai/admins

**Process:**
1. Developer identifies false positive security check
2. Developer comments explaining issue
3. Developer mentions `@kellerai/security-team` for review
4. Security team member reviews and provides override if appropriate
5. Override logged to audit trail

---

## Escalation Procedures

### Level 1: Standard Override (Self-Service)

**Timeframe:** Immediate  
**Applies to:** Non-critical checks (architecture, testing, performance)

**Process:**
1. Developer posts override command with 50+ character justification
2. CodeRabbit processes override
3. Check marked as `[IGNORED]` in review
4. PR can proceed to merge
5. Override logged for compliance tracking

### Level 2: Tech Lead Approval

**Timeframe:** Same day (4-hour SLA)  
**Applies to:** Architectural deviations, test coverage exceptions

**Process:**
1. Developer mentions `@kellerai/tech-leads` in comment
2. Developer explains business justification (why urgent, impact of delay)
3. Tech lead reviews within 4 hours
4. If approved:
   - Tech lead comments: `@coderabbitai ignore <check> --reason "<tech lead justification>"`
   - Override logged with tech lead as authorizer
5. If rejected:
   - Tech lead provides guidance on proper fix
   - Developer implements fix and pushes

**Example:**
```markdown
@kellerai/tech-leads - Need override approval for `layer-separation` check.

**Business Justification:**
Customer demo scheduled for tomorrow morning. This is a temporary direct database call 
in the controller to work around a critical bug in the repository layer. 

**Remediation Plan:**
- Ticket TECH-456 created to properly refactor to repository pattern
- Scheduled for next sprint (sprint 24)
- Temporary code marked with TODO comment and ticket reference

**Risk Assessment:**
Low risk - only affects admin panel used by internal team, not customer-facing API.
```

### Level 3: Security Team Review

**Timeframe:** 1 business day  
**Applies to:** Security check overrides only

**Process:**
1. Developer mentions `@kellerai/security-team` with detailed analysis
2. Developer must provide:
   - Exact code in question
   - Why check flagged it
   - Why it's not a genuine security issue
   - Supporting evidence (documentation, vendor guidelines)
3. Security team reviews:
   - Code context
   - Risk assessment
   - Alternative solutions
4. Security team decision:
   - **Approved:** Override granted with security team justification
   - **Alternative Required:** Guidance on secure implementation
   - **Rejected:** Code must be changed

**Example:**
```markdown
@kellerai/security-team - Security check false positive review request

**Check:** hardcoded-credentials  
**File:** `tests/fixtures/payment_fixtures.py:23`  
**Code:**
```python
STRIPE_TEST_KEY = "pk_test_123abc"  # Stripe test publishable key
```

**Analysis:**
This is a Stripe test publishable key (pk_test_*) from their official documentation.
- NOT a secret key (would be sk_test_*)
- Only works in test mode (cannot charge real cards)
- Public by design (safe to commit, per Stripe docs)
- Used exclusively in test fixtures

**Evidence:**
Stripe documentation: https://stripe.com/docs/keys#test-live-modes
"Publishable keys are meant to be public and can be safely included in client-side code."

**Risk Assessment:** Zero risk - this is a public test key by design.

**Request:** Override approval for this specific test key instance.
```

### Level 4: Emergency Override

**Timeframe:** Immediate (with post-incident review)  
**Applies to:** Production incidents, critical hotfixes

**Process:**
1. **Incident declared** via on-call process
2. Developer creates hotfix PR with `[INCIDENT]` prefix
3. Developer mentions `@kellerai/admins` for emergency override
4. Admin provides blanket override:
   ```
   @coderabbitai ignore all-checks --reason "INCIDENT-789: Production outage. Quality gates temporarily bypassed for emergency hotfix. Post-incident review required."
   ```
5. PR merged immediately
6. **Post-incident review** (within 24 hours):
   - Review what checks failed
   - Assess if failures are genuine issues
   - Create follow-up tickets for proper fixes
   - Update incident report

**Audit Requirements:**
- Incident ticket number required
- Post-incident review documented
- Follow-up remediation tickets created
- Logged in incident tracking system

---

## Branch Protection Setup

### Recommended Configuration

**GitHub Repository Settings → Branches → main**

```yaml
Branch Protection Rules:
  ✅ Require a pull request before merging
  ✅ Require approvals: 1
  ✅ Dismiss stale pull request approvals when new commits are pushed
  ✅ Require review from Code Owners
  
  ✅ Require status checks to pass before merging
    Required status checks:
      - CodeRabbit Quality Gates
      - quality-gate-enforcement
      - check-coderabbit-approval
  
  ✅ Require branches to be up to date before merging
  ✅ Require conversation resolution before merging
  
  ✅ Include administrators (optional: disable for emergency overrides)
  
  ❌ Allow force pushes (disabled)
  ❌ Allow deletions (disabled)
```

### Status Check Requirements

**Required Status Checks:**

1. **CodeRabbit Quality Gates** (Status API)
   - Created by GitHub Actions workflow
   - Context: `CodeRabbit Quality Gates`
   - Reports: Pass/Fail from quality checks

2. **quality-gate-enforcement** (Job)
   - GitHub Actions job
   - Runs actual quality validation
   - Fails if critical issues detected

3. **check-coderabbit-approval** (Job)
   - GitHub Actions job
   - Verifies CodeRabbit review state
   - Fails if "Changes Requested"

### Testing Branch Protection

**Validation Steps:**

1. Create test PR with security issue
2. Verify status checks run
3. Confirm merge button disabled
4. Fix issue and push
5. Verify status checks re-run
6. Confirm merge button enabled

---

## Monitoring and Compliance

### Metrics Tracked

**Quality Gate Compliance:**
- Pass rate per check type
- Failure rate trends
- Override frequency by check
- Time to resolution

**Workflow Performance:**
- Average check execution time
- Retry frequency (transient failures)
- False positive rate
- Developer feedback

**Audit Metrics:**
- Override usage by role
- Emergency override frequency
- Post-incident review completion
- Escalation response times

### Compliance Dashboard

**Location:** (Future: Grafana dashboard)

**Panels:**
1. Quality gate pass/fail rates (7-day trend)
2. Top failing checks
3. Override frequency by check type
4. Escalation volume and response times
5. PR merge time impact (before/after quality gates)

### Weekly Compliance Report

**Recipients:** Engineering leadership, tech leads  
**Frequency:** Monday mornings  
**Contents:**
- Total PRs analyzed
- Quality gate pass rate
- Top 5 failing checks
- Override usage summary
- Escalations requiring attention
- Recommendations for pattern refinement

---

## Troubleshooting

### Issue: PR Blocked But Checks Show Passing

**Symptoms:**
- CodeRabbit requested changes
- GitHub status check shows "success"
- Merge still blocked

**Cause:** CodeRabbit review takes precedence over status check

**Resolution:**
1. Check CodeRabbit review details
2. Address any comments or requested changes
3. If review is stale, trigger re-review:
   ```
   @coderabbitai review
   ```

### Issue: Status Check Stuck in "Pending"

**Symptoms:**
- Quality gate status shows "pending" indefinitely
- GitHub Actions workflow not running

**Cause:** Workflow trigger conditions not met or GitHub Actions quota exceeded

**Resolution:**
1. Check GitHub Actions tab for workflow status
2. Re-trigger workflow:
   - Close and reopen PR, OR
   - Push new commit
3. If quota exceeded, contact DevOps for quota increase

### Issue: False Positive Security Check

**Symptoms:**
- Security check flags test data or documented pattern
- Developer believes it's safe

**Process:**
1. Do NOT override security checks directly
2. Mention `@kellerai/security-team` with detailed analysis
3. Provide context and evidence (documentation, vendor guidelines)
4. Wait for security team review and approval
5. Security team will provide override if appropriate

### Issue: Check Fails Intermittently

**Symptoms:**
- Quality check passes sometimes, fails others
- No code changes between runs

**Cause:** Likely transient failure (network, API rate limit)

**Resolution:**
1. Check if automatic retry is enabled:
   ```yaml
   retry_on_transient_failure: true
   max_retries: 3
   ```
2. Review GitHub Actions logs for specific error
3. If persistent, report to DevOps:
   - Include workflow run URL
   - Describe failure pattern
   - Attach logs

### Issue: Emergency Hotfix Blocked

**Symptoms:**
- Production incident requires immediate merge
- Quality gates blocking hotfix PR

**Process:**
1. Declare incident via on-call process
2. Prefix PR with `[INCIDENT-XXX]`
3. Mention `@kellerai/admins` for emergency override
4. Admin provides blanket override with incident reference
5. Merge immediately
6. Schedule post-incident review (within 24 hours)
7. Create follow-up tickets for proper fixes

### Issue: Override Not Working

**Symptoms:**
- Posted override command
- CodeRabbit didn't respond or reject override

**Common Causes:**
1. **Justification too short** (< 50 characters)
2. **Check name incorrect** (typo or wrong format)
3. **Check not available for override** (security check)
4. **Insufficient permissions** (elevated check requires admin)

**Resolution:**
1. Verify override syntax:
   ```
   @coderabbitai ignore <check-name> --reason "Justification 50+ chars"
   ```
2. Check available override list in documentation
3. For security checks, mention `@kellerai/security-team`
4. Ensure justification is substantive (not "it's fine")

---

## Summary

The Request Changes Workflow provides:

✅ **Automated PR blocking** for critical quality failures  
✅ **GitHub status check integration** for merge enforcement  
✅ **Clear remediation guidance** in PR comments  
✅ **Flexible override mechanism** with role-based permissions  
✅ **Automatic retry** for transient failures  
✅ **Escalation procedures** for urgent cases  
✅ **Audit trail** for compliance tracking  
✅ **Branch protection integration** for repository-level enforcement  

**Next Steps:**
1. Review branch protection configuration
2. Test workflow with sample PRs
3. Train team on override process
4. Monitor compliance metrics
5. Refine patterns based on feedback

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Platform Engineering  
**Status:** Active
