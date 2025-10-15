# Knowledge Base Versioning and Update Procedures

**Version**: 1.0.0
**Last Updated**: 2025-10-14
**Status**: Production
**Owner**: KellerAI Engineering Team

---

## Table of Contents

1. [Overview](#overview)
2. [Version Control Workflow](#version-control-workflow)
3. [Review and Approval Process](#review-and-approval-process)
4. [Automated Validation](#automated-validation)
5. [Notification System](#notification-system)
6. [Roles and Responsibilities](#roles-and-responsibilities)
7. [Update Templates](#update-templates)
8. [Review Cycles](#review-cycles)
9. [Testing Procedures](#testing-procedures)

---

## Overview

### Purpose

The knowledge base versioning system ensures consistency, quality, and maintainability of documentation that powers CodeRabbit's contextual code reviews. This includes:

- `.cursorrules` files
- `CLAUDE.md` files
- Coding standards documentation
- Security and performance guidelines
- Architectural patterns

### Versioning Strategy

**Semantic Versioning**: `MAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes to knowledge base structure or format
- **MINOR**: New sections, significant content additions
- **PATCH**: Bug fixes, typo corrections, minor clarifications

### Version Metadata

Each knowledge base file includes a frontmatter section:

```markdown
---
version: 1.2.3
last_updated: 2025-10-14
reviewers:
  - alice@kellerai.com
  - bob@kellerai.com
status: production
changelog_url: docs/knowledge-base/CHANGELOG.md
---
```

---

## Version Control Workflow

### Git Branch Strategy

```
main (production)
  ├── develop (staging)
  │   ├── feature/kb-python-standards
  │   ├── feature/kb-security-updates
  │   └── hotfix/kb-typo-correction
```

### Workflow Steps

#### 1. Create Feature Branch

```bash
# Naming convention: feature/kb-<description>
git checkout -b feature/kb-update-react-patterns

# For urgent fixes
git checkout -b hotfix/kb-security-critical
```

#### 2. Make Changes

- Update knowledge base files
- Increment version number in frontmatter
- Add entry to `docs/knowledge-base/CHANGELOG.md`
- Update `last_updated` timestamp

#### 3. Automated Validation

GitHub Actions automatically validate all changes before merge.

#### 4. Create Pull Request with proper versioning documentation

#### 5. Review and Approval (minimum 2 reviewers)

#### 6. Merge to Develop for staging validation

#### 7. Production Deployment (weekly from develop to main)

---

## Review and Approval Process

### Reviewer Roles

#### Knowledge Base Maintainer (KBM)
- **Primary responsibility**: Content accuracy and quality
- **Approval required**: All changes
- **Domains**: Python, TypeScript/React, Security

#### Technical Lead (TL)
- **Primary responsibility**: Architectural alignment
- **Approval required**: Breaking changes, major updates

#### Documentation Specialist (DS)
- **Primary responsibility**: Clarity, grammar, formatting
- **Approval required**: New sections, significant rewrites

### Review SLAs

| Change Type | Review Time | Approvals Required |
|-------------|-------------|-------------------|
| Hotfix | 4 hours | 1 KBM |
| Minor update | 1 business day | 1 KBM, 1 DS |
| Major update | 3 business days | 2 KBM, 1 TL, 1 DS |
| Breaking change | 5 business days | 3 KBM, 1 TL, 1 DS |

---

## Automated Validation

### GitHub Actions Workflows

All knowledge base changes trigger automated validation:

1. **Markdown Syntax Validation**
2. **Version Number Verification**
3. **Changelog Entry Confirmation**
4. **Link Validation**
5. **Code Example Testing**
6. **Style Guide Compliance**

### CodeRabbit CLI Integration

All generated files must pass CodeRabbit review:

```bash
# After creating/updating KB files
coderabbit review --plain docs/knowledge-base/

# Apply suggestions iteratively
# Re-run until no issues found
```

**IMPORTANT - CodeRabbit CLI Scope:**
- CLI reviews focus on **formatting, style, and documentation conventions**
- Does NOT evaluate technical accuracy, completeness, or semantic correctness
- Human review required for content validation and architectural decisions

**Recommended Workflow:**
1. Establish a stable baseline version first (manually reviewed and approved)
2. Use CLI for incremental updates to catch formatting/style regressions
3. Escalate to human reviewers when CLI suggestions conflict with project standards

**Note:** If CLI suggestions contradict established patterns or human reviewer decisions, prefer human judgment and document the rationale in `.coderabbit-overrides.log`

---

## Notification System

### Notification Channels

1. **Slack Integration**: #kb-updates channel
2. **Email Notifications**: engineering@kellerai.com
3. **Dashboard Updates**: Real-time version display

### Notification Content

- Files changed
- Version increments
- Impact assessment
- Link to changes

---

## Roles and Responsibilities

### Knowledge Base Maintainer (KBM)

**Responsibilities**:
- Review and approve content changes
- Ensure technical accuracy
- Validate code examples
- Monitor changelog completeness

**Time Commitment**: 4-6 hours/week

### Technical Lead (TL)

**Responsibilities**:
- Approve breaking changes
- Ensure architectural alignment
- Define knowledge base strategy

**Time Commitment**: 2-3 hours/week

### Documentation Specialist (DS)

**Responsibilities**:
- Review for clarity and grammar
- Ensure consistent formatting
- Maintain style guide compliance

**Time Commitment**: 3-4 hours/week

### Contributors

**Responsibilities**:
- Submit improvements
- Fix errors
- Report inconsistencies

**Access Level**: All team members

---

## Update Templates

### Template: Minor Content Update

```markdown
---
version: X.Y.Z
last_updated: YYYY-MM-DD
reviewers:
  - reviewer1@kellerai.com
  - reviewer2@kellerai.com
status: production
changelog_url: docs/knowledge-base/CHANGELOG.md
---

# [Knowledge Base Section Title]

## What's New in vX.Y.Z

- Added clarification on [topic]
- Updated example for [feature]
- Fixed typo in [section]
```

### Template: Breaking Change

```markdown
## ⚠️ BREAKING CHANGE

**Version**: X.0.0
**Date**: YYYY-MM-DD

### What's Changing
[Description]

### Why This Change
[Rationale]

### Migration Guide
[Step-by-step instructions]

### Impact Assessment
- **Affected Projects**: [List]
- **Migration Effort**: [Estimate]
```

---

## Review Cycles

### Regular Review Schedule

| Activity | Frequency | Participants | Deliverable |
|----------|-----------|--------------|-------------|
| KB Accuracy Review | Monthly | All KBMs | Updated content |
| Standards Alignment | Quarterly | TL, KBMs | Architecture review |
| Comprehensive Audit | Bi-annually | All roles | Health report |
| Emergency Updates | As needed | Relevant KBM + TL | Hotfix |

### Monthly Review Process

**Week 1**: Collect feedback
**Week 2**: Plan updates
**Week 3**: Implement updates
**Week 4**: Review and deploy

---

## Testing Procedures

### Pre-Merge Testing

```bash
# 1. Run automated validation
make validate-kb

# 2. Test with CodeRabbit CLI
coderabbit review --plain docs/knowledge-base/

# 3. Apply suggestions
# (iterative until clean)

# 4. Run integration tests
pytest tests/knowledge_base/ -v
```

### Integration Testing

Test KB changes with sample PRs across different languages to verify CodeRabbit applies the updated knowledge correctly.

### Regression Testing

Ensure previous valid code still passes and known anti-patterns are still caught.

---

## Appendices

### Appendix A: Version History

| Version | Date | Summary | Author |
|---------|------|---------|--------|
| 1.0.0 | 2025-10-14 | Initial versioning system | Engineering Team |

### Appendix B: Related Documentation

- [Central Configuration Guide](central-config.md)
- [CodeRabbit Integration](cli-integration.md)
- [Knowledge Base Structure](../knowledge-base/README.md)

### Appendix C: Support and Contacts

**Questions**: #coderabbit-kb (Slack)
**Issues**: https://github.com/kellerai/coderabbit/issues
**Email**: kb-team@kellerai.com

---

**Document Version**: 1.0.0
**Last Reviewed**: 2025-10-14
**Next Review**: 2026-01-14
