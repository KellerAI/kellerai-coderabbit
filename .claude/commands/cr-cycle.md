---
description: Run full autonomous implement-review-fix cycle
allowedTools: ["Bash(coderabbit *)", "Read", "Edit", "Write", "Bash(git *)"]
---

Execute autonomous implement-review-fix cycle: $ARGUMENTS

This command implements a feature, reviews it, fixes issues, and repeats until quality standards are met.

Steps:

1. **Implementation Phase**:
   - Understand the feature requirements from: $ARGUMENTS
   - Implement the feature following best practices
   - Write appropriate tests if needed
   - Show summary of implementation

2. **Initial Review Phase**:
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-cycle-review-1.json
   ```
   - Parse review results
   - Categorize issues by severity

3. **Quality Gate Check**:
   - Count P0 (critical) issues
   - Count P1 (important) issues
   - Quality threshold: 0 P0 issues, ≤2 P1 issues

4. **Fix Phase** (if quality gate not met):
   - Implement fixes for P0 issues first
   - Then address P1 issues
   - Document all changes
   - Increment cycle counter

5. **Re-Review Phase** (after fixes):
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-cycle-review-N.json
   ```
   - Compare with previous review
   - Verify issues were resolved
   - Check for new issues introduced
   - Return to Quality Gate Check

6. **Completion Phase** (when quality gate passed):
   - Summarize implementation and all changes
   - List all review cycles completed
   - Show final review results with metrics
   - Generate suggested commit message based on changes
   - Ask if ready to commit

**Safety Limits**:
- Maximum 3 review-fix cycles to prevent infinite loops
- If limit reached without passing quality gate, report issues and ask for manual intervention
- Always verify fixes don't introduce new problems

**Progress Tracking**:
Throughout the cycle, maintain clear logging:
- Cycle N: [action taken]
- Issues: [resolved/remaining/new]
- Status: [in progress/quality gate passed/manual review needed]
