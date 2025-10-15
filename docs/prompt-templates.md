# CodeRabbit CLI Prompt Templates for Claude Code

This document contains reusable prompt templates for parsing CodeRabbit review output and implementing fixes systematically.

## Table of Contents

- [JSON Parsing Templates](#json-parsing-templates)
- [Fix Implementation Templates](#fix-implementation-templates)
- [Verification Templates](#verification-templates)
- [Workflow Templates](#workflow-templates)

## JSON Parsing Templates

### Template 1: Parse Complete Review

```markdown
Parse the CodeRabbit review JSON output and extract actionable items.

**Review JSON:**
```json
{review_json_content}
```

**Required Analysis:**

1. **Executive Summary**
   - Total issues found: [count]
   - Overall code quality score: [assessment]
   - Review confidence level: [high/medium/low]

2. **Critical Issues (P0 - Must Fix)**
   - Count: [number]
   - Categories: [list]
   - Blocking concerns: [yes/no]

3. **Important Issues (P1 - Should Fix)**
   - Count: [number]
   - Impact areas: [list]

4. **Minor Issues (P2 - Optional)**
   - Count: [number]
   - Quick wins: [list]

5. **Detailed Issue Breakdown**

For each issue, provide:
- **ID**: [sequential number]
- **File**: [path]
- **Line**: [line number or range]
- **Severity**: [P0/P1/P2]
- **Category**: [security/performance/quality/style/documentation]
- **Issue**: [description]
- **Impact**: [why this matters]
- **Suggested Fix**: [specific recommendation]
- **Effort**: [low/medium/high]

6. **Prioritized Action Plan**

Create implementation order based on:
- Severity (P0 first, then P1, then P2)
- Dependencies (if fixing one unblocks others)
- Effort (quick wins when similar severity)

**Output Format:**
```
Phase 1 (Critical): [P0 issues]
Phase 2 (Important): [P1 issues]
Phase 3 (Optional): [P2 issues if time permits]

Estimated total effort: [hours/complexity]
Recommended approach: [sequential/parallel/batched]
```
```

### Template 2: Parse Issues by Category

```markdown
Parse CodeRabbit review JSON and group issues by category for targeted fixes.

**Review JSON:**
```json
{review_json_content}
```

**Categorize issues into:**

**1. Security Issues**
- SQL injection risks
- XSS vulnerabilities
- Insecure authentication
- Data exposure
- Insecure dependencies

**2. Performance Issues**
- Inefficient algorithms (O(n²) → O(n log n))
- Database N+1 queries
- Memory leaks
- Unnecessary re-renders (React)
- Blocking operations

**3. Code Quality Issues**
- High complexity (cyclomatic > 10)
- Code duplication
- Poor error handling
- Unclear naming
- Missing type annotations

**4. Maintainability Issues**
- Insufficient documentation
- Missing tests
- Hard-coded values
- Tight coupling
- Violation of SOLID principles

**5. Style/Convention Issues**
- Formatting inconsistencies
- Naming conventions
- Import organization
- Comment quality

**Output for each category:**
- Count of issues
- Most critical items
- Quick fix recommendations
- Long-term improvements

**Suggested Fix Order:**
1. Security (always first)
2. Performance (if customer-facing impact)
3. Quality (improves development velocity)
4. Maintainability (reduces tech debt)
5. Style (improves readability)
```

### Template 3: Extract File-Specific Issues

```markdown
Parse CodeRabbit review JSON and organize by file for systematic fixes.

**Review JSON:**
```json
{review_json_content}
```

**For each file with issues:**

**File: [path/to/file.ext]**

Overview:
- Total issues: [count]
- Highest severity: [P0/P1/P2]
- Primary concerns: [list categories]
- Recommended action: [fix now/schedule/defer]

**Issues:**

1. **Line [number]** - [Severity]
   - Category: [category]
   - Issue: [description]
   - Current code:
     ```[language]
     [code snippet]
     ```
   - Suggested fix:
     ```[language]
     [fixed code]
     ```
   - Rationale: [why this fix]

2. [Additional issues...]

**File-Level Recommendations:**
- [Any architectural changes needed]
- [Refactoring suggestions]
- [Test coverage needs]

**Fix Strategy for This File:**
- [Sequential line-by-line / Batch changes / Refactor approach]
- [Estimated time]
- [Dependencies on other files]
```

## Fix Implementation Templates

### Template 4: Implement Specific Fix

```markdown
Implement CodeRabbit review fix with full context and verification.

**Fix Details:**
- **File**: {file_path}
- **Line**: {line_number} (or range: {start_line}-{end_line})
- **Severity**: {P0/P1/P2}
- **Category**: {security/performance/quality/style}
- **Issue**: {issue_description}
- **Suggested Fix**: {suggested_fix}

**Implementation Steps:**

1. **Read Current Context**
   - Read file: {file_path}
   - Understand surrounding code (20 lines before/after)
   - Identify dependencies and side effects

2. **Analyze Fix Impact**
   - What will this change affect?
   - Are there related areas that need updates?
   - Will this break existing tests?
   - Does this require new tests?

3. **Implement Fix**
   - Apply the suggested fix or equivalent improvement
   - Ensure code style consistency
   - Update related documentation/comments
   - Add explanatory comments if complex

4. **Verification**
   - Does the fix address the root cause?
   - Are there edge cases to handle?
   - Is error handling appropriate?
   - Does this follow project conventions?

5. **Output**
   - Show the exact changes made (diff format)
   - Explain why this approach was chosen
   - List any side effects or related updates needed
   - Suggest tests to verify the fix

**Before Code:**
```{language}
{original_code}
```

**After Code:**
```{language}
{fixed_code}
```

**Change Explanation:**
[Detailed explanation of what changed and why]

**Testing Recommendations:**
- [Specific test cases for this fix]
```

### Template 5: Batch Fix Implementation

```markdown
Implement multiple related fixes in batch for efficiency.

**Batch Details:**
- **Category**: {category} (e.g., all security issues)
- **File**: {file_path} (or "Multiple files")
- **Issue Count**: {count}
- **Total Effort**: {low/medium/high}

**Issues in Batch:**

1. {Issue 1 summary}
2. {Issue 2 summary}
3. [Additional issues...]

**Batch Implementation Strategy:**

**Step 1: Pre-Implementation Analysis**
- Identify overlapping changes
- Determine optimal fix order
- Check for conflicts between fixes
- List affected test files

**Step 2: Implement Fixes Sequentially**

For each fix:
- Read current file state
- Apply fix
- Update to reflect change
- Document change reason

**Step 3: Post-Implementation Review**
- Verify all fixes applied correctly
- Check no regressions introduced
- Ensure code still compiles/runs
- Update related documentation

**Step 4: Testing Strategy**
- [List tests to run]
- [New tests to create]
- [Integration test considerations]

**Implementation Order:**
1. [First fix - justification]
2. [Second fix - justification]
3. [Continue...]

**Expected Outcome:**
- All {count} issues resolved
- No new issues introduced
- Code quality improved
- Tests passing
```

## Verification Templates

### Template 6: Verify Fixes

```markdown
Verify that implemented fixes successfully address CodeRabbit review comments.

**Original Issues:**
```json
{original_issues_json}
```

**Verification Steps:**

1. **Run Fresh Review**
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-review-after.json
   ```

2. **Compare Results**

   **Before Fix:**
   - Total issues: [count]
   - P0 issues: [count]
   - P1 issues: [count]
   - P2 issues: [count]

   **After Fix:**
   - Total issues: [count]
   - P0 issues: [count]
   - P1 issues: [count]
   - P2 issues: [count]

3. **Issue Resolution Analysis**

   **Resolved Issues:** [count]
   - [List of resolved issue IDs with brief description]
   - Verification: ✓ No longer appears in new review

   **Partially Resolved:** [count]
   - [Issues that improved but not fully resolved]
   - Remaining work: [description]

   **Unresolved Issues:** [count]
   - [Issues that remain]
   - Reason: [why still present]
   - Next steps: [action plan]

   **New Issues Introduced:** [count]
   - [Any new issues from fixes]
   - Severity: [assessment]
   - Action required: [yes/no]

4. **Quality Metrics**

   - Overall improvement: [percentage]
   - Critical issues eliminated: [count]
   - Code quality score: [before] → [after]

5. **Recommendations**

   **Immediate Actions:**
   - [Any urgent fixes needed]

   **Follow-up Work:**
   - [Issues to address in next iteration]

   **Success Criteria:**
   - All P0 issues resolved: [yes/no]
   - P1 issues ≤ 2: [yes/no]
   - No new P0/P1 introduced: [yes/no]

   **Status: [PASSED / NEEDS WORK / MANUAL REVIEW REQUIRED]**
```

### Template 7: Regression Check

```markdown
Check for regressions or unintended side effects from fixes.

**Fixed Issues:**
[List of issues that were addressed]

**Regression Check Areas:**

1. **Functionality**
   - Do existing features still work?
   - Are there any broken behaviors?
   - Run test suite: [command]
   - Test results: [summary]

2. **Performance**
   - Any performance degradation?
   - Increased complexity?
   - Run benchmarks: [if applicable]
   - Results: [summary]

3. **Dependencies**
   - Are imports/dependencies still valid?
   - Any circular dependencies introduced?
   - Run dependency check: [command]

4. **Type Safety** (for TypeScript/typed languages)
   - Type checking: [command]
   - Any new type errors?
   - Results: [summary]

5. **Linting and Formatting**
   - Run linter: [command]
   - Run formatter check: [command]
   - Any new warnings?

6. **Edge Cases**
   - Test boundary conditions
   - Check error handling paths
   - Verify null/undefined handling

**Results Summary:**

✓ **Passed:**
- [List checks that passed]

⚠ **Warnings:**
- [List non-critical issues]

✗ **Failed:**
- [List any failures]
- Action required: [description]

**Overall Assessment: [SAFE TO COMMIT / NEEDS FIXES / REQUIRES REVIEW]**
```

## Workflow Templates

### Template 8: Complete Review-Fix Cycle

```markdown
Execute complete review-fix-verify cycle with quality gates.

**Objective:** [Feature/change being implemented]

**Cycle Iteration:** [1/2/3]

---

**PHASE 1: REVIEW**

```bash
coderabbit review --output=json > /tmp/review-cycle-{iteration}.json
```

Parse results using Template 1 (Parse Complete Review)

**Quality Gate 1:**
- P0 issues: [count] (must be 0 to pass)
- P1 issues: [count] (must be ≤ 2 to pass)
- Status: [PASS / FAIL]

If FAIL, proceed to PHASE 2. If PASS, proceed to PHASE 4.

---

**PHASE 2: FIX IMPLEMENTATION**

For each P0 issue:
- Use Template 4 (Implement Specific Fix)
- Document change

For P1 issues (if > 2):
- Prioritize by impact
- Use Template 4 or 5 (batch)
- Document changes

**Changes Summary:**
- Files modified: [list]
- Issues addressed: [P0: count, P1: count]
- Lines changed: [approximate]

---

**PHASE 3: VERIFICATION**

Use Template 6 (Verify Fixes)

```bash
coderabbit review --output=json > /tmp/review-cycle-{iteration}-after.json
```

Compare before/after
Run regression checks (Template 7)

**Quality Gate 2:**
- All P0 resolved: [yes/no]
- P1 ≤ 2: [yes/no]
- No new P0/P1: [yes/no]
- Status: [PASS / FAIL]

If FAIL and iteration < 3, increment iteration and return to PHASE 1.
If FAIL and iteration = 3, proceed to PHASE 5 (manual review).
If PASS, proceed to PHASE 4.

---

**PHASE 4: COMPLETION**

**Final Metrics:**
- Total cycles: [count]
- Issues resolved: [count]
- Final P0 count: [should be 0]
- Final P1 count: [should be ≤ 2]
- Code quality improvement: [percentage]

**Changes Summary:**
```
Files modified: [count]
Lines added: [count]
Lines deleted: [count]
```

**Suggested Commit Message:**
```
{type}: {brief description}

- Resolved {count} critical issues
- Fixed {count} important code quality issues
- Improved {specific aspects}

CodeRabbit review cycles: {count}
Final quality gate: PASSED
```

**Next Steps:**
1. Review changes: git diff
2. Run full test suite
3. Commit with suggested message
4. Create PR

**Status: READY FOR COMMIT**

---

**PHASE 5: MANUAL REVIEW REQUIRED**

Maximum iterations (3) reached without passing quality gate.

**Remaining Issues:**
[List of unresolved P0/P1 issues]

**Why Manual Review Needed:**
- [Complex issues requiring architectural decisions]
- [Unclear requirements or edge cases]
- [Potential breaking changes]
- [Other reasons]

**Recommendations:**
1. [Specific guidance]
2. [Consultation needed]
3. [Alternative approaches]

**Status: BLOCKED - MANUAL REVIEW REQUIRED**
```

### Template 9: Pre-Commit Review Workflow

```markdown
Execute pre-commit review workflow to ensure code quality before committing.

**Context:** About to commit changes

---

**Step 1: Pre-Commit Review**

```bash
git diff --cached
coderabbit review --output=json > /tmp/pre-commit-review.json
```

Parse with Template 1

---

**Step 2: Quality Gate**

**Blocking Issues (will prevent commit):**
- P0 (critical) issues: [count]
- Issues: [list if any]

**Non-Blocking Issues (warnings):**
- P1 (important) issues: [count]
- P2 (minor) issues: [count]

**Decision Tree:**

IF P0 count > 0:
  - Status: ❌ **COMMIT BLOCKED**
  - Action: Fix P0 issues before committing
  - Use Template 4 to fix
  - Re-run this workflow after fixes

ELSE IF P1 count > 3:
  - Status: ⚠️ **WARNING**
  - Recommendation: Consider fixing P1 issues
  - Ask user: "Proceed with commit? (y/n)"

ELSE:
  - Status: ✅ **COMMIT APPROVED**
  - Proceed to Step 3

---

**Step 3: Commit Preparation**

**Generate Commit Message:**
```
{type}({scope}): {description}

{detailed description of changes}

Quality checks:
- CodeRabbit review: PASSED
- P0 issues: 0
- P1 issues: {count}
- Code quality: {assessment}
```

**Commit Command:**
```bash
git commit -m "{generated message}"
```

**Post-Commit:**
- Run: `coderabbit review --commit=HEAD` to verify committed code
- Log review results for team metrics

**Status: COMMIT COMPLETED**
```

## Usage Examples

### Example 1: Using Template 1 for Parsing

Input:
```
Parse the CodeRabbit review JSON output and extract actionable items.

**Review JSON:**
{paste actual JSON from coderabbit review}

[Continue with Template 1...]
```

### Example 2: Using Template 4 for Fix

Input:
```
Implement CodeRabbit review fix with full context and verification.

**Fix Details:**
- **File**: src/auth.py
- **Line**: 42
- **Severity**: P0
- **Category**: security
- **Issue**: SQL injection vulnerability in login function
- **Suggested Fix**: Use parameterized queries instead of string concatenation

[Continue with Template 4...]
```

### Example 3: Complete Cycle with Template 8

Input:
```
Execute complete review-fix-verify cycle with quality gates.

**Objective:** Implement user authentication API endpoint

**Cycle Iteration:** 1

[Continue with Template 8...]
```

## Template Customization

### Adapting for Your Project

1. **Adjust Severity Thresholds:**
   - Modify P0/P1/P2 definitions based on project standards
   - Customize quality gate criteria

2. **Add Project-Specific Categories:**
   - Include domain-specific issue types
   - Add custom validation rules

3. **Integrate with CI/CD:**
   - Automate template execution in pipelines
   - Generate reports for dashboards

4. **Team Workflow Integration:**
   - Link to ticket system
   - Include team notification hooks
   - Connect with TaskMaster for tracking

## Summary

These templates provide:
- **Structured parsing** of CodeRabbit review output
- **Systematic fix implementation** with context and verification
- **Quality gates** to ensure standards are met
- **Complete workflows** for autonomous development cycles
- **Reusable patterns** for consistent code quality

For integration with Claude Code slash commands, these templates are referenced in the `/cr-*` command implementations.
