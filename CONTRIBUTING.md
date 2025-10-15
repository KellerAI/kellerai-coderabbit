# Contributing to KellerAI CodeRabbit Integration

Thank you for contributing to the KellerAI CodeRabbit integration project! This guide will help you understand our development workflow, coding standards, and contribution process.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Documentation Guidelines](#documentation-guidelines)
- [Pull Request Process](#pull-request-process)
- [Quality Gates](#quality-gates)
- [Review Process](#review-process)

---

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Focus on constructive feedback
- Collaborate openly and transparently
- Prioritize quality and maintainability
- Document decisions and rationale

---

## Getting Started

### Prerequisites

- **Python**: 3.13 or higher
- **Git**: Latest version
- **CodeRabbit CLI**: Installed via `./bin/install-coderabbit-cli.sh`
- **Development Tools**: pytest, ruff, mypy

### Initial Setup

1. **Clone and setup**
   ```bash
   git clone https://github.com/kellerai/coderabbit.git
   cd coderabbit
   ```

2. **Install dependencies**
   ```bash
   # Production dependencies only
   pip install -e .
   
   # Development dependencies (includes production deps)
   pip install -e ".[dev]"
   
   # All optional dependencies (dev + docs)
   pip install -e ".[dev,docs]"
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Run tests to verify setup**
   ```bash
   pytest quality-checks/tests/ -v
   ```

---

## Development Workflow

### Branch Strategy

- **Main Branch**: `main` - Production-ready code only
- **Feature Branches**: `feature/description` - New features
- **Fix Branches**: `fix/description` - Bug fixes
- **Docs Branches**: `docs/description` - Documentation updates

### Creating a Feature Branch

```bash
# Use the automated script
./scripts/create-feature-branch.sh feature-name

# Or manually
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

### Commit Message Format

Follow **Conventional Commits** specification:

```
type(scope): subject

body (optional)

footer (optional)
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(quality-checks): add memory leak detection to performance checks

fix(mcp-server): resolve caching issue in Context7 integration

docs(architecture): update MCP server deployment guide
```

---

## Coding Standards

### Python Code Style

We use **Ruff** for formatting, import sorting, and linting (replaces black, isort, and flake8).

**Format and lint your code before committing:**
```bash
# Format all Python files (replaces black + isort)
ruff format quality-checks/ mcp-servers/

# Lint and auto-fix issues (replaces flake8)
ruff check --fix quality-checks/ mcp-servers/

# Type check with mypy
mypy quality-checks/

# Or run all checks at once
ruff format quality-checks/ mcp-servers/ && \
ruff check --fix quality-checks/ mcp-servers/ && \
mypy quality-checks/
```

### Code Quality Rules

1. **Line Length**: Max 100 characters
2. **Docstrings**: Required for all public functions and classes (Google style)
3. **Type Hints**: Required for function signatures
4. **Complexity**: Max cyclomatic complexity of 10
5. **Imports**: Grouped and sorted (stdlib, third-party, local)

### Example Code

```python
"""Module for security vulnerability checks."""

from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class SecurityIssue:
    """Represents a detected security issue.
    
    Attributes:
        severity: Issue severity (critical, high, medium, low)
        description: Human-readable description
        line_number: Line where issue was detected
        recommendation: Suggested fix
    """
    severity: str
    description: str
    line_number: int
    recommendation: Optional[str] = None


def detect_hardcoded_credentials(code: str) -> List[SecurityIssue]:
    """Detect hardcoded credentials in source code.
    
    Args:
        code: Source code to analyze
        
    Returns:
        List of detected security issues
        
    Example:
        >>> code = 'API_KEY = "sk-123456"'
        >>> issues = detect_hardcoded_credentials(code)
        >>> len(issues)
        1
    """
    issues: List[SecurityIssue] = []
    # Implementation here
    return issues
```

---

## Testing Requirements

### Test Coverage

- **Minimum Coverage**: 80% overall
- **Quality Checks**: 90% coverage required
- **New Features**: Must include tests
- **Bug Fixes**: Must include regression tests

### Running Tests

```bash
# Run all tests
pytest quality-checks/tests/ -v

# Run with coverage
pytest quality-checks/tests/ --cov=quality_checks --cov-report=html

# Run specific test file
pytest quality-checks/tests/test_security_checks.py -v

# Run specific test
pytest quality-checks/tests/test_security_checks.py::test_detect_hardcoded_credentials -v
```

### Writing Tests

**Test Structure:**
```python
"""Tests for security checks module."""

import pytest
from quality_checks.security_checks import detect_hardcoded_credentials, SecurityIssue


class TestHardcodedCredentials:
    """Tests for hardcoded credential detection."""
    
    def test_detects_api_key_in_variable(self):
        """Should detect API key in variable assignment."""
        code = 'API_KEY = "sk-abc123def456"'
        issues = detect_hardcoded_credentials(code)
        
        assert len(issues) == 1
        assert issues[0].severity == "critical"
        assert "API_KEY" in issues[0].description
    
    def test_ignores_test_fixtures(self):
        """Should not flag test fixtures as vulnerabilities."""
        code = '''
        @pytest.fixture
        def mock_api_key():
            return "test-key-12345"
        '''
        issues = detect_hardcoded_credentials(code)
        
        assert len(issues) == 0
```

**Test Markers:**
```python
@pytest.mark.unit
def test_basic_functionality():
    """Unit test for basic functionality."""
    pass

@pytest.mark.integration
def test_integration_workflow():
    """Integration test for complete workflow."""
    pass

@pytest.mark.slow
def test_performance_benchmark():
    """Slow test for performance benchmarking."""
    pass
```

---

## Documentation Guidelines

### Documentation Standards

1. **README Files**: Every directory should have a README.md
2. **Inline Documentation**: All public APIs must have docstrings
3. **Architecture Docs**: Use ASCII diagrams for portability
4. **Examples**: Include practical, runnable code examples
5. **Updates**: Update docs in the same PR as code changes

### Docstring Format (Google Style)

```python
def analyze_performance(code: str, threshold: int = 10) -> Dict[str, Any]:
    """Analyze code for performance issues.
    
    Performs static analysis to detect common performance anti-patterns
    including N+1 queries, nested loops, and algorithm complexity issues.
    
    Args:
        code: Source code to analyze
        threshold: Maximum acceptable complexity (default: 10)
        
    Returns:
        Dictionary containing:
            - issues: List of detected performance issues
            - complexity_score: Overall complexity rating (0-100)
            - recommendations: List of suggested optimizations
            
    Raises:
        ValueError: If code is empty or threshold is invalid
        
    Example:
        >>> code = "for x in items:\\n    db.query(x)"
        >>> result = analyze_performance(code)
        >>> result['issues'][0]['type']
        'n_plus_one_query'
        
    Note:
        This is a static analysis tool and may produce false positives.
        Review all findings before making changes.
    """
    pass
```

### Documentation Checklist

- [ ] README.md updated if directory structure changes
- [ ] Docstrings added for new functions/classes
- [ ] Code examples included and tested
- [ ] Architecture diagrams updated if applicable
- [ ] CHANGELOG.md updated for breaking changes
- [ ] API documentation generated (`mkdocs build`)

---

## Pull Request Process

### Before Creating a PR

1. **Update from main**
   ```bash
   git checkout main
   git pull origin main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run full test suite**
   ```bash
   pytest quality-checks/tests/ --cov=quality_checks
   ```

3. **Format and lint code**
   ```bash
   ruff format quality-checks/ mcp-servers/
   ruff check --fix quality-checks/ mcp-servers/
   mypy quality-checks/
   ```

4. **Review your changes**
   ```bash
   git diff main...your-feature-branch
   ```

### PR Requirements

**Title Format:**
```
type(scope): Brief description

Example: feat(security): add SQL injection detection
```

**PR Description Template:**
```markdown
## Summary
Brief overview of changes (2-3 sentences)

## Changes Made
- Bullet list of specific changes
- Each change on its own line
- Use past tense (Added, Fixed, Updated)

## Testing
- Describe how you tested the changes
- Include test commands and results
- Note any edge cases tested

## Documentation
- List documentation updates
- Link to updated docs if applicable

## Breaking Changes
- List any breaking changes
- Include migration guide if needed

## Related Issues
Closes #123
Related to #456
```

### PR Checklist

Before submitting, ensure:

- [ ] Code follows project style guide (Ruff formatting + linting)
- [ ] All tests pass (`pytest quality-checks/tests/`)
- [ ] Test coverage meets requirements (≥80%)
- [ ] New tests added for new features
- [ ] Docstrings added for new public APIs
- [ ] Documentation updated
- [ ] Commit messages follow Conventional Commits
- [ ] PR title follows format: `type(scope): description`
- [ ] PR description is complete and clear
- [ ] No merge conflicts with main branch
- [ ] Self-review completed

---

## Quality Gates

### Automated Quality Checks

Every PR triggers automated quality checks:

1. **Security Checks**
   - Hardcoded credentials detection
   - SQL injection patterns
   - Unsafe deserialization
   - Sensitive data logging

2. **Architecture Checks**
   - Layer separation validation
   - Dependency injection compliance
   - Circular dependency detection

3. **Testing Checks**
   - New functions have tests
   - Bug fixes include regression tests
   - Test quality validation

4. **Performance Checks**
   - N+1 query detection
   - Algorithm complexity analysis
   - Memory leak patterns

5. **Breaking Changes Checks**
   - API signature changes
   - Removed public methods
   - Database schema changes

### Passing Quality Gates

**If checks fail:**
1. Review CodeRabbit's comments on your PR
2. Fix the identified issues
3. Push updates to your branch
4. Quality checks will re-run automatically

**Override Process:**
If you need to override a check, use:
```
@coderabbitai ignore <check-name> --reason "Detailed justification (50+ chars)"
```

See [docs/workflows/override-process-guide.md](docs/workflows/override-process-guide.md) for details.

---

## Review Process

### Review Timeline

- **Initial Review**: Within 1 business day
- **Follow-up Reviews**: Within 4 hours
- **Approval**: Requires 1 approval from tech lead
- **Merge**: Automated after approval and quality gates pass

### Reviewer Guidelines

**As a reviewer:**

1. **Review Scope**
   - Code quality and style
   - Test coverage and quality
   - Documentation completeness
   - Security implications
   - Performance impact

2. **Feedback Style**
   - Be constructive and specific
   - Explain the "why" behind suggestions
   - Distinguish between required changes and suggestions
   - Acknowledge good work

3. **Comment Types**
   ```
   REQUIRED: Must be addressed before merge
   SUGGESTION: Optional improvement
   QUESTION: Seeking clarification
   PRAISE: Positive feedback
   ```

**Example Reviews:**
```markdown
REQUIRED: Add input validation for the `threshold` parameter.
Without validation, negative values could cause unexpected behavior.

SUGGESTION: Consider extracting this logic into a separate function.
It would improve testability and reusability.

QUESTION: Why did we choose to use a dictionary here instead of a dataclass?
Just curious about the design decision.

PRAISE: Excellent test coverage! The edge cases are well thought out.
```

### Addressing Review Feedback

1. **Respond to all comments**
   - Mark resolved when addressed
   - Explain if you disagree (respectfully)
   - Ask for clarification if needed

2. **Push updates**
   ```bash
   git add .
   git commit -m "fix: address review feedback"
   git push origin your-feature-branch
   ```

3. **Re-request review**
   - Use GitHub's "Re-request review" button
   - Or comment: "@reviewer ready for re-review"

---

## Additional Resources

### Documentation

- **Architecture**: [docs/architecture/](docs/architecture/)
- **Workflows**: [docs/workflows/](docs/workflows/)
- **Quality Gates**: [docs/quality-gates/](docs/quality-gates/)
- **Standards**: [docs/standards/](docs/standards/)

### Tools

- **CodeRabbit CLI**: [docs/workflows/cli-integration.md](docs/workflows/cli-integration.md)
- **MCP Servers**: [docs/architecture/mcp-servers.md](docs/architecture/mcp-servers.md)
- **TaskMaster**: [.taskmaster/CLAUDE.md](.taskmaster/CLAUDE.md)

### Communication

- **Slack**: #coderabbit-feedback
- **Email**: engineering@kellerai.com
- **GitHub Issues**: Use for bugs and feature requests

---

## Questions?

If you have questions about contributing:

1. Check existing documentation in [docs/](docs/)
2. Search closed PRs for similar examples
3. Ask in Slack #coderabbit-feedback
4. Create a GitHub issue with the `question` label

---

**Thank you for contributing to KellerAI's code quality initiative!**

Last Updated: 2025-10-14
