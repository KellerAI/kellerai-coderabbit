# CodeRabbit CLI Usage Guide

Complete reference for using CodeRabbit CLI in development workflows.

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Authentication](#authentication)
- [Core Commands](#core-commands)
- [Review Workflows](#review-workflows)
- [Configuration](#configuration)
- [Git Integration](#git-integration)
- [Team Workflows](#team-workflows)
- [Advanced Usage](#advanced-usage)
- [Command Reference](#command-reference)

## Quick Start

```bash
# Install CLI
bash install-coderabbit-cli.sh

# Set up authentication
bash auth-setup.sh setup

# Initialize in your repository
cd /path/to/your/repo
coderabbit init

# Run your first review
coderabbit review
```

## Installation

### Using Installation Script

**Recommended for team deployment:**

```bash
# Download and run installation script
curl -fsSL https://raw.githubusercontent.com/kellerai/coderabbit/main/install-coderabbit-cli.sh | bash

# Or if you have the repo locally
bash install-coderabbit-cli.sh
```

The script will:
- Detect your OS and architecture
- Download the appropriate binary
- Install to `~/.local/bin/coderabbit`
- Configure your PATH
- Verify installation

### Manual Installation

```bash
# macOS (Apple Silicon)
curl -fsSL https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-macos-arm64 -o ~/.local/bin/coderabbit
chmod +x ~/.local/bin/coderabbit

# macOS (Intel)
curl -fsSL https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-macos-x64 -o ~/.local/bin/coderabbit
chmod +x ~/.local/bin/coderabbit

# Linux (x86_64)
curl -fsSL https://github.com/coderabbitai/coderabbit-cli/releases/latest/download/coderabbit-linux-x64 -o ~/.local/bin/coderabbit
chmod +x ~/.local/bin/coderabbit

# Add to PATH if needed
echo 'export PATH="$PATH:$HOME/.local/bin"' >> ~/.bashrc
source ~/.bashrc
```

### Verify Installation

```bash
coderabbit --version
coderabbit --help
```

## Authentication

### Team Onboarding (Recommended)

Use the complete onboarding script:

```bash
bash team-onboarding.sh
```

This will:
1. Install the CLI
2. Set up authentication
3. Configure git integration
4. Verify setup

### Manual Authentication Setup

```bash
# Interactive setup
bash auth-setup.sh setup

# Check status
bash auth-setup.sh status

# Test API connection
bash auth-setup.sh test

# Remove authentication
bash auth-setup.sh revoke
```

### Getting API Token

1. Visit https://app.coderabbit.ai/settings/api-tokens
2. Click "Generate New Token"
3. Name it (e.g., "Development Machine")
4. Copy the token (you won't see it again!)
5. Paste when prompted by auth-setup.sh

### Token Storage

Tokens are stored securely:
- **macOS**: System Keychain
- **Linux**: GNOME Keyring (if available)
- **Fallback**: `~/.config/coderabbit/token` (600 permissions)

## Core Commands

### Review Commands

```bash
# Review uncommitted changes
coderabbit review

# Review specific commit
coderabbit review --commit=HEAD
coderabbit review --commit=abc123

# Review specific file
coderabbit review --file=src/main.py

# Review with JSON output (for CI/automation)
coderabbit review --output=json

# Review with custom config
coderabbit review --config=.coderabbit.yaml

# Review with specific profile
coderabbit review --profile=strict
```

### Repository Commands

```bash
# Initialize CodeRabbit in repository
coderabbit init

# Show current configuration
coderabbit config show

# Validate configuration
coderabbit config validate
```

### Authentication Commands

```bash
# Login (interactive)
coderabbit auth login

# Show current user
coderabbit auth whoami

# Check authentication status
coderabbit auth status

# Logout
coderabbit auth logout
```

### Git Hooks Commands

```bash
# Install git hooks
coderabbit hooks install

# Uninstall git hooks
coderabbit hooks uninstall

# List installed hooks
coderabbit hooks list
```

## Review Workflows

### 1. Pre-Commit Review

Review changes before committing:

```bash
# Stage your changes
git add .

# Run review on staged changes
coderabbit review

# If issues found, fix them
# Then review again
coderabbit review

# When clean, commit
git commit -m "Your commit message"
```

### 2. Post-Implementation Review

Review after completing a feature:

```bash
# Implement feature
# ...

# Review all uncommitted changes
coderabbit review

# Save review results
coderabbit review --output=json > review-results.json

# Fix issues based on feedback

# Re-review
coderabbit review
```

### 3. PR Review Preparation

Prepare for pull request:

```bash
# Review all changes in branch
git diff main...HEAD | coderabbit review --diff

# Review specific commits
coderabbit review --commit=HEAD~3..HEAD

# Generate review summary for PR description
coderabbit review --output=json | jq '.summary'
```

### 4. Continuous Review

Integrate with development cycle:

```bash
# Watch for changes and auto-review
coderabbit watch

# Review on file save
coderabbit watch --on-save

# Review with specific interval
coderabbit watch --interval=300  # 5 minutes
```

## Configuration

### Repository Configuration

Create `.coderabbit.yaml` in repository root:

```yaml
# Review settings
profile: chill  # or: strict, balanced
auto_review: true
high_level_summary: true

# Language settings
language:
  python:
    version: "3.11"
    type_hints: required
  typescript:
    strict_mode: true
  javascript:
    es_version: "ES2022"

# Review focus
reviews:
  security: high
  performance: medium
  style: low

# Ignore patterns
ignore:
  - "*.min.js"
  - "dist/**"
  - "build/**"
  - "node_modules/**"

# Custom rules
rules:
  - no-console-log
  - require-tests
  - max-function-length: 50
```

### User Configuration

Global configuration at `~/.config/coderabbit/config.json`:

```json
{
  "api_url": "https://api.coderabbit.ai",
  "default_profile": "chill",
  "output_format": "pretty",
  "auto_fix": false,
  "verbose": false
}
```

### Environment Variables

```bash
# API configuration
export CODERABBIT_API_URL="https://api.coderabbit.ai"
export CODERABBIT_API_TOKEN="your-token"

# Output configuration
export CODERABBIT_OUTPUT_FORMAT="json"
export CODERABBIT_VERBOSE="1"

# Review configuration
export CODERABBIT_PROFILE="strict"
export CODERABBIT_AUTO_FIX="false"
```

## Git Integration

### Git Hooks

#### Pre-Commit Hook

Automatically review before commits:

```bash
#!/bin/bash
# .git/hooks/pre-commit

echo "Running CodeRabbit review..."
coderabbit review --output=json > /tmp/pre-commit-review.json

# Check for critical issues
CRITICAL=$(jq '.summary.critical' /tmp/pre-commit-review.json)

if [ "$CRITICAL" -gt 0 ]; then
    echo "❌ CodeRabbit found $CRITICAL critical issues!"
    echo "Fix issues before committing, or run: git commit --no-verify"
    exit 1
fi

echo "✅ CodeRabbit review passed!"
exit 0
```

#### Pre-Push Hook

Review before pushing:

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "Running CodeRabbit review on commits to be pushed..."

# Get commits to be pushed
COMMITS=$(git log @{u}..HEAD --pretty=format:"%H")

# Review each commit
for commit in $COMMITS; do
    coderabbit review --commit=$commit
done
```

#### Install Hooks

```bash
# Automated installation
coderabbit hooks install

# Or manually
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### Git Aliases

Add to `.gitconfig`:

```gitconfig
[alias]
    # Review before committing
    review = !coderabbit review

    # Review and commit if clean
    commit-review = !bash -c 'coderabbit review && git commit'

    # Review specific commit
    review-commit = !bash -c 'coderabbit review --commit=$1'

    # Review PR changes
    review-pr = !bash -c 'coderabbit review --pr=$1'
```

Usage:

```bash
git review
git commit-review -m "Add feature"
git review-commit HEAD~1
git review-pr 123
```

## Team Workflows

### Workflow 1: Individual Developer

```bash
# 1. Start working on feature
git checkout -b feature/new-feature

# 2. Implement feature
# ... code ...

# 3. Review frequently during development
coderabbit review

# 4. Fix issues as you go
# ... fix code ...

# 5. Final review before commit
coderabbit review --output=json > review.json

# 6. If clean, commit
git add .
git commit -m "Add new feature"

# 7. Push and create PR
git push origin feature/new-feature
gh pr create
```

### Workflow 2: Code Review Process

```bash
# Reviewer workflow
# 1. Check out PR branch
gh pr checkout 123

# 2. Review the changes
coderabbit review --commit=HEAD~5..HEAD

# 3. Generate review summary
coderabbit review --output=json | jq '.summary' > review-summary.txt

# 4. Provide feedback in PR
gh pr comment 123 --body-file review-summary.txt
```

### Workflow 3: CI/CD Integration

```yaml
# .github/workflows/coderabbit-review.yml
name: CodeRabbit Review

on:
  pull_request:
    types: [opened, synchronize]

jobs:
  review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install CodeRabbit CLI
        run: |
          curl -fsSL https://raw.githubusercontent.com/kellerai/coderabbit/main/install-coderabbit-cli.sh | bash
          echo "$HOME/.local/bin" >> $GITHUB_PATH

      - name: Authenticate
        env:
          CODERABBIT_API_TOKEN: ${{ secrets.CODERABBIT_API_TOKEN }}
        run: |
          mkdir -p ~/.config/coderabbit
          echo "$CODERABBIT_API_TOKEN" > ~/.config/coderabbit/token

      - name: Run Review
        run: |
          coderabbit review --output=json > review-results.json
          cat review-results.json

      - name: Check for Critical Issues
        run: |
          CRITICAL=$(jq '.summary.critical' review-results.json)
          if [ "$CRITICAL" -gt 0 ]; then
            echo "::error::Found $CRITICAL critical issues"
            exit 1
          fi

      - name: Post Review Comment
        if: always()
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const review = JSON.parse(fs.readFileSync('review-results.json'));
            const summary = `## CodeRabbit Review\n\n${review.summary.text}`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });
```

### Workflow 4: Pre-Release Quality Gate

```bash
#!/bin/bash
# scripts/pre-release-check.sh

echo "Running pre-release quality checks..."

# Review all changes since last tag
LAST_TAG=$(git describe --tags --abbrev=0)
coderabbit review --commit=$LAST_TAG..HEAD --output=json > release-review.json

# Parse results
CRITICAL=$(jq '.summary.critical' release-review.json)
IMPORTANT=$(jq '.summary.important' release-review.json)

# Quality gate
if [ "$CRITICAL" -gt 0 ] || [ "$IMPORTANT" -gt 5 ]; then
    echo "❌ Quality gate failed!"
    echo "Critical issues: $CRITICAL"
    echo "Important issues: $IMPORTANT"
    exit 1
fi

echo "✅ Quality gate passed!"
exit 0
```

## Advanced Usage

### Custom Review Profiles

Create custom profiles in `.coderabbit/profiles/`:

```yaml
# .coderabbit/profiles/security-focused.yaml
name: security-focused
description: Enhanced security review

focus:
  security: critical
  performance: low
  style: none

checks:
  - sql-injection
  - xss-vulnerabilities
  - insecure-dependencies
  - hardcoded-secrets
  - weak-crypto
  - input-validation

severity_thresholds:
  block_on_critical: true
  block_on_important: false
```

Usage:

```bash
coderabbit review --profile=security-focused
```

### Automated Fix Suggestions

```bash
# Review with fix suggestions
coderabbit review --suggest-fixes

# Apply suggested fixes automatically
coderabbit review --auto-fix

# Review and fix interactively
coderabbit review --interactive
```

### Batch Reviews

```bash
# Review multiple commits
for commit in $(git log --pretty=format:"%H" HEAD~10..HEAD); do
    coderabbit review --commit=$commit --output=json > "review-$commit.json"
done

# Aggregate results
jq -s 'map(.summary) | add' review-*.json
```

### Diff-Based Reviews

```bash
# Review specific diff
git diff > changes.diff
coderabbit review --diff=changes.diff

# Review between branches
git diff main...feature-branch | coderabbit review --diff

# Review staged changes
git diff --cached | coderabbit review --diff
```

### Context-Aware Reviews

```bash
# Include knowledge base context
coderabbit review --context=.cursorrules --context=CLAUDE.md

# Use project-specific rules
coderabbit review --rules=.coderabbit/rules.yaml

# Include dependencies context
coderabbit review --with-dependencies
```

## Command Reference

### `coderabbit review`

Run code review on changes.

**Syntax:**
```bash
coderabbit review [options]
```

**Options:**
- `--commit=<ref>` - Review specific commit or range
- `--file=<path>` - Review specific file
- `--diff=<file>` - Review from diff file
- `--output=<format>` - Output format: pretty, json, markdown
- `--profile=<name>` - Use specific review profile
- `--config=<path>` - Use custom configuration
- `--suggest-fixes` - Include fix suggestions
- `--auto-fix` - Automatically apply fixes
- `--interactive` - Interactive fix mode
- `--verbose` - Verbose output
- `--quiet` - Minimal output

**Examples:**
```bash
coderabbit review
coderabbit review --commit=HEAD
coderabbit review --file=src/main.py --output=json
coderabbit review --profile=strict --suggest-fixes
```

### `coderabbit init`

Initialize CodeRabbit in repository.

**Syntax:**
```bash
coderabbit init [options]
```

**Options:**
- `--profile=<name>` - Initialize with specific profile
- `--template=<type>` - Use project template (python, typescript, react, nodejs)
- `--interactive` - Interactive configuration
- `--force` - Overwrite existing configuration

**Examples:**
```bash
coderabbit init
coderabbit init --template=python
coderabbit init --profile=strict --interactive
```

### `coderabbit config`

Manage configuration.

**Subcommands:**
- `show` - Display current configuration
- `validate` - Validate configuration file
- `edit` - Edit configuration
- `reset` - Reset to defaults

**Examples:**
```bash
coderabbit config show
coderabbit config validate
coderabbit config edit
```

### `coderabbit auth`

Manage authentication.

**Subcommands:**
- `login` - Authenticate with API token
- `logout` - Remove authentication
- `status` - Check authentication status
- `whoami` - Show current user
- `refresh` - Refresh token

**Examples:**
```bash
coderabbit auth login
coderabbit auth status
coderabbit auth whoami
```

### `coderabbit hooks`

Manage git hooks.

**Subcommands:**
- `install` - Install git hooks
- `uninstall` - Remove git hooks
- `list` - List installed hooks
- `enable` - Enable specific hook
- `disable` - Disable specific hook

**Examples:**
```bash
coderabbit hooks install
coderabbit hooks list
coderabbit hooks disable pre-push
```

### `coderabbit watch`

Continuous review mode.

**Syntax:**
```bash
coderabbit watch [options]
```

**Options:**
- `--interval=<seconds>` - Review interval
- `--on-save` - Review on file save
- `--files=<pattern>` - Watch specific files
- `--exclude=<pattern>` - Exclude files

**Examples:**
```bash
coderabbit watch
coderabbit watch --on-save
coderabbit watch --interval=300 --files="src/**/*.py"
```

### Global Options

Available for all commands:

- `--help, -h` - Show help
- `--version, -v` - Show version
- `--verbose` - Verbose output
- `--quiet` - Minimal output
- `--no-color` - Disable colored output
- `--config=<path>` - Custom config file

## Output Formats

### Pretty Format (Default)

Human-readable colored output:

```
╔═══════════════════════════════════════╗
║        CodeRabbit Review Results      ║
╚═══════════════════════════════════════╝

✓ Review completed successfully

Summary:
  Total Issues: 5
  ● Critical: 1
  ● Important: 2
  ● Minor: 2

Files Reviewed: 3

Issues:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
src/auth.py:42
● CRITICAL | Security
SQL injection vulnerability
Suggested fix: Use parameterized queries
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### JSON Format

Machine-readable structured output:

```json
{
  "status": "success",
  "summary": {
    "total_issues": 5,
    "critical": 1,
    "important": 2,
    "minor": 2,
    "files_reviewed": 3
  },
  "files": [
    {
      "path": "src/auth.py",
      "issues": [
        {
          "line": 42,
          "severity": "critical",
          "category": "security",
          "message": "SQL injection vulnerability",
          "suggestion": "Use parameterized queries",
          "code_snippet": "cursor.execute(f'SELECT * FROM users WHERE id={user_id}')"
        }
      ]
    }
  ]
}
```

### Markdown Format

Documentation-friendly output:

```markdown
# CodeRabbit Review Results

**Summary:** 5 issues found (1 critical, 2 important, 2 minor)

## Issues

### src/auth.py

#### Line 42 - Critical (Security)

**Issue:** SQL injection vulnerability

**Current Code:**
```python
cursor.execute(f'SELECT * FROM users WHERE id={user_id}')
```

**Suggested Fix:** Use parameterized queries

**Corrected Code:**
```python
cursor.execute('SELECT * FROM users WHERE id=?', (user_id,))
```
```

## Integration Examples

### With TaskMaster

```bash
# Start task
task-master next
task-master set-status --id=1.2 --status=in-progress

# Implement feature
# ...

# Review and log results
coderabbit review --output=json > review.json
task-master update-subtask --id=1.2 --prompt="Review found $(jq '.summary.total_issues' review.json) issues"

# Fix issues
# ...

# Complete task
task-master set-status --id=1.2 --status=done
```

### With Claude Code

See [claude-integration.md](./claude-integration.md) for complete integration guide.

```bash
# Use slash commands
/cr-review           # Run review
/cr-fix              # Implement fixes
/cr-cycle            # Complete autonomous cycle
```

### With VS Code

```json
// .vscode/tasks.json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "CodeRabbit Review",
      "type": "shell",
      "command": "coderabbit review",
      "group": "test",
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

## Best Practices

### 1. Review Frequency

- **During Development**: Review every 30-60 minutes
- **Before Commits**: Always review staged changes
- **Before PRs**: Comprehensive review of all changes
- **After Major Refactors**: Full project review

### 2. Fix Prioritization

```
Critical (P0) → Must fix before commit
Important (P1) → Fix before PR
Minor (P2) → Fix if time permits
```

### 3. Configuration Management

- Use central configuration for team consistency
- Override locally only when necessary
- Document configuration decisions
- Version control `.coderabbit.yaml`

### 4. CI/CD Integration

- Block PRs on critical issues
- Warn on important issues
- Report metrics to dashboard
- Archive review results

### 5. Team Adoption

- Start with `chill` profile
- Gradually increase strictness
- Provide training and documentation
- Collect feedback and iterate

## Tips and Tricks

### Quick Fixes

```bash
# Review only changed files
git diff --name-only | xargs coderabbit review --file

# Review with auto-fix for style issues
coderabbit review --auto-fix --profile=style-only

# Save review for later reference
coderabbit review --output=json > "review-$(date +%Y%m%d-%H%M%S).json"
```

### Performance

```bash
# Skip expensive checks
coderabbit review --skip=performance,complexity

# Review only critical categories
coderabbit review --only=security,bugs

# Fast mode (basic checks only)
coderabbit review --fast
```

### Debugging

```bash
# Verbose output
coderabbit review --verbose

# Debug mode
CODERABBIT_DEBUG=1 coderabbit review

# Dry run
coderabbit review --dry-run
```

## Next Steps

1. **Complete Team Onboarding**: Run `team-onboarding.sh`
2. **Configure Repository**: Create `.coderabbit.yaml`
3. **Install Git Hooks**: Run `coderabbit hooks install`
4. **Integrate with Claude Code**: See [claude-integration.md](./claude-integration.md)
5. **Set Up CI/CD**: Add CodeRabbit to your pipeline
6. **Review Troubleshooting Guide**: See [troubleshooting.md](./troubleshooting.md)

## Support

- **Documentation**: See `/docs` directory
- **Issues**: Check [troubleshooting.md](./troubleshooting.md)
- **Team Support**: Contact your team lead
- **Official Docs**: https://docs.coderabbit.ai

---

**Version**: 1.0.0
**Last Updated**: 2025-10-14
