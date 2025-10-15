# Quality Gates Quick Reference

**Quick guide for developers** - For complete documentation see `docs/quality-checks-guide.md`

## What Are Quality Gates?

Automated checks that run on every PR to ensure code quality, security, and architecture compliance **before merge**.

## Current Status

- **Phase**: 1 - Warning Mode (first 2 weeks)
- **Mode**: Warnings shown, merge allowed
- **Target**: 95% compliance by Phase 4

## Common Quality Check Failures

### 1. Security: Hardcoded Credentials ❌

```python
# WRONG
API_KEY = "sk_live_abc123"

# CORRECT
import os
API_KEY = os.getenv("API_KEY")
```

### 2. Security: SQL Injection ❌

```python
# WRONG
query = f"SELECT * FROM users WHERE email = '{email}'"

# CORRECT
query = "SELECT * FROM users WHERE email = ?"
cursor.execute(query, (email,))
```

### 3. Architecture: Wrong Layer Dependency ❌

```python
# WRONG - Repository importing Controller
# In repositories/user_repo.py
from api.controllers import UserController

# CORRECT - Service importing Repository
# In services/user_service.py
from repositories.user_repository import UserRepository
```

### 4. Architecture: Missing Dependency Injection ❌

```python
# WRONG
@router.post("/users")
async def create_user(data: UserCreate):
    service = UserService()  # Direct instantiation
    
# CORRECT
@router.post("/users")
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
```

### 5. Testing: Missing Tests ❌

```python
# src/payment.py
def process_payment(amount: float) -> bool:
    return True

# REQUIRED: tests/test_payment.py
def test_process_payment_valid_amount():
    assert process_payment(100.0) == True

def test_process_payment_zero_amount():
    with pytest.raises(ValueError):
        process_payment(0)
```

### 6. Performance: N+1 Query ❌

```python
# WRONG
users = db.query(User).all()
for user in users:
    orders = db.query(Order).filter_by(user_id=user.id).all()

# CORRECT
from sqlalchemy.orm import selectinload
users = db.query(User).options(selectinload(User.orders)).all()
for user in users:
    orders = user.orders
```

### 7. Breaking Changes: Missing CHANGELOG ❌

```python
# Changed API signature
# Old: def get_user(user_id: int) -> User
# New: def get_user(user_id: int, email: str) -> User

# REQUIRED: Update CHANGELOG.md
## [Unreleased]

### Breaking Changes
- **API**: get_user() now requires email parameter
- **Migration**: Update all calls to include email
```

## PR Title Format

**Required format**: `type(scope): description`

Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`

```
✅ feat(auth): add JWT authentication
✅ fix(database): resolve connection pool leak
❌ Added new feature
❌ fix bug
```

## How to Override a Check

When you have a valid reason (false positive, special case):

```
@coderabbitai ignore <check-name> --reason "Detailed justification (min 50 chars)"
```

**Example:**
```
@coderabbitai ignore hardcoded-credentials --reason "This is a public test API key from the vendor's documentation, no production access"
```

**Requirements:**
- Justification ≥ 50 characters
- Explain WHY override is needed
- Security checks require tech lead approval

## Available Override Check Names

- `docstring-coverage`
- `pr-description`
- `issue-reference`
- `hardcoded-credentials` (requires approval)
- `sql-injection` (requires approval)
- `layer-separation`
- `dependency-injection`
- `new-functions-tests`
- `n-plus-one`
- `database-indexes`
- `algorithm-complexity`

**Cannot override:**
- `pr-title-format`
- `api-signature-changes`
- `removed-public-methods`

## Quality Check Results

After PR is created, CodeRabbit will comment with results:

```markdown
## Quality Check Results

✅ Security: No issues found
⚠️  Architecture: 2 warnings
  - services/user_service.py:15 - Consider using dependency injection
  - repositories/order_repo.py:42 - Avoid importing from service layer
  
❌ Testing: 1 error
  - src/payment.py:process_payment - No test found for new function
```

## What Happens in Each Phase?

| Phase | Weeks | Mode | Behavior |
|-------|-------|------|----------|
| **1** | 1-2 | Warning | Issues shown, merge allowed |
| **2** | 3-4 | Warning | More checks enabled |
| **3** | 5 | Warning + Preview | See what would block |
| **4** | 6+ | **Error** | Critical issues **block merge** |

## Getting Help

- **Docs**: `docs/quality-checks-guide.md`
- **Slack**: #code-quality
- **Examples**: `quality-checks/tests/`
- **False Positive?** Report in Slack

## Quick Tips

1. **Run tests before pushing** - Catch issues early
2. **Use environment variables** - Never hardcode secrets
3. **Follow layer architecture** - Controller → Service → Repository → Model
4. **Write tests** - Every new function needs tests
5. **Document breaking changes** - Update CHANGELOG.md
6. **Use async libraries** - httpx not requests in async code
7. **Add database indexes** - All foreign keys need indexes
8. **Check PR title** - Follow conventional commits format

## Common Questions

**Q: Why did my PR get flagged?**  
A: Check the CodeRabbit comment for specific issues and suggested fixes.

**Q: Can I merge if checks fail?**  
A: In warning mode (current), yes. In error mode (Phase 4), no.

**Q: How do I fix a false positive?**  
A: Use override with justification, then report the pattern.

**Q: Do I need tests for private functions?**  
A: No, only public functions (no leading underscore).

**Q: What's the difference between warning and error mode?**  
A: Warning shows issues but allows merge. Error blocks merge.

## Resources

- Complete Guide: `docs/quality-checks-guide.md`
- Configuration: `.coderabbit.yaml`
- Code Standards: `docs/standards/coding-standards.yaml`
- Quality Dashboard: https://quality.kellerai.com

---

**Last Updated**: 2025-10-14  
**Current Phase**: 1 - Warning Mode  
**Questions?** Ask in #code-quality Slack channel
