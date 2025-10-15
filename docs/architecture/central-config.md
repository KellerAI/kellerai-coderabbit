# CodeRabbit Central Configuration Architecture
## KellerAI Organization Strategy

**Document Version**: 1.0  
**Date**: 2025-10-14  
**Status**: Research Complete - Implementation Ready

---

## Executive Summary

This document provides the complete technical architecture for implementing CodeRabbit's central configuration repository strategy for KellerAI. The central configuration approach enables organization-wide baseline settings while maintaining flexibility for repository-specific customization through a well-defined inheritance hierarchy.

**Key Benefits**:
- Centralized governance of code review standards
- Consistent baseline configuration across all repositories
- Flexible repository-level overrides when needed
- Version-controlled configuration changes
- Reduced configuration maintenance overhead

---

## Table of Contents

1. [Central Repository Architecture](#1-central-repository-architecture)
2. [Configuration Hierarchy & Precedence](#2-configuration-hierarchy--precedence)
3. [Platform-Specific Implementation](#3-platform-specific-implementation)
4. [Repository Structure](#4-repository-structure)
5. [Inheritance & Override Patterns](#5-inheritance--override-patterns)
6. [Implementation Guide](#6-implementation-guide)
7. [Base Configuration Template](#7-base-configuration-template)
8. [Best Practices](#8-best-practices)

---

## 1. Central Repository Architecture

### 1.1 Core Concept

A **central configuration repository** is a special-purpose repository that contains organization-wide default settings for CodeRabbit. This repository acts as the fallback configuration source for any repository that doesn't define its own local `.coderabbit.yaml` file.

### 1.2 Architecture Diagram (ASCII)

```
┌─────────────────────────────────────────────────────────────┐
│                    KellerAI Organization                     │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │     kellerai/coderabbit (Central Repository)       │    │
│  │                                                     │    │
│  │  .coderabbit.yaml ← Organization baseline config   │    │
│  │  README.md                                          │    │
│  │  docs/                                              │    │
│  │    ├── customization-guide.md                       │    │
│  │    ├── override-examples.md                         │    │
│  │    └── changelog.md                                 │    │
│  │  templates/                                         │    │
│  │    ├── typescript-project.yaml                      │    │
│  │    ├── python-project.yaml                          │    │
│  │    └── monorepo.yaml                                │    │
│  └────────────────────────────────────────────────────┘    │
│                            │                                 │
│                            │ Inherits from (if no local     │
│                            │ .coderabbit.yaml exists)       │
│                            ▼                                 │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  Repository A     │  │  Repository B     │  ...          │
│  │                   │  │                   │               │
│  │  (uses central)   │  │  .coderabbit.yaml │               │
│  │                   │  │  (overrides)      │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

### 1.3 Key Requirements

1. **Repository Naming Convention**:
   - GitHub: `kellerai/coderabbit`
   - GitLab: `kellerai-group/coderabbit` (or `group/subgroup/coderabbit` for nested)
   - Azure DevOps: `kellerai-project/coderabbit`
   - Bitbucket Cloud: `kellerai-workspace/coderabbit`

2. **CodeRabbit Installation**: CodeRabbit must be explicitly installed on the central `coderabbit` repository to grant read access to the configuration file.

3. **Configuration File**: A `.coderabbit.yaml` file must exist in the repository root containing the organization-wide baseline settings.

---

## 2. Configuration Hierarchy & Precedence

### 2.1 Priority Levels (Highest to Lowest)

CodeRabbit resolves configuration using strict priority rules. Higher priority sources completely override lower priority sources.

```
┌─────────────────────────────────────────────────────────────┐
│                   Configuration Resolution                   │
│                         (Top → Bottom)                       │
└─────────────────────────────────────────────────────────────┘

  Priority 1: Repository File (.coderabbit.yaml in repo)
       │
       │  ↓ If not found, check next level
       │
  Priority 2: Central Repository (kellerai/coderabbit/.coderabbit.yaml)
       │
       │  ↓ If not found, check next level
       │
  Priority 3: Repository UI Settings (CodeRabbit Dashboard - Repo Settings)
       │
       │  ↓ If not found, check next level
       │
  Priority 4: Organization UI Settings (CodeRabbit Dashboard - Org Settings)
       │
       │  ↓ If not found, use defaults
       │
  Priority 5: CodeRabbit Schema Defaults
```

### 2.2 Configuration Source Visibility

CodeRabbit displays the active configuration source in PR comments:

- **Repository file**: `Path: .coderabbit.yaml`
- **Central repository**: `Repository: coderabbit/.coderabbit.yaml`
- **UI settings**: `CodeRabbit UI`

### 2.3 Resolution Logic

```
IF repository has .coderabbit.yaml THEN
    USE repository .coderabbit.yaml (ignores all other sources)
ELSE IF central coderabbit repository exists AND has .coderabbit.yaml THEN
    USE central .coderabbit.yaml
ELSE IF repository has UI settings configured THEN
    USE repository UI settings
ELSE IF organization has UI settings configured THEN
    USE organization UI settings
ELSE
    USE CodeRabbit default schema values
END IF
```

**Important**: Repository-level `.coderabbit.yaml` files provide **complete override**, not partial merging. If a repository defines its own config file, the central configuration is entirely ignored.

---

## 3. Platform-Specific Implementation

### 3.1 GitHub

**Central Repository Location**: `organization/coderabbit`

**Example**: `kellerai/coderabbit`

**Features**:
- Organization-level central configuration
- All repositories within the organization inherit from central config
- Full support for all CodeRabbit features

**Setup Steps**:
1. Create repository: `kellerai/coderabbit`
2. Add `.coderabbit.yaml` to repository root
3. Install CodeRabbit app on the `coderabbit` repository
4. All organization repositories automatically inherit settings

**Inheritance Scope**: Organization-wide

---

### 3.2 GitLab

**Central Repository Location**: `group/coderabbit` or `group/subgroup/coderabbit`

**Example**: 
- Top-level: `kellerai-group/coderabbit`
- Nested: `kellerai-group/backend-team/coderabbit`

**Features**:
- Supports nested group hierarchies
- Subgroups can have their own central config
- More granular configuration control for large organizations

**Setup Steps**:
1. Create repository: `kellerai-group/coderabbit`
2. Add `.coderabbit.yaml` to repository root
3. Install CodeRabbit on the `coderabbit` repository
4. All repositories in the group/subgroup inherit settings

**Inheritance Scope**: 
- Group-level for top-level `coderabbit` repository
- Subgroup-level for nested `subgroup/coderabbit` repository

**Advanced Pattern** (Nested Groups):
```
kellerai-group/
├── coderabbit/              ← Organization-wide defaults
├── frontend-team/
│   ├── coderabbit/          ← Frontend-specific overrides
│   ├── react-app/
│   └── vue-dashboard/
└── backend-team/
    ├── coderabbit/          ← Backend-specific overrides
    ├── api-service/
    └── worker-service/
```

---

### 3.3 Azure DevOps

**Central Repository Location**: `project/coderabbit`

**Example**: `kellerai-project/coderabbit`

**Features**:
- Project-level central configuration only
- **No cross-project configuration sharing**
- Each project requires its own `coderabbit` repository

**Setup Steps**:
1. Create repository: `coderabbit` within the project
2. Add `.coderabbit.yaml` to repository root
3. Configure personal access token (PAT) with appropriate scopes
4. Install CodeRabbit on the `coderabbit` repository
5. All repositories within the same project inherit settings

**Inheritance Scope**: Project-level only

**Limitations**:
- Cannot share configuration across multiple Azure DevOps projects
- Organizations with multiple projects need separate central configs per project

---

### 3.4 Bitbucket Cloud

**Central Repository Location**: `workspace/coderabbit`

**Example**: `kellerai-workspace/coderabbit`

**Features**:
- Workspace-level central configuration
- All repositories within the workspace inherit from central config

**Setup Steps**:
1. Create repository: `coderabbit` within the workspace
2. Add `.coderabbit.yaml` to repository root
3. Install CodeRabbit on the `coderabbit` repository
4. All workspace repositories automatically inherit settings

**Inheritance Scope**: Workspace-wide

---

### 3.5 Bitbucket Server (On-Premises)

**Status**: Central configuration **not yet implemented**

**Workaround**: Use individual repository settings via:
- Local `.coderabbit.yaml` files in each repository
- CodeRabbit UI settings for each repository

---

### 3.6 Platform Comparison Matrix

| Platform | Central Config Support | Scope | Nested Hierarchies | Cross-Project Sharing |
|----------|------------------------|-------|--------------------|-----------------------|
| **GitHub** | ✅ Yes | Organization | No | Yes |
| **GitLab** | ✅ Yes | Group/Subgroup | ✅ Yes | Yes |
| **Azure DevOps** | ✅ Yes | Project | No | ❌ No |
| **Bitbucket Cloud** | ✅ Yes | Workspace | No | Yes |
| **Bitbucket Server** | ❌ No | N/A | N/A | N/A |

---

## 4. Repository Structure

### 4.1 Recommended Central Repository Structure

```
kellerai/coderabbit/
│
├── .coderabbit.yaml              # Primary organization-wide configuration
│
├── README.md                      # Repository overview and usage instructions
│
├── docs/
│   ├── customization-guide.md    # How to customize/override settings
│   ├── configuration-reference.md # Detailed field explanations
│   ├── override-examples.md      # Common override patterns
│   ├── changelog.md              # Configuration change history
│   └── migration-guide.md        # Migrating from UI to YAML config
│
├── templates/                     # Pre-configured templates for common scenarios
│   ├── typescript-project.yaml
│   ├── python-project.yaml
│   ├── react-frontend.yaml
│   ├── nodejs-backend.yaml
│   ├── monorepo.yaml
│   ├── microservices.yaml
│   └── documentation-repo.yaml
│
├── scripts/                       # Automation scripts
│   ├── validate-config.sh        # Validate YAML syntax
│   ├── sync-to-repos.sh          # Sync config to multiple repos
│   └── generate-report.sh        # Generate config coverage report
│
└── .github/                       # Repository-specific automation
    └── workflows/
        └── validate-yaml.yml     # CI validation of config changes
```

### 4.2 Documentation Requirements

**README.md** should include:
- Purpose of the central configuration repository
- How to use and customize the configuration
- Links to detailed documentation
- Contact information for configuration changes

**docs/customization-guide.md** should cover:
- When to use central config vs repository overrides
- How to create repository-specific `.coderabbit.yaml` files
- Common customization patterns
- Template usage instructions

**docs/changelog.md** should track:
- All changes to the central configuration
- Date, author, and rationale for changes
- Impact assessment for each change

---

## 5. Inheritance & Override Patterns

### 5.1 Complete Override Pattern

**Use Case**: Repository needs entirely different configuration

**Implementation**: Create `.coderabbit.yaml` in repository root

```yaml
# Repository: special-project/.coderabbit.yaml
# This completely overrides central configuration

language: "en-US"
reviews:
  profile: "assertive"  # Different from central "chill"
  auto_review:
    enabled: true
    drafts: true        # Different from central setting
```

**Result**: Central configuration is completely ignored for this repository.

---

### 5.2 Incremental Override Pattern (Using Remote Config)

**Use Case**: Repository wants to extend central config with additional settings

**Implementation**: Use `remote_config` to reference central config, then add overrides

```yaml
# Repository: specific-project/.coderabbit.yaml
# Inherit from central, then override specific settings

remote_config:
  url: "https://raw.githubusercontent.com/kellerai/coderabbit/main/.coderabbit.yaml"

# Override specific settings
reviews:
  path_filters:
    - path-filters:
        - "!**/generated/**"  # Additional exclusion for this repo
```

**Note**: `remote_config` is an advanced feature. Check CodeRabbit documentation for latest support status.

---

### 5.3 Pure Inheritance Pattern

**Use Case**: Repository uses central configuration without modifications

**Implementation**: Do not create `.coderabbit.yaml` in the repository

**Result**: Repository automatically inherits all settings from `kellerai/coderabbit/.coderabbit.yaml`

---

### 5.4 Template-Based Override Pattern

**Use Case**: Repository needs a specialized configuration for a specific project type

**Implementation**: Copy template from central repo and customize

```bash
# Copy template from central repository
curl -o .coderabbit.yaml \
  https://raw.githubusercontent.com/kellerai/coderabbit/main/templates/typescript-project.yaml

# Edit as needed for repository-specific requirements
```

---

### 5.5 Override Decision Matrix

| Scenario | Recommended Approach | Configuration Location |
|----------|----------------------|------------------------|
| Standard repository following org conventions | Pure Inheritance | No local config needed |
| Repository needs minor path exclusions | Complete Override | Local `.coderabbit.yaml` |
| Repository requires different review profile | Complete Override | Local `.coderabbit.yaml` |
| Project-specific linting tools | Complete Override | Local `.coderabbit.yaml` |
| Documentation-only repository | Template-Based | Copy from `templates/documentation-repo.yaml` |
| Experimental features testing | Complete Override | Local `.coderabbit.yaml` |

---

## 6. Implementation Guide

### 6.1 Phase 1: Central Repository Setup

**Step 1: Create Central Repository**

```bash
# GitHub example
gh repo create kellerai/coderabbit --public --description "KellerAI CodeRabbit Central Configuration"

# Clone repository
git clone https://github.com/kellerai/coderabbit.git
cd coderabbit
```

**Step 2: Create Base Configuration**

Create `.coderabbit.yaml` with organization-wide baseline settings (see Section 7).

**Step 3: Add Documentation**

```bash
# Create directory structure
mkdir -p docs templates scripts

# Create README
cat > README.md << 'EOF'
# KellerAI CodeRabbit Central Configuration

This repository contains the organization-wide default configuration for CodeRabbit code reviews.

## How It Works

All KellerAI repositories automatically inherit these settings unless they define their own `.coderabbit.yaml` file.

## Customization

See [docs/customization-guide.md](docs/customization-guide.md) for details on overriding settings.

## Templates

Pre-configured templates are available in the `templates/` directory.
EOF
```

**Step 4: Commit and Push**

```bash
git add .
git commit -m "Initial central configuration for KellerAI"
git push origin main
```

---

### 6.2 Phase 2: CodeRabbit Installation

**Step 1: Install CodeRabbit App**

1. Navigate to CodeRabbit dashboard: https://app.coderabbit.ai
2. Select "Add Repositories"
3. Grant access to the `kellerai/coderabbit` repository
4. Install CodeRabbit on the repository

**Step 2: Verify Installation**

Create a test PR in the central repository to confirm CodeRabbit can read the configuration.

---

### 6.3 Phase 3: Rollout to Repositories

**Step 1: Audit Existing Configurations**

```bash
# Identify repositories with local .coderabbit.yaml files
gh repo list kellerai --limit 1000 --json name,defaultBranchRef \
  | jq -r '.[] | .name' \
  | while read repo; do
      if gh api repos/kellerai/$repo/contents/.coderabbit.yaml &>/dev/null; then
        echo "✓ $repo has local config"
      else
        echo "○ $repo will inherit from central"
      fi
    done
```

**Step 2: Communicate Changes**

Notify development teams about:
- Central configuration repository creation
- Inheritance behavior
- How to override settings if needed
- Timeline for rollout

**Step 3: Monitor Adoption**

Track which repositories are using central config vs local overrides:
- Review CodeRabbit PR comments for configuration source indicators
- Maintain a dashboard of configuration coverage

---

### 6.4 Phase 4: Maintenance & Evolution

**Ongoing Tasks**:

1. **Configuration Updates**:
   - Review and update central config quarterly
   - Document all changes in `docs/changelog.md`
   - Communicate breaking changes to teams

2. **Template Maintenance**:
   - Keep templates in sync with central config
   - Add new templates as project patterns emerge
   - Deprecate outdated templates

3. **Monitoring**:
   - Track adoption rates
   - Collect feedback from development teams
   - Identify common override patterns (may indicate need for central config updates)

4. **Governance**:
   - Establish approval process for central config changes
   - Require PR reviews for configuration modifications
   - Use branch protection on central repository

---

## 7. Base Configuration Template

### 7.1 Organization-Wide Baseline: `.coderabbit.yaml`

```yaml
# ============================================================================
# KellerAI CodeRabbit Central Configuration
# ============================================================================
# This configuration serves as the organization-wide baseline for all
# repositories that do not define their own .coderabbit.yaml file.
#
# Configuration Hierarchy (Highest to Lowest Priority):
#   1. Repository .coderabbit.yaml (this overrides everything)
#   2. Central repository coderabbit/.coderabbit.yaml (THIS FILE)
#   3. Repository UI settings
#   4. Organization UI settings
#   5. CodeRabbit schema defaults
#
# Documentation: https://docs.coderabbit.ai/reference/configuration
# Templates: https://github.com/kellerai/coderabbit/tree/main/templates
# ============================================================================

# ============================================================================
# GLOBAL SETTINGS
# ============================================================================

# Language for CodeRabbit reviews and comments
# Options: "en-US", "en-GB", "es", "fr", "de", "ja", "ko", "pt-BR", "zh-CN", "zh-TW"
# Default: "en-US"
language: "en-US"

# Custom tone instructions for CodeRabbit's review style
# Max length: 250 characters
# Example: "Expert code reviewer providing concise, actionable advice"
tone_instructions: "Professional and constructive code reviewer focusing on security, performance, and maintainability"

# Enable experimental early access features
# Options: true, false
# Default: false
early_access: false

# Enable free tier features (for applicable plans)
# Options: true, false
# Default: true
enable_free_tier: true

# ============================================================================
# REVIEWS CONFIGURATION
# ============================================================================

reviews:
  # Review profile determines the intensity and depth of code reviews
  # Options: "chill" (fewer, high-confidence comments), "assertive" (thorough, detailed reviews)
  # Default: "assertive"
  # Recommendation: Start with "chill" to avoid overwhelming teams, adjust based on feedback
  profile: "chill"

  # Generate high-level summary of PR changes
  # Options: true, false
  # Default: true
  high_level_summary: true

  # Include a poem in the review summary (fun feature)
  # Options: true, false
  # Default: true
  poem: false

  # Display review status in PR comments
  # Options: true, false
  # Default: true
  review_status: true

  # Request changes workflow (marks PR as "Changes Requested" if issues found)
  # Options: true, false
  # Default: false
  # Recommendation: Enable for stricter quality gates
  request_changes_workflow: false

  # Automatically collapse CodeRabbit comments after they are resolved
  # Options: true, false
  # Default: true
  collapse_walkthrough: true

  # Auto-review configuration
  auto_review:
    # Enable automatic code reviews on new PRs
    # Options: true, false
    # Default: true
    enabled: true

    # Automatically review draft PRs
    # Options: true, false
    # Default: false
    # Recommendation: Disable to reduce noise, enable if draft reviews are valuable
    drafts: false

    # Base branches to automatically review
    # Default: ["main", "master", "develop", "dev"]
    # Recommendation: Customize based on your branching strategy
    base_branches:
      - "main"
      - "develop"

    # Skip auto-review if PR title contains these keywords (case-insensitive)
    # Useful for work-in-progress PRs or specific workflows
    # Default: []
    ignore_title_keywords:
      - "WIP"
      - "DO NOT REVIEW"
      - "DRAFT"

  # Path-based review instructions
  # Allows customizing review behavior for specific file paths or patterns
  path_instructions:
    - path: "src/**/*.ts"
      instructions: |
        Review TypeScript code for:
        - Type safety and proper TypeScript usage
        - Adherence to functional programming principles
        - Proper error handling patterns
        - Unnecessary type assertions (avoid "as" keyword when possible)

    - path: "src/**/*.test.ts"
      instructions: |
        Review test files for:
        - Comprehensive test coverage
        - Clear test descriptions
        - Proper use of test doubles (mocks, stubs, spies)
        - Isolation between tests

    - path: "**/*.py"
      instructions: |
        Review Python code for:
        - PEP 8 compliance
        - Type hints usage
        - Proper exception handling
        - Docstring completeness

    - path: "infrastructure/**/*"
      instructions: |
        Review infrastructure code for:
        - Security best practices
        - Resource tagging and naming conventions
        - Cost optimization opportunities
        - Proper secret management

  # Path filters - include or exclude specific file patterns from review
  path_filters:
    # Patterns to exclude from reviews
    # Uses gitignore-style glob patterns
    - "!**/node_modules/**"
    - "!**/dist/**"
    - "!**/build/**"
    - "!**/*.generated.*"
    - "!**/coverage/**"
    - "!**/.next/**"
    - "!**/vendor/**"
    - "!**/*.min.js"
    - "!**/*.min.css"
    - "!**/package-lock.json"
    - "!**/yarn.lock"
    - "!**/pnpm-lock.yaml"

  # Tool-specific configuration
  tools:
    # Static analysis and linting tools
    # Each tool can be enabled/disabled and configured
    
    # ESLint (JavaScript/TypeScript)
    eslint:
      enabled: true
      
    # Ruff (Python)
    ruff:
      enabled: true
      
    # Gitleaks (Secret scanning)
    gitleaks:
      enabled: true
      
    # Semgrep (SAST - Static Application Security Testing)
    semgrep:
      enabled: true
      rules:
        - "p/security-audit"
        - "p/owasp-top-ten"
      
    # GitHub Actions workflow linting
    actionlint:
      enabled: true
      
    # ShellCheck (Shell script analysis)
    shellcheck:
      enabled: true
      
    # Hadolint (Dockerfile linting)
    hadolint:
      enabled: true
      
    # markdownlint (Markdown linting)
    markdownlint:
      enabled: true

  # Reviewer assignment (Enterprise feature)
  # Automatically assign reviewers based on path patterns
  # reviewer_assignment:
  #   enabled: true
  #   assignments:
  #     - path: "src/frontend/**"
  #       reviewers: ["frontend-team"]
  #     - path: "src/backend/**"
  #       reviewers: ["backend-team"]

  # Label management
  # Automatically add labels to PRs based on conditions
  labels:
    # Label PRs that need attention
    - name: "needs-review"
      conditions:
        - review_status: "pending"

    # Label PRs with security issues
    - name: "security"
      conditions:
        - tool: "gitleaks"
          has_findings: true
        - tool: "semgrep"
          has_findings: true

# ============================================================================
# CHAT CONFIGURATION
# ============================================================================

chat:
  # Enable automatic replies from CodeRabbit
  # Options: true, false
  # Default: true
  auto_reply: true

# ============================================================================
# KNOWLEDGE BASE CONFIGURATION
# ============================================================================

knowledge_base:
  # Opt out of knowledge base features (disables data retention for learning)
  # Options: true, false
  # Default: false
  opt_out: false

  # Learnings configuration
  learnings:
    # Scope of learnings to use
    # Options: "local" (repository-specific), "global" (organization-wide), "auto"
    # Default: "auto" (local for public repos, global for private repos)
    scope: "auto"

  # Pull requests configuration
  pull_requests:
    # Scope of PR history to use for knowledge base
    # Options: "local", "global", "auto"
    # Default: "auto"
    scope: "auto"

  # Issues configuration
  issues:
    # Scope of issue history to use for knowledge base
    # Options: "local", "global", "auto"
    # Default: "auto"
    scope: "auto"

  # Code guidelines learning
  code_guidelines:
    # Enable learning from organizational coding standards
    # Options: true, false
    # Default: true
    enabled: true

    # File patterns for guideline documents
    # CodeRabbit will learn from these files
    filePatterns:
      - "**/CONTRIBUTING.md"
      - "**/CODING_STANDARDS.md"
      - "**/STYLE_GUIDE.md"
      - "**/.github/PULL_REQUEST_TEMPLATE.md"

  # Integration with issue tracking systems
  integrations:
    # Jira integration
    jira:
      # Options: "auto" (disabled for public repos), "enabled", "disabled"
      # Default: "auto"
      usage: "auto"
      # project_keys:
      #   - "KELLER"

    # Linear integration
    linear:
      # Options: "auto", "enabled", "disabled"
      # Default: "auto"
      usage: "auto"
      # team_keys:
      #   - "KELLER"

    # MCP (Model Context Protocol) servers for additional context
    mcp:
      # Options: "auto", "enabled", "disabled"
      # Default: "auto"
      usage: "auto"

# ============================================================================
# CODE GENERATION CONFIGURATION
# ============================================================================

code_generation:
  # Docstring generation
  docstrings:
    # Language for generated docstrings
    # Options: "en-US", "es", "fr", etc.
    # Default: "en-US"
    language: "en-US"

    # Path-specific docstring instructions
    path_instructions:
      - path: "**/*.py"
        instructions: |
          Generate docstrings following Google Python Style Guide format.
          Include Args, Returns, Raises sections.
          
      - path: "**/*.ts"
        instructions: |
          Generate JSDoc-style docstrings for TypeScript.
          Include @param, @returns, @throws tags.

  # Unit test generation
  unit_tests:
    # Path-specific test generation instructions
    path_instructions:
      - path: "src/**/*.ts"
        instructions: |
          Generate unit tests using Jest framework.
          Follow Arrange-Act-Assert pattern.
          Include edge cases and error scenarios.
          
      - path: "**/*.py"
        instructions: |
          Generate unit tests using pytest framework.
          Use fixtures for common test data.
          Include parametrized tests for multiple scenarios.

# ============================================================================
# END OF CONFIGURATION
# ============================================================================
```

### 7.2 Template Examples

#### TypeScript Project Template: `templates/typescript-project.yaml`

```yaml
# TypeScript Project Configuration Template
# Copy this to your repository as .coderabbit.yaml and customize

language: "en-US"
tone_instructions: "TypeScript expert focusing on type safety and modern practices"

reviews:
  profile: "chill"
  high_level_summary: true
  auto_review:
    enabled: true
    drafts: false

  path_instructions:
    - path: "src/**/*.ts"
      instructions: |
        Review for type safety, avoid 'any' types, use proper generics.
        
    - path: "**/*.test.ts"
      instructions: |
        Ensure comprehensive test coverage with Jest best practices.

  path_filters:
    - "!**/node_modules/**"
    - "!**/dist/**"
    - "!**/*.d.ts"

  tools:
    eslint:
      enabled: true
```

#### Python Project Template: `templates/python-project.yaml`

```yaml
# Python Project Configuration Template
# Copy this to your repository as .coderabbit.yaml and customize

language: "en-US"
tone_instructions: "Python expert focusing on Pythonic code and PEP compliance"

reviews:
  profile: "chill"
  high_level_summary: true
  auto_review:
    enabled: true

  path_instructions:
    - path: "**/*.py"
      instructions: |
        Review for PEP 8 compliance, type hints, docstrings, and Pythonic patterns.

  tools:
    ruff:
      enabled: true
    gitleaks:
      enabled: true
```

---

## 8. Best Practices

### 8.1 Configuration Management

1. **Version Control All Changes**:
   - Treat configuration as code
   - Require PR reviews for central config changes
   - Use semantic versioning for major configuration changes

2. **Document Rationale**:
   - Add comments explaining non-obvious settings
   - Maintain changelog with justification for changes
   - Link to relevant team discussions or RFCs

3. **Test Before Rolling Out**:
   - Test configuration changes in a sandbox repository first
   - Create test PRs to verify CodeRabbit behavior
   - Validate YAML syntax with automated checks

4. **Gradual Rollout**:
   - Start with conservative settings ("chill" profile)
   - Collect feedback from teams before tightening
   - Monitor impact on PR review velocity

### 8.2 Override Strategy

1. **Default to Inheritance**:
   - Most repositories should use central config
   - Only override when truly necessary
   - Document reason for overrides in repository README

2. **Track Overrides**:
   - Maintain list of repositories with custom configs
   - Periodically review if overrides are still needed
   - Consider promoting common patterns to central config

3. **Avoid Duplication**:
   - Use templates instead of copying full configs
   - Reference central config as baseline when possible
   - Keep repository-specific configs minimal

### 8.3 Organization Governance

1. **Establish Ownership**:
   - Assign DRI (Directly Responsible Individual) for central config
   - Define approval process for changes
   - Create escalation path for configuration issues

2. **Regular Reviews**:
   - Quarterly review of central configuration
   - Annual audit of repository overrides
   - Continuous monitoring of CodeRabbit effectiveness

3. **Communication**:
   - Announce configuration changes in team channels
   - Provide migration guides for breaking changes
   - Maintain FAQ for common questions

### 8.4 Security & Compliance

1. **Secret Scanning**:
   - Always enable Gitleaks
   - Configure Semgrep with security rulesets
   - Review security findings promptly

2. **Data Retention**:
   - Understand CodeRabbit's data retention policies
   - Configure `knowledge_base.opt_out` appropriately
   - Document compliance requirements

3. **Access Control**:
   - Protect central repository with branch protection rules
   - Require code owners for configuration changes
   - Audit access to CodeRabbit dashboard

### 8.5 Performance Optimization

1. **Path Filters**:
   - Exclude generated files and large binaries
   - Filter out third-party dependencies
   - Focus reviews on business logic

2. **Tool Selection**:
   - Enable only relevant linting tools
   - Disable noisy or low-value checks
   - Balance thoroughness with review speed

3. **Review Scope**:
   - Use `ignore_title_keywords` for WIP PRs
   - Configure `base_branches` appropriately
   - Disable draft PR reviews if not needed

---

## Appendix A: Configuration Hierarchy Flowchart

```
┌──────────────────────────────────────────────────────────────┐
│         CodeRabbit Configuration Resolution Process          │
└──────────────────────────────────────────────────────────────┘

                     Pull Request Created
                              │
                              ▼
              ┌───────────────────────────────┐
              │  Check for local repository   │
              │    .coderabbit.yaml file      │
              └───────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │                   │
                  FOUND             NOT FOUND
                    │                   │
                    ▼                   ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │  USE Repository     │  │  Check for central  │
        │  .coderabbit.yaml   │  │  coderabbit repo    │
        │                     │  │  .coderabbit.yaml   │
        │  (PRIORITY 1)       │  └─────────────────────┘
        │  STOP HERE          │            │
        └─────────────────────┘  ┌─────────┴─────────┐
                                 │                   │
                               FOUND             NOT FOUND
                                 │                   │
                                 ▼                   ▼
                    ┌─────────────────────┐  ┌─────────────────────┐
                    │  USE Central Repo   │  │  Check for repo     │
                    │  .coderabbit.yaml   │  │  UI settings        │
                    │                     │  └─────────────────────┘
                    │  (PRIORITY 2)       │            │
                    │  STOP HERE          │  ┌─────────┴─────────┐
                    └─────────────────────┘  │                   │
                                           FOUND             NOT FOUND
                                             │                   │
                                             ▼                   ▼
                                ┌─────────────────────┐  ┌─────────────────────┐
                                │  USE Repository     │  │  Check for org      │
                                │  UI Settings        │  │  UI settings        │
                                │                     │  └─────────────────────┘
                                │  (PRIORITY 3)       │            │
                                │  STOP HERE          │  ┌─────────┴─────────┐
                                └─────────────────────┘  │                   │
                                                       FOUND             NOT FOUND
                                                         │                   │
                                                         ▼                   ▼
                                            ┌─────────────────────┐  ┌─────────────────────┐
                                            │  USE Organization   │  │  USE CodeRabbit     │
                                            │  UI Settings        │  │  Schema Defaults    │
                                            │                     │  │                     │
                                            │  (PRIORITY 4)       │  │  (PRIORITY 5)       │
                                            │  STOP HERE          │  │  STOP HERE          │
                                            └─────────────────────┘  └─────────────────────┘

Legend:
  PRIORITY 1 = Highest (always wins)
  PRIORITY 5 = Lowest (fallback defaults)
```

---

## Appendix B: Platform Setup Checklist

### GitHub Setup Checklist

- [ ] Create repository: `kellerai/coderabbit`
- [ ] Add `.coderabbit.yaml` to repository root
- [ ] Create documentation in `docs/` directory
- [ ] Add templates to `templates/` directory
- [ ] Install CodeRabbit app on the `coderabbit` repository
- [ ] Verify CodeRabbit can access the repository (create test PR)
- [ ] Enable branch protection on `main` branch
- [ ] Add CODEOWNERS file for configuration approval
- [ ] Communicate rollout to development teams
- [ ] Audit existing repository configurations

### GitLab Setup Checklist

- [ ] Create repository: `kellerai-group/coderabbit` (or nested path)
- [ ] Add `.coderabbit.yaml` to repository root
- [ ] Create documentation in `docs/` directory
- [ ] Add templates to `templates/` directory
- [ ] Install CodeRabbit on the `coderabbit` repository
- [ ] Verify CodeRabbit can access the repository (create test MR)
- [ ] Enable merge request approval rules
- [ ] Configure code owners for configuration changes
- [ ] Communicate rollout to development teams
- [ ] Audit existing repository configurations

### Azure DevOps Setup Checklist

- [ ] Create repository: `coderabbit` within project
- [ ] Add `.coderabbit.yaml` to repository root
- [ ] Create documentation in `docs/` directory
- [ ] Add templates to `templates/` directory
- [ ] Generate Personal Access Token (PAT) with appropriate scopes
- [ ] Install CodeRabbit using PAT
- [ ] Verify CodeRabbit can access the repository (create test PR)
- [ ] Enable branch policies on default branch
- [ ] Configure required reviewers for configuration changes
- [ ] Communicate rollout to development teams
- [ ] Note: Each project needs its own `coderabbit` repository

### Bitbucket Cloud Setup Checklist

- [ ] Create repository: `coderabbit` within workspace
- [ ] Add `.coderabbit.yaml` to repository root
- [ ] Create documentation in `docs/` directory
- [ ] Add templates to `templates/` directory
- [ ] Install CodeRabbit on the `coderabbit` repository
- [ ] Verify CodeRabbit can access the repository (create test PR)
- [ ] Enable branch permissions on main branch
- [ ] Configure default reviewers for configuration changes
- [ ] Communicate rollout to development teams
- [ ] Audit existing repository configurations

---

## Appendix C: Troubleshooting

### Configuration Not Being Applied

**Symptom**: CodeRabbit is not using the central configuration

**Possible Causes**:
1. Repository has a local `.coderabbit.yaml` file (takes precedence)
2. CodeRabbit is not installed on the central `coderabbit` repository
3. Central repository name is incorrect for the platform
4. YAML syntax errors in configuration file

**Resolution Steps**:
1. Check for local `.coderabbit.yaml` in the repository
2. Verify CodeRabbit app installation on central repository
3. Validate YAML syntax: https://www.yamllint.com/
4. Check CodeRabbit PR comment for configuration source indicator

### Platform-Specific Issues

#### GitHub: "Configuration not found"
- Verify repository name is exactly `organization/coderabbit`
- Check organization name matches CodeRabbit installation

#### GitLab: Nested groups not working
- Ensure nested path is correct: `group/subgroup/coderabbit`
- Verify CodeRabbit is installed at the correct group level

#### Azure DevOps: Cross-project configuration not working
- Expected behavior: Azure DevOps only supports project-level configuration
- Solution: Create separate `coderabbit` repository in each project

### YAML Validation Errors

**Symptom**: Configuration changes break CodeRabbit reviews

**Resolution**:
1. Use YAML validator: https://docs.coderabbit.ai/reference/yaml-validator
2. Check for common errors:
   - Incorrect indentation (YAML is whitespace-sensitive)
   - Unquoted special characters
   - Typos in field names
3. Test in sandbox repository before rolling out

---

## Appendix D: Additional Resources

### Official CodeRabbit Documentation
- Configuration Reference: https://docs.coderabbit.ai/reference/configuration
- Central Configuration Guide: https://docs.coderabbit.ai/configuration/central-configuration
- YAML Template: https://docs.coderabbit.ai/reference/yaml-template

### Community Resources
- Awesome CodeRabbit: https://github.com/coderabbitai/awesome-coderabbit
- Example Configurations: https://github.com/coderabbitai/awesome-coderabbit/tree/main/configs

### Support
- Documentation: https://docs.coderabbit.ai
- Discord Community: https://discord.gg/coderabbit
- Email Support: support@coderabbit.ai

---

## Document Changelog

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-10-14 | Research Agent | Initial comprehensive architecture document |

---

**END OF DOCUMENT**
