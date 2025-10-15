# CodeRabbit Configuration Inheritance Model

## Overview

CodeRabbit uses a hierarchical configuration system that allows organization-wide defaults while providing flexibility for project-specific customization.

## Inheritance Hierarchy

```
┌─────────────────────────────────────────────┐
│ Organization Baseline                       │
│ (.coderabbit.yaml in kellerai/coderabbit)   │
│                                             │
│ - Global defaults for all repositories     │
│ - "Chill" review profile                   │
│ - Common language settings                 │
│ - Baseline quality thresholds              │
└──────────────────┬──────────────────────────┘
                   ↓ inherits from
┌─────────────────────────────────────────────┐
│ Project Template                            │
│ (templates/{type}/.coderabbit.yaml)         │
│                                             │
│ - Language-specific overrides              │
│ - Framework-specific patterns              │
│ - Technology-specific focus areas          │
└──────────────────┬──────────────────────────┘
                   ↓ inherits from
┌─────────────────────────────────────────────┐
│ Project Local Configuration                 │
│ (.coderabbit.yaml in your repository)       │
│                                             │
│ - Project-specific customizations          │
│ - Team preferences                         │
│ - Override specific settings               │
└─────────────────────────────────────────────┘
```

## Merge Rules

### 1. Object Merging (Deep Merge)

Objects are merged deeply, combining properties from all levels:

**Example: Reviews Configuration**

```yaml
# Organization Baseline
reviews:
  profile: chill
  high_level_summary: true
  focus:
    - security
    - performance

# Project Template (Python)
reviews:
  focus:
    - type_hints
    - pep8

# Result (Deep Merged)
reviews:
  profile: chill                  # from baseline
  high_level_summary: true        # from baseline
  focus:
    - security                    # from baseline
    - performance                 # from baseline
    - type_hints                  # from template
    - pep8                        # from template
```

### 2. Array Concatenation (Unique Values)

Arrays are concatenated, keeping only unique values:

**Example: File Exclusions**

```yaml
# Organization Baseline
reviews:
  scope:
    exclude:
      - "node_modules/**"
      - "dist/**"

# Project Local Config
reviews:
  scope:
    exclude:
      - "generated/**"
      - "vendor/**"

# Result (Concatenated)
reviews:
  scope:
    exclude:
      - "node_modules/**"      # from baseline
      - "dist/**"              # from baseline
      - "generated/**"         # from local
      - "vendor/**"            # from local
```

### 3. Primitive Override (Most Specific Wins)

Primitive values (strings, numbers, booleans) are overridden by more specific configurations:

**Example: Comment Limits**

```yaml
# Organization Baseline
comments:
  max_comments: 30
  style: auto
  tone: professional

# Project Local Config
comments:
  max_comments: 50
  style: detailed

# Result (Overridden)
comments:
  max_comments: 50          # overridden by local
  style: detailed           # overridden by local
  tone: professional        # inherited from baseline
```

## Inheritance Examples

### Example 1: Python Project Using Template

**Organization Baseline** (`kellerai/coderabbit/.coderabbit.yaml`):
```yaml
reviews:
  profile: chill
  auto_review:
    enabled: true

comments:
  max_comments: 30

languages:
  python:
    version: "3.11"
```

**Python Template** (`kellerai/coderabbit/templates/python/.coderabbit.yaml`):
```yaml
reviews:
  focus:
    - type_hints
    - pep8

languages:
  python:
    tools:
      - ruff
      - mypy
```

**Project Local Config** (`your-project/.coderabbit.yaml`):
```yaml
reviews:
  focus:
    - security  # Add security focus

languages:
  python:
    version: "3.12"  # Override Python version
```

**Final Effective Configuration**:
```yaml
reviews:
  profile: chill              # from baseline
  auto_review:
    enabled: true             # from baseline
  focus:
    - type_hints              # from template
    - pep8                    # from template
    - security                # from local

comments:
  max_comments: 30            # from baseline

languages:
  python:
    version: "3.12"           # overridden by local
    tools:                    # from template
      - ruff
      - mypy
```

### Example 2: React Project Without Template

**Organization Baseline** (`kellerai/coderabbit/.coderabbit.yaml`):
```yaml
reviews:
  profile: chill
  high_level_summary: true

comments:
  max_comments: 30

languages:
  typescript:
    version: "5.0"
```

**Project Local Config** (`your-react-app/.coderabbit.yaml`):
```yaml
reviews:
  focus:
    - react_best_practices
    - accessibility

comments:
  max_comments: 40

languages:
  typescript:
    focus:
      - hooks_usage
      - component_props
```

**Final Effective Configuration**:
```yaml
reviews:
  profile: chill                    # from baseline
  high_level_summary: true          # from baseline
  focus:
    - react_best_practices          # from local
    - accessibility                 # from local

comments:
  max_comments: 40                  # overridden by local

languages:
  typescript:
    version: "5.0"                  # from baseline
    focus:
      - hooks_usage                 # from local
      - component_props             # from local
```

## Configuration Scopes

### Organization Baseline Scope

**Best used for:**
- Organization-wide standards
- Common language settings
- Baseline quality thresholds
- Shared ignore patterns

**Should NOT contain:**
- Project-specific patterns
- Overly strict requirements
- Framework-specific rules

**Example:**
```yaml
# Good baseline settings
reviews:
  profile: chill                   # Reasonable default
  auto_review:
    enabled: true                  # Enable for all

comments:
  max_comments: 30                 # Conservative default

# Avoid in baseline
quality_checks:
  docstring_coverage:
    threshold: 0.95               # Too strict for baseline
```

### Template Scope

**Best used for:**
- Language-specific patterns
- Framework conventions
- Technology-specific tools
- Common project structures

**Should NOT contain:**
- Organization policies
- Project-specific paths
- Team preferences

**Example:**
```yaml
# Good template settings (Python)
languages:
  python:
    focus:
      - type_hints
      - pep8
    tools:
      - ruff
      - mypy

# Avoid in template
reviews:
  profile: assertive             # Organization policy
```

### Local Configuration Scope

**Best used for:**
- Project-specific customizations
- Team preferences
- Override thresholds
- Custom patterns

**Can override:**
- Any baseline setting
- Any template setting
- Quality thresholds

**Example:**
```yaml
# Good local overrides
reviews:
  focus:
    - database_queries           # Project-specific
    - api_compatibility          # Team concern

comments:
  max_comments: 50              # Team prefers more feedback

languages:
  python:
    patterns:
      - id: use-new-orm
        pattern: "OldORM\\("
        message: "Use NewORM instead"
        severity: warning
```

## Inheritance Best Practices

### 1. Start Minimal

Begin with organization baseline only, add customization as needed:

```bash
# Start with no local config
# CodeRabbit uses organization baseline

# Add config only if needed
# cp templates/python/.coderabbit.yaml .
```

### 2. Override Strategically

Only override what's necessary:

```yaml
# ❌ Don't copy entire baseline
reviews:
  profile: chill
  auto_review:
    enabled: true
  # ... 50 more lines

# ✅ Override only what changes
reviews:
  profile: assertive
```

### 3. Document Overrides

Explain why settings differ from baseline:

```yaml
reviews:
  profile: assertive  # Team prefers detailed feedback

comments:
  max_comments: 50    # Complex codebase needs more comments
```

### 4. Test Inheritance

Verify configuration merges correctly:

```bash
# Create test PR
git checkout -b test/config
echo "# Test" >> TEST.md
git add TEST.md
git commit -m "test: configuration inheritance"
git push -u origin test/config

# Check CodeRabbit review matches expectations
```

### 5. Use Templates Appropriately

Choose the right starting point:

```
No customization → Use baseline (no local config)
Language-specific → Use template
Complex custom → Start with template, customize
```

## Verifying Effective Configuration

### Method 1: Test PR

Create a test PR and observe CodeRabbit's behavior:

```bash
# Create test changes
git checkout -b test/verify-config
echo "def test(): pass" >> test.py
git add test.py
git commit -m "test: verify configuration"
git push -u origin test/verify-config
gh pr create --title "Test Configuration"
```

Check:
- Review profile (chill vs assertive)
- Number of comments
- Focus areas mentioned
- Quality checks triggered

### Method 2: Configuration Query

Check CodeRabbit's configuration detection:

```bash
# View detected configuration (if CodeRabbit CLI available)
coderabbit config show
```

### Method 3: GitHub Actions Logs

Review validation workflow logs:

```bash
# Check GitHub Actions workflow
gh run list --workflow=config-test.yml
gh run view <run-id> --log
```

## Troubleshooting Inheritance

### Issue: Local Config Not Applied

**Symptoms:**
- Reviews ignore local settings
- Baseline settings used instead

**Causes:**
1. YAML syntax error
2. Incorrect indentation
3. Typo in configuration key

**Solutions:**
```bash
# Validate YAML syntax
yamllint .coderabbit.yaml

# Check for common errors
grep -E "^\t" .coderabbit.yaml  # Check for tabs (should use spaces)
```

### Issue: Template Not Inherited

**Symptoms:**
- Template settings missing
- Only baseline applies

**Causes:**
1. Template not in correct location
2. Incorrect template reference

**Solutions:**
- Verify template path in kellerai/coderabbit repository
- Ensure CodeRabbit can access organization repository

### Issue: Unexpected Overrides

**Symptoms:**
- Settings don't match expectations
- Values from wrong level

**Causes:**
1. Primitive override unexpected
2. Array concatenation not understood

**Solutions:**
- Review merge rules above
- Use null to reset inherited values:

```yaml
# Reset inherited array
reviews:
  focus: null  # Clear all inherited focus areas
  focus:
    - security  # Start fresh
```

## Advanced Inheritance Patterns

### Conditional Inheritance

Use different configs for different environments:

```yaml
# .coderabbit.yaml
reviews:
  profile: chill  # Development default

# .coderabbit.production.yaml (branch-specific)
reviews:
  profile: assertive  # Stricter for production
```

### Partial Template Usage

Mix multiple templates:

```yaml
# Start with TypeScript template
# Add React-specific settings
reviews:
  focus:
    - type_safety      # from TypeScript
    - hooks_usage      # add React focus
```

### Gradual Enforcement

Start lenient, increase over time:

```yaml
# Phase 1: Warnings only
quality_checks:
  docstring_coverage:
    enabled: true
    threshold: 0.70
    mode: warning

# Phase 2: Increase threshold
quality_checks:
  docstring_coverage:
    threshold: 0.85

# Phase 3: Enforce
quality_checks:
  docstring_coverage:
    mode: error
```

## Summary

- **Three Levels**: Baseline → Template → Local
- **Merge Rules**: Deep merge objects, concatenate arrays, override primitives
- **Start Simple**: Use baseline, add customization as needed
- **Override Strategically**: Only change what's necessary
- **Test Thoroughly**: Verify inheritance with test PRs

For more examples, see:
- [Customization Guide](customization-guide.md)
- [Configuration Reference](configuration-reference.md)
- [Override Procedures](override-procedures.md)

---

**Last Updated**: 2025-10-14
**Maintained by**: KellerAI DevOps Team
