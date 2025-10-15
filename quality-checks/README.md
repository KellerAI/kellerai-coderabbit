# Quality Checks Module

Comprehensive pre-merge quality validation system for the KellerAI CodeRabbit integration.

## Overview

This module provides automated quality gates that enforce organizational standards before code reaches production. It includes:

- **Security Checks**: Detect vulnerabilities and sensitive data exposure
- **Architecture Checks**: Enforce layered architecture patterns
- **Test Coverage Checks**: Ensure adequate testing for new code
- **Performance Checks**: Flag potential performance issues
- **Breaking Changes Checks**: Require documentation for API changes

## Module Structure

```
quality-checks/
├── __init__.py                      # Package exports
├── security_checks.py               # Security validation
├── architecture_checks.py           # Architecture compliance
├── test_coverage_checks.py          # Test coverage validation
├── performance_checks.py            # Performance analysis
├── breaking_changes_checks.py       # Breaking change detection
├── quality_orchestrator.py          # Orchestrates all checks
├── tests/                           # Comprehensive test suite
│   ├── test_security_checks.py
│   ├── test_architecture_checks.py
│   ├── test_test_coverage_checks.py
│   ├── test_performance_checks.py
│   ├── test_breaking_changes_checks.py
│   └── test_quality_orchestrator.py
└── README.md                        # This file
```

## Usage

### Basic Usage

```python
from quality_checks import QualityCheckOrchestrator

# Create orchestrator in warning mode (allow merge)
orchestrator = QualityCheckOrchestrator(mode="warning")

# Validate a PR
result = orchestrator.validate_pr(
    pr_title="feat(auth): add JWT authentication",
    pr_description="Implementing JWT auth system...",
    changed_files={
        "src/auth.py": "code content...",
        "tests/test_auth.py": "test content..."
    },
    old_files={
        "src/auth.py": "old code content..."  # For breaking change detection
    }
)

# Check results
if result.passed:
    print("✓ All quality checks passed!")
else:
    print(f"✗ Found {result.total_issues} issues")
    print(f"  Critical: {result.critical_issues}")
    print(f"  High: {result.high_issues}")
    print(f"  Medium: {result.medium_issues}")

# Generate report
report = orchestrator.generate_report(result)
print(report)

# Export as JSON
json_output = orchestrator.export_results_json(result)
```

### Error Mode (Block Merge)

```python
# Create orchestrator in error mode (block merge on failures)
orchestrator = QualityCheckOrchestrator(mode="error")

result = orchestrator.validate_pr(...)

if not result.passed:
    print("MERGE BLOCKED: Critical or high severity issues found")
    sys.exit(1)
```

### Individual Check Usage

```python
from quality_checks import SecurityValidator

# Use security validator independently
validator = SecurityValidator()

findings = validator.validate_file(
    "src/auth.py",
    "API_KEY = 'hardcoded_secret'"  # Will be flagged
)

for finding in findings:
    print(f"{finding.severity}: {finding.message}")
    print(f"  File: {finding.file_path}:{finding.line_number}")
    print(f"  Fix: {finding.suggested_fix}")
```

## Check Categories

### 1. Security Checks

**Detects:**
- Hardcoded credentials (API keys, passwords, tokens)
- SQL injection vulnerabilities
- Sensitive data logging (PII, credentials)
- Unsafe deserialization (pickle, eval, exec)

**Severity:** Critical/High  
**Mode:** Error (blocks merge)

**Example:**

```python
# ❌ FAILS Security Check
API_KEY = "sk_live_1234567890"
query = f"SELECT * FROM users WHERE email = '{user_email}'"
logger.info(f"Password: {password}")

# ✅ PASSES Security Check
API_KEY = os.getenv("API_KEY")
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (user_email,))
logger.info(f"User authenticated: {user_id}")
```

### 2. Architecture Checks

**Validates:**
- Layer separation (Controller → Service → Repository → Model)
- Dependency injection usage (FastAPI Depends)
- Async patterns (httpx instead of requests)
- Circular dependency detection

**Severity:** Medium/High  
**Mode:** Warning

**Example:**

```python
# ❌ FAILS Architecture Check
# In repositories/user_repository.py
from services.user_service import UserService  # Wrong direction!

# ✅ PASSES Architecture Check
# In services/user_service.py
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
```

### 3. Test Coverage Checks

**Requires:**
- Unit tests for new public functions
- Regression tests for bug fixes
- Test quality (assertions, fixtures)

**Severity:** Medium/High  
**Mode:** Error (for critical paths)

**Example:**

```python
# src/calculator.py
def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# tests/test_calculator.py - REQUIRED
def test_add_positive_numbers():
    assert add(2, 3) == 5

def test_add_negative_numbers():
    assert add(-2, -3) == -5
```

### 4. Performance Checks

**Detects:**
- N+1 query patterns
- Missing database indexes
- Inefficient algorithms (nested loops)
- Memory leaks (unbounded caches)

**Severity:** Medium/High  
**Mode:** Warning

**Example:**

```python
# ❌ FAILS Performance Check (N+1)
users = session.query(User).all()
for user in users:
    orders = session.query(Order).filter_by(user_id=user.id).all()

# ✅ PASSES Performance Check (Eager Loading)
users = session.query(User).options(selectinload(User.orders)).all()
for user in users:
    orders = user.orders  # Already loaded
```

### 5. Breaking Changes Checks

**Detects:**
- API signature changes (parameters, return types)
- Removed public methods/classes
- Database schema changes
- Requires CHANGELOG.md updates

**Severity:** High/Critical  
**Mode:** Error

**Example:**

```python
# ❌ FAILS Breaking Changes Check
# Old: def get_user(user_id: int) -> User
# New: def get_user(user_id: int, email: str) -> User
# REQUIRES: CHANGELOG.md update

# CHANGELOG.md
## [Unreleased]

### Breaking Changes
- **API**: `get_user()` now requires email parameter
- **Migration**: Update all calls to include email
```

## Configuration

Quality checks are configured in `.coderabbit.yaml`:

```yaml
quality_checks:
  enabled: true
  mode: warning  # or "error"
  
  # Built-in checks
  docstring_coverage:
    enabled: true
    threshold: 0.85
    
  # Custom checks
  custom_checks:
    security:
      enabled: true
      mode: error
    architecture:
      enabled: true
      mode: warning
    testing:
      enabled: true
      mode: error
    performance:
      enabled: true
      mode: warning
    breaking_changes:
      enabled: true
      mode: error
```

## Testing

Run the comprehensive test suite:

```bash
# Run all tests
pytest quality-checks/tests/ -v

# Run specific check tests
pytest quality-checks/tests/test_security_checks.py -v

# Run with coverage
pytest quality-checks/tests/ --cov=quality-checks --cov-report=html

# Run integration tests only
pytest quality-checks/tests/test_quality_orchestrator.py -v
```

## Development

### Adding a New Check

1. **Create Check Class** in appropriate file:

```python
# quality-checks/security_checks.py
class NewSecurityCheck:
    def check(self, file_path: str, content: str) -> List[SecurityFinding]:
        findings = []
        # Implementation
        return findings
```

2. **Add to Validator**:

```python
class SecurityValidator:
    def __init__(self):
        self.checks = [
            HardcodedCredentialsCheck(),
            SQLInjectionCheck(),
            NewSecurityCheck(),  # Add here
        ]
```

3. **Write Tests**:

```python
# quality-checks/tests/test_security_checks.py
class TestNewSecurityCheck:
    def test_detects_vulnerability(self):
        check = NewSecurityCheck()
        findings = check.check("file.py", "vulnerable code")
        assert len(findings) > 0
```

4. **Update Documentation**:
   - Add to this README
   - Update `docs/quality-checks-guide.md`
   - Add example to `.coderabbit.yaml`

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings (Google format)
- Keep functions focused and testable
- Use dataclasses for findings

## Integration

### CodeRabbit Integration

Quality checks are automatically run by CodeRabbit on every PR. Configuration is in `.coderabbit.yaml`.

### CI/CD Integration

```yaml
# .github/workflows/quality-checks.yml
name: Quality Checks

on: [pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run Quality Checks
        run: |
          python -m quality_checks.cli \
            --pr-title "${{ github.event.pull_request.title }}" \
            --pr-description "${{ github.event.pull_request.body }}" \
            --mode error
```

### Pre-commit Hook

```python
# .git/hooks/pre-commit
#!/usr/bin/env python3
from quality_checks import QualityCheckOrchestrator

orchestrator = QualityCheckOrchestrator(mode="warning")
# Run checks on staged files
```

## Override Mechanism

Quality checks can be overridden with justification:

```
# In PR comment
@coderabbitai ignore security-check --reason "This is test data only, no actual credentials"
```

**Requirements:**
- Justification ≥ 50 characters
- Logged in audit trail
- May require elevated permissions for security checks

## Performance

- **Average runtime**: < 5 seconds for typical PR
- **Parallel execution**: Checks run concurrently
- **Caching**: AST parsing cached per file
- **Scalability**: Tested with PRs up to 100 files

## Troubleshooting

### False Positives

If a check incorrectly flags valid code:

1. Use override mechanism with justification
2. Report false positive pattern to team
3. Pattern will be refined in check implementation

### Check Not Running

1. Verify `quality_checks.enabled: true` in config
2. Check file patterns match (not excluded)
3. Review check mode (`off`, `warning`, `error`)
4. Check CI/CD logs for errors

### Performance Issues

If checks are slow:

1. Check file size (very large files may take longer)
2. Review regex patterns for optimization
3. Consider excluding generated files
4. Use `mode: warning` during development

## Support

- **Documentation**: `docs/quality-checks-guide.md`
- **Issues**: GitHub Issues
- **Slack**: #code-quality channel
- **Email**: engineering@kellerai.com

## Version History

- **1.0.0** (2025-10-14): Initial release with 5 check categories
  - Security validation
  - Architecture compliance
  - Test coverage requirements
  - Performance analysis
  - Breaking changes detection

## License

Internal use only - KellerAI © 2025
