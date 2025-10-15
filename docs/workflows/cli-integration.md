# CodeRabbit CLI Workflow Integration Guide

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Comprehensive guide for Claude Code + CodeRabbit CLI workflows

---

## Executive Summary

CodeRabbit CLI transforms code review from a post-commit activity into an integrated development workflow. When combined with Claude Code, it enables autonomous implement-review-fix cycles that catch issues before they reach pull requests.

**Key Capabilities:**
- Pre-commit code reviews
- Integration with AI coding agents (Claude Code, Codex, Gemini)
- Autonomous quality gates
- Background execution for non-blocking workflows
- AI-optimized output formats

---

## Table of Contents

1. [Installation & Setup](#1-installation--setup)
2. [Core Workflow Patterns](#2-core-workflow-patterns)
3. [Claude Code Integration](#3-claude-code-integration)
4. [Command Reference](#4-command-reference)
5. [Optimization Guide](#5-optimization-guide)
6. [Troubleshooting](#6-troubleshooting)

---

## 1. Installation & Setup

### 1.1 CLI Installation

**macOS / Linux:**

```bash
# Install CodeRabbit CLI
curl -fsSL https://cli.coderabbit.ai/install.sh | sh

# Restart shell
source ~/.zshrc  # or source ~/.bashrc

# Verify installation
coderabbit --version
```

**Windows (WSL Recommended):**

CodeRabbit CLI has best support on WSL. See Windows setup guide in docs.

### 1.2 Authentication

**One-Time Setup:**

```bash
# Login to CodeRabbit
coderabbit auth login

# Opens browser for authentication
# Copy token from browser
# Paste token back to terminal

# Verify authentication
coderabbit auth status
```

**Output:**
```
✅ Authenticated as: developer@kellerai.com
   Organization: KellerAI
   Plan: Pro
   Token expires: 2025-11-14
```

**Note:** Authentication persists across sessions and works with Claude Code.

### 1.3 Repository Configuration

**Optional: Create `.coderabbit-cli.yaml`**

```yaml
# .coderabbit-cli.yaml (project root)

# Default review type
default_type: all  # all, committed, uncommitted

# Base branch for comparisons
base_branch: main

# Custom config files to include
config_files:
  - CLAUDE.md
  - .cursorrules

# Output preferences
output:
  no_color: false
  format: interactive  # interactive, plain, prompt-only
```

### 1.4 Shell Aliases (Recommended)

**Add to `~/.zshrc` or `~/.bashrc`:**

```bash
# CodeRabbit CLI shortcuts
alias cr='coderabbit'
alias crr='coderabbit --prompt-only'  # For AI agents
alias cru='coderabbit --type uncommitted'  # Quick check
alias crp='coderabbit --plain'  # Detailed output

# Claude Code + CodeRabbit workflow
alias crc='claude code'  # Quick Claude Code launch
```

Apply changes:
```bash
source ~/.zshrc
```

---

## 2. Core Workflow Patterns

### 2.1 Pre-Commit Review

**Use Case:** Catch issues before committing

**Workflow:**

```bash
# 1. Make changes to code
vim src/authentication.py

# 2. Review uncommitted changes
coderabbit --type uncommitted

# 3. Review findings
# [Interactive UI shows issues]

# 4. Fix issues

# 5. Re-run review
coderabbit --type uncommitted

# 6. Commit when clean
git add .
git commit -m "Add JWT authentication [AUTH-123]"
```

**Git Hook (Optional):**

```bash
# .git/hooks/pre-commit
#!/bin/bash

echo "🤖 Running CodeRabbit pre-commit review..."

coderabbit --type uncommitted --plain

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  CodeRabbit found issues. Review above."
    read -p "Commit anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Commit aborted. Fix issues and try again."
        exit 1
    fi
fi

echo "✅ Pre-commit review complete"
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 2.2 Feature Branch Review

**Use Case:** Review entire feature branch before creating PR

**Workflow:**

```bash
# 1. Complete feature on branch
git checkout -b feature/user-auth
# ... implement feature ...
git add .
git commit -m "Implement user authentication"

# 2. Review branch against main
coderabbit --base main --type all

# 3. Review comprehensive output
# [Shows all changes since branching from main]

# 4. Fix all issues found

# 5. Final check
coderabbit --base main --type all

# 6. Push when clean
git push origin feature/user-auth

# 7. Create PR (CodeRabbit will review again automatically)
```

### 2.3 Incremental Development

**Use Case:** Review during active development

**Workflow:**

```bash
# Start feature
git checkout -b feature/payment-processing

# Implement first part
vim src/payment/processor.py
coderabbit --type uncommitted  # Quick check
# Fix issues immediately

# Commit first part
git add src/payment/processor.py
git commit -m "Add payment processor base"

# Implement second part
vim src/payment/validator.py
coderabbit --type uncommitted  # Check new changes
# Fix issues

# Continue iterating...
```

**Benefits:**
- Catch issues early (while context is fresh)
- Smaller review scopes (faster)
- Learn from mistakes immediately

### 2.4 Bug Fix Validation

**Use Case:** Ensure bug fix doesn't introduce new issues

**Workflow:**

```bash
# 1. Create bug fix branch
git checkout -b fix/memory-leak-in-cache

# 2. Implement fix
vim src/cache/memory_manager.py

# 3. Review fix specifically
coderabbit --type uncommitted

# 4. Check for:
# - Fix addresses root cause
# - No new issues introduced
# - Appropriate error handling

# 5. Add regression test
vim tests/test_cache_memory.py

# 6. Final review
coderabbit --type uncommitted

# 7. Commit fix
git commit -am "Fix memory leak in cache manager [BUG-789]"
```

---

## 3. Claude Code Integration

### 3.1 Autonomous Implement-Review-Fix Cycle

**The Power Pattern:**

```
Developer → Claude Code → CodeRabbit → Claude Code → Clean Code
            (Implement)   (Review)      (Fix Issues)
```

**Example Prompt:**

```
Implement user authentication with JWT tokens from LINEAR-456.

After implementation:
1. Run coderabbit --prompt-only in the background
2. Let it run as long as needed (do NOT timeout)
3. Review all findings from CodeRabbit
4. Fix all critical and high-severity issues
5. Document any warnings that are intentional
6. Create a summary of changes and fixes applied

Focus areas for CodeRabbit review:
- Security (auth handling, token storage)
- Error handling completeness
- Test coverage for auth flows
```

**What Happens:**

1. **Claude Implements Feature**
   - Writes authentication code
   - Creates JWT token logic
   - Adds middleware
   - Implements login/logout

2. **Claude Runs CodeRabbit**
   ```bash
   coderabbit --prompt-only &
   ```
   - Runs in background
   - Doesn't block Claude
   - Generates AI-optimized output

3. **Claude Reads Results**
   - Parses CodeRabbit findings
   - Identifies critical issues
   - Creates fix plan

4. **Claude Applies Fixes**
   - Fixes security issues
   - Adds error handling
   - Improves test coverage
   - Documents intentional patterns

5. **Result:**
   - Feature implemented
   - All issues resolved
   - Code ready for PR

### 3.2 Prompt Templates

#### Template 1: Feature Implementation with Review

```
Implement [feature description] from [ISSUE-ID].

Requirements:
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

After implementation:
1. Run `coderabbit --prompt-only` in background
2. Allow full review time (up to 30 minutes if needed)
3. Review all CodeRabbit findings
4. Fix critical and high-severity issues
5. Document warnings that are acceptable
6. Provide summary of implementation and fixes

Review focus:
- [Focus area 1, e.g., "Security validation"]
- [Focus area 2, e.g., "Error handling"]
- [Focus area 3, e.g., "Test coverage"]
```

#### Template 2: Bug Fix with Validation

```
Fix bug described in [ISSUE-ID] where [bug description].

Root cause analysis needed:
- Identify why bug occurred
- Check for similar patterns elsewhere
- Add regression test

After fix:
1. Run `coderabbit --prompt-only` to validate
2. Ensure no new issues introduced
3. Verify test coverage for bug scenario
4. Check for similar issues in codebase

Provide:
- Root cause explanation
- Fix description
- Test strategy
- CodeRabbit validation results
```

#### Template 3: Refactoring with Quality Checks

```
Refactor [component] to [goal].

Objectives:
- [Objective 1]
- [Objective 2]

Constraints:
- Maintain API compatibility
- No behavior changes
- Improve performance/maintainability

Process:
1. Implement refactoring
2. Run `coderabbit --prompt-only --type all`
3. Verify no regressions introduced
4. Check all tests still pass
5. Document any intentional changes

Provide:
- Refactoring summary
- Performance/complexity improvements
- CodeRabbit validation
- Test results
```

### 3.3 Background Execution Best Practices

**Why Background Execution:**
- CodeRabbit reviews take 7-30+ minutes
- Claude can continue working
- Non-blocking development flow

**How to Ensure Background Execution:**

```
CRITICAL PROMPT PATTERN:

"Run coderabbit --prompt-only in the background.
Let it run as long as needed - do NOT timeout.
Check back periodically to see if it's complete."
```

**Checking Progress:**

```
# In Claude Code chat:
Is CodeRabbit finished running yet?

# Claude will check:
$ ps aux | grep coderabbit
# or
$ tail -f coderabbit-output.txt
```

**When Review Completes:**

Claude automatically:
1. Reads output file
2. Parses findings
3. Creates task list
4. Shows you the plan
5. Implements fixes systematically

### 3.4 Handling CodeRabbit Output

**Three Output Modes:**

**1. Interactive Mode (Default)**
```bash
coderabbit  # Interactive UI
```
- Browsable terminal UI
- Click to expand findings
- Apply fixes individually
- **Use:** Manual development

**2. Plain Text Mode**
```bash
coderabbit --plain
```
- Detailed text output
- All findings listed
- File paths and line numbers
- **Use:** Logging, CI/CD

**3. Prompt-Only Mode (AI-Optimized)**
```bash
coderabbit --prompt-only
```
- Token-efficient
- Natural language descriptions
- Structured for AI parsing
- **Use:** Claude Code integration

**Example Prompt-Only Output:**

```
CodeRabbit Review Results
=========================

Critical Issues (2):

1. Security Vulnerability - Hardcoded API Key
   File: src/config.py, Line 15
   Issue: API key hardcoded in source code
   Recommendation: Move to environment variable
   
2. SQL Injection Risk
   File: src/database/queries.py, Line 42
   Issue: String concatenation in SQL query
   Recommendation: Use parameterized query

Warnings (3):

1. Missing Error Handling
   File: src/api/users.py, Line 67
   Issue: Exception not caught in API endpoint
   Recommendation: Add try-catch with proper error response

[... more findings ...]

Summary:
- 2 Critical issues require immediate attention
- 3 Warnings should be addressed
- 5 Info items for consideration
- 12 files reviewed, 847 lines analyzed
```

Claude Code can easily parse this and create fixes.

### 3.5 Advanced Claude Code Workflows

#### Workflow 1: Multi-Stage Feature Development

```
Phase 1: Plan and Design
"Create architectural design for [feature] following our layered architecture.
Output design document with:
- Component structure
- API endpoints
- Database schema
- Integration points"

Phase 2: Implementation
"Implement the design from the document above.
Follow our coding standards from CLAUDE.md.
After implementation, run coderabbit --prompt-only and fix any issues."

Phase 3: Testing
"Create comprehensive tests for the implementation.
Include:
- Unit tests for all services
- Integration tests for API endpoints
- Edge case coverage
Run coderabbit to verify test quality."

Phase 4: Documentation
"Document the feature including:
- API documentation
- Usage examples
- Integration guide
Run final coderabbit review on everything."
```

#### Workflow 2: Continuous Quality Loop

```
# CLAUDE.md addition for continuous quality:

When implementing features:
1. Implement MVP functionality
2. Run coderabbit --prompt-only for initial review
3. Fix critical issues
4. Add test coverage
5. Run coderabbit again to verify tests
6. Refactor based on warnings
7. Final coderabbit check
8. Only then commit code

This ensures:
- Issues caught early
- Progressive quality improvement
- Clean commits
- Reduced PR review time
```

#### Workflow 3: Team Standard Enforcement

```yaml
# In CLAUDE.md:

## CodeRabbit Integration Standards

### When to Run CodeRabbit:
- Before every commit
- After implementing any feature
- After fixing any bug
- Before pushing to remote

### Required Checks:
- Zero critical issues
- All warnings acknowledged or fixed
- Test coverage >= 80%
- Security patterns validated

### Handling Warnings:
- Document why warning is acceptable, OR
- Fix the warning
- Never ignore warnings silently
```

---

## 4. Command Reference

### 4.1 Basic Commands

```bash
# Default review (interactive mode)
coderabbit

# Review with specific type
coderabbit --type all          # Committed + uncommitted (default)
coderabbit --type committed    # Only committed changes
coderabbit --type uncommitted  # Only uncommitted changes

# Review against specific branch
coderabbit --base main         # Compare against main
coderabbit --base develop      # Compare against develop

# Review against specific commit
coderabbit --base-commit abc123
```

### 4.2 Output Modes

```bash
# Interactive (default) - browsable UI
coderabbit

# Plain text - detailed output
coderabbit --plain

# Prompt-only - AI-optimized
coderabbit --prompt-only

# No colors (for logging)
coderabbit --no-color
```

### 4.3 Configuration Options

```bash
# Use custom config files
coderabbit --config claude.md .cursorrules

# Specify working directory
coderabbit --cwd /path/to/project

# Combine options
coderabbit --type uncommitted --plain --config claude.md
```

### 4.4 Authentication Commands

```bash
# Login (one-time)
coderabbit auth login

# Check status
coderabbit auth status

# Logout
coderabbit auth logout
```

### 4.5 Short Alias

All commands support `cr` shorthand:

```bash
cr                    # Same as: coderabbit
cr --prompt-only      # Same as: coderabbit --prompt-only
cr auth status        # Same as: coderabbit auth status
```

### 4.6 Complete Examples

**Example 1: Quick uncommitted check**
```bash
cr --type uncommitted
```

**Example 2: Feature branch review for AI**
```bash
cr --base main --prompt-only > review.txt
```

**Example 3: Review with custom config**
```bash
cr --config ~/team/.coderabbit-standards.md --plain
```

**Example 4: Check specific directory**
```bash
cr --cwd ~/projects/api-service --type uncommitted
```

---

## 5. Optimization Guide

### 5.1 Speed Optimization

**Problem:** Reviews take too long

**Solutions:**

#### 1. Scope Reduction

```bash
# Fast: Only uncommitted (2-5 min)
cr --type uncommitted

# Medium: Feature branch (5-15 min)
cr --base main --type committed

# Slow: Large staging branch (15-30+ min)
cr --base develop --type all
```

**Recommendation:** Review incrementally during development

#### 2. Smaller Changesets

```bash
# Instead of one large PR:
git checkout -b feature/auth-complete
# ... 2000 lines of changes ...
cr  # 30 minutes 😟

# Do incremental commits:
git checkout -b feature/auth-jwt
# ... 200 lines ...
cr  # 3 minutes ✅
git commit

git checkout -b feature/auth-middleware
# ... 150 lines ...
cr  # 2 minutes ✅
git commit
```

#### 3. Strategic Review Points

Review at logical checkpoints:

```
Component Complete → cr
Integration Point → cr
Before Commit → cr
Before Push → cr (optional)
```

### 5.2 Context Optimization

**Problem:** Reviews miss important context

**Solutions:**

#### 1. Custom Configuration Files

```bash
# Create review-focus.md
cat > review-focus.md << 'EOF'
# Review Focus

For this change, focus on:
1. Security: Authentication and authorization
2. Performance: Database query optimization
3. Testing: Coverage for auth flows

Ignore:
- Stylistic issues
- Documentation format
- Import ordering
EOF

# Use in review
cr --config review-focus.md
```

#### 2. Leverage Existing Standards

```bash
# CodeRabbit auto-reads these:
# - CLAUDE.md (if Pro plan)
# - .cursorrules
# - .github/copilot-instructions.md

# Just run review:
cr  # Automatically uses standards
```

#### 3. Paid Plan Benefits

| Feature | Free | Pro |
|---------|------|-----|
| Basic Analysis | ✅ | ✅ |
| Learnings | ❌ | ✅ |
| Context-Aware | ❌ | ✅ |
| Team Standards | ❌ | ✅ |
| Rate Limits | Low | High |

**Recommendation:** Pro plan for teams

### 5.3 Workflow Efficiency

**Pattern 1: Commit-Review Loop**

```bash
# Inefficient:
# Write code → commit → push → PR → CodeRabbit review → fix → repeat

# Efficient:
# Write code → cr → fix → commit → push → PR → quick final review
```

**Pattern 2: Incremental Quality**

```bash
#!/bin/bash
# save as: dev-loop.sh

while true; do
    # Watch for file changes
    inotifywait -r src/ -e modify
    
    # Quick review
    echo "🤖 Running quick CodeRabbit review..."
    cr --type uncommitted --plain | grep -E "(Critical|Error)" || true
    
    echo "✅ Review complete. Continue coding..."
done
```

**Pattern 3: Git Hooks Integration**

```bash
# .git/hooks/pre-commit
#!/bin/bash
cr --type uncommitted --no-color > /tmp/cr-review.txt
CRITICAL_COUNT=$(grep -c "Critical" /tmp/cr-review.txt || true)

if [ $CRITICAL_COUNT -gt 0 ]; then
    cat /tmp/cr-review.txt
    exit 1
fi
```

---

## 6. Troubleshooting

### 6.1 Common Issues

#### Issue: "Authentication required"

**Symptoms:**
```
❌ Error: Authentication required
   Run 'coderabbit auth login' to authenticate
```

**Solution:**
```bash
coderabbit auth login
# Follow browser authentication flow
```

**Note:** Must authenticate OUTSIDE Claude Code initially.

#### Issue: "No changes detected"

**Symptoms:**
```
ℹ️  No changes detected in repository
```

**Causes:**
- No git changes (staged or unstaged)
- Wrong working directory
- Git repository not initialized

**Solutions:**
```bash
# Check git status
git status

# Verify in git repo
git rev-parse --git-dir

# Specify correct directory
cr --cwd /correct/path
```

#### Issue: Review takes too long

**Symptoms:**
- Review running > 30 minutes
- No progress indicators

**Solutions:**

```bash
# 1. Check review is actually running
ps aux | grep coderabbit

# 2. Review smaller scope
cr --type uncommitted  # Instead of --type all

# 3. Review specific files
# (Not directly supported, but can stage specific files)
git add specific_file.py
cr --type uncommitted
```

#### Issue: Claude Code timeout

**Symptoms:**
Claude Code stops waiting for CodeRabbit review

**Solution in Prompt:**
```
Run coderabbit --prompt-only in the background.
IMPORTANT: Do NOT timeout. Let it run up to 30 minutes.
Check periodically: "Is CodeRabbit done?"
When complete, parse results and create fix plan.
```

#### Issue: False positives

**Symptoms:**
CodeRabbit flags intentional patterns as issues

**Solutions:**

**1. Add Learnings:**
```bash
# In PR comment (after pushing):
@coderabbitai this pattern is intentional because [reason]
@coderabbitai remember not to flag [pattern] in [context]
```

**2. Document in Code:**
```python
# CodeRabbit: This timeout is intentionally high for batch operations
BATCH_TIMEOUT = 300  # 5 minutes
```

**3. Update .coderabbit.yaml:**
```yaml
reviews:
  ignore_patterns:
    - "test_*.py:unused_variable"
    - "migrations/*.py:line_too_long"
```

### 6.2 Performance Troubleshooting

#### Review Timing Guidelines

| Scope | Expected Time | Acceptable |
|-------|--------------|------------|
| Uncommitted (small) | 2-5 min | 10 min |
| Feature branch | 5-15 min | 20 min |
| Large PR | 15-30 min | 45 min |

If exceeding "Acceptable", reduce scope.

#### Memory Issues

**Symptoms:**
- System slowdown during review
- Out of memory errors

**Solutions:**
```bash
# 1. Close other applications

# 2. Review in smaller pieces
cr --type uncommitted  # Only working directory

# 3. Increase system resources (Docker/VM)
```

### 6.3 Integration Issues

#### Claude Code Can't Run CodeRabbit

**Symptoms:**
```
Command not found: coderabbit
```

**Solutions:**

**1. Verify Installation:**
```bash
# Outside Claude Code:
which coderabbit
# Should output: /usr/local/bin/coderabbit
```

**2. Check PATH:**
```bash
echo $PATH | grep coderabbit
```

**3. Reinstall if needed:**
```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
source ~/.zshrc
```

**4. Test in Claude Code:**
```
# Ask Claude to run:
Run this command: which coderabbit
```

#### Authentication Expires

**Symptoms:**
```
❌ Token expired
```

**Solution:**
```bash
# Re-authenticate
coderabbit auth login
```

**Prevention:**
- Tokens last 30 days
- Set calendar reminder to refresh

---

## Appendix: Quick Reference

### Essential Commands

```bash
# Quick uncommitted review
cr --type uncommitted

# AI-optimized output
cr --prompt-only

# Feature branch review
cr --base main

# Check auth status
cr auth status
```

### Claude Code Prompt Pattern

```
Implement [feature] from [ISSUE-ID].

After implementation:
1. Run `coderabbit --prompt-only` in background
2. Let it run fully (up to 30 minutes)
3. Fix all critical issues
4. Document warnings
5. Provide summary

Focus: [security/performance/testing/etc.]
```

### Workflow Checklist

- [ ] Install CodeRabbit CLI
- [ ] Authenticate (`cr auth login`)
- [ ] Test basic review (`cr --type uncommitted`)
- [ ] Test Claude Code integration
- [ ] Set up shell aliases
- [ ] Add to team documentation
- [ ] Train team on workflows

---

## Summary

This guide provides:

1. ✅ **Installation & Setup**: Complete setup instructions
2. ✅ **Core Workflows**: Pre-commit, feature branch, incremental
3. ✅ **Claude Code Integration**: Autonomous implement-review-fix
4. ✅ **Command Reference**: All CLI options documented
5. ✅ **Optimization**: Speed and context improvements
6. ✅ **Troubleshooting**: Common issues and solutions

**Key Takeaways:**

- **CLI enables pre-commit reviews** (catch issues early)
- **Claude Code + CodeRabbit = autonomous quality** (implement-review-fix)
- **Use `--prompt-only` mode** for AI agent integration
- **Run in background** for non-blocking workflow
- **Review incrementally** for speed

**Next Steps:**

1. Install CLI on team machines
2. Test workflow with sample feature
3. Create team prompt templates
4. Document in team wiki
5. Train team on patterns
6. Measure time savings

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Integration & Tooling Research Agent  
**Status:** Complete
