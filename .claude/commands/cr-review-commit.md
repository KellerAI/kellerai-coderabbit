---
description: Review a specific git commit using CodeRabbit
allowedTools: ["Bash(coderabbit *)", "Bash(git *)"]
---

Review a specific git commit: $ARGUMENTS

Steps:

1. Validate the commit reference exists:
   ```bash
   git rev-parse --verify $ARGUMENTS
   ```

2. Show commit details:
   ```bash
   git show --stat $ARGUMENTS
   ```

3. Run CodeRabbit review on the commit:
   ```bash
   coderabbit review --commit=$ARGUMENTS --output=json > /tmp/coderabbit-commit-review.json
   ```

4. Read and parse the review results from /tmp/coderabbit-commit-review.json

5. Present findings organized by:
   - File affected
   - Issue severity (critical, important, minor)
   - Issue category (security, performance, style, etc.)
   - Suggested improvements

6. Provide recommendations:
   - Should this commit be amended?
   - Are there blocking issues for merge?
   - What follow-up work is needed?

7. If issues found, ask if fixes should be implemented in a follow-up commit
