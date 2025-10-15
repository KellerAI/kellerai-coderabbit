# Architecture and Integration Strategy

## Integration Architecture

### Three-Surface Strategy
CodeRabbit provides three integration surfaces working together:

1. **Pull Request Reviews** (Primary Surface)
   - Automatic reviews on PR creation/update
   - Contextual feedback with line-level comments
   - Issue tracking integration (Jira/Linear)
   - Knowledge base learning from team patterns

2. **IDE Integration** (Real-time Surface)
   - VSCode extension for local analysis
   - File-level reviews before commit
   - Real-time feedback during development
   - Integrated with editor workflow

3. **CLI Reviews** (Autonomous Surface)
   - Terminal-based reviews for automation
   - Integration with AI coding agents (Claude Code)
   - Background execution support
   - AI-optimized output (`--prompt-only` mode)

### Integration Layers

**Layer 1: Code Review Engine**
- Core AI analysis and feedback generation
- Pattern detection and security scanning
- Performance and architecture validation

**Layer 2: Context Enrichment**
- MCP server integration for external context
- Issue tracking for requirement validation
- Knowledge base for team learnings
- Code guidelines (`.cursorrules`, `CLAUDE.md`)

**Layer 3: Quality Gates**
- Pre-merge checks (built-in and custom)
- Request changes workflow for blocking
- Enforcement modes (warning vs error)

**Layer 4: AI Workflow Automation**
- Claude Code autonomous workflows
- Implement-review-fix cycles
- Background execution patterns

## MCP Server Architecture

```
CodeRabbit (MCP Client)
├── Context7 MCP → Library documentation
├── Confluence MCP → Internal documentation
├── Notion MCP → Product requirements
└── Custom KellerAI MCP → Standards and ADRs
```

### Context7 MCP
- **Purpose:** Up-to-date library documentation
- **Libraries:** React, FastAPI, pytest, pandas, requests
- **Usage:** Validate library usage, check for deprecated methods
- **Tools:** `resolve-library-id`, `get-library-docs`

### Documentation MCPs
- **Confluence:** Engineering docs, ADRs, API specs, security guidelines
- **Notion:** PRDs, design docs, team standards, meeting notes
- **Usage:** Pull business and architectural context

### Custom KellerAI MCP
- **Purpose:** Serve organizational standards
- **Content:** `standards.yaml`, ADRs, team preferences, pattern approvals
- **Tools:** 
  - `get_coding_standards`: Retrieve by category
  - `search_adr`: Find architectural decisions
  - `get_team_preferences`: Code review preferences
  - `check_pattern_approval`: Verify pattern usage

## Quality Gate Strategy

### Built-in Checks
1. **Docstrings:** 85% minimum coverage, error mode
2. **PR Title:** Format validation, warning mode
3. **PR Description:** Template compliance, error mode
4. **Issue Assessment:** Scope validation, warning mode

### Custom Checks
1. **Breaking Changes Documentation:** Error mode
   - Detects API signature changes
   - Requires documentation in PR and CHANGELOG
   - Validates migration guides

2. **Security & Sensitive Data:** Error mode
   - Hardcoded credentials detection
   - SQL injection patterns
   - Sensitive data in logs
   - Missing authentication

3. **Architecture Compliance:** Warning mode
   - Layered architecture validation
   - Dependency flow checks
   - Async pattern enforcement
   - DI framework usage

4. **Test Coverage Requirements:** Error mode
   - New functions require tests
   - Bug fixes need regression tests
   - Critical paths 90%+ coverage

5. **Performance Impact Assessment:** Warning mode
   - N+1 query detection
   - Algorithm complexity analysis
   - Memory usage patterns
   - Missing indexes

## Enforcement Strategy

### Mode Hierarchy
- **Off:** Check disabled
- **Warning:** Display but don't block
- **Error:** Block merge if fails

### Request Changes Workflow
When enabled, error-mode check failures trigger GitHub/GitLab "Request Changes" status, blocking merge until:
- Issues are fixed, OR
- Developer overrides with `@coderabbitai ignore pre-merge checks`

### Phased Enforcement
1. **Week 1-2:** All checks in warning mode (gather data)
2. **Week 3-4:** Critical checks to error mode (security, breaking changes)
3. **Week 5+:** Full enforcement based on team readiness

## Claude Code Autonomous Workflows

### Implement-Review-Fix Cycle
```
Prompt → Claude Code → Implement → CodeRabbit CLI → Review → Fix → Clean Code
```

**Process:**
1. Developer gives feature request to Claude Code
2. Claude implements the feature
3. Claude runs `coderabbit --prompt-only` in background
4. Claude parses findings and creates fix plan
5. Claude applies fixes systematically
6. Code ready for PR with all issues addressed

### Key Patterns
- **Background Execution:** Use `coderabbit --prompt-only &` to avoid blocking
- **Prompt Template:** "Run coderabbit --prompt-only in the background. Let it run as long as needed (do NOT timeout). Parse results and fix all critical issues."
- **Output Mode:** `--prompt-only` provides AI-optimized natural language output
- **Review Scope:** `--type uncommitted` for quick checks, `--base main` for full branch review

## Central Configuration Strategy

### GitHub/GitLab Pattern
```
kellerai/coderabbit/ (central repo)
└── .coderabbit.yaml (organization-wide config)

kellerai/project-a/ → inherits from central
kellerai/project-b/ → inherits from central
kellerai/project-c/ 
└── .coderabbit.yaml → overrides central
```

### Configuration Hierarchy (Highest to Lowest)
1. Repository `.coderabbit.yaml` (complete override)
2. Central `coderabbit/.coderabbit.yaml` (organization baseline)
3. Repository UI settings
4. Organization UI settings
5. CodeRabbit schema defaults

### Central Config Benefits
- Centralized governance
- Consistent standards across organization
- Flexible repository-level overrides
- Version-controlled configuration changes
- Reduced maintenance overhead

## Technology Stack
- **CodeRabbit:** AI code review platform (Pro tier)
- **Claude Code:** AI coding assistant with CLI
- **MCP:** Model Context Protocol for context
- **Context7:** Library documentation MCP
- **TaskMaster AI:** Project management and PRD parsing
- **Git Platforms:** GitHub, GitLab (primary targets)
