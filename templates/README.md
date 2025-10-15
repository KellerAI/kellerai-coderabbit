# CodeRabbit Configuration Templates

This directory contains project-specific configuration templates that extend the organization-wide baseline CodeRabbit configuration.

## Available Templates

### 1. TypeScript Template (`typescript/`)
For TypeScript projects with focus on type safety and modern TS patterns.

**Use for:**
- Pure TypeScript libraries
- TypeScript Node.js backends
- TypeScript utility packages

**Key Features:**
- Type safety enforcement (90% coverage)
- TSDoc documentation requirements
- Strict mode compliance checks
- Async/await pattern validation

### 2. Python Template (`python/`)
For Python projects with focus on type hints and PEP 8 compliance.

**Use for:**
- Python libraries
- FastAPI/Flask backends
- Django applications
- Python CLI tools

**Key Features:**
- Type hint coverage (80%)
- Docstring coverage (85%)
- PEP 8 compliance
- Security pattern checks

### 3. React Template (`react/`)
For React applications with focus on hooks, components, and performance.

**Use for:**
- React web applications
- React Native projects
- Next.js applications

**Key Features:**
- Hooks usage validation
- Component design patterns
- Performance optimization checks
- Accessibility (WCAG AA) compliance

### 4. Node.js Template (`nodejs/`)
For Node.js backend services with focus on async patterns and API design.

**Use for:**
- Express.js APIs
- NestJS applications
- Node.js microservices
- GraphQL servers

**Key Features:**
- Async/await pattern enforcement
- API design validation
- Security checks (dependency vulnerabilities)
- Error handling patterns

## How to Use Templates

### Option 1: Copy Template (Recommended)
1. Navigate to your project root
2. Copy the appropriate template:
   ```bash
   cp /path/to/kellerai/coderabbit/templates/{template-type}/.coderabbit.yaml .
   ```
3. Customize as needed for your project

### Option 2: Extend via Git Submodule
```bash
# Add central config as submodule
git submodule add https://github.com/kellerai/coderabbit .coderabbit-central

# Symlink or reference the template
ln -s .coderabbit-central/templates/{template-type}/.coderabbit.yaml .
```

### Option 3: Use Organization Baseline (No Template)
If your project doesn't need customization, simply don't include a local `.coderabbit.yaml`. CodeRabbit will automatically use the organization baseline from `kellerai/coderabbit` repository.

## Template Inheritance Model

Templates inherit from the organization baseline using deep merge:

```
Organization Baseline (.coderabbit.yaml)
  ↓ (inherits + overrides)
Template (.coderabbit.yaml in templates/{type}/)
  ↓ (inherits + overrides)
Project Local Config (.coderabbit.yaml in your repo)
```

**Merge Rules:**
- **Objects**: Deep merge (nested keys combine)
- **Arrays**: Concatenate unique values
- **Primitives**: Override (project > template > baseline)

## Customizing Templates for Your Project

After copying a template, you can override specific settings:

### Example: Adjust Review Intensity

```yaml
# In your project's .coderabbit.yaml
reviews:
  profile: assertive  # Override from 'chill' to 'assertive'

comments:
  max_comments: 50    # Increase from template default
```

### Example: Add Project-Specific Patterns

```yaml
# In your project's .coderabbit.yaml
languages:
  python:
    patterns:
      # Add custom pattern specific to your project
      - id: custom-validation
        pattern: "process_data\\("
        message: "Use the new process_data_v2() function"
        severity: warning
```

### Example: Adjust Quality Thresholds

```yaml
# In your project's .coderabbit.yaml
quality_checks:
  docstring_coverage:
    threshold: 0.95  # Increase from 0.85 to 0.95
```

## Template Development Guidelines

When contributing new templates or updating existing ones:

1. **Test Inheritance**: Use the config-test workflow to validate
2. **Document Overrides**: Add comments explaining why settings differ from baseline
3. **Provide Examples**: Include usage examples in template comments
4. **Follow Naming**: Use technology names (typescript, python, react, nodejs)

## Testing Your Configuration

After applying a template, test it:

```bash
# Validate YAML syntax
yamllint .coderabbit.yaml

# Test with CodeRabbit CLI (if available)
coderabbit config validate

# Create a test PR to see CodeRabbit in action
```

## Template Maintenance

Templates are maintained by:
- **Primary Owner**: Tech Leads (@kellerai/tech-leads)
- **Contributors**: All developers can propose improvements
- **Review Process**: PR with approval from tech lead required

## Getting Help

- **Questions**: Open discussion in #code-reviews Slack channel
- **Issues**: Create issue in kellerai/coderabbit repository
- **Custom Templates**: Reach out to tech leads for guidance

## Version History

- **v1.0** (2025-10-14): Initial templates for TypeScript, Python, React, Node.js
- Future versions will be tracked in CHANGELOG.md

---

**Maintained by**: KellerAI DevOps Team
**Last Updated**: 2025-10-14
