# KellerAI Knowledge Base for CodeRabbit

**Version:** 1.0
**Last Updated:** 2025-10-14
**Maintained By:** KellerAI Platform Team

---

## Overview

This knowledge base contains comprehensive development standards, coding guidelines, and best practices for KellerAI engineering teams. These documents are designed to be referenced by CodeRabbit during code reviews to ensure consistency, quality, and security across all projects.

## Knowledge Base Structure

```
knowledge-base/
├── README.md                        # This file
├── CLAUDE.md                        # Main architectural guidelines
├── SECURITY_STANDARDS.md            # Security best practices
├── PERFORMANCE_GUIDELINES.md        # Performance optimization guidelines
└── cursorrules/                     # Language-specific coding standards
    ├── .cursorrules-python          # Python development standards
    ├── .cursorrules-typescript      # TypeScript/JavaScript standards
    ├── .cursorrules-react           # React development standards
    └── .cursorrules-nodejs          # Node.js/API development standards
```

## Document Descriptions

### Core Documents

#### CLAUDE.md
**Comprehensive Development Reference (8,500+ lines)**

- System architecture overview
- Technology stack specifications
- Design principles (SOLID, DDD, CQRS)
- API design guidelines (REST, GraphQL)
- Data modeling conventions
- Security best practices
- Performance optimization strategies
- Testing requirements
- Documentation standards
- Code review process
- Deployment and DevOps guidelines

**When to reference**: For architectural decisions, system design, API contracts, data modeling.

#### SECURITY_STANDARDS.md
**Security Best Practices and Compliance (1,200+ lines)**

- OWASP Top 10 compliance guidelines
- Authentication and authorization patterns
- Input validation and sanitization
- Secrets management
- Security testing procedures
- Automated security scanning
- Vulnerability prevention

**When to reference**: For security-related code changes, authentication flows, data protection.

#### PERFORMANCE_GUIDELINES.md
**Performance Optimization Handbook (1,100+ lines)**

- Performance benchmarks and targets
- Database query optimization
- Caching strategies
- Frontend performance optimization
- ML model optimization
- Monitoring and profiling
- Load testing procedures

**When to reference**: For performance-critical code, database queries, frontend optimizations.

### Language-Specific Standards

#### .cursorrules-python
**Python Development Standards (1,400+ lines)**

Topics covered:
- PEP 8 compliance and naming conventions
- Type hints and type safety (mandatory)
- Google-style docstrings
- Error handling patterns
- AI/ML specific standards (reproducibility, model development)
- Performance optimization (vectorization, efficient data structures)
- Security standards (input validation, SQL injection prevention)
- Testing requirements (pytest, >80% coverage)
- Common anti-patterns to avoid

**When to reference**: For Python code reviews, AI/ML projects, data processing pipelines.

#### .cursorrules-typescript
**TypeScript/JavaScript Development Standards (1,300+ lines)**

Topics covered:
- Strict TypeScript configuration
- Type safety best practices (avoid `any`, use type guards)
- Async programming patterns
- Error handling and custom error classes
- Documentation standards (JSDoc)
- Testing with Jest/Vitest
- Performance optimization (memoization, caching)
- Security (XSS prevention, input validation)
- Common anti-patterns to avoid

**When to reference**: For TypeScript/JavaScript code reviews, backend services, tooling.

#### .cursorrules-react
**React Development Standards (1,200+ lines)**

Topics covered:
- Modern React patterns (functional components, hooks)
- Component structure and organization
- Hooks best practices (useState, useEffect, useCallback, useMemo)
- Custom hooks development
- Performance optimization (React.memo, code splitting, lazy loading)
- State management (Context, Zustand)
- Forms and validation (React Hook Form, Zod)
- Accessibility (A11y, semantic HTML, ARIA)
- Error boundaries
- Testing with React Testing Library
- Common anti-patterns to avoid

**When to reference**: For React component reviews, frontend applications, UI development.

#### .cursorrules-nodejs
**Node.js and API Development Standards (1,400+ lines)**

Topics covered:
- API framework standards (Express, NestJS)
- Request/response patterns
- Authentication and authorization (JWT, API keys, RBAC)
- Rate limiting
- Database operations (Prisma, query optimization, transactions)
- Error handling and custom error classes
- Logging (structured logging, Winston)
- Background jobs and queues (Bull)
- Testing (unit and integration tests)
- Security (input validation, CORS, Helmet)
- Common anti-patterns to avoid

**When to reference**: For API development, backend services, microservices.

## Version Control and Updates

### Versioning Strategy

We use **semantic versioning** for knowledge base documents:

- **Major version (X.0.0)**: Breaking changes, significant restructuring
- **Minor version (1.X.0)**: New sections, enhanced guidelines, non-breaking additions
- **Patch version (1.0.X)**: Typo fixes, clarifications, minor corrections

**Current Version**: 1.0.0

### Update Procedures

#### 1. Proposing Changes

Create a proposal document with:
- **Rationale**: Why is this change needed?
- **Impact**: What code/projects are affected?
- **Implementation**: How will this be rolled out?

Submit via:
```bash
# Create feature branch
git checkout -b knowledge-base/add-graphql-guidelines

# Make changes
# ...

# Commit with conventional commit format
git commit -m "docs(kb): add GraphQL API guidelines"

# Create PR
gh pr create --title "Add GraphQL API guidelines" --label "documentation"
```

#### 2. Review Process

All knowledge base changes require:
- **Technical review**: 2 senior engineers
- **Security review**: Security team (for security-related changes)
- **Platform team approval**: Final sign-off

#### 3. Change Management

After approval:
1. Update `Last Updated` date in document header
2. Update version number if applicable
3. Add entry to CHANGELOG.md
4. Notify engineering team via Slack/email
5. Update related documentation and training materials

#### 4. Deprecation Process

When deprecating guidelines:
1. Mark as deprecated with clear migration path
2. Provide 90-day notice before removal
3. Update all related documents
4. Provide training on new guidelines

### Change Log

#### Version 1.0.0 (2025-10-14)
- Initial release of comprehensive knowledge base
- Created CLAUDE.md with architectural guidelines
- Created SECURITY_STANDARDS.md
- Created PERFORMANCE_GUIDELINES.md
- Created language-specific .cursorrules files
  - Python development standards
  - TypeScript/JavaScript standards
  - React development standards
  - Node.js/API development standards

## CodeRabbit Integration

### Automatic Knowledge Base Detection

CodeRabbit automatically detects and uses knowledge base files with these patterns:

```yaml
# .coderabbit.yaml
knowledge_base:
  opt_out: false
  code_guidelines:
    enabled: true
    file_patterns:
      - "**/.cursorrules*"
      - "**/CLAUDE.md"
      - "**/knowledge-base/**/*.md"
      - "**/docs/standards/**/*.md"
```

### Referencing in Reviews

CodeRabbit will automatically reference knowledge base documents when:
- Code violates documented standards
- Security issues match OWASP guidelines
- Performance anti-patterns are detected
- Testing requirements are not met
- Documentation is missing or incomplete

Example review comment:
```
⚠️ Security Issue: Hardcoded API key detected

According to SECURITY_STANDARDS.md (A05: Security Misconfiguration):
All secrets must be stored in environment variables, never hardcoded.

Recommendation:
- Move API key to .env file
- Add to .env.example with placeholder
- Use process.env.API_KEY in code

Reference: knowledge-base/SECURITY_STANDARDS.md#secrets-management
```

## Usage Guidelines

### For Developers

**Before starting a new project:**
1. Read CLAUDE.md for architectural guidance
2. Review language-specific .cursorrules for your stack
3. Set up linters and formatters per standards

**During development:**
- Reference standards when making design decisions
- Use checklists from knowledge base before submitting PRs
- Consult SECURITY_STANDARDS.md for any security-related code

**During code reviews:**
- Reference specific sections of knowledge base
- Link to examples in .cursorrules files
- Suggest improvements based on documented best practices

### For Code Reviewers

**Review checklist:**
- [ ] Code follows language-specific standards (.cursorrules)
- [ ] Security checklist items verified (SECURITY_STANDARDS.md)
- [ ] Performance considerations addressed (PERFORMANCE_GUIDELINES.md)
- [ ] Architectural patterns followed (CLAUDE.md)
- [ ] Tests meet coverage requirements
- [ ] Documentation updated

**Providing feedback:**
- Always cite specific knowledge base sections
- Link to examples when suggesting changes
- Explain "why" by referencing documented principles
- Be constructive and educational

### For Team Leads

**Onboarding new team members:**
1. Assign knowledge base reading as part of onboarding
2. Create training sessions covering key documents
3. Pair new engineers with experienced developers for knowledge transfer

**Maintaining standards:**
- Quarterly review of knowledge base relevance
- Gather feedback from team on pain points
- Propose updates through RFC process
- Ensure CI/CD enforces documented standards

## Training and Resources

### Recommended Reading Order

**Week 1: Fundamentals**
1. CLAUDE.md - Architecture Overview (sections 1-4)
2. Language-specific .cursorrules for your primary stack
3. SECURITY_STANDARDS.md - OWASP Top 10 section

**Week 2: Deep Dive**
1. CLAUDE.md - API Design and Data Modeling (sections 5-6)
2. PERFORMANCE_GUIDELINES.md - Benchmarks and optimization
3. SECURITY_STANDARDS.md - Full security checklist

**Week 3: Advanced Topics**
1. CLAUDE.md - Testing, deployment, monitoring (sections 9-12)
2. PERFORMANCE_GUIDELINES.md - ML optimization, profiling
3. All language-specific standards relevant to your work

### Training Materials

**Available resources:**
- Video walkthroughs of each major document
- Interactive workshops on security and performance
- Code review training with knowledge base integration
- Quarterly "standards update" sessions

### Slack Channels

- `#engineering-standards`: Discuss knowledge base updates
- `#code-review`: Ask questions about standards
- `#security`: Security-specific questions
- `#performance`: Performance optimization discussions

## Feedback and Contributions

We welcome feedback and contributions from all engineers!

### How to Contribute

1. **Report issues**: Found an error or unclear guideline?
   - Open an issue in GitHub with label `documentation`
   - Include document name and section reference

2. **Suggest improvements**: Have a better way to explain something?
   - Create a proposal document
   - Discuss in `#engineering-standards` Slack channel
   - Submit PR with proposed changes

3. **Add examples**: Found a great code example?
   - Submit PR with addition to relevant .cursorrules file
   - Include context and explanation

4. **Request new sections**: Need guidance on a new topic?
   - Open discussion issue
   - Propose outline for new section
   - Volunteer to draft if able

### Recognition

Contributors to knowledge base improvements are recognized in:
- Monthly engineering newsletter
- Annual engineering awards
- Career development reviews

## Support

### Getting Help

**For questions about:**
- **Architectural decisions**: Ask in `#engineering-standards` or tag `@platform-team`
- **Security concerns**: Ask in `#security` or tag `@security-team`
- **Performance issues**: Ask in `#performance` or tag `@performance-team`
- **General standards**: Ask in `#code-review`

**For urgent clarifications:**
- DM the document maintainer (see document header)
- Ping `@platform-team` in Slack
- Schedule office hours with senior engineers

### Document Owners

| Document | Owner | Contact |
|----------|-------|---------|
| CLAUDE.md | Platform Team | platform@kellerai.com |
| SECURITY_STANDARDS.md | Security Team | security@kellerai.com |
| PERFORMANCE_GUIDELINES.md | Platform Team | platform@kellerai.com |
| .cursorrules-python | Backend Team Lead | backend-lead@kellerai.com |
| .cursorrules-typescript | Backend Team Lead | backend-lead@kellerai.com |
| .cursorrules-react | Frontend Team Lead | frontend-lead@kellerai.com |
| .cursorrules-nodejs | Backend Team Lead | backend-lead@kellerai.com |

---

## Quick Reference Links

- [CLAUDE.md - Full Architectural Guidelines](./CLAUDE.md)
- [SECURITY_STANDARDS.md - Security Best Practices](./SECURITY_STANDARDS.md)
- [PERFORMANCE_GUIDELINES.md - Performance Optimization](./PERFORMANCE_GUIDELINES.md)
- [.cursorrules-python - Python Standards](./cursorrules/.cursorrules-python)
- [.cursorrules-typescript - TypeScript Standards](./cursorrules/.cursorrules-typescript)
- [.cursorrules-react - React Standards](./cursorrules/.cursorrules-react)
- [.cursorrules-nodejs - Node.js Standards](./cursorrules/.cursorrules-nodejs)

---

**Last Updated**: 2025-10-14
**Next Review**: 2026-01-14
**Questions?** Contact platform@kellerai.com or ask in `#engineering-standards`
