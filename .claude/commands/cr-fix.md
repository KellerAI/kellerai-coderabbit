---
description: Automatically implement fixes for CodeRabbit review comments
allowedTools: ["Bash(coderabbit *)", "Read", "Edit", "Write"]
---

Implement fixes for CodeRabbit review findings.

Steps:

1. If no review file exists at /tmp/coderabbit-review.json, run a fresh review:
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-review.json
   ```

2. Read and parse the review JSON to extract actionable items

3. Prioritize fixes:
   - P0: Security vulnerabilities, critical bugs (fix immediately)
   - P1: Code quality, performance issues (fix proactively)
   - P2: Style, documentation (fix if time permits)

4. For each high-priority issue (P0 and P1):
   - Read the affected file to understand context
   - Implement the suggested fix or equivalent improvement
   - Use Edit tool to make changes
   - Document the change with clear comments if needed

5. After implementing all fixes:
   - Show summary of changes made
   - Run re-review to verify improvements:
     ```bash
     coderabbit review --output=json > /tmp/coderabbit-review-after.json
     ```
   - Compare before/after results
   - Report remaining issues if any

6. Ask if the user is ready to commit the changes
