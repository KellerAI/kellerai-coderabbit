# Quality Checks Guide

## Overview

CodeRabbit quality checks provide automated pre-merge validation to ensure code quality, security, architecture compliance, test coverage, performance, and proper documentation of breaking changes.

**Current Status**: Phase 1 - Warning Mode (14 days)
**Target Compliance**: 95% by Phase 4

---

## Table of Contents

1. [Built-in Quality Checks](#built-in-quality-checks)
2. [Custom Quality Checks](#custom-quality-checks)
3. [Execution Modes](#execution-modes)
4. [Override Mechanism](#override-mechanism)
5. [Gradual Rollout Plan](#gradual-rollout-plan)
6. [Troubleshooting](#troubleshooting)

---

## Built-in Quality Checks

### 1. Docstring Coverage (85% threshold)

**Enabled**: Yes
**Mode**: Warning
**Threshold**: 85%

**Requirements**:
- All public functions, classes, and modules must have docstrings
- Follow Google docstring format
- Include Args, Returns, Raises, and Examples sections

**Excluded**:
- Test files (`tests/**`)
- Migration files (`migrations/**`)
- `__init__.py` files
- Script files (`scripts/**`)

**Example**:
```python
def calculate_total(items: list[Item]) -> Decimal:
    """
    Calculate the total price of all items.

    Args:
        items: List of Item objects with price attributes

    Returns:
        Total price as Decimal

    Raises:
        ValueError: If items list is empty

    Examples:
        >>> items = [Item(price=10.50), Item(price=20.00)]
        >>> calculate_total(items)
        Decimal('30.50')
    """
    if not items:
        raise ValueError("Items list cannot be empty")
    return sum(item.price for item in items)
```

### 2. PR Title Format

**Enabled**: Yes
**Mode**: Error (always enforced)
**Pattern**: Conventional Commits

**Format**: `type(scope): description`

**Valid Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions or changes
- `chore`: Build process or auxiliary tool changes
- `build`: Build system changes
- `ci`: CI configuration changes

**Examples**:
- ✅ `feat(auth): add JWT authentication`
- ✅ `fix(database): resolve connection pool exhaustion`
- ✅ `docs: update API documentation`
- ❌ `Added new feature` (missing type)
- ❌ `fix bug` (too vague)

### 3. PR Description Required

**Enabled**: Yes
**Mode**: Warning
**Min Length**: 100 characters

**Required Sections**:
- `## Summary`
- `## Changes`
- `## Testing`

**Use the PR template** (`.github/PULL_REQUEST_TEMPLATE.md`)

### 4. Issue Reference Required

**Enabled**: Yes
**Mode**: Warning
**Pattern**: `(ENG|PROD|INFRA)-\d+`

**Requirements**:
- Link to Linear issue in PR description or title
- Format: `ENG-123`, `PROD-45`, `INFRA-67`

**Exceptions** (allowed without issue link):
- `docs:` - Documentation changes
- `chore:` - Maintenance tasks
- `style:` - Code formatting

**Example**:
```markdown
Fixes ENG-123

## Summary
This PR implements JWT authentication for the API.
```

### 5. Automated Issue Assessment

**Enabled**: Yes
**Mode**: Warning

**Validates**:
- PR scope matches linked Linear issue
- All requirements in issue are addressed
- Changes align with issue description

---

## Custom Quality Checks

### Security Checks (Mode: Error)

#### 1. Hardcoded Credentials

**Severity**: Critical
**Detects**:
- API keys
- Passwords
- AWS credentials
- Tokens
- Private keys
- Database credentials
- OAuth/JWT secrets

**Example Violation**:
```python
# ❌ BAD
API_KEY = "sk-1234567890abcdef"
DB_PASSWORD = "my_secret_pass"

# ✅ GOOD
import os
API_KEY = os.getenv("API_KEY")
DB_PASSWORD = os.getenv("DB_PASSWORD")
```

#### 2. SQL Injection

**Severity**: Critical
**Detects**:
- String concatenation in SQL queries
- F-strings in SQL
- Unparameterized queries

**Example Violation**:
```python
# ❌ BAD
cursor.execute(f"SELECT * FROM users WHERE email = '{user_email}'")

# ✅ GOOD
cursor.execute("SELECT * FROM users WHERE email = %s", (user_email,))
```

#### 3. Sensitive Data Logging

**Severity**: High
**Detects**:
- Logging of passwords, tokens, secrets
- Logging of PII (SSN, credit cards, etc.)

**Example Violation**:
```python
# ❌ BAD
logger.info(f"User password: {user.password}")

# ✅ GOOD
logger.info(f"User authentication successful for {user.id}")
```

#### 4. Unsafe Deserialization

**Severity**: Critical
**Detects**:
- `pickle.loads()` on untrusted data
- `yaml.load()` without Loader
- `eval()` and `exec()`

**Example Violation**:
```python
# ❌ BAD
data = pickle.loads(untrusted_data)

# ✅ GOOD
import json
data = json.loads(untrusted_data)
```

---

### Architecture Checks (Mode: Warning)

#### 1. Layer Separation

**Severity**: Medium
**Validates**: Layered architecture compliance

**Rules**:
- Controller → Service → Repository → Model
- No reverse dependencies
- No circular dependencies

**Example Violation**:
```python
# ❌ BAD: Repository importing from Service
# In repositories/user_repository.py
from services.user_service import UserService  # Violation!

# ✅ GOOD: Use dependency injection
# In api/user_controller.py
from services.user_service import UserService
from repositories.user_repository import UserRepository

service = UserService(UserRepository())
```

#### 2. Dependency Injection

**Severity**: Medium
**Requires**: FastAPI `Depends()` in controllers/API routes

**Example Violation**:
```python
# ❌ BAD
@app.get("/users")
def get_users():
    service = UserService()  # Direct instantiation
    return service.get_all()

# ✅ GOOD
@app.get("/users")
def get_users(service: UserService = Depends()):
    return service.get_all()
```

#### 3. Async Patterns

**Severity**: Medium
**Requires**: Async libraries for I/O in async functions

**Example Violation**:
```python
# ❌ BAD
async def fetch_data():
    response = requests.get(url)  # Blocks event loop!
    return response.json()

# ✅ GOOD
async def fetch_data():
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.json()
```

---

### Test Coverage Checks (Mode: Warning)

#### 1. New Functions Have Tests

**Severity**: Medium
**Requires**: Test file with `test_<function_name>` for new functions

**Example**:
```python
# src/services/calculator.py
def add_numbers(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b

# tests/services/test_calculator.py
def test_add_numbers():
    """Test add_numbers function."""
    assert add_numbers(2, 3) == 5
```

#### 2. Bug Fix Regression Tests

**Severity**: High
**Requires**: New tests for PRs with `fix:` prefix

**Rationale**: Prevent bugs from reoccurring

---

### Performance Checks (Mode: Warning)

#### 1. N+1 Query Detection

**Severity**: High
**Detects**: Database queries inside loops

**Example Violation**:
```python
# ❌ BAD - N+1 query
users = session.query(User).all()
for user in users:
    posts = session.query(Post).filter_by(user_id=user.id).all()  # N queries!

# ✅ GOOD - Eager loading
users = session.query(User).options(joinedload(User.posts)).all()
for user in users:
    posts = user.posts  # Already loaded
```

#### 2. Missing Database Indexes

**Severity**: Medium
**Requires**: Indexes on foreign keys

**Example Violation**:
```python
# ❌ BAD
user_id = Column(Integer, ForeignKey('users.id'))

# ✅ GOOD
user_id = Column(Integer, ForeignKey('users.id'), index=True)
```

#### 3. Algorithm Complexity

**Severity**: Medium
**Detects**: Nested loops, inefficient operations

**Example Violation**:
```python
# ❌ BAD - O(n²)
for item1 in items:
    for item2 in items:
        if item1.id == item2.related_id:
            process(item1, item2)

# ✅ GOOD - O(n) using dict
items_by_id = {item.id: item for item in items}
for item in items:
    if item.related_id in items_by_id:
        process(item, items_by_id[item.related_id])
```

---

### Breaking Changes Checks (Mode: Error)

#### 1. API Signature Changes

**Severity**: High
**Requires**: CHANGELOG.md update

**Example**:
```markdown
## [Unreleased]

### CHANGED
- **API**: `get_user(user_id)` signature changed to `get_user(user_id, include_deleted=False)`.
  This is backwards compatible with default parameter.
```

#### 2. Removed Public Methods

**Severity**: Critical
**Requires**: CHANGELOG.md with BREAKING CHANGES section

**Example**:
```markdown
## [Unreleased]

### BREAKING CHANGES
- **Removed**: `UserService.delete_user()` method. Use `UserService.deactivate_user()` instead.
```

---

## Execution Modes

### Warning Mode (Current - Phase 1)

- Issues are **reported** but do not block merge
- Team learns about quality standards
- Feedback is provided for improvement
- PRs can still be merged

**Purpose**: Training and adoption

### Error Mode (Phase 4 - After 5 weeks)

- Critical and High severity issues **block merge**
- Medium and Low severity issues are warnings
- Breaking changes **must** be documented
- Security issues **cannot** be merged

**Purpose**: Enforce quality standards

---

## Override Mechanism

### When to Use Overrides

- **False Positives**: Check incorrectly flags valid code
- **Special Cases**: Legitimate exceptions to rules
- **Technical Debt**: Temporary acceptance with plan to fix

### Override Command Format

```
@coderabbitai ignore <check-name> --reason "<justification>"
```

**Requirements**:
- Justification must be ≥50 characters
- Must explain WHY override is needed
- Logged in audit trail

### Available Check Names

**Built-in**:
- `docstring-coverage`
- `pr-title-format` (cannot override)
- `pr-description`
- `issue-reference`

**Security** (requires elevated permissions):
- `hardcoded-credentials`
- `sql-injection`
- `sensitive-data-logging`
- `unsafe-deserialization`

**Architecture**:
- `layer-separation`
- `dependency-injection`
- `async-patterns`

**Testing**:
- `new-functions-tests`
- `bug-fix-regression`

**Performance**:
- `n-plus-one`
- `database-indexes`
- `algorithm-complexity`

**Breaking Changes** (cannot override):
- `api-signature-changes`
- `removed-public-methods`

### Permission Levels

**Tech Leads** (kellerai/tech-leads):
- Can override all non-security checks
- Override is logged

**Admins/Security Team** (kellerai/admins, kellerai/security-team):
- Can override security checks
- Requires strong justification
- Override is audited

### Example Override

```
@coderabbitai ignore hardcoded-credentials --reason "This is a public test API key provided by the vendor for development environments only. It has no access to production data and is documented in their public documentation."
```

**Logged as**:
```json
{
  "user": "john.doe",
  "timestamp": "2025-10-14T10:30:00Z",
  "check_name": "hardcoded-credentials",
  "justification": "This is a public test API key...",
  "pr_number": 123,
  "pr_title": "feat(api): add payment integration"
}
```

---

## Gradual Rollout Plan

### Phase 1: Initial Rollout (Weeks 1-2)

**Mode**: Warning
**Target Compliance**: 50%

**Focus**:
- Team training on quality standards
- Documentation and examples
- Gather feedback on false positives

### Phase 2: Training Phase (Weeks 3-4)

**Mode**: Warning
**Target Compliance**: 75%

**Focus**:
- Address common issues
- Refine check patterns
- Build team habits

### Phase 3: Enforcement Preparation (Week 5)

**Mode**: Warning with enforcement preview
**Target Compliance**: 90%

**Focus**:
- Final adjustments
- Preview error mode behavior
- Ensure team readiness

### Phase 4: Full Enforcement (Week 6+)

**Mode**: Error
**Target Compliance**: 95%

**Focus**:
- Enforce quality gates
- Monitor compliance metrics
- Continuous improvement

---

## Troubleshooting

### Issue: Too many false positives

**Solution**:
1. Use override mechanism with justification
2. Report false positive patterns to team
3. Patterns will be refined in configuration

### Issue: Don't understand why check failed

**Solution**:
1. Read the check message and suggested fix
2. Review this documentation
3. Check example code in guide
4. Ask in #code-quality Slack channel

### Issue: Need to merge urgently despite failures

**Solution**:
1. Use override mechanism (requires tech lead approval)
2. Create follow-up issue to address violations
3. Link follow-up issue in override justification

### Issue: Check is blocking valid code

**Solution**:
1. Verify code is actually correct
2. Check if there's a better pattern (suggested fix)
3. If truly a false positive, use override
4. Report pattern for exclusion in future

---

## Metrics and Reporting

### Tracked Metrics

- **Compliance Rate**: % of PRs passing all checks
- **Override Frequency**: How often overrides are used
- **Check Failure Rate**: Which checks fail most often
- **Time to Fix**: How long to resolve issues

### Weekly Reports

Reports are generated automatically and shared in:
- #code-quality Slack channel
- Email to engineering leadership
- Quality dashboard (Grafana)

### Compliance Dashboard

View real-time compliance at: `https://quality.kellerai.com`

**Metrics**:
- Current compliance rate
- Trending over time
- Top failing checks
- Team performance

---

## Resources

- **Configuration**: `.coderabbit.yaml`
- **Code Standards**: `docs/standards/coding-standards.yaml`
- **Approved Patterns**: `docs/standards/approved-patterns.yaml`
- **Quality Checks Source**: `quality-checks/`
- **Support**: #code-quality Slack channel
- **Issues**: [GitHub Issues](https://github.com/kellerai/coderabbit/issues)

---

## Feedback and Improvements

Quality checks are continuously improved based on team feedback.

**How to provide feedback**:
1. Report false positives in #code-quality
2. Suggest new checks via GitHub issues
3. Request pattern refinements
4. Share success stories

**Quality Check Updates**: Configuration is versioned and changes are communicated via:
- Slack announcements
- CHANGELOG.md
- Team meetings

---

**Last Updated**: 2025-10-14
**Version**: 1.0.0
**Status**: Phase 1 - Warning Mode
