# CodeRabbit CLI Integration with Claude Code

This guide provides comprehensive integration patterns for using CodeRabbit CLI with Claude Code to enable autonomous implement-review-fix development cycles.

## Table of Contents

- [Overview](#overview)
- [Installation & Setup](#installation--setup)
- [Slash Commands](#slash-commands)
- [Prompt Templates](#prompt-templates)
- [Autonomous Workflows](#autonomous-workflows)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

The CodeRabbit CLI integration enables Claude Code to:

1. **Run automated code reviews** on uncommitted changes
2. **Parse review feedback** in structured JSON format
3. **Automatically implement fixes** based on review comments
4. **Re-review after fixes** to verify improvements
5. **Support autonomous development cycles** with minimal human intervention

## Installation & Setup

### Prerequisites

1. CodeRabbit CLI installed and authenticated:
   ```bash
   bash install-coderabbit-cli.sh
   bash auth-setup.sh setup
   ```

2. Claude Code properly configured with tool access

### Configuration

Add to `.claude/settings.json`:

```json
{
  "allowedTools": [
    "Bash(coderabbit *)",
    "Edit",
    "Read",
    "Write"
  ]
}
```

## Slash Commands

### 1. Review Current Changes

**Command**: `/cr-review`

**Location**: `.claude/commands/cr-review.md`

```markdown
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

2. Read and parse the review results

3. Summarize key findings:
   - Critical issues (security, bugs)
   - Code quality suggestions
   - Performance improvements
   - Style and maintainability

4. Provide a prioritized action plan

5. Ask if you should implement the suggested fixes
```

### 2. Auto-Fix Review Issues

**Command**: `/cr-fix`

**Location**: `.claude/commands/cr-fix.md`

```markdown
---
description: Automatically implement fixes for CodeRabbit review comments
allowedTools: ["Bash(coderabbit *)", "Read", "Edit", "Write"]
---

Implement fixes for CodeRabbit review findings: $ARGUMENTS

Steps:

1. If no review file provided, run a fresh review:
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-review.json
   ```

2. Parse review JSON to extract actionable items

3. Prioritize fixes:
   - P0: Security vulnerabilities, bugs
   - P1: Code quality, performance
   - P2: Style, documentation

4. For each high-priority issue:
   - Read the affected file
   - Implement the suggested fix
   - Document the change

5. After all fixes:
   - Show summary of changes
   - Run re-review to verify improvements
   - Report remaining issues if any

6. Ask if ready to commit changes
```

### 3. Review Specific Commit

**Command**: `/cr-review-commit`

**Location**: `.claude/commands/cr-review-commit.md`

```markdown
---
description: Review a specific git commit using CodeRabbit
allowedTools: ["Bash(coderabbit *)", "Bash(git *)"]
---

Review a specific git commit: $ARGUMENTS

Steps:

1. Validate commit reference exists:
   ```bash
   git rev-parse --verify $ARGUMENTS
   ```

2. Run CodeRabbit review on the commit:
   ```bash
   coderabbit review --commit=$ARGUMENTS --output=json > /tmp/coderabbit-commit-review.json
   ```

3. Parse and analyze review results

4. Present findings organized by:
   - File affected
   - Issue severity
   - Suggested improvements

5. Provide recommendations for follow-up actions
```

### 4. Implement-Review-Fix Cycle

**Command**: `/cr-cycle`

**Location**: `.claude/commands/cr-cycle.md`

```markdown
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
   - Write appropriate tests

2. **Review Phase**:
   ```bash
   coderabbit review --output=json > /tmp/coderabbit-cycle-review.json
   ```

3. **Analysis Phase**:
   - Parse review results
   - Categorize issues by severity
   - Determine if quality threshold met (no P0/P1 issues)

4. **Fix Phase** (if issues found):
   - Implement fixes for identified issues
   - Document changes made
   - Return to Review Phase

5. **Completion Phase** (when quality threshold met):
   - Summarize implementation
   - List all review cycles completed
   - Show final review results
   - Prepare commit message suggestion
   - Ask if ready to commit

Maximum iterations: 3 cycles to prevent infinite loops
```

## Prompt Templates

### Template 1: Parse Review JSON

```markdown
Parse the CodeRabbit review JSON and extract actionable items.

Review JSON:
```json
{review_json_content}
```

Provide:
1. **Summary**: Overall code quality assessment
2. **Critical Issues**: Security, bugs (must fix)
3. **Important Issues**: Code quality, performance (should fix)
4. **Minor Issues**: Style, documentation (optional)
5. **Action Plan**: Prioritized list of fixes to implement

For each issue include:
- File and line number
- Issue description
- Suggested fix
- Priority level (P0/P1/P2)
```

### Template 2: Implement Specific Fix

```markdown
Implement the following CodeRabbit review fix:

**File**: {file_path}
**Line**: {line_number}
**Issue**: {issue_description}
**Suggestion**: {suggested_fix}
**Category**: {category} (e.g., security, performance, style)

Steps:
1. Read the current file content
2. Understand the context around the issue
3. Implement the suggested fix or an equivalent improvement
4. Ensure the fix doesn't break existing functionality
5. Document the change clearly

Provide the fixed code and explain the changes made.
```

### Template 3: Verify Fixes

```markdown
Verify that the implemented fixes address the CodeRabbit review comments.

Original Issues:
{original_issues_list}

Steps:
1. Run a fresh CodeRabbit review on current changes
2. Compare new review with original issues
3. Identify which issues are resolved
4. Identify any new issues introduced
5. Report on:
   - Issues fixed
   - Issues remaining
   - New issues (if any)
   - Overall quality improvement

Recommend next steps based on results.
```

## Autonomous Workflows

### Workflow 1: Pre-Commit Review

Automatically review code before committing:

```bash
# In .git/hooks/pre-commit
#!/bin/bash
coderabbit review --output=json > /tmp/pre-commit-review.json

if [ $? -ne 0 ]; then
    echo "CodeRabbit review found issues. Run: claude -c '/cr-fix' to address them."
    exit 1
fi

echo "CodeRabbit review passed!"
```

### Workflow 2: Continuous Improvement

Regular autonomous code improvement sessions:

1. Run `/cr-review` to identify improvement opportunities
2. Prioritize issues by impact and effort
3. Run `/cr-fix` to implement high-value improvements
4. Verify improvements with re-review
5. Commit changes incrementally

### Workflow 3: Feature Development with Reviews

Integrated feature development:

1. Implement feature functionality
2. Run `/cr-review` to catch issues early
3. Fix critical issues immediately
4. Refine based on quality suggestions
5. Final `/cr-review` before PR
6. Use review summary in PR description

## Best Practices

### 1. Review Frequency

- **Pre-commit**: Always review before committing
- **During development**: Review after completing each logical unit
- **Before PR**: Comprehensive review of all changes

### 2. Fix Prioritization

```
P0 (Must Fix):
- Security vulnerabilities
- Critical bugs
- Breaking changes

P1 (Should Fix):
- Code quality issues
- Performance problems
- Test coverage gaps

P2 (Consider):
- Style improvements
- Documentation updates
- Minor optimizations
```

### 3. Autonomous Mode Guidelines

- **Set iteration limits**: Prevent infinite review-fix loops (max 3 cycles)
- **Manual review for complex issues**: Some fixes require human judgment
- **Verify fixes**: Always re-review after implementing fixes
- **Document changes**: Clear comments on AI-implemented fixes

### 4. JSON Output Parsing

Key JSON structure to parse:

```json
{
  "summary": {
    "total_issues": 10,
    "critical": 2,
    "important": 5,
    "minor": 3
  },
  "files": [
    {
      "path": "src/main.py",
      "issues": [
        {
          "line": 42,
          "severity": "critical",
          "category": "security",
          "message": "Potential SQL injection vulnerability",
          "suggestion": "Use parameterized queries"
        }
      ]
    }
  ]
}
```

### 5. Integration with TaskMaster

Track review cycles in TaskMaster:

```bash
# Log review findings
task-master update-subtask --id=X.Y --prompt="CodeRabbit review identified: [issues]"

# Log fixes implemented
task-master update-subtask --id=X.Y --prompt="Fixed issues: [list]"

# Final verification
task-master update-subtask --id=X.Y --prompt="Review passed with [metrics]"
```

## Advanced Integration Patterns

### Pattern 1: Diff-Based Reviews

Review only specific changes:

```bash
# Review changes since last commit
coderabbit review --diff="HEAD"

# Review specific file
coderabbit review --file="src/module.py"

# Review PR changes
coderabbit review --pr=123
```

### Pattern 2: Custom Review Profiles

Use different profiles for different contexts:

```bash
# Strict security review
coderabbit review --profile=security

# Performance-focused review
coderabbit review --profile=performance

# Quick style check
coderabbit review --profile=style-only
```

### Pattern 3: Review with Context

Include project context in reviews:

```bash
# Review with knowledge base context
coderabbit review --context=.cursorrules --context=CLAUDE.md

# Review with configuration
coderabbit review --config=.coderabbit.yaml
```

## Troubleshooting

### Common Issues

**1. Review command fails**

```bash
# Check CLI installation
coderabbit --version

# Verify authentication
bash auth-setup.sh status

# Test API connection
bash auth-setup.sh test
```

**2. JSON parsing errors**

```bash
# Validate JSON output
coderabbit review --output=json | jq .

# Use pretty-printed JSON
coderabbit review --output=json --pretty
```

**3. Claude Code can't access review results**

Ensure review output is saved to accessible location:

```bash
# Save to project temp directory
coderabbit review --output=json > ./.coderabbit-review.json

# Or use system temp with proper permissions
coderabbit review --output=json > /tmp/coderabbit-review.json
chmod 644 /tmp/coderabbit-review.json
```

**4. Fix implementation fails**

- Read the full file context before editing
- Verify line numbers haven't shifted after previous edits
- Test fixes incrementally
- Use git diff to verify changes

### Debug Mode

Enable verbose logging:

```bash
export CODERABBIT_DEBUG=1
coderabbit review --verbose
```

## Example Session

Complete autonomous fix session:

```bash
# Terminal session example
$ claude

> /cr-review

[Running CodeRabbit review...]
[Parsing results...]

Found 8 issues:
- 2 critical (security)
- 4 important (code quality)
- 2 minor (style)

Critical Issues:
1. src/auth.py:42 - SQL injection risk
2. src/api.py:128 - Unvalidated user input

Should I implement fixes? (yes)

> yes

[Implementing fix 1/2: SQL injection prevention...]
[Updated src/auth.py with parameterized query]

[Implementing fix 2/2: Input validation...]
[Added validation layer in src/api.py]

[Re-running review to verify fixes...]

All critical issues resolved!
Remaining: 4 quality improvements, 2 style issues

Continue with quality improvements? (yes/no)

> yes

[Implementing quality improvements...]
[Complete]

Final review results:
✓ No critical issues
✓ No important issues
- 2 minor style suggestions (optional)

Changes ready for commit. Create commit? (yes/no)
```

## Summary

This integration enables:

- **Automated reviews** integrated into development workflow
- **Intelligent fix implementation** based on structured feedback
- **Autonomous improvement cycles** with quality verification
- **Seamless Claude Code interaction** via slash commands
- **Comprehensive tracking** through TaskMaster integration

For support, see [troubleshooting guide](./troubleshooting.md) or contact your team lead.
