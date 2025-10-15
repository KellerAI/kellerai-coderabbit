# KellerAI CodeRabbit Central Configuration Repository

> This document describes the central configuration repository structure that should be created as `kellerai/coderabbit` on GitHub.

## Repository Purpose

The `kellerai/coderabbit` repository serves as the central configuration source for CodeRabbit automated code reviews across all KellerAI projects. It provides:

- **Organization Baseline**: Default settings applied to all repositories
- **Project Templates**: Language-specific configurations (TypeScript, Python, React, Node.js)
- **Automated Validation**: GitHub Actions for configuration testing
- **Comprehensive Documentation**: Usage guides and customization examples

## Quick Start

### For New Projects

No setup required! CodeRabbit automatically applies the organization baseline to any repository without a local `.coderabbit.yaml` file.

### For Existing Projects

Choose one of three approaches:

1. **Use Baseline** (no local config) - Organization defaults apply automatically
2. **Apply Template** - Copy language-specific template for customization
3. **Custom Config** - Create project-specific configuration

## Configuration Inheritance

```
Organization Baseline (.coderabbit.yaml in kellerai/coderabbit)
  ↓ inherits from
Project Template (templates/{type}/.coderabbit.yaml)
  ↓ inherits from
Project Local Config (.coderabbit.yaml in your repo)
```

**Merge Behavior:**
- Objects: Deep merge (combine nested properties)
- Arrays: Concatenate unique values
- Primitives: Override (most specific wins)

## Available Templates

### TypeScript Template
**Best for**: TypeScript libraries, TS Node.js backends
- 90% type coverage enforcement
- TSDoc documentation requirements
- Async/await pattern validation

### Python Template
**Best for**: Python libraries, FastAPI/Flask/Django apps
- 80% type hint coverage
- 85% docstring coverage
- PEP 8 compliance

### React Template
**Best for**: React web apps, React Native, Next.js
- Hooks validation
- Component design patterns
- WCAG AA accessibility

### Node.js Template
**Best for**: Express/NestJS APIs, microservices
- Async/await pattern enforcement
- API design validation
- Security checks

## Repository Structure

```
kellerai/coderabbit/
├── .github/
│   ├── workflows/           # CI/CD workflows
│   ├── CODEOWNERS          # Code ownership
│   └── PULL_REQUEST_TEMPLATE.md
├── templates/              # Project templates
│   ├── typescript/
│   ├── python/
│   ├── react/
│   └── nodejs/
├── docs/                   # Documentation
│   ├── configuration-reference.md
│   ├── inheritance-model.md
│   ├── customization-guide.md
│   └── override-procedures.md
├── scripts/                # Validation scripts
├── .coderabbit.yaml       # Organization baseline
├── README.md              # Main documentation
└── REPOSITORY_SETUP.md    # Setup guide
```

## Key Features

### Baseline Configuration
- **Review Profile**: "Chill" (balanced feedback)
- **Auto-review**: Enabled for non-draft PRs
- **High-level Summaries**: Quick PR understanding
- **Language Support**: Python, TypeScript, JavaScript

### Automated Validation
- **YAML Syntax**: Validates all configuration files
- **Inheritance Testing**: Ensures templates merge correctly
- **Deployment Notifications**: Alerts team of changes

### Quality Framework
- **Docstring Coverage**: 85% threshold
- **Type Hints**: Language-specific requirements
- **Security Checks**: Pattern-based vulnerability detection
- **Performance**: N+1 query detection, complexity analysis

## Usage Examples

### Copy Template to Project

```bash
# Navigate to project
cd /path/to/your/project

# Copy appropriate template
cp /path/to/kellerai/coderabbit/templates/python/.coderabbit.yaml .

# Commit
git add .coderabbit.yaml
git commit -m "Add CodeRabbit configuration"
```

### Customize Configuration

```yaml
# .coderabbit.yaml in your project
# Inherits from organization baseline

# Override review intensity
reviews:
  profile: assertive  # Change from 'chill' to 'assertive'

comments:
  max_comments: 50    # Increase from default 30

# Add project-specific patterns
languages:
  python:
    patterns:
      - id: use-new-api
        pattern: "old_function\\("
        message: "Use new_function() instead"
        severity: warning
```

### Enable Quality Checks

```yaml
quality_checks:
  enabled: true

  docstring_coverage:
    enabled: true
    threshold: 0.90  # 90% required

  pr_title_format:
    enabled: true
    pattern: "^(feat|fix|docs):"
```

## Testing Configuration

### Local Validation

```bash
# Check YAML syntax
yamllint .coderabbit.yaml

# Run validation script
./scripts/validate-yaml.sh
```

### Create Test PR

```bash
# Create test branch
git checkout -b test/coderabbit-config

# Make small change
echo "# Test" >> TEST.md

# Create PR
git add TEST.md
git commit -m "test: CodeRabbit configuration"
git push -u origin test/coderabbit-config
```

CodeRabbit should review within 5 minutes.

## Contributing

### Contribution Process

1. **Create Issue**: Describe proposed change
2. **Get Approval**: Tech leads review
3. **Create Branch**: `feature/your-change`
4. **Test Changes**: Run validation scripts
5. **Create PR**: 2 tech lead approvals required
6. **Merge**: After all checks pass

### Requirements

- ✅ YAML syntax validation passes
- ✅ Configuration tests pass
- ✅ Documentation updated
- ✅ 2 tech lead approvals
- ✅ All GitHub Actions green

## Support

### Getting Help

- **Slack**: #code-reviews channel
- **Issues**: Create in kellerai/coderabbit repo
- **Documentation**: See docs/ directory
- **Tech Leads**: Direct message for urgent issues

### Common Issues

**CodeRabbit not reviewing:**
- Check if PR is in draft mode
- Verify configuration syntax
- Confirm GitHub App permissions

**Configuration not applied:**
- Check for local config overrides
- Wait 5 minutes for cache refresh
- Validate YAML syntax

**Reviews too verbose/brief:**
```yaml
reviews:
  profile: chill  # or 'assertive'
comments:
  max_comments: 30
  style: auto  # or 'brief', 'detailed'
```

## Maintenance

### Maintainers

- **Tech Leads**: Configuration approval
- **DevOps Team**: Infrastructure and automation
- **Security Team**: Security configuration review

### Update Schedule

- **Monthly**: Review baseline configuration
- **Quarterly**: Update project templates
- **As Needed**: Bug fixes and urgent changes

## Version History

- **v1.0** (2025-10-14): Initial release
  - Baseline organization configuration
  - TypeScript, Python, React, Node.js templates
  - GitHub Actions validation workflows
  - Comprehensive documentation

---

**Repository**: github.com/kellerai/coderabbit
**Maintained by**: KellerAI DevOps Team
**Last Updated**: 2025-10-14
