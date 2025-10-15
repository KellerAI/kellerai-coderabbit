# CodeRabbit Pre-merge Checks Specification

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Complete specification for quality gates and pre-merge validation

---

## Executive Summary

Pre-merge checks act as automated quality gates enforcing organizational standards before code reaches production. CodeRabbit provides 4 built-in checks and supports unlimited custom checks defined in natural language.

**Key Benefits:**
- Consistent standards enforcement
- Early issue detection (before merge)
- Reduced manual review burden
- Automated compliance checking
- Team-specific guardrails

---

## Table of Contents

1. [Built-in Checks Configuration](#1-built-in-checks-configuration)
2. [Custom Checks Library](#2-custom-checks-library)
3. [Enforcement Strategy](#3-enforcement-strategy)
4. [Implementation Examples](#4-implementation-examples)
5. [Testing & Validation](#5-testing--validation)
6. [Best Practices](#6-best-practices)

---

## 1. Built-in Checks Configuration

### 1.1 Docstring Coverage Check

**Purpose:** Ensure adequate code documentation for maintainability

**Configuration:**

```yaml
# .coderabbit.yaml
reviews:
  pre_merge_checks:
    docstrings:
      mode: "error"  # Block merge if fails
      threshold: 85  # 85% minimum coverage
```

**What It Checks:**
- Functions with docstrings vs total functions
- Class documentation
- Module-level docstrings
- Parameter and return value documentation

**Calculation:**
```
Coverage = (Functions with docstrings / Total public functions) × 100
```

**Pass Criteria:**
- Coverage >= threshold (85%)
- All public APIs documented
- Critical modules at 100%

**Exemptions:**
- Private functions (leading underscore)
- Test files
- Simple getters/setters (if configured)
- Legacy code (with @legacy decorator)

**Example Pass:**
```python
def calculate_total(items: List[Item]) -> Decimal:
    """Calculate total price for items including tax.
    
    Args:
        items: List of items to calculate total for
        
    Returns:
        Total price including tax as Decimal
        
    Raises:
        ValueError: If items list is empty
    """
    if not items:
        raise ValueError("Cannot calculate total for empty items")
    return sum(item.price for item in items) * Decimal("1.10")
```

**Example Fail:**
```python
def calculate_total(items):  # ❌ No docstring
    return sum(item.price for item in items) * 1.10
```

**Recommended Settings by Project Type:**

| Project Type | Threshold | Mode |
|-------------|-----------|------|
| Library/SDK | 95% | error |
| API Service | 85% | error |
| Internal Tool | 75% | warning |
| Prototype | 60% | warning |

### 1.2 PR Title Validation

**Purpose:** Standardize PR titles for clarity and traceability

**Configuration:**

```yaml
reviews:
  pre_merge_checks:
    title:
      mode: "warning"
      requirements: |
        PR titles must follow these rules:
        1. Start with imperative verb: Add, Fix, Update, Remove, Refactor, Improve
        2. Keep under 60 characters for readability
        3. Include issue reference in format [ISSUE-123] or (ISSUE-123)
        4. Use sentence case, not Title Case
        5. No trailing period
        
        Examples:
        ✅ Add user authentication with JWT [AUTH-456]
        ✅ Fix memory leak in data processor [BUG-789]
        ❌ Added new feature (past tense)
        ❌ fix bug (not capitalized)
        ❌ This is a very long title that exceeds the 60 character limit significantly
```

**Validation Logic:**
1. Check imperative verb (whitelist: Add, Fix, Update, Remove, Refactor, Improve, Optimize, Implement)
2. Character count <= 60
3. Regex for issue reference: `\[(ISSUE|PROJ)-\d+\]`
4. First character uppercase, rest lowercase (except acronyms)
5. No trailing punctuation

**Pass Examples:**
```
✅ Add JWT authentication middleware [AUTH-123]
✅ Fix race condition in payment processor [BUG-456]
✅ Update API documentation for v2 endpoints [DOC-789]
✅ Remove deprecated legacy authentication [TECH-012]
```

**Fail Examples:**
```
❌ Added new feature (past tense, no issue ref)
❌ fix bug (not capitalized)
❌ Implement the complete user authentication system with OAuth2, JWT tokens, and refresh token rotation [AUTH-123] (too long)
❌ Update docs. (trailing period)
```

**Recommended Mode:**
- **warning**: Allow overrides with explanation
- **error**: Only if strictly enforced organizationally

### 1.3 PR Description Validation

**Purpose:** Ensure PRs have complete context and documentation

**Configuration:**

```yaml
reviews:
  pre_merge_checks:
    description:
      mode: "error"  # Require proper descriptions
```

**What It Checks:**
- Description follows GitHub/GitLab PR template
- All required sections completed
- Minimum content length (not just template)
- Links to issues/tickets
- Test plan included

**Standard PR Template:**

```markdown
## Summary
<!-- Brief overview of changes (2-3 sentences) -->

## Changes
<!-- Bullet list of specific changes -->
- Change 1
- Change 2

## Issue Reference
<!-- Link to issue/ticket -->
Fixes #123
Related to #456

## Test Plan
<!-- How to test these changes -->
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Breaking Changes
<!-- Any breaking changes? If none, write "None" -->
None

## Screenshots/Videos
<!-- If UI changes, add screenshots -->
```

**Pass Criteria:**
- All sections present (not just template)
- Summary >= 50 characters
- At least one change listed
- Issue reference present
- Test plan completed (checkboxes checked)

**Example Pass:**
```markdown
## Summary
This PR implements JWT-based authentication to replace the legacy session-based auth system. Includes token refresh mechanism and proper error handling.

## Changes
- Implement JWT token generation and validation
- Add refresh token rotation
- Update login/logout endpoints
- Add authentication middleware
- Migrate existing session data

## Issue Reference
Fixes #AUTH-123
Related to #SEC-456

## Test Plan
- [x] Unit tests for token generation/validation
- [x] Integration tests for login/logout flow
- [x] Manual testing with Postman
- [x] Security review completed

## Breaking Changes
Session-based authentication endpoints are deprecated. Clients must update to use JWT tokens. Migration guide: docs/migration-auth.md
```

**Example Fail:**
```markdown
## Summary
Updated auth

## Changes
- stuff

## Test Plan
Tested it
```

**Recommended Mode:** `error` (proper documentation is critical)

### 1.4 Issue Assessment Check

**Purpose:** Ensure PRs address linked issues without scope creep

**Configuration:**

```yaml
reviews:
  pre_merge_checks:
    issue_assessment:
      mode: "warning"  # Inform but don't block
```

**What It Checks:**
1. **Issue Linkage**: PR references at least one issue
2. **Scope Alignment**: Changes relate to linked issue requirements
3. **Out-of-Scope Detection**: Identifies unrelated changes
4. **Requirement Coverage**: All issue acceptance criteria addressed

**Validation Process:**

```
1. Extract issue references from PR (title/description/commits)
2. Fetch issue details from tracking system (Jira/Linear/GitHub)
3. Analyze PR diff (files changed, lines modified)
4. Compare PR changes to issue requirements
5. Flag out-of-scope changes
6. Report coverage of acceptance criteria
```

**Pass Scenarios:**
```
✅ PR changes align with issue requirements
✅ All acceptance criteria addressed
✅ Minor refactoring related to fix is acceptable
✅ Test updates related to feature are in-scope
```

**Warning Scenarios:**
```
⚠️  PR includes unrelated bug fixes
⚠️  Changes in unrelated modules
⚠️  Feature additions not in issue scope
⚠️  Missing implementation of acceptance criteria
```

**Example Assessment:**

```markdown
## Issue Assessment: ✅ PASS (with notes)

**Linked Issue:** AUTH-123 - Implement JWT Authentication

**Issue Requirements:**
1. ✅ JWT token generation - Addressed
2. ✅ Token validation middleware - Addressed
3. ✅ Refresh token mechanism - Addressed
4. ⚠️  Rate limiting for auth endpoints - Not mentioned in issue, added in PR

**Out-of-Scope Changes Detected:**
- Modified database connection pooling (should be separate PR)
- Updated logging format globally (should be separate PR)

**Recommendation:**
Consider splitting unrelated changes (connection pooling, logging) into separate PRs for cleaner history and easier rollback if needed.
```

**Recommended Mode:**
- **warning**: Inform developer, allow merge
- Use **error** only if scope discipline is critical

---

## 2. Custom Checks Library

### 2.1 Breaking Changes Documentation

**Purpose:** Ensure all breaking changes are properly documented

```yaml
custom_checks:
  - name: "Breaking Changes Documentation"
    mode: "error"
    instructions: |
      This check ensures all breaking changes are properly documented.
      
      PASS CONDITIONS:
      - No breaking changes detected, OR
      - All breaking changes documented in both:
        1. PR description "Breaking Changes" section
        2. CHANGELOG.md with version and date
        3. Migration guide if user-facing
      
      FAIL CONDITIONS:
      - Breaking changes to public APIs without documentation
      - Changes to CLI arguments/flags without docs
      - Database schema changes without migration scripts
      - Configuration changes without upgrade guide
      - HTTP API changes (endpoints, params, responses) without docs
      
      BREAKING CHANGE INDICATORS:
      1. Function/method signature changes:
         - Added/removed parameters
         - Changed parameter types
         - Changed return types
         - Removed functions/methods
      
      2. API Contract Changes:
         - New required fields in requests
         - Removed fields from responses
         - Changed endpoint URLs
         - Modified authentication requirements
      
      3. Database Schema:
         - Added/removed tables or columns
         - Changed column types
         - Modified constraints
         - Changed indexes
      
      4. Configuration Changes:
         - New required environment variables
         - Removed/renamed config keys
         - Changed default values
      
      5. Dependency Changes:
         - Bumped major versions
         - Removed dependencies
         - Changed minimum versions
      
      EXEMPTIONS:
      - Internal/private code (not in public API)
      - Code marked with @internal or _private prefix
      - Test code and test fixtures
      - Development/debugging code
      
      DOCUMENTATION REQUIREMENTS:
      
      Breaking Changes in PR Description:
      ```markdown
      ## Breaking Changes
      
      ### API: Changed login endpoint
      - **Change**: POST /auth/login now requires email instead of username
      - **Migration**: Update client code to send email field
      - **Example**: See docs/api-migration-v2.md
      
      ### Database: Users table schema change
      - **Change**: username column renamed to email
      - **Migration**: Run migration script: scripts/migrate_v2.0.0.sql
      - **Rollback**: scripts/rollback_v2.0.0.sql included
      ```
      
      CHANGELOG.md Entry:
      ```markdown
      ## [2.0.0] - 2025-10-14
      
      ### Breaking Changes
      - Changed login endpoint to use email instead of username
      - Renamed users.username column to users.email
      
      ### Migration Guide
      See MIGRATION_v2.md for complete upgrade instructions.
      ```
      
      VERIFICATION STEPS:
      1. Scan git diff for breaking change patterns
      2. Check PR description for Breaking Changes section
      3. Verify CHANGELOG.md updated with version bump
      4. For user-facing changes, verify migration guide exists
      5. For database changes, verify migration scripts present
      
      PASS/FAIL DECISION:
      - PASS if no breaking changes OR all documented properly
      - FAIL if breaking changes found without complete documentation
      - INCONCLUSIVE if unable to determine (require manual review)
```

**Testing This Check:**

Create test PR with breaking change:

```python
# Before
def authenticate(username: str, password: str) -> Token:
    pass

# After (breaking change)
def authenticate(email: str, password: str) -> Token:  # username → email
    pass
```

Expected result: FAIL until Breaking Changes section added to PR description.

### 2.2 Security & Sensitive Data Check

**Purpose:** Prevent security vulnerabilities and sensitive data leaks

```yaml
custom_checks:
  - name: "Security & Sensitive Data Validation"
    mode: "error"
    instructions: |
      This check prevents common security vulnerabilities and sensitive data exposure.
      
      CRITICAL FAILURES (Immediate Fail):
      
      1. Hardcoded Credentials/Secrets
         Pattern Detection:
         - password = "..."
         - api_key = "..."
         - secret = "..."
         - token = "sk_live_..." or "pk_live_..."
         - AWS keys: AKIA[A-Z0-9]{16}
         - Private keys: -----BEGIN PRIVATE KEY-----
         
         Recommendation: Use environment variables or secret management
         
      2. SQL Injection Vulnerabilities
         Pattern Detection:
         - String concatenation in SQL: f"SELECT * FROM users WHERE id = {user_id}"
         - Use of % formatting in SQL: "SELECT * FROM %s" % table
         - Dynamic table/column names without whitelist
         
         Recommendation: Use parameterized queries or ORM
         Example: cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
         
      3. Command Injection
         Pattern Detection:
         - os.system() with user input
         - subprocess with shell=True and user input
         - eval() or exec() with user input
         
         Recommendation: Use subprocess with shell=False and argument list
         
      4. Sensitive Data in Logs
         Pattern Detection in logging statements:
         - password, passwd, pwd
         - token, auth, authorization
         - secret, key, credential
         - ssn, social_security
         - credit_card, cvv, card_number
         
         Recommendation: Redact sensitive fields before logging
         
      5. Missing Input Validation
         Pattern Detection:
         - API endpoints without request validation
         - User input passed directly to dangerous functions
         - File operations with user-provided paths
         - URL redirects with user input
         
         Recommendation: Validate all user input with schemas (Pydantic, etc.)
      
      6. Authentication Bypass
         Pattern Detection:
         - New API endpoints without @require_auth decorator
         - admin_required decorator commented out
         - Authentication checks in if False or if True branches
         
         Recommendation: All endpoints must have authentication
         
      7. Insecure Cryptography
         Pattern Detection:
         - MD5 or SHA1 for passwords (use bcrypt, argon2)
         - Custom crypto implementations
         - Hardcoded encryption keys
         - Use of DES, RC4, or other deprecated algorithms
         
         Recommendation: Use vetted libraries (cryptography, bcrypt)
      
      8. SSRF (Server-Side Request Forgery)
         Pattern Detection:
         - HTTP requests with user-provided URLs
         - URL fetching without domain whitelist
         - Webhook endpoints without validation
         
         Recommendation: Validate and whitelist URLs
      
      WARNING CONDITIONS (Flag for Review):
      
      1. Information Disclosure
         - Detailed error messages exposed to users
         - Stack traces in API responses
         - Debug mode enabled in production configs
         
      2. Missing Rate Limiting
         - Login endpoints without rate limiting
         - Password reset without rate limiting
         - API endpoints without throttling
         
      3. Weak Session Management
         - Sessions without timeout
         - Session IDs in URLs
         - Missing secure/httpOnly flags on cookies
      
      PASS CONDITIONS:
      - No security vulnerabilities detected
      - Existing vulnerabilities properly fixed
      - Security best practices followed
      - Sensitive data properly handled
      
      VERIFICATION TOOLS:
      - Regex pattern matching for common vulnerabilities
      - Abstract Syntax Tree (AST) analysis for code patterns
      - Search for known vulnerable function calls
      - Check for missing security decorators/middleware
      
      EXEMPTIONS:
      - Test code (test_*.py, *_test.py)
      - Mock data and fixtures
      - Example code in documentation (clearly marked)
      - Code in security/ that implements crypto (if reviewed)
      
      FAIL EXAMPLES:
      
      ❌ Hardcoded credential:
      ```python
      API_KEY = "sk_live_abc123xyz"
      ```
      
      ❌ SQL injection:
      ```python
      query = f"SELECT * FROM users WHERE email = '{email}'"
      cursor.execute(query)
      ```
      
      ❌ Logging sensitive data:
      ```python
      logger.info(f"User login: {username}, password: {password}")
      ```
      
      ❌ Missing auth:
      ```python
      @app.post("/api/users/delete")  # No @require_auth!
      async def delete_user(user_id: int):
          return delete_user_from_db(user_id)
      ```
      
      PASS EXAMPLES:
      
      ✅ Environment variable:
      ```python
      API_KEY = os.environ.get("API_KEY")
      ```
      
      ✅ Parameterized query:
      ```python
      cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
      ```
      
      ✅ Redacted logging:
      ```python
      logger.info(f"User login: {username}, password: [REDACTED]")
      ```
      
      ✅ Protected endpoint:
      ```python
      @app.post("/api/users/delete")
      @require_auth
      @require_role("admin")
      async def delete_user(user_id: int):
          return delete_user_from_db(user_id)
      ```
```

### 2.3 Architecture Compliance Check

**Purpose:** Enforce layered architecture and design patterns

```yaml
custom_checks:
  - name: "Architecture Compliance"
    mode: "warning"
    instructions: |
      Verify code follows KellerAI layered architecture patterns.
      
      ARCHITECTURE OVERVIEW:
      
      Layer Structure:
      1. API/Controller Layer (api/, controllers/)
         - HTTP request/response handling
         - Input validation
         - Route definitions
         - NO business logic
         - NO direct database access
      
      2. Service Layer (services/)
         - Business logic and orchestration
         - Transaction management
         - Calls to multiple repositories
         - NO HTTP concerns (request/response objects)
         - NO direct database queries (use repositories)
      
      3. Repository Layer (repositories/)
         - Data access and persistence
         - Database queries
         - ORM operations
         - Cache management
         - NO business logic
      
      4. Model Layer (models/)
         - Domain entities
         - Value objects
         - Data structures
         - NO behavior (except simple methods)
      
      RULES:
      
      1. Dependency Flow
         ✅ Allowed: Controller → Service → Repository → Model
         ❌ Prohibited: Repository → Controller
         ❌ Prohibited: Model → Service
         ❌ Prohibited: Service → Controller
      
      2. Controller Rules
         ✅ Accept HTTP requests
         ✅ Validate input (Pydantic models)
         ✅ Call service methods
         ✅ Return HTTP responses
         ❌ NO business logic
         ❌ NO database calls
         ❌ NO direct model instantiation with logic
      
      3. Service Rules
         ✅ Implement business logic
         ✅ Orchestrate repository calls
         ✅ Manage transactions
         ✅ Throw domain exceptions
         ❌ NO HTTP request/response handling
         ❌ NO direct database queries
         ❌ NO import from controllers
      
      4. Repository Rules
         ✅ Execute database queries
         ✅ Manage ORM operations
         ✅ Handle caching
         ✅ Return models/entities
         ❌ NO business logic
         ❌ NO service layer imports
         ❌ NO HTTP concerns
      
      PATTERNS TO ENFORCE:
      
      1. Dependency Injection
         ✅ Services injected via constructor
         ✅ Use FastAPI Depends()
         ❌ NO global service instances
         ❌ NO singleton pattern (except config)
         
         Example:
         ```python
         @router.post("/users")
         async def create_user(
             data: UserCreate,
             service: UserService = Depends(get_user_service)
         ):
             return await service.create_user(data)
         ```
      
      2. Error Handling
         ✅ Custom exceptions for business errors
         ✅ Global exception handler at API boundary
         ✅ Structured logging
         ❌ NO bare except: clauses
         ❌ NO swallowing exceptions silently
         
         Example:
         ```python
         class UserNotFoundError(DomainException):
             pass
         
         @app.exception_handler(DomainException)
         async def domain_exception_handler(request, exc):
             return JSONResponse(status_code=400, content={"error": str(exc)})
         ```
      
      3. Async Patterns
         ✅ I/O operations use async/await
         ✅ Database calls are async
         ✅ HTTP requests use httpx (async)
         ❌ NO synchronous I/O in async functions
         ❌ NO blocking calls without thread pool
         
         Example:
         ```python
         async def get_user(user_id: int) -> User:
             return await db.execute(select(User).where(User.id == user_id))
         ```
      
      4. API Versioning
         ✅ Endpoints include /v1/ or /v2/
         ✅ Breaking changes increment version
         ✅ Old versions deprecated gracefully
         ❌ NO unversioned endpoints
         
         Example:
         ```python
         @router.get("/api/v1/users/{user_id}")
         async def get_user_v1(user_id: int):
             pass
         ```
      
      VIOLATION DETECTION:
      
      Check for these patterns in the diff:
      
      1. Business Logic in Controllers:
         - Complex conditionals in controller methods
         - Calculations or transformations
         - Multiple repository calls from controller
      
      2. Database Calls Outside Repositories:
         - db.execute() in service or controller
         - Direct SQL in non-repository code
         - ORM queries outside repository layer
      
      3. Circular Dependencies:
         - Service importing controller
         - Repository importing service
         - Model importing service or repository
      
      4. Missing Dependency Injection:
         - Service instantiation with new/init in controllers
         - Global service variables
         - Singleton pattern (except config)
      
      5. Synchronous I/O in Async Context:
         - requests.get() instead of httpx
         - time.sleep() instead of asyncio.sleep()
         - Blocking file I/O in async functions
      
      PASS CONDITIONS:
      - Code follows layered architecture
      - Dependencies flow correctly
      - Async patterns used properly
      - DI framework utilized
      
      EXEMPTIONS ALLOWED WHEN:
      - Documented in PR with architectural reasoning
      - Approved by tech lead (noted in PR comments)
      - Temporary workaround with TODO and ticket reference
      - Legacy code being migrated (marked with # LEGACY comment)
      
      FAIL EXAMPLES:
      
      ❌ Business logic in controller:
      ```python
      @router.post("/orders")
      async def create_order(data: OrderCreate):
          # ❌ Business logic in controller!
          if data.total > 1000:
              discount = data.total * 0.1
          else:
              discount = 0
          
          order = Order(total=data.total - discount)
          db.add(order)
          await db.commit()
          return order
      ```
      
      ❌ Database call in service:
      ```python
      class UserService:
          async def create_user(self, data: UserCreate):
              # ❌ Direct DB access from service!
              user = User(**data.dict())
              db.add(user)
              await db.commit()
              return user
      ```
      
      PASS EXAMPLES:
      
      ✅ Proper layering:
      ```python
      # Controller
      @router.post("/orders")
      async def create_order(
          data: OrderCreate,
          service: OrderService = Depends(get_order_service)
      ):
          return await service.create_order(data)
      
      # Service
      class OrderService:
          def __init__(self, repo: OrderRepository):
              self.repo = repo
          
          async def create_order(self, data: OrderCreate) -> Order:
              # Business logic here
              discount = self._calculate_discount(data.total)
              order_data = OrderData(
                  total=data.total - discount,
                  discount=discount
              )
              return await self.repo.create(order_data)
          
          def _calculate_discount(self, total: Decimal) -> Decimal:
              return total * Decimal("0.1") if total > 1000 else Decimal("0")
      
      # Repository
      class OrderRepository:
          async def create(self, data: OrderData) -> Order:
              order = Order(**data.dict())
              db.add(order)
              await db.commit()
              await db.refresh(order)
              return order
      ```
```

### 2.4 Test Coverage Check

**Purpose:** Ensure adequate test coverage for new code

```yaml
custom_checks:
  - name: "Test Coverage Requirements"
    mode: "error"
    instructions: |
      Verify adequate test coverage for all new code.
      
      REQUIREMENTS:
      
      1. New Public Functions
         - Every new public function needs unit tests
         - Test file location: tests/unit/<module>_test.py
         - Naming: test_<function_name>_<scenario>
         - Minimum scenarios: happy path + error case
      
      2. New API Endpoints
         - Integration tests required
         - Test file: tests/integration/api/<endpoint>_test.py
         - Cover: success response, validation errors, auth failures
      
      3. Bug Fixes
         - Regression test required
         - Test must fail without the fix
         - Test must pass with the fix
      
      4. Critical Paths Coverage
         - Authentication: 90%+ coverage
         - Payment processing: 95%+ coverage
         - Data transformation: 85%+ coverage
         - Background jobs: 80%+ coverage
      
      TEST STRUCTURE:
      
      tests/
      ├── unit/           # Unit tests for functions/classes
      ├── integration/    # Integration tests for components
      └── e2e/           # End-to-end tests for workflows
      
      NAMING CONVENTIONS:
      
      Format: test_<function>_<scenario>_<expected_result>
      
      Examples:
      - test_create_user_valid_data_returns_user()
      - test_create_user_duplicate_email_raises_error()
      - test_authenticate_invalid_password_returns_none()
      - test_process_payment_insufficient_funds_fails()
      
      COVERAGE RULES:
      
      1. Happy Path (Required)
         - Test successful execution
         - Valid inputs
         - Expected outputs
      
      2. Error Cases (Required)
         - Invalid inputs
         - Boundary conditions
         - Exception handling
      
      3. Edge Cases (Recommended)
         - Empty inputs
         - Null values
         - Maximum values
         - Concurrent access
      
      TEST QUALITY:
      
      ✅ Good Test:
      ```python
      def test_calculate_discount_over_threshold_applies_10_percent():
          # Arrange
          order_total = Decimal("1500.00")
          expected_discount = Decimal("150.00")
          
          # Act
          discount = calculate_discount(order_total)
          
          # Assert
          assert discount == expected_discount
      
      def test_calculate_discount_under_threshold_returns_zero():
          # Arrange
          order_total = Decimal("500.00")
          
          # Act
          discount = calculate_discount(order_total)
          
          # Assert
          assert discount == Decimal("0")
      ```
      
      ❌ Poor Test:
      ```python
      def test_discount():
          assert calculate_discount(1500) == 150  # Magic numbers, no context
      ```
      
      VERIFICATION PROCESS:
      
      1. Identify New Code
         - Scan git diff for new functions/classes
         - Identify new API endpoints
         - Find modified functions
      
      2. Check for Tests
         - Search tests/ directory for corresponding test files
         - Verify test naming follows convention
         - Count test scenarios per function
      
      3. Calculate Coverage
         - New public functions with tests / Total new public functions
         - Must be >= 90% for critical paths
         - Must be >= 80% for standard code
      
      4. Verify Test Quality
         - Tests follow AAA pattern (Arrange/Act/Assert)
         - Clear test names
         - No commented-out tests
         - Mocks used appropriately
      
      FAIL CONDITIONS:
      
      - New public function without any tests
      - New API endpoint without integration test
      - Bug fix without regression test
      - Critical path coverage < 90%
      - Standard code coverage < 80%
      - Tests exist but are disabled/skipped
      
      PASS CONDITIONS:
      
      - All new public APIs have tests
      - Coverage meets thresholds
      - Tests are well-structured
      - Bug fixes include regression tests
      
      EXEMPTIONS:
      
      Allowed without tests (document in PR):
      - Simple getters/setters
      - Data classes with no logic
      - Configuration files
      - Manual scripts (mark as @manual)
      - Prototypes (mark as @prototype)
      
      EXAMPLES:
      
      ❌ FAIL - No tests:
      ```python
      # src/services/payment.py (NEW FILE)
      async def process_payment(amount: Decimal) -> PaymentResult:
          # ... complex payment logic ...
          pass
      
      # No corresponding test file found!
      ```
      
      ✅ PASS - Tests present:
      ```python
      # src/services/payment.py
      async def process_payment(amount: Decimal) -> PaymentResult:
          # ... payment logic ...
          pass
      
      # tests/unit/services/payment_test.py
      async def test_process_payment_valid_amount_succeeds():
          result = await process_payment(Decimal("100.00"))
          assert result.success is True
      
      async def test_process_payment_zero_amount_fails():
          with pytest.raises(ValueError):
              await process_payment(Decimal("0"))
      ```
```

### 2.5 Performance Considerations Check

**Purpose:** Flag potential performance issues early

```yaml
custom_checks:
  - name: "Performance Impact Assessment"
    mode: "warning"
    instructions: |
      Identify potential performance issues before they reach production.
      
      CRITICAL PERFORMANCE ISSUES:
      
      1. N+1 Query Problems
         
         Detection:
         - Loop containing database queries
         - Accessing relationships in loops without eager loading
         
         Example Violation:
         ```python
         users = await db.execute(select(User))
         for user in users:
             # ❌ N+1 problem!
             orders = await db.execute(
                 select(Order).where(Order.user_id == user.id)
             )
         ```
         
         Solution:
         ```python
         # ✅ Eager loading
         users = await db.execute(
             select(User).options(selectinload(User.orders))
         )
         for user in users:
             orders = user.orders  # Already loaded
         ```
      
      2. Inefficient Algorithms
         
         Detection:
         - Nested loops over large datasets
         - O(n²) or worse complexity on hot paths
         - Unnecessary sorting in loops
         
         Example Violation:
         ```python
         def find_duplicates(items):
             duplicates = []
             for i in range(len(items)):
                 for j in range(i+1, len(items)):  # ❌ O(n²)
                     if items[i] == items[j]:
                         duplicates.append(items[i])
             return duplicates
         ```
         
         Solution:
         ```python
         def find_duplicates(items):
             seen = set()
             duplicates = set()
             for item in items:  # ✅ O(n)
                 if item in seen:
                     duplicates.add(item)
                 seen.add(item)
             return list(duplicates)
         ```
      
      3. Memory Issues
         
         Detection:
         - Loading entire datasets into memory
         - Large object allocations in loops
         - Missing pagination
         - No streaming for large files
         
         Example Violation:
         ```python
         async def export_users():
             users = await db.execute(select(User))  # ❌ Loads all!
             return [user.to_dict() for user in users.all()]
         ```
         
         Solution:
         ```python
         async def export_users():
             # ✅ Generator/streaming
             async for batch in db.stream(select(User).execution_options(yield_per=100)):
                 for user in batch:
                     yield user.to_dict()
         ```
      
      4. Missing Database Indexes
         
         Detection:
         - Queries on unindexed columns
         - WHERE clauses without indexes
         - Foreign keys without indexes
         
         Check in migrations:
         ```python
         # ❌ No index on frequently queried column
         op.add_column('orders', sa.Column('user_id', sa.Integer()))
         
         # ✅ With index
         op.add_column('orders', sa.Column('user_id', sa.Integer(), index=True))
         op.create_foreign_key('fk_orders_user', 'orders', 'users', 
                              ['user_id'], ['id'])
         ```
      
      5. Synchronous I/O on Hot Path
         
         Detection:
         - Blocking calls in async functions
         - requests.get() instead of httpx in async code
         - file I/O without async
         - time.sleep() instead of asyncio.sleep()
         
         Example Violation:
         ```python
         @router.get("/users/{id}")
         async def get_user(id: int):
             # ❌ Blocking call in async handler!
             response = requests.get(f"http://api.example.com/users/{id}")
             return response.json()
         ```
         
         Solution:
         ```python
         @router.get("/users/{id}")
         async def get_user(id: int):
             # ✅ Async HTTP client
             async with httpx.AsyncClient() as client:
                 response = await client.get(f"http://api.example.com/users/{id}")
                 return response.json()
         ```
      
      6. Missing Caching
         
         Detection:
         - Expensive computations repeated
         - Same data fetched multiple times
         - No cache for external API calls
         
         Example:
         ```python
         # ✅ Add caching for expensive operations
         from functools import lru_cache
         
         @lru_cache(maxsize=128)
         def calculate_complex_metric(data_id: int):
             # expensive calculation
             pass
         ```
      
      7. Unbounded Operations
         
         Detection:
         - Queries without LIMIT
         - Loops without max iterations
         - Recursion without depth limit
         
         Example Violation:
         ```python
         # ❌ No limit on results
         users = await db.execute(select(User))
         
         # ✅ With limit and pagination
         users = await db.execute(
             select(User).limit(100).offset(page * 100)
         )
         ```
      
      DETECTION STRATEGY:
      
      1. Static Analysis
         - Search for nested loops
         - Find database queries in loops
         - Identify blocking calls in async functions
         - Check for missing pagination
      
      2. Pattern Matching
         - Regex for common anti-patterns
         - AST analysis for complexity
         - Dependency analysis for N+1 problems
      
      3. Context Understanding
         - Hot paths (API endpoints, background jobs)
         - Data volume (small vs large datasets)
         - Frequency (called once vs millions of times)
      
      PASS CONDITIONS:
      
      - No critical performance issues
      - Performance impact documented
      - Load testing performed for critical changes
      - Caching strategy in place for expensive operations
      - Database queries optimized
      
      FAIL/WARNING CONDITIONS:
      
      ⚠️  WARNING:
      - Potential N+1 query problem
      - O(n²) algorithm on non-hot path
      - Missing index on new foreign key
      - Unbounded query on small table
      
      🚫 CRITICAL (consider error mode):
      - N+1 on hot path (API endpoint)
      - Blocking I/O in async API handler
      - Loading entire large table into memory
      - O(n²) or worse on hot path
      
      REPORTING FORMAT:
      
      ```markdown
      ## Performance Assessment
      
      ### Issues Found: 2
      
      #### 🔴 CRITICAL: N+1 Query in API Endpoint
      **Location:** src/api/orders.py:45
      **Issue:** Database query inside loop for user orders
      **Impact:** O(n) database calls, will slow down with scale
      **Recommendation:** Use selectinload() for eager loading
      
      #### ⚠️  WARNING: Missing Index
      **Location:** migrations/add_order_status.py
      **Issue:** New status column frequently queried but not indexed
      **Impact:** Table scans on order queries
      **Recommendation:** Add index on status column
      
      ### Performance Documentation
      ✅ Load testing results included in PR description
      ✅ Caching strategy documented
      ❌ No query optimization plan mentioned
      ```
      
      EXEMPTIONS:
      
      - Administrative tools (used infrequently)
      - One-time migration scripts
      - Development/testing code
      - Prototype code (marked as such)
      
      Note: This check is WARNING mode to allow case-by-case assessment.
      Developers should acknowledge warnings and explain if acceptable.
```

---

## 3. Enforcement Strategy

### 3.1 Mode Configuration

**Three Enforcement Modes:**

| Mode | Behavior | Use Case |
|------|----------|----------|
| `off` | Check disabled, not run | Temporarily disable check |
| `warning` | Display warnings, allow merge | Informational feedback |
| `error` | Block merge if fails | Hard requirement |

**Mode Selection Guidelines:**

```yaml
# Critical quality gates
mode: "error"
examples:
  - Security issues
  - Breaking changes without docs
  - Missing test coverage
  - Hardcoded credentials

# Style and best practices
mode: "warning"
examples:
  - Architecture suggestions
  - Performance considerations
  - Code organization
  - Documentation completeness

# Temporarily disabled
mode: "off"
examples:
  - Check under development
  - False positive issues
  - Team not ready for enforcement
```

### 3.2 Request Changes Workflow

**Enable PR Blocking:**

```yaml
# .coderabbit.yaml
reviews:
  request_changes_workflow: true  # Enable blocking
  
  pre_merge_checks:
    docstrings:
      mode: "error"  # Will block merge
```

**How It Works:**

1. CodeRabbit runs pre-merge checks
2. If any `error` mode check fails:
   - CodeRabbit posts "Request Changes" review
   - GitHub/GitLab blocks merge
   - PR shows "Changes requested" status
3. Developer must either:
   - Fix the issue
   - Override with `@coderabbitai ignore pre-merge checks`

**Override Process:**

```
# In PR comment
@coderabbitai ignore pre-merge checks

# CodeRabbit response:
✅ Pre-merge check failures ignored for this PR.
   Failed checks are marked [IGNORED] in walkthrough.
   This override applies only to this PR.
```

**Governance:**

- Override requires justification in PR comments
- Tech lead approval for security/breaking change overrides
- Track override frequency (should be rare)

### 3.3 Phase Rollout Strategy

**Phase 1: Warning Mode (Week 1-2)**

```yaml
pre_merge_checks:
  docstrings:
    mode: "warning"  # Gather feedback
  title:
    mode: "warning"
  description:
    mode: "warning"
  custom_checks:
    - mode: "warning"  # All custom checks
```

**Goals:**
- Collect data on pass/fail rates
- Identify false positives
- Refine check instructions
- Train team on expectations

**Phase 2: Error Mode for Critical Checks (Week 3-4)**

```yaml
pre_merge_checks:
  docstrings:
    mode: "error"  # Enforce
  description:
    mode: "error"  # Enforce
  custom_checks:
    - name: "Security"
      mode: "error"  # Critical
    - name: "Architecture"
      mode: "warning"  # Still gathering feedback
```

**Phase 3: Full Enforcement (Week 5+)**

```yaml
pre_merge_checks:
  # All built-in checks
  docstrings:
    mode: "error"
  title:
    mode: "warning"  # Style preference
  description:
    mode: "error"
  issue_assessment:
    mode: "warning"
  
  # Custom checks
  custom_checks:
    - name: "Breaking Changes"
      mode: "error"
    - name: "Security"
      mode: "error"
    - name: "Test Coverage"
      mode: "error"
    - name: "Architecture"
      mode: "warning"
    - name: "Performance"
      mode: "warning"
```

---

## 4. Implementation Examples

### Complete .coderabbit.yaml

```yaml
# .coderabbit.yaml - KellerAI Configuration
language: "en-US"

reviews:
  # Enable request changes workflow for blocking
  request_changes_workflow: true
  
  # Pre-merge checks configuration
  pre_merge_checks:
    
    # Built-in Check 1: Docstring Coverage
    docstrings:
      mode: "error"
      threshold: 85
    
    # Built-in Check 2: PR Title
    title:
      mode: "warning"
      requirements: |
        1. Start with imperative verb (Add, Fix, Update, Remove, Refactor)
        2. Keep under 60 characters
        3. Include issue reference [ISSUE-123]
        4. Use sentence case
    
    # Built-in Check 3: PR Description
    description:
      mode: "error"
    
    # Built-in Check 4: Issue Assessment
    issue_assessment:
      mode: "warning"
    
    # Custom Checks
    custom_checks:
      
      # Custom Check 1: Breaking Changes
      - name: "Breaking Changes Documentation"
        mode: "error"
        instructions: |
          [Full instructions from section 2.1]
      
      # Custom Check 2: Security
      - name: "Security & Sensitive Data"
        mode: "error"
        instructions: |
          [Full instructions from section 2.2]
      
      # Custom Check 3: Architecture
      - name: "Architecture Compliance"
        mode: "warning"
        instructions: |
          [Full instructions from section 2.3]
      
      # Custom Check 4: Test Coverage
      - name: "Test Coverage Requirements"
        mode: "error"
        instructions: |
          [Full instructions from section 2.4]
      
      # Custom Check 5: Performance
      - name: "Performance Impact Assessment"
        mode: "warning"
        instructions: |
          [Full instructions from section 2.5]

# Review settings
reviews:
  profile: "chill"
  request_changes_workflow: true
  high_level_summary: true
  
# Path filters
reviews:
  path_filters:
    - "!tests/**"
    - "!docs/**"
```

---

## 5. Testing & Validation

### Test Suite for Pre-merge Checks

Create test PRs to validate each check:

**Test 1: Docstring Coverage**

```python
# Create PR with insufficient docstrings
# Expected: FAIL with coverage percentage

def calculate_total(items):  # No docstring
    return sum(item.price for item in items)

def apply_discount(total, rate):  # No docstring
    return total * (1 - rate)
```

**Test 2: Breaking Changes**

```python
# Create PR with breaking change, no documentation
# Expected: FAIL until Breaking Changes section added

# Before
def authenticate(username: str) -> Token:
    pass

# After
def authenticate(email: str) -> Token:  # Breaking change!
    pass
```

**Test 3: Security Issues**

```python
# Create PR with hardcoded credential
# Expected: FAIL immediately

API_KEY = "sk_live_abc123"  # Should trigger security check
```

**Test 4: Test Coverage**

```python
# Add new function without tests
# Expected: FAIL until tests added

def process_payment(amount: Decimal) -> Result:
    # Complex payment logic
    pass

# No corresponding test file!
```

### Validation Checklist

- [ ] All checks show in CodeRabbit dashboard
- [ ] Warning mode checks display but don't block
- [ ] Error mode checks block merge (with request_changes_workflow)
- [ ] Override command works: `@coderabbitai ignore pre-merge checks`
- [ ] Check results appear in PR walkthrough
- [ ] Failed checks show specific reasons
- [ ] Passed checks are collapsible
- [ ] [IGNORED] tag appears for overridden checks

---

## 6. Best Practices

### Writing Effective Custom Checks

**1. Be Specific and Actionable**

❌ Bad:
```yaml
instructions: "Code should be clean and follow best practices"
```

✅ Good:
```yaml
instructions: |
  Check for these specific issues:
  1. Functions longer than 50 lines (split into smaller functions)
  2. More than 3 levels of nesting (refactor for clarity)
  3. Duplicate code blocks (extract to shared function)
```

**2. Provide Clear Examples**

Include both failing and passing examples in instructions.

**3. Define Exemptions**

Specify when rules don't apply:
```yaml
Exemptions:
- Test code (test_*.py)
- Migration scripts
- Legacy code (marked with @legacy)
```

**4. Use Structured Format**

```yaml
instructions: |
  PASS CONDITIONS:
  - [specific condition 1]
  - [specific condition 2]
  
  FAIL CONDITIONS:
  - [specific failure 1]
  - [specific failure 2]
  
  VERIFICATION STEPS:
  1. [how to check]
  2. [what to look for]
```

### Iterative Refinement

**Start Simple:**
```yaml
# Version 1: Basic check
- name: "Security Check"
  instructions: "Flag hardcoded credentials"
```

**Expand Based on Feedback:**
```yaml
# Version 2: More comprehensive
- name: "Security Check"
  instructions: |
    Check for:
    1. Hardcoded credentials
    2. SQL injection patterns
    3. Sensitive data in logs
```

**Add Nuance:**
```yaml
# Version 3: With exemptions and examples
- name: "Security Check"
  instructions: |
    [Detailed instructions with examples and exemptions]
```

### Team Alignment

1. **Review Draft Checks with Team**
   - Share proposed checks
   - Gather feedback
   - Adjust based on concerns

2. **Start in Warning Mode**
   - Collect data on false positives
   - Refine instructions
   - Switch to error mode when ready

3. **Document Override Reasons**
   - Track why overrides happen
   - Update checks to reduce false positives
   - Share learnings with team

4. **Regular Review Cadence**
   - Monthly check review
   - Update based on new patterns
   - Remove obsolete checks

---

## Summary

This specification provides:

1. ✅ **4 Built-in Checks**: Docstrings, PR title, description, issue assessment
2. ✅ **5 Custom Checks**: Breaking changes, security, architecture, testing, performance
3. ✅ **Enforcement Strategy**: Warning vs error modes, phased rollout
4. ✅ **Implementation Guide**: Complete .coderabbit.yaml configuration
5. ✅ **Testing Procedures**: Validation checklist and test cases
6. ✅ **Best Practices**: Writing effective checks, team alignment

**Next Steps:**

1. Review this specification with team
2. Start with Phase 1 (warning mode)
3. Create test PRs to validate each check
4. Collect feedback and refine
5. Move to error mode for critical checks
6. Monitor override frequency
7. Iterate based on team experience

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Integration & Tooling Research Agent  
**Status:** Complete
