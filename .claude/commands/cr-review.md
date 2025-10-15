---
description: Run CodeRabbit review on current uncommitted changes
allowedTools: ["Bash(coderabbit *)", "Read"]
---

Run a CodeRabbit code review on uncommitted changes and analyze the results.

Steps:

1. Run CodeRabbit review with JSON output:
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-review.json
   ```

2. Read and parse the review results from /tmp/coderabbit-review.json

3. Summarize key findings:
   - Critical issues (security, bugs)
   - Code quality suggestions
   - Performance improvements
   - Style and maintainability

4. Provide a prioritized action plan organized by:
   - P0 (Must Fix): Security vulnerabilities, critical bugs
   - P1 (Should Fix): Code quality, performance issues
   - P2 (Consider): Style improvements, documentation

5. Ask if I should implement the suggested fixes automatically
