# GitHub Repository Setup Guide: kellerai/coderabbit

## Overview

This document outlines the setup procedures for the `kellerai/coderabbit` central configuration repository that serves as the organization-wide baseline for CodeRabbit code reviews.

## Repository Creation

### Step 1: Create Repository

1. Navigate to GitHub organization: `https://github.com/kellerai`
2. Click "New repository"
3. Configure repository settings:
   - **Repository name**: `coderabbit`
   - **Description**: "Central CodeRabbit configuration and knowledge base for KellerAI organization"
   - **Visibility**: Private (organization repositories only)
   - **Initialize with**:
     - README.md (will be overwritten with custom content)
     - .gitignore (Node.js, Python)
     - LICENSE (MIT or organization standard)

### Step 2: Repository Settings

Navigate to Settings > General:

**Features:**
- ✅ Issues
- ✅ Projects (for tracking configuration changes)
- ✅ Discussions (for team collaboration)
- ✅ Wiki (for extended documentation)

**Pull Requests:**
- ✅ Allow merge commits
- ✅ Allow squash merging
- ✅ Allow rebase merging
- ✅ Automatically delete head branches

**Merge button:**
- ✅ Require approval before merge
- ✅ Dismiss stale pull request approvals when new commits are pushed

## Branch Protection Rules

### Main Branch Protection

Navigate to Settings > Branches > Add rule:

**Branch name pattern**: `main`

**Protect matching branches:**
- ✅ Require a pull request before merging
  - ✅ Require approvals: 2
  - ✅ Dismiss stale pull request approvals when new commits are pushed
  - ✅ Require review from Code Owners
- ✅ Require status checks to pass before merging
  - ✅ Require branches to be up to date before merging
  - **Required status checks:**
    - `yaml-validation` (GitHub Actions workflow)
    - `config-test` (GitHub Actions workflow)
- ✅ Require conversation resolution before merging
- ✅ Require signed commits
- ✅ Require linear history
- ✅ Include administrators
- ✅ Restrict pushes to specified actors (Tech Leads only)

### Development Branch Protection

**Branch name pattern**: `develop`

**Protect matching branches:**
- ✅ Require a pull request before merging
  - ✅ Require approvals: 1
- ✅ Require status checks to pass before merging
  - **Required status checks:**
    - `yaml-validation`
    - `config-test`
- ✅ Require conversation resolution before merging

## Team Access Permissions

Navigate to Settings > Manage access:

### Admin Access
- **Team**: `kellerai/admins`
- **Permission**: Admin
- **Capabilities**: Full repository access, settings management, security settings

### Tech Lead Access
- **Team**: `kellerai/tech-leads`
- **Permission**: Maintain
- **Capabilities**: Push to protected branches (with PR approval), manage issues/PRs, merge approved PRs

### Developer Access
- **Team**: `kellerai/developers`
- **Permission**: Write
- **Capabilities**: Create branches, create PRs, comment on issues/PRs

### Read-Only Access
- **Team**: `kellerai/contractors`
- **Permission**: Read
- **Capabilities**: Clone repository, read configuration files

## CODEOWNERS File

Create `.github/CODEOWNERS` file:

```
# Global code owners for central configuration
* @kellerai/tech-leads

# Baseline configuration requires tech lead approval
/.coderabbit.yaml @kellerai/tech-leads @kellerai/admins

# Template configurations require review from relevant specialists
/templates/typescript/* @kellerai/frontend-leads
/templates/python/* @kellerai/backend-leads
/templates/react/* @kellerai/frontend-leads

# GitHub Actions workflows require DevOps approval
/.github/workflows/* @kellerai/devops @kellerai/tech-leads

# Documentation can be updated by any developer (with PR approval)
/docs/* @kellerai/developers
README.md @kellerai/developers
```

## Repository Secrets

Navigate to Settings > Secrets and variables > Actions:

### Required Secrets

1. **CODERABBIT_API_KEY**
   - Description: API key for CodeRabbit CLI authentication
   - Usage: GitHub Actions workflows for automated testing

2. **SLACK_WEBHOOK_URL** (Optional)
   - Description: Slack webhook for configuration change notifications
   - Usage: Notify team when baseline config is updated

3. **GITHUB_TOKEN**
   - Description: Automatically provided by GitHub Actions
   - Usage: Push validation results, create comments on PRs

## GitHub Actions Workflows

### Required Status Checks

Create workflow files in `.github/workflows/`:

1. **yaml-validation.yml**
   - Validates YAML syntax of all configuration files
   - Runs on: Push, Pull Request
   - Required for merge

2. **config-test.yml**
   - Tests configuration inheritance
   - Validates template configurations
   - Runs on: Pull Request
   - Required for merge

3. **deploy-notification.yml**
   - Notifies team when configuration is updated
   - Runs on: Push to main
   - Optional but recommended

## Security Settings

Navigate to Settings > Code security and analysis:

**Dependency graph:**
- ✅ Enabled

**Dependabot alerts:**
- ✅ Enabled for security vulnerabilities
- ✅ Enabled for vulnerable dependencies

**Dependabot security updates:**
- ✅ Enabled

**Code scanning:**
- ✅ GitHub Advanced Security (if available)
- ✅ CodeQL analysis for YAML/JSON files

**Secret scanning:**
- ✅ Enabled to prevent accidental API key commits

## Initial Repository Structure

```
kellerai/coderabbit/
├── .github/
│   ├── CODEOWNERS                 # Code ownership rules
│   ├── workflows/
│   │   ├── yaml-validation.yml    # YAML syntax validation
│   │   ├── config-test.yml        # Configuration testing
│   │   └── deploy-notification.yml # Deployment notifications
│   ├── ISSUE_TEMPLATE/
│   │   ├── config-change.md       # Template for config change requests
│   │   └── bug-report.md          # Template for config bug reports
│   └── PULL_REQUEST_TEMPLATE.md   # PR template for config changes
├── templates/
│   ├── typescript/
│   │   └── .coderabbit.yaml       # TypeScript project template
│   ├── python/
│   │   └── .coderabbit.yaml       # Python project template
│   ├── react/
│   │   └── .coderabbit.yaml       # React project template
│   └── nodejs/
│       └── .coderabbit.yaml       # Node.js project template
├── docs/
│   ├── configuration-reference.md  # Complete config reference
│   ├── inheritance-model.md        # How inheritance works
│   ├── customization-guide.md      # Guide for teams to customize
│   └── override-procedures.md      # How to override central config
├── scripts/
│   ├── validate-yaml.sh            # YAML validation script
│   └── test-config.sh              # Configuration testing script
├── .coderabbit.yaml                # Organization baseline configuration
├── .gitignore                      # Git ignore patterns
├── LICENSE                         # Repository license
└── README.md                       # Repository documentation
```

## Validation Checklist

Before finalizing repository setup, verify:

- [ ] Repository created with correct name and visibility
- [ ] Branch protection rules configured for main and develop
- [ ] Team access permissions assigned correctly
- [ ] CODEOWNERS file created and reviewed
- [ ] Repository secrets configured (at minimum: CODERABBIT_API_KEY)
- [ ] GitHub Actions workflows created and tested
- [ ] Security settings enabled (Dependabot, secret scanning)
- [ ] Initial repository structure matches specification
- [ ] README.md provides clear repository purpose and usage
- [ ] All configuration files validated with YAML linter

## Post-Setup Tasks

After repository is created and configured:

1. **Test Configuration Inheritance**
   - Create test repository without local `.coderabbit.yaml`
   - Verify CodeRabbit detects and applies central configuration
   - Test with sample PR to confirm review settings work

2. **Team Onboarding**
   - Share repository link with development team
   - Schedule walkthrough session for configuration customization
   - Document common configuration patterns and examples

3. **Monitoring Setup**
   - Set up GitHub Insights dashboard
   - Configure notifications for failed workflow runs
   - Establish monthly review cycle for configuration effectiveness

## Troubleshooting

### Common Issues

**Issue**: Branch protection prevents initial push
- **Solution**: Temporarily disable branch protection, push initial commit, re-enable protection

**Issue**: GitHub Actions workflows fail on first run
- **Solution**: Verify secrets are configured correctly, check workflow YAML syntax

**Issue**: CODEOWNERS file not enforcing reviews
- **Solution**: Ensure team names match exactly (case-sensitive), verify team members have correct access

**Issue**: Configuration inheritance not working
- **Solution**: Verify CodeRabbit GitHub App has organization-wide access, check repository naming matches exactly

## Support and Maintenance

**Primary Contacts:**
- Tech Lead: Sarah Chen (Tech Lead) - schen@kellerai.com
- DevOps Lead: Marcus Rodriguez (DevOps Lead) - mrodriguez@kellerai.com
- CodeRabbit Admin: Alex Kim (CodeRabbit Admin) - akim@kellerai.com

**Resources:**
- CodeRabbit Documentation: https://docs.coderabbit.ai
- GitHub Branch Protection: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches
- CODEOWNERS Syntax: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners

---

**Document Version**: 1.0
**Last Updated**: 2025-10-14
**Maintained by**: KellerAI DevOps Team
