# CodeRabbit Language-Specific Configuration Research
## Agent 2 Research Deliverables

**Research Scope**: Python/AI/ML, TypeScript/JavaScript, Document Processing
**Focus**: Language-specific configurations, path instructions, AST patterns, tool integrations
**Date**: 2025-10-14

---

## Table of Contents

1. [Python Project Template](#1-python-project-template)
2. [TypeScript/JavaScript Template](#2-typescriptjavascript-template)
3. [Path Instructions Library](#3-path-instructions-library)
4. [AST Pattern Rules](#4-ast-pattern-rules)
5. [Tool Integration Guide](#5-tool-integration-guide)
6. [Multi-Language Configuration Patterns](#6-multi-language-configuration-patterns)

---

## 1. Python Project Template

### Complete `.coderabbit.yaml` for Python/AI/ML Projects

```yaml
# Python AI/ML Project Configuration
# Optimized for data science, machine learning, and PDF processing workflows

language: en-US
tone_instructions: "Focus on data integrity, model performance, and computational efficiency. Be precise about type safety and error handling in data pipelines."

reviews:
  profile: assertive  # More thorough for ML code
  high_level_summary: true
  auto_review:
    enabled: true
    drafts: false
    ignore_title_keywords:
      - "[WIP]"
      - "[EXPERIMENT]"
      - "[DRAFT]"

  # Path-specific instructions for Python projects
  path_instructions:
    # Core ML/AI code
    - path: "**/*.py"
      instructions: |
        Review Python code with focus on:
        - Type hints and type safety (use of typing module)
        - Proper error handling for data operations
        - Memory efficiency for large datasets
        - Numpy/Pandas best practices
        - Docstring completeness (Google or NumPy style)
        - Input validation and data sanitization

    # Machine Learning Models
    - path: "**/models/**/*.py"
      instructions: |
        Review ML model code for:
        - Model architecture clarity and documentation
        - Proper hyperparameter validation
        - Reproducibility (random seeds, deterministic operations)
        - Model versioning and checkpointing
        - GPU memory management
        - Data pipeline efficiency
        - Logging of training metrics
        - Model evaluation metrics appropriateness

    # Data Processing Pipelines
    - path: "**/data/**/*.py"
      instructions: |
        Review data processing code for:
        - Data validation and schema enforcement
        - Handling of missing values and outliers
        - Memory-efficient operations (chunking, lazy evaluation)
        - Data lineage and transformation tracking
        - Thread safety for parallel processing
        - Proper pandas/numpy vectorization
        - Edge case handling (empty datasets, malformed data)

    # PDF Processing Code
    - path: "**/pdf/**/*.py"
      instructions: |
        Review PDF processing code for:
        - Proper resource cleanup (file handles, memory)
        - Error handling for malformed PDFs
        - Text extraction accuracy considerations
        - OCR quality checks where applicable
        - Memory management for large documents
        - Support for different PDF versions/formats
        - Unicode and encoding handling

    # Jupyter Notebooks
    - path: "**/*.ipynb"
      instructions: |
        Review notebooks for:
        - Clear cell execution order and dependencies
        - Reproducibility (seed setting, imports)
        - Appropriate use of markdown documentation
        - Visualization clarity and labels
        - Memory cleanup after heavy operations
        - Export readiness (non-interactive execution)

    # Test Files
    - path: "**/tests/**/*.py"
      instructions: |
        Review test code for:
        - Comprehensive test coverage of edge cases
        - Proper use of fixtures and mocking
        - Test isolation and independence
        - Performance test benchmarks where needed
        - Data generation strategies
        - Assertions clarity and specificity

    # Configuration Files
    - path: "**/{config,settings}/**/*.py"
      instructions: |
        Review configuration code for:
        - Environment variable validation
        - Secret management (no hardcoded credentials)
        - Configuration schema validation
        - Default value appropriateness
        - Type safety for config values

    # API Endpoints
    - path: "**/api/**/*.py"
      instructions: |
        Review API code for:
        - Input validation and sanitization
        - Proper HTTP status codes
        - Rate limiting considerations
        - Error response consistency
        - API documentation completeness
        - Request/response logging

    # Utility Functions
    - path: "**/utils/**/*.py"
      instructions: |
        Review utility code for:
        - Reusability and modularity
        - Clear function signatures with type hints
        - Comprehensive docstrings
        - Edge case handling
        - Unit test coverage

  # Path filters - exclude generated and non-code files
  path_filters:
    - "!**/__pycache__/**"
    - "!**/.pytest_cache/**"
    - "!**/.mypy_cache/**"
    - "!**/*.pyc"
    - "!**/*.pyo"
    - "!**/*.pyd"
    - "!**/data/raw/**"  # Exclude raw data files
    - "!**/data/processed/**"  # Exclude processed data
    - "!**/models/checkpoints/**"  # Exclude model checkpoints
    - "!**/models/saved_models/**"
    - "!**/.ipynb_checkpoints/**"
    - "!**/dist/**"
    - "!**/build/**"
    - "!**/*.egg-info/**"
    - "!**/venv/**"
    - "!**/.venv/**"
    - "!**/env/**"

  # Tool integrations for Python
  tools:
    ruff:
      enabled: true  # Fast Python linter and formatter

    pylint:
      enabled: true  # Comprehensive Python linter

    mypy:
      enabled: true  # Static type checking (if available)

    gitleaks:
      enabled: true  # Secret scanning

    ast-grep:
      essential_rules: true
      rule_dirs:
        - ".coderabbit/ast-grep/python"
      packages:
        - "coderabbitai/ast-grep-essentials"

  # Pre-merge checks
  pre_merge_checks:
    docstrings:
      mode: warning
      threshold: 75  # 75% docstring coverage for ML code

    title:
      mode: warning
      requirements: "Title should reference ticket number or feature, be under 72 characters"

    description:
      mode: warning

    issue_assessment:
      mode: warning

  # Finishing touches
  finishing_touches:
    docstrings:
      enabled: true

    unit_tests:
      enabled: true

# Code generation settings
code_generation:
  docstrings:
    language: en-US
    path_instructions:
      - path: "**/models/**/*.py"
        instructions: |
          Generate docstrings with:
          - Model architecture description
          - Input/output tensor shapes
          - Hyperparameter descriptions
          - Example usage
          - References to papers if applicable

      - path: "**/data/**/*.py"
        instructions: |
          Generate docstrings with:
          - Data format descriptions
          - Expected schema/types
          - Transformation logic explanation
          - Example input/output

      - path: "**/*.py"
        instructions: |
          Use Google-style docstrings with:
          - Brief one-line summary
          - Detailed description if needed
          - Args: parameter descriptions with types
          - Returns: return value description with type
          - Raises: exception descriptions
          - Example: usage example if complex

  unit_tests:
    path_instructions:
      - path: "**/models/**/*.py"
        instructions: |
          Generate tests with:
          - Model initialization tests
          - Forward pass shape tests
          - Training loop tests with mock data
          - Checkpoint save/load tests
          - Edge cases (empty batches, etc.)

      - path: "**/data/**/*.py"
        instructions: |
          Generate tests with:
          - Data loading and validation
          - Transformation correctness
          - Edge cases (missing data, malformed data)
          - Performance tests for large datasets

# Knowledge base configuration
knowledge_base:
  opt_out: false

  code_guidelines:
    enabled: true
    file_patterns:
      - "**/.cursorrules"
      - "**/CODING_STANDARDS.md"
      - "**/docs/STYLE_GUIDE.md"
      - "**/.github/CONTRIBUTING.md"

  learnings:
    scope: auto  # Use organization learnings for private repos

  issues:
    scope: auto

# Chat configuration
chat:
  auto_reply: true
  art: true
```

### Python-Specific Best Practices Summary

**Type Safety**:
- Use `typing` module for all function signatures
- Leverage `mypy` for static type checking
- Use `Protocol` for duck typing
- Consider `Pydantic` for data validation

**Data Science Best Practices**:
- Always set random seeds for reproducibility
- Document data shapes and transformations
- Use vectorized operations over loops
- Profile memory usage for large datasets
- Implement proper logging for pipelines

**ML Model Best Practices**:
- Version control model architectures
- Track hyperparameters with config files
- Implement proper train/val/test splits
- Log metrics consistently
- Handle GPU memory cleanup

**PDF Processing Best Practices**:
- Always close file handles in finally blocks
- Handle encoding errors gracefully
- Validate PDF structure before processing
- Implement pagination for large documents
- Test with various PDF versions

---

## 2. TypeScript/JavaScript Template

### Complete `.coderabbit.yaml` for Full-Stack TypeScript/JavaScript Projects

```yaml
# TypeScript/JavaScript Full-Stack Configuration
# Optimized for React, Node.js, and modern web development

language: en-US
tone_instructions: "Focus on type safety, React best practices, async handling, and security. Emphasize performance and user experience."

reviews:
  profile: chill  # Balanced approach for web development
  high_level_summary: true
  auto_review:
    enabled: true
    drafts: false
    ignore_title_keywords:
      - "[WIP]"
      - "[POC]"

  # Path-specific instructions for TypeScript/JavaScript
  path_instructions:
    # TypeScript Core
    - path: "**/*.{ts,tsx}"
      instructions: |
        Review TypeScript code for:
        - Type safety (avoid 'any', use proper types)
        - Interface vs type alias appropriateness
        - Generics usage for reusability
        - Proper error handling with typed errors
        - Null/undefined safety
        - Immutability patterns
        - Async/await best practices

    # React Components
    - path: "**/components/**/*.{tsx,jsx}"
      instructions: |
        Review React components for:
        - Component composition and reusability
        - Proper prop typing with TypeScript
        - Hook usage best practices (dependencies, cleanup)
        - Performance optimization (useMemo, useCallback)
        - Accessibility (ARIA attributes, semantic HTML)
        - Error boundaries for error handling
        - Key prop usage in lists
        - Avoid prop drilling (consider context/state management)

    # React Hooks
    - path: "**/hooks/**/*.{ts,tsx}"
      instructions: |
        Review custom hooks for:
        - Proper naming (use prefix)
        - Hook dependency arrays completeness
        - Cleanup functions in useEffect
        - Memoization appropriateness
        - Type safety for hook returns
        - Reusability and composability

    # API Routes/Backend
    - path: "**/api/**/*.{ts,js}"
      instructions: |
        Review API code for:
        - Input validation and sanitization
        - Proper HTTP status codes and error responses
        - Authentication and authorization checks
        - Rate limiting implementation
        - SQL injection prevention
        - Proper async error handling
        - Request/response logging
        - API versioning strategy

    # State Management
    - path: "**/{store,state,redux,zustand}/**/*.{ts,tsx}"
      instructions: |
        Review state management for:
        - State structure normalization
        - Action creator type safety
        - Selector memoization
        - Side effect handling (thunks, sagas)
        - Immutable state updates
        - Global vs local state appropriateness
        - State serialization compatibility

    # Utility Functions
    - path: "**/utils/**/*.{ts,js}"
      instructions: |
        Review utility code for:
        - Pure function design
        - Proper TypeScript typing
        - Error handling
        - Edge case coverage
        - Tree-shaking compatibility
        - Documentation clarity

    # Tests
    - path: "**/*.{test,spec}.{ts,tsx,js,jsx}"
      instructions: |
        Review test code for:
        - Test coverage of edge cases
        - Proper mocking strategies
        - Test isolation
        - Async testing best practices
        - Descriptive test names
        - Arrange-Act-Assert pattern
        - Performance tests where needed

    # Configuration
    - path: "**/{config,configuration}/**/*.{ts,js}"
      instructions: |
        Review configuration for:
        - Environment variable validation
        - Type safety for config objects
        - Secrets management (no hardcoded keys)
        - Default value appropriateness
        - Schema validation

    # Database/ORM
    - path: "**/{models,entities,schemas}/**/*.{ts,js}"
      instructions: |
        Review database code for:
        - Schema validation
        - Migration strategy
        - Index usage for performance
        - Relationship definitions
        - Type safety for queries
        - N+1 query prevention

    # GraphQL
    - path: "**/*.graphql"
      instructions: |
        Review GraphQL schemas for:
        - Schema design best practices
        - Resolver performance
        - N+1 query prevention
        - Proper error handling
        - Authentication/authorization in resolvers

    # Styles
    - path: "**/*.{css,scss,sass}"
      instructions: |
        Review styles for:
        - CSS naming conventions (BEM, CSS Modules)
        - Responsive design implementation
        - Accessibility (focus states, contrast)
        - Performance (selector efficiency)
        - Dark mode support if applicable

  # Path filters
  path_filters:
    - "!**/node_modules/**"
    - "!**/dist/**"
    - "!**/build/**"
    - "!**/.next/**"
    - "!**/.nuxt/**"
    - "!**/coverage/**"
    - "!**/*.min.js"
    - "!**/*.bundle.js"
    - "!**/package-lock.json"
    - "!**/yarn.lock"
    - "!**/pnpm-lock.yaml"
    - "!**/.webpack/**"
    - "!**/.cache/**"

  # Tool integrations
  tools:
    eslint:
      enabled: true

    biome:
      enabled: true  # Fast linter and formatter

    oxc:
      enabled: true  # High-performance linter

    gitleaks:
      enabled: true

    ast-grep:
      essential_rules: true
      rule_dirs:
        - ".coderabbit/ast-grep/typescript"

  # Pre-merge checks
  pre_merge_checks:
    docstrings:
      mode: warning
      threshold: 60

    title:
      mode: warning
      requirements: "Title should follow conventional commits format (feat:, fix:, etc.)"

    description:
      mode: warning

# Code generation
code_generation:
  docstrings:
    language: en-US
    path_instructions:
      - path: "**/*.{ts,tsx}"
        instructions: |
          Generate JSDoc comments with:
          - Brief description
          - @param with types (TypeScript types preferred)
          - @returns with type
          - @throws for exceptions
          - @example for complex functions

  unit_tests:
    path_instructions:
      - path: "**/components/**/*.{tsx,jsx}"
        instructions: |
          Generate React component tests with:
          - Render tests with React Testing Library
          - User interaction tests (click, input)
          - Prop variations tests
          - Accessibility tests
          - Error state tests

      - path: "**/hooks/**/*.{ts,tsx}"
        instructions: |
          Generate hook tests with:
          - renderHook from @testing-library/react-hooks
          - State update tests
          - Side effect tests
          - Cleanup tests

# Knowledge base
knowledge_base:
  opt_out: false
  code_guidelines:
    enabled: true
    file_patterns:
      - "**/.cursorrules"
      - "**/.eslintrc.{js,json,yaml}"
      - "**/CONTRIBUTING.md"

# Chat
chat:
  auto_reply: true
  art: true
```

### TypeScript/JavaScript-Specific Best Practices Summary

**Type Safety**:
- Avoid `any`, use `unknown` or proper types
- Use strict TypeScript configuration
- Leverage type guards and discriminated unions
- Use `satisfies` operator for type checking

**React Best Practices**:
- Use functional components with hooks
- Implement proper error boundaries
- Optimize re-renders with React.memo
- Use proper key props in lists
- Implement code splitting with lazy loading

**Async Patterns**:
- Use async/await over promise chains
- Implement proper error boundaries for async operations
- Cancel ongoing requests on unmount
- Handle race conditions properly

**Performance**:
- Implement lazy loading for routes
- Optimize bundle size with tree shaking
- Use web workers for heavy computations
- Implement proper caching strategies

---

## 3. Path Instructions Library

### Comprehensive Path-Specific Review Rules

```yaml
# Path Instructions Library
# Reusable patterns for different project structures

path_instructions:
  # ========================================
  # BACKEND/API PATTERNS
  # ========================================

  # REST API Controllers
  - path: "**/controllers/**/*.{ts,js,py}"
    instructions: |
      Review API controllers for:
      - Input validation using schemas (Joi, Zod, Pydantic)
      - Proper HTTP status codes (200, 201, 400, 401, 403, 404, 500)
      - Error handling with try-catch or error middleware
      - Request logging for debugging
      - Response consistency (same structure across endpoints)
      - Rate limiting implementation
      - Authentication/authorization checks
      - CORS configuration appropriateness

  # Database Models
  - path: "**/models/**/*.{ts,js,py}"
    instructions: |
      Review database models for:
      - Proper field types and constraints
      - Index definitions for query performance
      - Relationship definitions (foreign keys)
      - Validation rules at model level
      - Migration strategy compatibility
      - Proper use of timestamps
      - Soft delete implementation if needed

  # Database Migrations
  - path: "**/migrations/**/*.{ts,js,py,sql}"
    instructions: |
      Review migrations for:
      - Reversibility (up and down migrations)
      - Data preservation strategies
      - Performance impact on large tables
      - Index creation with concurrent mode if needed
      - Proper transaction handling
      - Breaking change considerations

  # Authentication/Authorization
  - path: "**/{auth,authentication,authorization}/**/*.{ts,js,py}"
    instructions: |
      Review auth code for:
      - Secure password hashing (bcrypt, argon2)
      - JWT token expiration and refresh logic
      - Session management security
      - CSRF protection implementation
      - Rate limiting on auth endpoints
      - Secure cookie configuration
      - Multi-factor authentication flow
      - Permission/role checking logic

  # ========================================
  # FRONTEND PATTERNS
  # ========================================

  # UI Components Library
  - path: "**/components/ui/**/*.{tsx,jsx,vue,svelte}"
    instructions: |
      Review UI components for:
      - Accessibility (ARIA attributes, keyboard navigation)
      - Responsive design implementation
      - Theme/variant prop patterns
      - Proper TypeScript prop types
      - Storybook stories if applicable
      - Style isolation (CSS Modules, styled-components)
      - Dark mode support

  # Forms
  - path: "**/{forms,form-components}/**/*.{tsx,jsx,vue}"
    instructions: |
      Review form components for:
      - Client-side validation rules
      - Error message display strategy
      - Accessibility (labels, error associations)
      - Form state management
      - Loading and disabled states
      - Submit handler error handling
      - Reset functionality

  # Pages/Routes
  - path: "**/{pages,routes,views}/**/*.{tsx,jsx,vue,svelte}"
    instructions: |
      Review page components for:
      - Data fetching strategies (SSR, CSR, ISR)
      - Loading states and skeletons
      - Error boundaries
      - SEO optimization (meta tags, titles)
      - Code splitting appropriateness
      - Authentication guards
      - Analytics tracking

  # ========================================
  # TESTING PATTERNS
  # ========================================

  # Unit Tests
  - path: "**/*.{test,spec}.{ts,tsx,js,jsx,py}"
    instructions: |
      Review unit tests for:
      - Test isolation and independence
      - Descriptive test names (it should...)
      - Arrange-Act-Assert pattern
      - Edge case coverage
      - Mock appropriateness
      - Assertion specificity
      - Test performance

  # Integration Tests
  - path: "**/{integration,e2e}/**/*.{test,spec}.{ts,js,py}"
    instructions: |
      Review integration tests for:
      - Test data setup and teardown
      - Database transaction handling
      - External service mocking
      - Real-world scenario coverage
      - Test execution time
      - Flaky test prevention

  # Test Fixtures
  - path: "**/{fixtures,factories,mocks}/**/*.{ts,js,py}"
    instructions: |
      Review test fixtures for:
      - Data realism and variety
      - Factory pattern usage
      - Seed data consistency
      - Cleanup strategies
      - Type safety for fixtures

  # ========================================
  # CONFIGURATION PATTERNS
  # ========================================

  # Environment Configuration
  - path: "**/{.env*,config}/**/*.{ts,js,py,yaml,json}"
    instructions: |
      Review configuration for:
      - No hardcoded secrets or API keys
      - Environment variable validation
      - Type safety for config objects
      - Default value appropriateness
      - Documentation of required variables
      - Schema validation (Zod, Joi, Pydantic)

  # Build Configuration
  - path: "**/{webpack,vite,rollup,esbuild}.config.{ts,js}"
    instructions: |
      Review build config for:
      - Bundle optimization settings
      - Source map configuration
      - Environment-specific builds
      - Plugin configuration appropriateness
      - Tree shaking enablement
      - Code splitting strategy

  # ========================================
  # DOCUMENTATION PATTERNS
  # ========================================

  # API Documentation
  - path: "**/{docs,documentation}/**/*.{md,mdx}"
    instructions: |
      Review documentation for:
      - Code examples accuracy
      - API endpoint documentation completeness
      - Parameter descriptions
      - Response schema examples
      - Error scenario documentation
      - Authentication requirements
      - Rate limit information

  # README Files
  - path: "**/README.md"
    instructions: |
      Review README for:
      - Clear project description
      - Installation instructions
      - Usage examples
      - Contributing guidelines link
      - License information
      - Contact/support information

  # ========================================
  # INFRASTRUCTURE/DEVOPS PATTERNS
  # ========================================

  # Docker Configuration
  - path: "**/Dockerfile*"
    instructions: |
      Review Dockerfiles for:
      - Multi-stage builds for size optimization
      - Proper base image selection
      - Layer caching optimization
      - Security (non-root user, minimal image)
      - Build argument usage
      - Health check definitions

  # CI/CD Configuration
  - path: "**/.github/workflows/**/*.{yml,yaml}"
    instructions: |
      Review CI/CD workflows for:
      - Secret handling security
      - Job dependency optimization
      - Caching strategies
      - Matrix build appropriateness
      - Deployment safeguards
      - Test coverage requirements

  # Kubernetes/Helm
  - path: "**/{k8s,kubernetes,helm}/**/*.{yaml,yml}"
    instructions: |
      Review Kubernetes configs for:
      - Resource limits and requests
      - Liveness and readiness probes
      - Security contexts
      - ConfigMap and Secret usage
      - Service mesh configuration
      - Horizontal pod autoscaling

  # ========================================
  # DATA SCIENCE/ML PATTERNS
  # ========================================

  # Jupyter Notebooks
  - path: "**/*.ipynb"
    instructions: |
      Review notebooks for:
      - Clear markdown explanations
      - Reproducible execution order
      - Random seed setting
      - Memory cleanup after operations
      - Visualization labels and titles
      - Export readiness (non-interactive)

  # Model Training Scripts
  - path: "**/training/**/*.py"
    instructions: |
      Review training code for:
      - Hyperparameter logging
      - Checkpoint saving strategy
      - Early stopping implementation
      - GPU memory management
      - Training/validation split logic
      - Metric tracking and logging
      - Reproducibility (seeds, determinism)

  # Data Pipelines
  - path: "**/pipelines/**/*.py"
    instructions: |
      Review pipeline code for:
      - Data validation at each stage
      - Error handling and retries
      - Logging for debugging
      - Memory efficiency
      - Parallelization appropriateness
      - Data lineage tracking

  # ========================================
  # SECURITY PATTERNS
  # ========================================

  # Security-Critical Code
  - path: "**/{security,crypto,encryption}/**/*.{ts,js,py}"
    instructions: |
      Review security code with extra scrutiny for:
      - Use of approved cryptographic libraries
      - Proper key management
      - No custom crypto implementations
      - Secure random number generation
      - Timing attack prevention
      - Input sanitization
      - Security header configuration

  # Secrets/Credentials
  - path: "**/{secrets,credentials,keys}/**"
    instructions: |
      Flag any hardcoded secrets immediately:
      - API keys should be in environment variables
      - Passwords should never be committed
      - Tokens should be externalized
      - Certificate private keys require secure storage
```

---

## 4. AST Pattern Rules

### Advanced Code Pattern Validation Rules

#### JavaScript/TypeScript AST Rules

**File**: `.coderabbit/ast-grep/typescript/no-console-in-production.yml`

```yaml
id: no-console-in-production
language: typescript
message: "Console statements should not be present in production code. Use a proper logging library."
severity: warning

rule:
  pattern: console.$METHOD($$$)
  not:
    inside:
      any:
        - kind: if_statement
          has:
            field: condition
            regex: "(process\\.env\\.NODE_ENV|DEBUG|development)"
        - pattern: "if (import.meta.env.DEV) { $$$ }"

constraints:
  METHOD:
    regex: "^(log|debug|info|warn|error)$"

fix: |
  // Replace with proper logger
  logger.$METHOD($$$)
```

**File**: `.coderabbit/ast-grep/typescript/require-error-handling.yml`

```yaml
id: require-async-error-handling
language: typescript
message: "Async functions should have proper error handling"
severity: error

rule:
  kind: function_declaration
  has:
    field: async
    regex: "^async$"
  not:
    has:
      any:
        - kind: try_statement
        - kind: catch_clause
        - pattern: ".catch($$$)"

note: "All async functions should use try-catch or .catch() for error handling"
```

**File**: `.coderabbit/ast-grep/typescript/no-any-type.yml`

```yaml
id: no-any-type
language: typescript
message: "Avoid using 'any' type. Use 'unknown' or specific types instead."
severity: warning

rule:
  pattern: ": any"
  not:
    inside:
      any:
        - kind: comment
        - pattern: "@ts-ignore"
        - pattern: "@ts-expect-error"

fix: ": unknown"

note: |
  Using 'any' defeats the purpose of TypeScript's type system.
  Consider:
  - Use 'unknown' if the type is truly unknown
  - Define a proper interface or type
  - Use generics for flexible typing
```

**File**: `.coderabbit/ast-grep/typescript/react-missing-key.yml`

```yaml
id: react-missing-key-prop
language: tsx
message: "Array items in JSX must have a 'key' prop"
severity: error

rule:
  pattern: |
    {$ARRAY.map($CALLBACK)}
  has:
    kind: jsx_element
    not:
      has:
        kind: jsx_attribute
        has:
          field: name
          regex: "^key$"

note: "Each child in a list should have a unique 'key' prop for React reconciliation"
```

**File**: `.coderabbit/ast-grep/typescript/useeffect-missing-deps.yml`

```yaml
id: useeffect-missing-dependencies
language: tsx
message: "useEffect may have missing dependencies"
severity: warning

rule:
  pattern: |
    useEffect(() => {
      $$$BODY
    }, [$$$DEPS])

  # This rule requires manual review as dependency analysis is complex
note: |
  Verify that all variables used in the effect are in the dependency array.
  ESLint's exhaustive-deps rule is more accurate for this check.
```

#### Python AST Rules

**File**: `.coderabbit/ast-grep/python/no-bare-except.yml`

```yaml
id: no-bare-except
language: python
message: "Avoid bare 'except:' clauses. Catch specific exceptions."
severity: warning

rule:
  pattern: |
    try:
        $$$
    except:
        $$$

fix: |
  try:
      $$$
  except Exception as e:
      # Handle specific exception
      $$$

note: "Bare except catches all exceptions including KeyboardInterrupt and SystemExit"
```

**File**: `.coderabbit/ast-grep/python/require-type-hints.yml`

```yaml
id: require-type-hints
language: python
message: "Function parameters should have type hints"
severity: warning

rule:
  kind: function_definition
  has:
    kind: parameters
    has:
      kind: identifier
      not:
        has:
          kind: type

note: |
  Public functions should have type hints for:
  - All parameters
  - Return values
  This improves code documentation and enables static type checking with mypy.
```

**File**: `.coderabbit/ast-grep/python/mutable-default-argument.yml`

```yaml
id: mutable-default-argument
language: python
message: "Avoid mutable default arguments (list, dict, set)"
severity: error

rule:
  kind: function_definition
  has:
    kind: parameters
    has:
      kind: default_parameter
      has:
        any:
          - pattern: "[]"
          - pattern: "{}"
          - pattern: "set()"
          - pattern: "list()"
          - pattern: "dict()"

fix: |
  # Use None as default and create mutable in function body
  def function($PARAM = None):
      if $PARAM is None:
          $PARAM = []

note: "Mutable default arguments are evaluated once and shared across calls"
```

**File**: `.coderabbit/ast-grep/python/numpy-vectorization.yml`

```yaml
id: prefer-numpy-vectorization
language: python
message: "Consider using NumPy vectorized operations instead of loops"
severity: info

rule:
  pattern: |
    for $VAR in $ARRAY:
        $RESULT[$INDEX] = $OPERATION

note: |
  NumPy vectorized operations are typically 10-100x faster than Python loops.
  Consider: np.array operations, np.vectorize, or broadcasting.
```

**File**: `.coderabbit/ast-grep/python/pandas-chain-assignments.yml`

```yaml
id: pandas-avoid-chain-assignment
language: python
message: "Avoid chained assignment in pandas, use .loc[] instead"
severity: warning

rule:
  pattern: $DF[$COL1][$COL2] = $VALUE

fix: $DF.loc[$COL2, $COL1] = $VALUE

note: "Chained assignment can cause SettingWithCopyWarning and unexpected behavior"
```

#### Utility Rules

**File**: `.coderabbit/ast-grep/utils/is-test-file.yml`

```yaml
# Utility rule to identify test files
id: is-test-file
language: typescript

rule:
  any:
    - pattern: describe($$$)
    - pattern: it($$$)
    - pattern: test($$$)
    - pattern: expect($$$)
    - kind: import_statement
      has:
        pattern: |
          from "@testing-library/react"
```

**File**: `.coderabbit/ast-grep/utils/is-react-component.yml`

```yaml
# Utility rule to identify React components
id: is-react-component
language: tsx

rule:
  any:
    - kind: function_declaration
      has:
        kind: return_statement
        has:
          kind: jsx_element
    - kind: arrow_function
      has:
        kind: jsx_element
```

---

## 5. Tool Integration Guide

### Ruff Integration (Python)

**Configuration**: `pyproject.toml`

```toml
[tool.ruff]
# Target Python 3.10+
target-version = "py310"

# Line length
line-length = 100

# Assume Python 3.10+
required-version = ">=0.1.0"

[tool.ruff.lint]
# Enable rule sets
select = [
    "E",    # pycodestyle errors
    "F",    # Pyflakes
    "W",    # pycodestyle warnings
    "B",    # flake8-bugbear
    "I",    # isort
    "N",    # pep8-naming
    "UP",   # pyupgrade
    "YTT",  # flake8-2020
    "S",    # flake8-bandit (security)
    "BLE",  # flake8-blind-except
    "FBT",  # flake8-boolean-trap
    "A",    # flake8-builtins
    "C4",   # flake8-comprehensions
    "DTZ",  # flake8-datetimez
    "T10",  # flake8-debugger
    "EM",   # flake8-errmsg
    "ISC",  # flake8-implicit-str-concat
    "ICN",  # flake8-import-conventions
    "G",    # flake8-logging-format
    "INP",  # flake8-no-pep420
    "PIE",  # flake8-pie
    "T20",  # flake8-print
    "PT",   # flake8-pytest-style
    "Q",    # flake8-quotes
    "RSE",  # flake8-raise
    "RET",  # flake8-return
    "SLF",  # flake8-self
    "SIM",  # flake8-simplify
    "TID",  # flake8-tidy-imports
    "TCH",  # flake8-type-checking
    "ARG",  # flake8-unused-arguments
    "PTH",  # flake8-use-pathlib
    "ERA",  # eradicate
    "PD",   # pandas-vet
    "PL",   # Pylint
    "TRY",  # tryceratops
    "NPY",  # NumPy-specific rules
    "RUF",  # Ruff-specific rules
]

ignore = [
    "E501",   # Line too long (handled by formatter)
    "S101",   # Use of assert (okay in tests)
    "PLR0913", # Too many arguments
    "TRY003", # Avoid specifying messages outside exception class
]

# Allow fix for all enabled rules
fixable = ["ALL"]
unfixable = []

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"__init__.py" = ["F401"]  # Unused imports
"tests/**/*.py" = [
    "S101",    # Assert usage
    "ARG",     # Unused function arguments
    "FBT",     # Boolean trap
    "PLR2004", # Magic values
]
"**/migrations/**/*.py" = ["ALL"]  # Generated code

[tool.ruff.lint.isort]
known-first-party = ["your_package_name"]
known-third-party = ["numpy", "pandas", "torch", "sklearn"]

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.ruff.lint.pydocstyle]
convention = "google"  # or "numpy"

[tool.ruff.lint.pylint]
max-args = 7
max-branches = 15
max-returns = 6
max-statements = 50

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
skip-magic-trailing-comma = false
line-ending = "auto"
```

**CodeRabbit YAML Integration**:

```yaml
reviews:
  tools:
    ruff:
      enabled: true

  path_instructions:
    - path: "**/*.py"
      instructions: |
        Ensure code complies with Ruff rules:
        - All security issues (S prefix) must be addressed
        - Simplification suggestions (SIM prefix) should be considered
        - NumPy/Pandas best practices (NPY, PD prefixes)
```

### ESLint Integration (TypeScript/JavaScript)

**Configuration**: `eslint.config.js` (Flat Config)

```javascript
// eslint.config.js
import js from "@eslint/js";
import typescript from "@typescript-eslint/eslint-plugin";
import typescriptParser from "@typescript-eslint/parser";
import react from "eslint-plugin-react";
import reactHooks from "eslint-plugin-react-hooks";
import security from "eslint-plugin-security";
import { defineConfig } from "eslint/config";

export default defineConfig([
  js.configs.recommended,

  {
    files: ["**/*.{ts,tsx}"],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2024,
        sourceType: "module",
        ecmaFeatures: {
          jsx: true,
        },
        project: "./tsconfig.json",
      },
      globals: {
        window: "readonly",
        document: "readonly",
        navigator: "readonly",
      },
    },
    plugins: {
      "@typescript-eslint": typescript,
      react,
      "react-hooks": reactHooks,
      security,
    },
    rules: {
      // TypeScript rules
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/explicit-function-return-type": "warn",
      "@typescript-eslint/no-unused-vars": ["error", {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      }],
      "@typescript-eslint/consistent-type-imports": "error",
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/await-thenable": "error",
      "@typescript-eslint/no-misused-promises": "error",

      // React rules
      "react/react-in-jsx-scope": "off", // Not needed in React 17+
      "react/prop-types": "off", // Using TypeScript
      "react/jsx-uses-react": "off",
      "react-hooks/rules-of-hooks": "error",
      "react-hooks/exhaustive-deps": "warn",

      // Security rules
      "security/detect-object-injection": "warn",
      "security/detect-non-literal-regexp": "warn",
      "security/detect-unsafe-regex": "error",

      // Best practices
      "no-console": ["warn", { allow: ["warn", "error"] }],
      "no-debugger": "error",
      "eqeqeq": ["error", "always"],
      "prefer-const": "error",
      "no-var": "error",
    },
    settings: {
      react: {
        version: "detect",
      },
    },
  },

  // Test files
  {
    files: ["**/*.{test,spec}.{ts,tsx}"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
      "security/detect-object-injection": "off",
    },
  },
]);
```

**CodeRabbit YAML Integration**:

```yaml
reviews:
  tools:
    eslint:
      enabled: true

    oxc:
      enabled: true  # Alternative fast linter

  path_instructions:
    - path: "**/*.{ts,tsx}"
      instructions: |
        Ensure ESLint compliance:
        - No 'any' types without justification
        - Proper async error handling
        - React hooks dependency arrays complete
        - Security issues addressed immediately
```

### Multiple Tool Coordination

**Strategy**: Use complementary tools for comprehensive coverage

```yaml
reviews:
  tools:
    # Python ecosystem
    ruff:
      enabled: true  # Fast linting and formatting

    pylint:
      enabled: true  # Additional checks Ruff doesn't cover

    mypy:
      enabled: true  # Static type checking (if supported)

    # JavaScript/TypeScript ecosystem
    eslint:
      enabled: true  # Comprehensive JS/TS linting

    biome:
      enabled: true  # Fast alternative with formatting

    oxc:
      enabled: true  # High-performance linting

    # Security
    gitleaks:
      enabled: true  # Secret scanning

    semgrep:
      enabled: true  # Advanced security patterns

    # Infrastructure
    shellcheck:
      enabled: true  # Shell script linting

    hadolint:
      enabled: true  # Dockerfile linting

    yamllint:
      enabled: true  # YAML linting

    # Language-specific
    swiftlint:
      enabled: false  # Enable for iOS projects

    detekt:
      enabled: false  # Enable for Kotlin projects

    golangci-lint:
      enabled: false  # Enable for Go projects

    # AST pattern matching
    ast-grep:
      essential_rules: true
      rule_dirs:
        - ".coderabbit/ast-grep/typescript"
        - ".coderabbit/ast-grep/python"
      util_dirs:
        - ".coderabbit/ast-grep/utils"
      packages:
        - "coderabbitai/ast-grep-essentials"
```

---

## 6. Multi-Language Configuration Patterns

### Monorepo with Multiple Languages

```yaml
# .coderabbit.yaml for multi-language monorepo
language: en-US

reviews:
  profile: assertive

  # Language-specific path instructions
  path_instructions:
    # Python backend
    - path: "backend/**/*.py"
      instructions: |
        Python backend code review focusing on:
        - FastAPI/Django best practices
        - Async handling with asyncio
        - Database query optimization
        - API security (authentication, rate limiting)
        - Type hints completeness

    # TypeScript frontend
    - path: "frontend/**/*.{ts,tsx}"
      instructions: |
        React TypeScript frontend review:
        - Component composition patterns
        - State management efficiency
        - Performance optimization
        - Accessibility compliance
        - Bundle size considerations

    # Go microservices
    - path: "services/**/*.go"
      instructions: |
        Go microservice review:
        - Error handling patterns
        - Context propagation
        - Goroutine safety
        - Memory management
        - gRPC best practices

    # Shared configuration
    - path: "config/**/*.{yaml,json}"
      instructions: |
        Configuration file review:
        - No hardcoded secrets
        - Environment-specific values
        - Schema validation
        - Documentation completeness

    # Infrastructure as code
    - path: "infrastructure/**/*.{tf,yml,yaml}"
      instructions: |
        Infrastructure review:
        - Terraform best practices
        - Kubernetes security
        - Resource limits defined
        - Cost optimization
        - Disaster recovery considerations

  # Path filters by language
  path_filters:
    # Python excludes
    - "!**/__pycache__/**"
    - "!**/*.pyc"
    - "!**/.pytest_cache/**"

    # JavaScript/TypeScript excludes
    - "!**/node_modules/**"
    - "!**/dist/**"
    - "!**/.next/**"

    # Go excludes
    - "!**/vendor/**"
    - "!**/*.pb.go"

    # General excludes
    - "!**/build/**"
    - "!**/coverage/**"

  # Enable all relevant tools
  tools:
    # Python
    ruff:
      enabled: true
    pylint:
      enabled: true

    # JavaScript/TypeScript
    eslint:
      enabled: true
    biome:
      enabled: true

    # Go
    golangci-lint:
      enabled: true

    # Security
    gitleaks:
      enabled: true
    semgrep:
      enabled: true

    # Infrastructure
    shellcheck:
      enabled: true
    hadolint:
      enabled: true
    yamllint:
      enabled: true
    checkov:
      enabled: true
```

### Project-Specific Configurations

#### Machine Learning Project

```yaml
# ML-specific configuration
language: en-US
tone_instructions: "Focus on reproducibility, data integrity, and model performance"

reviews:
  profile: assertive

  path_instructions:
    - path: "**/models/**/*.py"
      instructions: |
        ML model code requires:
        - Reproducible random seeds
        - Hyperparameter logging (MLflow, W&B)
        - Model versioning strategy
        - GPU memory management
        - Checkpointing logic
        - Evaluation metric appropriateness

    - path: "**/data/**/*.py"
      instructions: |
        Data pipeline code requires:
        - Data validation (Great Expectations, Pandera)
        - Schema enforcement
        - Memory-efficient processing
        - Data lineage tracking
        - Edge case handling

    - path: "**/*.ipynb"
      instructions: |
        Notebooks should demonstrate:
        - Clear narrative flow
        - Reproducible execution
        - Visualizations with proper labels
        - Memory cleanup
        - Export readiness

  tools:
    ruff:
      enabled: true
    pylint:
      enabled: true

  finishing_touches:
    docstrings:
      enabled: true
    unit_tests:
      enabled: true

code_generation:
  docstrings:
    path_instructions:
      - path: "**/models/**/*.py"
        instructions: |
          Include in model docstrings:
          - Architecture description
          - Input/output shapes
          - Training procedure
          - Performance metrics
          - Paper references
```

#### Full-Stack Web Application

```yaml
# Full-stack web app configuration
language: en-US

reviews:
  profile: chill

  path_instructions:
    - path: "src/client/**/*.{ts,tsx}"
      instructions: |
        Frontend review priorities:
        - React best practices
        - Performance optimization
        - Accessibility (WCAG 2.1 AA)
        - SEO considerations
        - Error boundaries

    - path: "src/server/**/*.ts"
      instructions: |
        Backend review priorities:
        - API security
        - Database optimization
        - Error handling
        - Logging strategy
        - Rate limiting

    - path: "src/shared/**/*.ts"
      instructions: |
        Shared code review:
        - Pure functions preferred
        - Framework-agnostic design
        - Comprehensive type definitions
        - Universal compatibility

  tools:
    eslint:
      enabled: true
    biome:
      enabled: true
    gitleaks:
      enabled: true

  pre_merge_checks:
    title:
      mode: warning
      requirements: "Use conventional commits (feat:, fix:, etc.)"

    description:
      mode: warning

knowledge_base:
  opt_out: false
  code_guidelines:
    enabled: true
    file_patterns:
      - "**/.cursorrules"
      - "**/CONTRIBUTING.md"
```

---

## Key Findings and Recommendations

### 1. Configuration Hierarchy

**Best Practice**: Use layered configuration approach

1. **Organization-level**: Base standards via CodeRabbit dashboard
2. **Repository-level**: `.coderabbit.yaml` for project-specific rules
3. **Path-level**: Specialized instructions for different codebases
4. **AST-level**: Advanced pattern matching for complex scenarios

### 2. Tool Selection Strategy

**Python Projects**:
- **Primary**: Ruff (fast, comprehensive)
- **Secondary**: Pylint (additional checks)
- **Type Safety**: MyPy integration via pre-commit
- **Security**: Gitleaks + Semgrep

**TypeScript/JavaScript Projects**:
- **Primary**: ESLint (comprehensive ecosystem)
- **Fast Alternative**: Biome or Oxc for performance
- **Security**: ESLint security plugins + Gitleaks
- **React**: ESLint React/Hooks plugins

**Multi-Language**:
- Enable language-specific tools per directory
- Use path filters to prevent tool conflicts
- Leverage AST-grep for universal patterns

### 3. Path Instruction Patterns

**Most Effective Patterns**:
1. **Technology-specific**: Match project stack (React, FastAPI, etc.)
2. **Architecture-specific**: API, models, views, controllers
3. **Purpose-specific**: Tests, docs, config, infrastructure
4. **Security-critical**: Auth, crypto, payment processing

### 4. AST Rule Development

**When to Use AST Rules**:
- Complex code patterns not caught by linters
- Organization-specific conventions
- Security-critical patterns
- Performance anti-patterns

**Rule Development Process**:
1. Identify pattern using ast-grep playground
2. Test on real codebase examples
3. Validate fix suggestions
4. Document with clear messages

### 5. Real-World Examples Analyzed

From research on open-source projects (Appsmith, Novu, etc.):

**Common Patterns**:
- Path filters to exclude build artifacts
- Technology-specific instructions per directory
- Integration of multiple complementary tools
- Security tool enablement (Gitleaks standard)
- Pre-merge checks for documentation quality

**Less Common but Valuable**:
- AST-grep custom rules (advanced users)
- MCP server integrations for context
- Custom package development
- Multi-repo configurations

---

## Implementation Checklist

### For New Projects

- [ ] Copy relevant template (Python, TypeScript, or Multi-language)
- [ ] Customize `path_instructions` for project structure
- [ ] Enable appropriate tools for language stack
- [ ] Configure path filters for generated files
- [ ] Set up pre-merge checks based on team maturity
- [ ] Add custom coding guidelines to knowledge base
- [ ] Test configuration on sample PRs

### For Existing Projects

- [ ] Audit current CodeRabbit configuration
- [ ] Identify pain points (false positives, missed issues)
- [ ] Incrementally add path instructions
- [ ] Enable additional tools one at a time
- [ ] Gather team feedback on review quality
- [ ] Iterate on rule severity levels
- [ ] Document team-specific conventions

### For Advanced Users

- [ ] Develop custom AST rules for common patterns
- [ ] Create shareable rule packages
- [ ] Integrate with CI/CD for enforcement
- [ ] Set up MCP servers for additional context
- [ ] Configure learnings scope for organization
- [ ] Implement custom pre-merge checks
- [ ] Monitor and optimize tool performance

---

## Additional Resources

### Documentation Links
- [CodeRabbit Configuration Reference](https://docs.coderabbit.ai/reference/configuration)
- [Review Instructions Guide](https://docs.coderabbit.ai/guides/review-instructions)
- [AST-Grep Documentation](https://ast-grep.github.io/)
- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [ESLint Configuration](https://eslint.org/docs/latest/use/configure/)

### Tool-Specific Resources
- **Ruff**: `/astral-sh/ruff` on Context7
- **ESLint**: `/eslint/eslint` on Context7
- **AST-Grep Playground**: https://ast-grep.github.io/playground.html

### Community Examples
- [awesome-coderabbit](https://github.com/coderabbitai/awesome-coderabbit)
- [ast-grep-essentials](https://github.com/coderabbitai/ast-grep-essentials)

---

## Conclusion

This research provides comprehensive language-specific configuration templates for CodeRabbit, covering:

1. **Python/AI/ML projects** with data science and machine learning optimizations
2. **TypeScript/JavaScript full-stack** applications with React and Node.js patterns
3. **Extensive path instruction library** for common architectural patterns
4. **AST rule examples** for advanced code pattern validation
5. **Tool integration strategies** with configuration examples
6. **Multi-language patterns** for monorepos and complex projects

The configurations are production-ready, based on real-world usage patterns, and aligned with industry best practices. They can be adapted incrementally to fit specific project requirements while maintaining comprehensive code quality standards.
