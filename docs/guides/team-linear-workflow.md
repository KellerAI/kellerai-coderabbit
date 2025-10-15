# Team Workflow Guide: Linear Integration with CodeRabbit

**Version:** 1.0
**Last Updated:** 2025-10-14
**Audience:** All KellerAI Development Team Members
**Purpose:** Guide for using Linear issue tracking with CodeRabbit PR reviews

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Creating Linear Issues](#creating-linear-issues)
3. [Linking PRs to Issues](#linking-prs-to-issues)
4. [Understanding Scope Validation](#understanding-scope-validation)
5. [PR Workflow](#pr-workflow)
6. [Best Practices](#best-practices)
7. [Common Scenarios](#common-scenarios)
8. [Troubleshooting](#troubleshooting)
9. [FAQs](#faqs)

---

## Quick Start

### For Developers

**Before Creating a PR:**
1. Create or identify a Linear issue for your work
2. Note the issue ID (e.g., `ENG-123`)
3. Include the issue ID in your PR description

**Example PR Description:**
```markdown
## Summary
Implement JWT authentication system

## Changes
- Added JWT token generation
- Implemented login/signup endpoints
- Added authentication middleware

## Related Issues
Closes ENG-123
```

**What Happens Next:**
- CodeRabbit automatically validates your PR scope against the Linear issue
- You'll receive feedback if your changes don't align with the issue
- Linear issue gets automatically updated with a link to your PR

---

## Creating Linear Issues

### When to Create an Issue

Create a Linear issue for:
- ✅ New features or enhancements
- ✅ Bug fixes
- ✅ Technical debt or refactoring
- ✅ Documentation improvements
- ✅ Performance optimizations

Don't create issues for:
- ❌ Typo fixes (< 5 lines)
- ❌ Dependency version bumps (unless security-related)
- ❌ Whitespace/formatting only changes

### Issue Quality Checklist

A good Linear issue includes:
- [ ] **Clear title** describing the work
- [ ] **Description** with acceptance criteria
- [ ] **Team assignment** (ENG, PROD, INFRA)
- [ ] **Priority level** (Urgent, High, Medium, Low)
- [ ] **Labels** for categorization

**Example Good Issue:**

```
Title: Implement JWT-based user authentication

Description:
Add JWT authentication system to secure API endpoints.

Requirements:
- Generate JWT tokens on successful login
- Validate tokens on protected routes
- Implement token refresh mechanism
- Add logout functionality

Acceptance Criteria:
- [ ] Users can login with email/password
- [ ] Protected routes reject unauthenticated requests
- [ ] Token refresh works before expiration
- [ ] Logout invalidates tokens

Technical Notes:
- Use HS256 algorithm for signing
- 15-minute token expiration
- 7-day refresh token expiration
```

---

## Linking PRs to Issues

### Linking Methods

#### Method 1: Using Keywords (Recommended)

Include one of these keywords followed by the issue ID in your PR description:

- `Closes ENG-123` - Marks issue as done when PR merges
- `Fixes ENG-123` - Same as Closes
- `Resolves ENG-123` - Same as Closes
- `Relates to ENG-123` - Links without auto-closing

**Example:**
```markdown
## Summary
Fix authentication token expiration bug

## Changes
- Extended token lifetime to 15 minutes
- Added token refresh endpoint

Fixes ENG-456
```

#### Method 2: Direct Reference

Simply mention the issue ID anywhere in the PR description:

```markdown
This PR implements the authentication system described in ENG-123.
```

**Note:** Direct references are detected but have lower confidence. Use keywords for best results.

### Multiple Issue Links

You can link multiple issues:

```markdown
## Related Issues
Closes ENG-123
Relates to PROD-456
Depends on INFRA-789
```

**Best Practice:** Link to the primary issue using `Closes`, and reference related issues with `Relates to`.

---

## Understanding Scope Validation

### What is Scope Validation?

CodeRabbit automatically compares your PR file changes against the linked Linear issue to detect:
- ✅ **In-scope changes**: Files that align with the issue requirements
- ⚠️ **Out-of-scope changes**: Files unrelated to the issue
- ❓ **Ambiguous changes**: Files that may or may not be relevant

### Validation Results

You'll receive one of three outcomes:

#### ✅ PASS - All Changes in Scope

```
✅ Scope Validation: PASS
- 4/4 files in scope (100%)
- All changes align with ENG-123 requirements
```

**Action:** No action needed. Your PR is well-scoped!

#### ⚠️ WARNING - Some Scope Drift

```
⚠️ Scope Validation: WARNING
- 3/5 files in scope (60%)
- 2/5 files may be out of scope

Out of Scope Files:
- src/billing/invoice.py
- src/frontend/ProductList.tsx

Recommendations:
1. Consider splitting unrelated changes into separate PRs
2. Update ENG-123 if these changes are actually required
```

**Action:** Review the flagged files. Consider:
- Splitting them into a separate PR
- Updating the Linear issue to include this scope
- Explaining why they're necessary in a PR comment

#### ❌ FAIL - Significant Scope Drift

```
❌ Scope Validation: FAIL
- 1/6 files in scope (17%)
- 5/6 files are out of scope
- Scope drift score: 0.83

This PR appears to address multiple unrelated issues.
```

**Action:** Split your PR or link to additional issues that cover all changes.

### Why Scope Validation Matters

1. **Easier Code Review**: Focused PRs are faster to review
2. **Better Git History**: Each commit addresses a specific issue
3. **Clearer Rollbacks**: Easier to revert specific features
4. **Faster Iteration**: Smaller PRs merge faster

---

## PR Workflow

### Standard Workflow

```
1. Create Linear Issue
   ↓
2. Create Feature Branch
   ↓
3. Implement Changes
   ↓
4. Create PR with Issue Reference
   ↓
5. CodeRabbit Reviews & Validates
   ↓
6. Address Feedback
   ↓
7. Merge PR (Issue Auto-Closes)
```

### Detailed Steps

#### Step 1: Create Linear Issue

```bash
# In Linear
1. Click "+ New Issue"
2. Select team (ENG, PROD, INFRA)
3. Write clear title and description
4. Set priority and labels
5. Note the issue ID (e.g., ENG-123)
```

#### Step 2: Create Feature Branch

```bash
# Use descriptive branch names with issue ID
git checkout -b feat/ENG-123-add-authentication

# Alternative naming patterns:
# fix/ENG-456-token-expiration
# refactor/INFRA-789-database-queries
# docs/PROD-101-api-documentation
```

#### Step 3: Implement Changes

```bash
# Make focused commits
git commit -m "feat: add JWT token generation (ENG-123)"
git commit -m "feat: add login endpoint (ENG-123)"
git commit -m "test: add authentication tests (ENG-123)"
```

#### Step 4: Create PR

```bash
# Push branch
git push origin feat/ENG-123-add-authentication

# Create PR with gh CLI
gh pr create \
  --title "feat: Implement JWT authentication (ENG-123)" \
  --body "$(cat <<'EOF'
## Summary
Implement JWT-based user authentication system

## Changes
- Added JWT token generation service
- Implemented login/signup endpoints
- Added authentication middleware
- Comprehensive test coverage

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Related Issues
Closes ENG-123

## Screenshots
_Add if applicable_
EOF
)"
```

#### Step 5: Review CodeRabbit Feedback

**Within 2-3 minutes, CodeRabbit will:**
1. Post a review with code suggestions
2. Post scope validation results
3. Update Linear issue with PR link

**Review the feedback:**
- Code quality suggestions
- Security concerns
- Performance issues
- Scope validation results

#### Step 6: Address Feedback

```bash
# Make requested changes
git add .
git commit -m "fix: address CodeRabbit feedback"
git push

# CodeRabbit automatically re-reviews
```

#### Step 7: Merge

```bash
# After approval, merge PR
gh pr merge --squash

# Linear issue automatically moves to "Done"
```

---

## Best Practices

### DO ✅

1. **Create issues before PRs**
   - Define scope and acceptance criteria first
   - Get team alignment on approach

2. **Use descriptive issue titles**
   - Good: "Implement JWT authentication with refresh tokens"
   - Bad: "Auth stuff"

3. **Keep PRs focused**
   - One issue per PR (ideally)
   - Related changes can reference multiple issues

4. **Write detailed descriptions**
   - Explain WHY, not just WHAT
   - Include testing instructions
   - Add screenshots for UI changes

5. **Update issues proactively**
   - Discovered additional work? Update the issue
   - Scope changed? Reflect it in Linear

6. **Respond to validation warnings**
   - Don't ignore scope drift warnings
   - Either split the PR or justify the changes

### DON'T ❌

1. **Don't skip issue creation**
   - Even for small changes, create an issue
   - Makes tracking and history easier

2. **Don't mix unrelated changes**
   - Typo fixes + feature work = bad
   - Keep each PR focused on one thing

3. **Don't ignore CodeRabbit feedback**
   - Address all suggestions or explain why not
   - Security warnings should never be ignored

4. **Don't force-push after review**
   - Breaks review history
   - Use new commits for changes

5. **Don't merge without linking issues**
   - All PRs should reference at least one issue
   - Exception: Emergent hotfixes (document afterward)

---

## Common Scenarios

### Scenario 1: Bug Fix

**Linear Issue:**
```
Title: Fix token expiration causing premature logouts
Priority: High
Labels: bug, auth
```

**PR:**
```markdown
## Summary
Fix JWT token expiration bug

## Root Cause
Tokens were expiring after 1 minute instead of 15 minutes due to
millisecond vs second confusion in expiration calculation.

## Fix
- Corrected expiration time calculation
- Added test to prevent regression
- Verified manually with 15-minute session

## Related Issues
Fixes ENG-456

## Testing
- [x] Unit test added: test_token_expiration_correct()
- [x] Manual testing: Logged in and remained active for 20 minutes
- [x] No premature logouts observed
```

### Scenario 2: Feature with Multiple Components

**Linear Issues:**
- `ENG-100`: Main feature (user profile system)
- `ENG-101`: Database schema (dependency)
- `ENG-102`: API endpoints (dependency)
- `ENG-103`: Frontend components (dependency)

**Approach:**
```bash
# PR 1: Database schema
git checkout -b feat/ENG-101-user-profile-schema
# ... implement schema ...
gh pr create --title "feat: Add user profile database schema (ENG-101)"
# PR description: "Closes ENG-101, Relates to ENG-100"

# PR 2: API endpoints (after PR 1 merges)
git checkout -b feat/ENG-102-user-profile-api
# ... implement API ...
gh pr create --title "feat: Add user profile API endpoints (ENG-102)"
# PR description: "Closes ENG-102, Relates to ENG-100, Depends on ENG-101"

# PR 3: Frontend (after PR 2 merges)
git checkout -b feat/ENG-103-user-profile-ui
# ... implement UI ...
gh pr create --title "feat: Add user profile UI components (ENG-103)"
# PR description: "Closes ENG-103, Closes ENG-100"
```

**Benefits:**
- Each PR is focused and reviewable
- Dependencies are clear
- Main issue (ENG-100) tracks overall progress

### Scenario 3: Scope Drift During Development

**Situation:**
While implementing authentication (ENG-123), you discover the user model needs refactoring.

**Approach:**

**Option A: Update the Issue (If closely related)**
1. Update ENG-123 description to include refactoring
2. Add comment explaining the scope expansion
3. Continue with the PR

**Option B: Create Separate Issue (If substantially different)**
1. Create new issue ENG-124: "Refactor user model for authentication"
2. Link issues: ENG-123 depends on ENG-124
3. Create separate PR for ENG-124
4. Wait for it to merge before continuing ENG-123

**Choose Option B when:**
- Change is >100 lines
- Different area of codebase
- Could be reviewed independently
- Different priority level

### Scenario 4: Handling Validation Warnings

**CodeRabbit Warning:**
```
⚠️ Scope Validation: WARNING
Out of scope: src/utils/date_formatter.py

Recommendation: Consider splitting into separate PR
```

**Response Options:**

**Option 1: Split the PR**
```bash
# Create separate PR for utility function
git checkout -b feat/date-formatter
git checkout main -- src/utils/date_formatter.py
git commit -m "feat: add date formatter utility"
gh pr create --title "feat: Add date formatter utility"

# Remove from original PR
git checkout feat/ENG-123-auth
git rm src/utils/date_formatter.py
git commit -m "remove: date formatter (moved to separate PR)"
```

**Option 2: Justify the Inclusion**
```markdown
## Response to Scope Validation

The date formatter (`src/utils/date_formatter.py`) is in-scope because:

1. JWT tokens include `iat` and `exp` timestamps
2. We need consistent date formatting for token validation
3. This utility is specific to authentication (not general-purpose)
4. It's only 30 lines and tightly coupled to auth logic

Keeping this in the same PR maintains atomic deployment of the auth system.
```

---

## Troubleshooting

### Issue: CodeRabbit Didn't Detect My Issue Link

**Symptoms:**
- PR created but CodeRabbit doesn't mention the Linear issue
- No scope validation performed

**Causes & Solutions:**

1. **Issue ID misspelled**
   ```markdown
   # Wrong
   Closes ENG123    # Missing hyphen
   Closes eng-123   # Wrong case
   Closes EN-123    # Wrong team key

   # Correct
   Closes ENG-123
   ```

2. **Issue ID not in PR description**
   - Check: Issue link is in PR body, not just commit messages
   - Solution: Edit PR description to add issue reference

3. **Team key not configured**
   - Check: Is your team key in `.coderabbit.yaml`?
   - Current teams: ENG, PROD, INFRA
   - Solution: Ask admin to add your team key

4. **Issue doesn't exist in Linear**
   - Verify: Does ENG-123 exist in Linear?
   - Solution: Create the issue or fix the reference

### Issue: Scope Validation Seems Wrong

**Symptoms:**
- CodeRabbit flags in-scope files as out-of-scope
- Validation seems overly strict

**Causes & Solutions:**

1. **Vague issue description**
   ```markdown
   # Vague (hard to validate)
   Title: Improve system
   Description: Make things better

   # Specific (easy to validate)
   Title: Implement JWT authentication
   Description: Add JWT-based authentication with login/signup endpoints
   ```

2. **Missing technical keywords**
   ```markdown
   # Before (lacks keywords)
   Description: Add user access control

   # After (includes keywords)
   Description: Implement JWT authentication system with
   login/signup endpoints and token validation middleware
   ```

3. **File names don't match scope**
   - Issue mentions "authentication" but file is `user_access.py`
   - CodeRabbit may not recognize the connection
   - Solution: Add comment explaining the relationship

### Issue: Linear Issue Not Auto-Closing

**Symptoms:**
- PR merged but Linear issue still "In Progress"

**Causes & Solutions:**

1. **Used wrong keyword**
   ```markdown
   # These DON'T auto-close:
   Relates to ENG-123
   Addresses ENG-123
   Mentioned in ENG-123

   # These DO auto-close:
   Closes ENG-123
   Fixes ENG-123
   Resolves ENG-123
   ```

2. **Webhook delivery failed**
   - Check: Linear Settings → API → Webhooks → View Deliveries
   - Solution: Manual close or contact admin

3. **PR was closed (not merged)**
   - Only merged PRs trigger auto-close
   - Closed PRs don't affect Linear status

### Issue: Multiple PRs for Same Issue

**Symptoms:**
- Created second PR for ENG-123, but first one still exists

**Solution:**
```markdown
# In second PR, reference the first PR
This PR supersedes #123 (previous implementation).

Closes ENG-123
```

Or:
```bash
# Close first PR
gh pr close 123 --comment "Superseded by #124"

# Reference in second PR
Closes ENG-123 (supersedes #123)
```

---

## FAQs

### General Questions

**Q: Do I need a Linear issue for every PR?**
A: Yes, with rare exceptions (emergency hotfixes, dependency bumps). Issues provide context and tracking.

**Q: Can one PR close multiple issues?**
A: Yes, but consider if it's too broad. If issues are closely related, it's fine:
```markdown
Closes ENG-123
Closes ENG-124
```

**Q: Can multiple PRs work on the same issue?**
A: Yes, for large features split into sub-tasks. Use `Relates to ENG-123` instead of `Closes` for all but the final PR.

### Workflow Questions

**Q: When should I create a Linear issue?**
A: Before you start coding. Define the work, get alignment, then implement.

**Q: What if I find additional work during implementation?**
A: Either update the issue description (small additions) or create a new issue (substantial work) and link them.

**Q: How do I handle dependencies between issues?**
A: Use Linear's "Blocked by" feature and reference in PR descriptions:
```markdown
Closes ENG-124
Depends on ENG-123 (must merge first)
```

### Technical Questions

**Q: Why is scope validation flagging my test files?**
A: Test files are usually considered in-scope. If flagged, the issue description might lack testing keywords. Update the issue to mention testing requirements.

**Q: Can I disable scope validation for my PR?**
A: Scope validation is informational only (doesn't block merging). If you believe it's incorrect, explain in a comment. Don't ignore it—it's often catching real issues.

**Q: What if CodeRabbit is wrong about scope?**
A: Post a comment explaining why the flagged files are in-scope. Example:
```markdown
@coderabbitai The database migration (`migrations/001_add_users.py`) is
in-scope because the authentication system requires the users table schema.
```

---

## Summary

### Key Takeaways

1. **Always create Linear issues** before starting work
2. **Reference issues in PR descriptions** using keywords like `Closes ENG-123`
3. **Keep PRs focused** on a single issue when possible
4. **Address scope validation warnings** by splitting PRs or justifying changes
5. **Update issues proactively** when scope changes during development

### Quick Reference

**Creating Issues:**
- Clear title + description with acceptance criteria
- Assign to correct team (ENG/PROD/INFRA)
- Set priority and labels

**Linking PRs:**
```markdown
Closes ENG-123      # Auto-closes on merge
Fixes ENG-123       # Auto-closes on merge
Resolves ENG-123    # Auto-closes on merge
Relates to ENG-123  # Links without closing
```

**Branch Naming:**
```bash
feat/ENG-123-short-description
fix/ENG-456-bug-description
refactor/INFRA-789-what-changed
```

**Getting Help:**
- Review this guide
- Check docs/configuration/linear-authentication-setup.md for technical details
- Ask in #engineering-help Slack channel
- Contact DevOps team for integration issues

---

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Maintained By:** DevOps Team
**Feedback:** Submit issues to ENG team in Linear
