---
allowedTools:
  - Bash(coderabbit:*)
  - BashOutput
  - Read
  - Edit
  - Write
model: claude-sonnet-4-5-20250929
---

# CodeRabbit CLI Review with Iterative Improvement

Run CodeRabbit CLI review on uncommitted changes with automatic fix application until quality gates are met.

## Parameters

**Syntax**: `/coderabbit-review [--type=TYPE] [--config=PATH] [--max-cycles=N]`

- `--type`: Review scope (default: uncommitted)
  - `uncommitted` - Only unstaged/staged changes
  - `committed` - Last commit
  - `all` - All files
- `--config`: Path to custom .coderabbit.yaml (default: project root)
- `--max-cycles`: Maximum review iterations (default: 3)

## Workflow

### 1. Initial Review

Run CodeRabbit CLI review:
```bash
coderabbit review --plain --type=$TYPE
```

### 2. Issue Categorization

Parse results and categorize by severity:
- **P0 (Critical)**: Security vulnerabilities, breaking changes, critical bugs
- **P1 (Important)**: Bug risks, architectural issues, significant code quality problems
- **P2 (Minor)**: Style preferences, minor optimizations, documentation

### 3. Apply Fixes

For each issue (P0 first, then P1):
1. Read the affected file
2. Understand the issue and suggested fix
3. Apply the fix using Edit tool
4. Document the change

### 4. Re-run Review

After applying fixes, re-run CodeRabbit review to verify improvements.

### 5. Iteration Control

Continue until one of:
- ✅ **Quality gate passed**: 0 P0 issues, ≤2 P1 issues
- ⚠️ **Max cycles reached**: Stop after N iterations (default: 3)
- ❌ **No improvements**: Stop if issues don't decrease between cycles

### 6. Final Report

Provide summary:
- Issues found: P0 / P1 / P2 counts
- Fixes applied: count and description
- Quality gate status: PASS / FAIL
- Remaining issues: list if any

## Example Usage

```bash
# Review uncommitted changes (default)
/coderabbit-review

# Review specific scope
/coderabbit-review --type=committed

# Extended iteration cycles
/coderabbit-review --max-cycles=5

# Custom configuration
/coderabbit-review --config=.coderabbit-strict.yaml
```

## Quality Gate Criteria

**PASS** requires:
- Zero (0) P0 Critical issues
- Two (2) or fewer P1 Important issues
- Any number of P2 Minor issues acceptable

**FAIL** if:
- Any P0 Critical issues remain after max cycles
- More than 2 P1 Important issues remain

## Integration with Development Workflow

### Pre-Commit Hook
```bash
# Add to .git/hooks/pre-commit
/coderabbit-review --type=uncommitted --max-cycles=2
```

### Pre-PR Validation
```bash
# Before creating pull request
/coderabbit-review --type=all --max-cycles=3
```

### CI/CD Integration
See `.github/workflows/kb-validation.yml` for automated review integration.

## Notes

- Uses CodeRabbit CLI `--plain` mode for human-readable terminal output
- Applies fixes iteratively with automatic re-validation
- Stops when quality gates are met or max iterations reached
- Logs all applied fixes for audit trail
- Compatible with `.coderabbit.yaml` configuration inheritance

## Dependencies

**Task Master Dependencies**:
- Task 6: Install CodeRabbit CLI ✅
- Task 8: Configure .coderabbit.yaml ✅

**CLI Requirements**:
- CodeRabbit CLI installed (`coderabbit --version`)
- Authenticated (`coderabbit auth login --api-key`)
- Valid `.coderabbit.yaml` configuration file

---

**Version**: 1.0.0
**Created**: 2025-10-15
**Task**: 14 - Create CodeRabbit CLI slash command
