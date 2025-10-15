# Quality Gate Override Process Guide

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Complete guide for using @coderabbitai ignore command and override justification requirements

---

## Overview

The quality gate override system allows developers to bypass specific check failures when there is valid justification. This guide covers the complete override process, from command syntax to audit requirements.

**Key Principles:**
- 🔒 Security checks require elevated permissions
- 📝 All overrides require 50+ character justification
- 📊 All overrides are logged for compliance tracking
- ✅ Self-service for non-critical checks
- 🚨 Never override without valid reason

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Command Syntax](#command-syntax)
3. [Available Override Checks](#available-override-checks)
4. [Justification Requirements](#justification-requirements)
5. [Override Examples](#override-examples)
6. [Role-Based Permissions](#role-based-permissions)
7. [Audit Trail](#audit-trail)
8. [Common Scenarios](#common-scenarios)

---

## Quick Reference

### Basic Override Command

```
@coderabbitai ignore <check-name> --reason "Detailed justification (minimum 50 characters explaining why this override is necessary)"
```

### Check Categories

| Category | Self-Service | Requires Approval | Never Override |
|----------|-------------|-------------------|----------------|
| Architecture | ✅ Yes | Recommended | - |
| Testing | ✅ Yes | Recommended | - |
| Performance | ✅ Yes | Context-dependent | - |
| Documentation | ✅ Yes | Optional | - |
| Security | ❌ No | @kellerai/security-team | ⚠️ Critical only |
| Breaking Changes | ❌ No | Must update CHANGELOG | ❌ Always enforced |

---

## Command Syntax

### Full Command Format

```
@coderabbitai ignore <check-name> --reason "<justification>"
```

**Components:**

1. **@coderabbitai** - Triggers CodeRabbit bot
2. **ignore** - Override command keyword
3. **<check-name>** - Specific check to override (kebab-case)
4. **--reason** - Flag for justification (required)
5. **"<justification>"** - Explanation text (50+ chars)

### Command Variants

**Single Check Override:**
```
@coderabbitai ignore layer-separation --reason "Temporary direct database call for hotfix TECH-456. Proper repository pattern implementation scheduled for Sprint 24 (ticket TECH-457). Risk is low as this only affects internal admin panel."
```

**Multiple Check Override (NOT SUPPORTED):**
```
❌ @coderabbitai ignore layer-separation,dependency-injection
```
Each check requires separate override command.

**Emergency Override (Admins Only):**
```
@coderabbitai ignore all-checks --reason "INCIDENT-789: Production outage. Emergency hotfix deployment. Post-incident review scheduled for 2025-10-15. Authorized by @admin-name."
```

---

## Available Override Checks

### Architectural Checks (Self-Service)

**layer-separation**
- **Description:** Enforces layered architecture (Controller → Service → Repository → Model)
- **Common Reason:** Temporary workaround for repository layer bug
- **Example Justification:** "Direct database call in controller to bypass caching bug TECH-789 in repository layer. Scheduled for proper fix in Sprint 24 (TECH-790). Low risk - internal admin only."

**dependency-injection**
- **Description:** Requires use of FastAPI Depends() for dependencies
- **Common Reason:** Legacy integration compatibility
- **Example Justification:** "Third-party library requires direct instantiation without DI framework. Documented in ARCHITECTURE.md section 4.2. Alternative solutions evaluated in TECH-456."

**async-patterns**
- **Description:** Enforces async/await for I/O operations
- **Common Reason:** Synchronous library requirement
- **Example Justification:** "External library (legacy-api-client) does not support async. Wrapped in thread pool executor as documented in service layer. Performance impact minimal (<10ms)."

### Testing Checks (Self-Service)

**new-functions-tests**
- **Description:** Requires tests for new functions
- **Common Reason:** Integration test coverage deferred
- **Example Justification:** "Unit tests provided for core logic. Integration tests deferred to Sprint 24 due to test environment setup dependency on INFRA-123. Covered by manual QA checklist."

**bug-fix-regression**
- **Description:** Requires regression tests for bug fixes
- **Common Reason:** Bug non-reproducible in test environment
- **Example Justification:** "Bug only reproduces in production with specific data set that cannot be replicated in test. Manual regression test procedure documented in TESTING.md. Monitoring added via DATADOG-456."

### Performance Checks (Self-Service)

**n-plus-one**
- **Description:** Detects N+1 query patterns
- **Common Reason:** Small dataset with acceptable performance
- **Example Justification:** "Admin panel with max 50 users. Query runs <100ms with current data volume. Optimization ticket PERF-789 created for when user count exceeds 100. Monitoring in place."

**database-indexes**
- **Description:** Requires indexes on foreign keys
- **Common Reason:** Index scheduled for next release
- **Example Justification:** "Index creation requires downtime. Scheduled for next maintenance window (2025-10-20). Current query volume low (<10 qps). Performance impact minimal until then."

**algorithm-complexity**
- **Description:** Flags inefficient algorithms (O(n²) or worse)
- **Common Reason:** Small dataset makes optimization unnecessary
- **Example Justification:** "Nested loop operates on admin-configured rules (max 10 items). Performance <5ms with current data. Optimization not justified for admin-only feature with low usage."

### Documentation Checks (Self-Service)

**docstring-coverage**
- **Description:** Requires 85% docstring coverage
- **Common Reason:** Private/internal functions
- **Example Justification:** "Internal helper functions in _utils.py module. Not part of public API. Covered by comprehensive tests. Documentation focus is on public API (currently at 95% coverage)."

### Security Checks (Elevated Permissions Required)

**hardcoded-credentials**
- **Description:** Detects hardcoded API keys, passwords, tokens
- **Requires:** @kellerai/security-team approval
- **Example Justification:** "Stripe test publishable key (pk_test_*) from official documentation. Test mode only, cannot charge real cards. Safe to commit per Stripe security guidelines. Used exclusively in test fixtures."

**sql-injection**
- **Description:** Detects SQL injection vulnerabilities
- **Requires:** @kellerai/security-team approval
- **Example Justification:** "Dynamic table name from ENUM type with explicit whitelist validation. Input validated against [\\'users\\', \\'orders\\', \\'products\\'] enum. SQL injection not possible with enum constraint."

**sensitive-data-logging**
- **Description:** Detects logging of sensitive information
- **Requires:** @kellerai/security-team approval
- **Example Justification:** "Log statement redacts actual password value. Variable name contains 'password' but logs '[REDACTED]' placeholder. False positive from variable name pattern matching."

**unsafe-deserialization**
- **Description:** Detects unsafe pickle/eval usage
- **Requires:** @kellerai/security-team approval
- **Example Justification:** "pickle.loads() on data from internal microservice with mutual TLS authentication. Data signed with HMAC-SHA256. Safe in this controlled environment. Alternatives evaluated in SEC-456."

### Non-Overridable Checks

**pr-title-format**
- **Enforcement:** Always enforced
- **Reason:** Required for automated changelog generation
- **Solution:** Fix PR title to match: `type(scope): description`

**api-signature-changes**
- **Enforcement:** Always enforced
- **Reason:** Must document breaking changes in CHANGELOG
- **Solution:** Update CHANGELOG.md with version bump and migration guide

**removed-public-methods**
- **Enforcement:** Always enforced
- **Reason:** Critical breaking change requiring documentation
- **Solution:** Add "BREAKING CHANGES" section to CHANGELOG.md

---

## Justification Requirements

### Minimum Requirements

All override justifications must include:

1. ✅ **Minimum 50 characters** (substantive explanation)
2. ✅ **Why override is necessary** (context and reasoning)
3. ✅ **Mitigation or remediation plan** (if temporary)
4. ✅ **Risk assessment** (impact if issue is genuine)
5. ✅ **Ticket reference** (for tracking follow-up)

### Good Justification Template

```
@coderabbitai ignore <check-name> --reason "[Context: Why situation exists] [Justification: Why override is acceptable] [Mitigation: How risk is managed] [Timeline: When proper fix will be implemented] [Reference: Ticket ID for tracking]"
```

### Examples: Good vs Bad

**✅ GOOD:**
```
@coderabbitai ignore layer-separation --reason "Direct database query in controller bypasses repository caching bug (TECH-789). Scheduled for proper fix in Sprint 24 (TECH-790 created). Risk is LOW - only affects internal admin panel, not customer-facing API. Temporary workaround includes explicit transaction handling for safety."
```
**Length:** 267 characters  
**Contains:** Context, justification, mitigation, timeline, ticket reference  
**Risk assessment:** Clear ("LOW" with reasoning)

**❌ BAD:**
```
@coderabbitai ignore layer-separation --reason "Need to merge this quickly"
```
**Length:** 28 characters (too short)  
**Missing:** Context, justification, mitigation, timeline  
**No risk assessment**

**❌ BAD:**
```
@coderabbitai ignore layer-separation --reason "It's fine, trust me. I know what I'm doing here."
```
**Length:** 52 characters (meets minimum but not substantive)  
**Missing:** Actual justification, context, mitigation  
**No technical reasoning**

---

## Override Examples

### Example 1: Architecture Deviation (Self-Service)

**Scenario:** Direct database call needed to bypass repository layer bug

**Command:**
```markdown
@coderabbitai ignore layer-separation --reason "Temporary direct database call in OrderController.create_expedited_order() to bypass caching bug in OrderRepository (TECH-789). This is required for Acme Corp demo (Friday deadline, $2M contract renewal). Proper repository pattern fix scheduled for Sprint 24 (TECH-790). Risk: LOW - isolated to new expedited shipping feature, does not affect existing order processing. Includes explicit transaction handling and rollback on error."
```

**Result:** ✅ Override approved (self-service)

---

### Example 2: Test Coverage Exception (Tech Lead Approval)

**Scenario:** Integration tests deferred due to environment dependency

**Command:**
```markdown
@kellerai/tech-leads - Requesting tech lead approval for test coverage exception

**Business Context:**
Customer demo scheduled for Friday requires immediate merge of payment gateway integration. Integration test environment requires infrastructure changes (INFRA-123) with 2-week lead time.

**Technical Context:**
- Unit tests provided for all core payment logic (100% coverage)
- Integration tests blocked by missing test payment gateway sandbox
- Manual QA checklist created and executed successfully

**Risk Assessment:**
MEDIUM - Integration untested in automated suite, but mitigated by:
- Comprehensive unit test coverage
- Manual QA validation completed
- Monitoring alerts configured (DATADOG-456)
- Gradual rollout plan (5% → 25% → 100%)

**Remediation Plan:**
- Integration test environment: INFRA-123 (due Sprint 24)
- Integration tests: TECH-791 (blocked by INFRA-123)
- Target completion: End of Sprint 24

@coderabbitai ignore new-functions-tests --reason "TECH LEAD APPROVED: Integration tests deferred to Sprint 24 pending test environment setup (INFRA-123). Unit tests provide 100% coverage of payment logic. Manual QA completed. Gradual rollout with monitoring mitigates integration risk. Approved by @tech-lead-name on 2025-10-14."
```

**Result:** ✅ Override approved with tech lead authorization

---

### Example 3: Security False Positive (Security Team Review)

**Scenario:** Test API key flagged as hardcoded credential

**Command:**
```markdown
@kellerai/security-team - Security check false positive review request

**Check:** hardcoded-credentials (CRITICAL)
**File:** `tests/fixtures/stripe_fixtures.py:23`
**Flagged Code:**
```python
STRIPE_TEST_PUBLISHABLE_KEY = "pk_test_51Hqz..." # Stripe test publishable key
```

**Security Analysis:**
This is a Stripe test mode **publishable** key (pk_test_*), NOT a secret key. According to Stripe documentation, publishable keys are designed to be public and safe to commit.

**Evidence:**
1. Key type: `pk_test_*` indicates TEST PUBLISHABLE key
   - NOT `sk_test_*` (secret key) or `pk_live_*` (production)
2. Stripe Official Documentation: https://stripe.com/docs/keys
   > "Publishable API keys are meant to be publicly accessible in your web or mobile app's client-side code"
3. Test mode restrictions:
   - Cannot charge real credit cards
   - Rate-limited by Stripe
   - Only interacts with test data

**Context:**
- Location: Test fixtures directory (`tests/fixtures/`)
- Usage: Test data only, never in production code
- Purpose: Reproducible test fixtures for integration tests

**Risk Assessment:**
ZERO - Publishable test keys are public by design. Even if exposed, they:
- Cannot access production data
- Cannot charge real money
- Are rate-limited by Stripe
- Only work in test mode

**Request:**
Override approval for Stripe test publishable keys in test fixtures. Consider updating check pattern to exclude `pk_test_*` in `tests/**` directories to reduce false positives.

---

**SECURITY TEAM RESPONSE:**

**Decision:** APPROVED

**Review Summary:**
Analyzed hardcoded-credentials check flagging Stripe test publishable key. Confirmed this is a false positive:
1. ✅ Key type is pk_test_* (publishable, test mode)
2. ✅ Stripe documentation confirms public keys safe to commit
3. ✅ Located in test fixtures, not production code
4. ✅ Test mode keys cannot access real data or charge real cards
5. ✅ No security risk

**Recommendation:**
Approve override. Created SEC-123 to refine hardcoded-credentials pattern to exclude test publishable keys (pk_test_*, pk_dev_*) in test directories.

@coderabbitai ignore hardcoded-credentials --reason "SECURITY TEAM APPROVED: Stripe test publishable key (pk_test_*) in test fixtures is false positive. Publishable keys are safe to commit per Stripe documentation. Test mode keys cannot access production data. No security risk. Approved by @security-reviewer on 2025-10-14. Follow-up: SEC-123 to refine check pattern."

**Approval Timestamp:** 2025-10-14 15:30 PST  
**Reviewer:** @security-team-member
```

**Result:** ✅ Override approved with security team authorization

---

### Example 4: Emergency Incident (Admin Override)

**Scenario:** Production outage requires immediate hotfix

**Command:**
```markdown
🚨 **EMERGENCY OVERRIDE REQUEST** 🚨

**Incident:** INCIDENT-789 (SEV-1)
**Status:** Production outage - payment processing down
**Impact:** 80% of users affected, ~$50K/hour revenue loss
**Duration:** Ongoing since 02:00 PST (45 minutes)

**Hotfix PR:** #1234 - [INCIDENT-789] Restore payment processing

**Quality Gate Failures:**
- `algorithm-complexity` - Nested loop in payment retry logic
- `new-functions-tests` - No tests for new retry mechanism

**Emergency Justification:**
Cannot wait for proper implementation due to:
1. Customer impact: 80% of users cannot complete purchases
2. Revenue impact: ~$50K/hour loss
3. SLA breach: 99.9% uptime SLA breached at 60-minute mark
4. Immediate fix available: Hotfix tested manually in staging

**Post-Incident Commitment:**
- Post-incident review: 2025-10-15 10:00am PST (scheduled)
- Follow-up tickets:
  - PERF-791: Optimize payment retry algorithm
  - TECH-792: Add comprehensive retry mechanism tests
- Timeline: Proper fixes by end of Sprint 24

**On-Call Engineer:** @engineer-name  
**Incident Commander:** @ic-name

@kellerai/admins - Emergency override authorization requested

---

**ADMIN RESPONSE:**

🚨 **EMERGENCY OVERRIDE GRANTED** 🚨

**Incident:** INCIDENT-789 (SEV-1)  
**Authorized By:** @admin-name  
**Timestamp:** 2025-10-14 02:45 PST

**Authorization:**
Emergency override approved for production incident. All quality gate checks bypassed for critical hotfix deployment.

@coderabbitai ignore all-checks --reason "EMERGENCY OVERRIDE - INCIDENT-789: Production payment processing outage affecting 80% of users. Revenue loss ~$50K/hour. Immediate hotfix required to restore service. Quality gate checks temporarily bypassed. POST-INCIDENT REVIEW REQUIRED within 24 hours (scheduled 2025-10-15 10:00am). Follow-up tickets created: PERF-791, TECH-792. Authorized by @admin-name at 2025-10-14 02:45 PST."

**Post-Incident Requirements:**
1. ✅ Deploy hotfix immediately
2. ⏳ Post-incident review: 2025-10-15 10:00am
3. ⏳ Create follow-up tickets for quality issues
4. ⏳ Document in incident report
5. ⏳ Engineering leadership notification

**MERGE AUTHORIZED - DEPLOY IMMEDIATELY**
```

**Result:** ✅ Emergency override granted, requires post-incident review

---

## Role-Based Permissions

### Override Authorization Matrix

| Check Type | Self-Service | Tech Lead | Security Team | Admin |
|------------|--------------|-----------|---------------|--------|
| Architecture | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Testing | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Performance | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Documentation | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| Security (Standard) | ❌ No | ❌ No | ✅ Yes | ✅ Yes |
| Security (Critical) | ❌ No | ❌ No | ✅ Yes (documented) | ✅ Yes |
| Breaking Changes | ❌ No | ⚠️ With CHANGELOG | ⚠️ With CHANGELOG | ✅ Yes |
| Emergency All | ❌ No | ❌ No | ❌ No | ✅ Yes |

### GitHub Teams

**@kellerai/tech-leads**
- Architecture exceptions
- Testing coverage exceptions
- Performance trade-offs
- Response SLA: 4 hours (business hours)

**@kellerai/security-team**
- All security check overrides
- Elevated permission checks
- Security incident responses
- Response SLA: 8 hours (business hours)

**@kellerai/admins**
- Emergency overrides
- All-checks bypass
- Incident response
- Response SLA: Immediate (24/7 on-call)

---

## Audit Trail

### Override Logging

**All overrides logged to:** `.coderabbit-overrides.log`

**Log Format (JSON Lines):**
```json
{
  "timestamp": "2025-10-14T14:30:00Z",
  "pr_number": 456,
  "pr_title": "feat(orders): add expedited shipping",
  "check_name": "layer-separation",
  "override_level": "self-service",
  "requested_by": "developer-name",
  "approved_by": "developer-name",
  "justification": "Temporary direct database call for hotfix TECH-456...",
  "ticket_reference": "TECH-456",
  "business_justification": "Acme Corp demo deadline",
  "remediation_ticket": "TECH-457",
  "risk_level": "low"
}
```

### Compliance Reporting

**Weekly Override Report:**
- Total overrides by type
- Override frequency by developer
- Most overridden checks
- Average justification quality score

**Monthly Security Review:**
- All security overrides reviewed
- False positive patterns identified
- Check refinement recommendations

**Quarterly Audit:**
- Compliance with override policies
- Emergency override usage analysis
- Escalation response time adherence

---

## Common Scenarios

### Scenario 1: "I don't have time to fix this"

**❌ Not a valid reason**

**Alternative:**
- If truly urgent, use tech lead escalation with business justification
- Explain customer impact and timeline constraints
- Provide remediation plan with specific dates

### Scenario 2: "This check is wrong"

**✅ May be valid (false positive)**

**Process:**
1. Determine check type (architectural vs security)
2. For architecture: Self-service with detailed explanation
3. For security: Mention @kellerai/security-team with evidence
4. Include documentation/references proving false positive

### Scenario 3: "We'll fix it later"

**❌ Not sufficient alone**

**Required:**
- Create ticket for "later" fix
- Include ticket ID in justification
- Specify timeline (Sprint number or date)
- Explain why delay is acceptable (risk assessment)

### Scenario 4: "This is test code"

**✅ May be valid**

**Justification:**
- Confirm code is in `tests/` directory
- Explain why production rules don't apply
- Reference testing standards if applicable

### Scenario 5: "Customer deadline"

**✅ Valid for tech lead escalation**

**Required:**
- Business justification (customer name, contract value)
- Technical context (why fix is complex)
- Remediation plan (when will proper fix be implemented)
- Risk assessment (what could go wrong)

---

## Summary

**Key Takeaways:**

1. ✅ **Self-service available** for architecture, testing, performance, documentation checks
2. 🔒 **Security requires elevated permissions** - mention @kellerai/security-team
3. 📝 **50+ character justification** mandatory - be substantive
4. 🎟️ **Include ticket references** for tracking remediation
5. ⚖️ **Assess risk** and explain mitigation
6. 📊 **All overrides logged** for compliance and pattern analysis
7. 🚨 **Emergency path exists** for production incidents (admins only)

**Documentation References:**
- [Escalation Procedures](./escalation-procedures.md)
- [Request Changes Enforcement](./request-changes-enforcement.md)
- [Quality Gates Quick Reference](../QUALITY_GATES_QUICK_REFERENCE.md)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Platform Engineering  
**Status:** Active
