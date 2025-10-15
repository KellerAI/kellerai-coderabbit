# Key Technologies and Patterns

## CodeRabbit Platform

### Core Capabilities
- **AI-Powered Analysis:** Context-aware code review using LLMs
- **Multi-Surface Integration:** PR reviews, IDE extension, CLI
- **Adaptive Learning:** Learns from team patterns and preferences
- **Security Scanning:** Built-in vulnerability detection
- **Performance Analysis:** Identifies efficiency issues

### Pricing Tiers
- **Free:** Open source repos, basic analysis, limited daily usage
- **Pro:** Unlimited private repos, learnings, context-aware, MCP integration, pre-merge checks
- **Enterprise:** Self-hosted, SSO/SAML, custom SLA, advanced analytics

**Recommendation:** Pro tier for KellerAI ($20-50/user/month estimated)

## Model Context Protocol (MCP)

### What is MCP?
Standardized protocol for connecting AI systems to external data sources. CodeRabbit acts as MCP client, consuming data from MCP servers.

### Architecture
```
MCP Servers (Data Sources) → MCP Protocol → CodeRabbit (Client) → Enhanced Reviews
```

### Available MCP Servers

**1. Context7**
- **Purpose:** Library documentation
- **Provider:** Pre-built, no setup needed
- **Content:** React, FastAPI, pytest, pandas, etc.
- **Usage:** Validate library API usage, check for deprecated methods

**2. Confluence**
- **Purpose:** Internal documentation
- **Provider:** `@modelcontextprotocol/server-confluence`
- **Content:** ADRs, technical specs, API docs, security guidelines
- **Setup:** Requires API token and space configuration

**3. Notion**
- **Purpose:** Product requirements and design docs
- **Provider:** `@modelcontextprotocol/server-notion`
- **Content:** PRDs, feature specs, design docs, meeting notes
- **Setup:** Requires integration token and page sharing

**4. Custom KellerAI MCP**
- **Purpose:** Organizational standards
- **Implementation:** Python MCP server
- **Content:** `standards.yaml`, ADRs, team preferences, pattern approvals
- **Tools:** 
  - `get_coding_standards`
  - `search_adr`
  - `get_team_preferences`
  - `check_pattern_approval`

## Claude Code Integration

### What is Claude Code?
AI coding assistant with CLI integration for autonomous development workflows.

### Key Features for CodeRabbit Integration
- **CLI Access:** Can run terminal commands including CodeRabbit CLI
- **Background Execution:** Non-blocking command execution
- **Prompt Processing:** Understands AI-optimized output (`--prompt-only`)
- **Autonomous Workflows:** Implement-review-fix cycles without human intervention

### Integration Pattern
```
Developer Prompt → Claude Code
                 ↓
              Implement Feature
                 ↓
      Run: coderabbit --prompt-only &
                 ↓
         Parse Review Results
                 ↓
           Create Fix Plan
                 ↓
           Apply Fixes
                 ↓
          Clean Code Ready
```

### Prompt Template Pattern
```
Implement [feature] from [ISSUE-ID].

After implementation:
1. Run `coderabbit --prompt-only` in background
2. Let it run as long as needed (do NOT timeout)
3. Review all findings
4. Fix critical and high-severity issues
5. Document any warnings that are intentional

Focus areas: [security/performance/testing]
```

## CodeRabbit CLI

### Installation
```bash
curl -fsSL https://cli.coderabbit.ai/install.sh | sh
```

### Authentication
```bash
coderabbit auth login  # One-time setup
coderabbit auth status  # Verify
```

### Core Commands
```bash
# Review types
coderabbit --type all          # Committed + uncommitted
coderabbit --type uncommitted  # Only working directory
coderabbit --type committed    # Only committed changes

# Output modes
coderabbit                     # Interactive (default)
coderabbit --plain             # Detailed text
coderabbit --prompt-only       # AI-optimized

# Comparison
coderabbit --base main         # Compare against branch
coderabbit --base-commit abc123  # Compare against commit
```

### Output Modes

**Interactive Mode (Default)**
- Browsable terminal UI
- Expandable findings
- Apply fixes individually
- Use: Manual development

**Plain Text Mode**
- Detailed text output
- All findings listed
- File paths and line numbers
- Use: Logging, CI/CD

**Prompt-Only Mode (AI-Optimized)**
- Token-efficient
- Natural language descriptions
- Structured for AI parsing
- Use: Claude Code integration

### Performance Characteristics
- Uncommitted review: 2-5 minutes
- Feature branch: 5-15 minutes
- Large PR: 15-30+ minutes

**Optimization:** Review incrementally during development for faster feedback

## Pre-merge Checks

### Built-in Checks

**1. Docstring Coverage**
```yaml
docstrings:
  mode: "error"
  threshold: 85  # percentage
```
- Calculates: (Functions with docstrings / Total public functions) × 100
- Exemptions: Private functions, test files, legacy code

**2. PR Title Validation**
```yaml
title:
  mode: "warning"
  requirements: |
    1. Start with imperative verb
    2. Keep under 60 characters
    3. Include issue reference [ISSUE-123]
    4. Use sentence case
```

**3. PR Description Validation**
```yaml
description:
  mode: "error"
```
- Validates against PR template
- Ensures all required sections completed
- Checks for issue references and test plan

**4. Issue Assessment**
```yaml
issue_assessment:
  mode: "warning"
```
- Validates PR addresses linked issue
- Detects out-of-scope changes
- Checks requirement coverage

### Custom Checks

Written in natural language, unlimited quantity:

**Structure:**
```yaml
custom_checks:
  - name: "Check Name"
    mode: "error" | "warning" | "off"
    instructions: |
      PASS CONDITIONS:
      - [condition 1]
      
      FAIL CONDITIONS:
      - [condition 1]
      
      VERIFICATION STEPS:
      1. [step 1]
      
      EXEMPTIONS:
      - [when rule doesn't apply]
```

**Example Categories:**
- **Breaking Changes:** Documentation requirements
- **Security:** Credential scanning, SQL injection, sensitive data
- **Architecture:** Layered architecture compliance, DI patterns
- **Testing:** Coverage requirements, regression tests
- **Performance:** N+1 queries, algorithm complexity, memory usage

### Enforcement Modes

**Off:** Check disabled, not run

**Warning:** Display warnings, allow merge
- Use for: Style, best practices, informational feedback

**Error:** Block merge if fails (with request_changes_workflow enabled)
- Use for: Security, breaking changes, test coverage, critical requirements

### Request Changes Workflow
```yaml
reviews:
  request_changes_workflow: true
```
When enabled, error-mode failures trigger GitHub/GitLab "Request Changes" status, blocking merge.

**Override:** `@coderabbitai ignore pre-merge checks`

## Central Configuration

### Repository Pattern
```
kellerai/coderabbit/           # Central config repository
└── .coderabbit.yaml          # Organization baseline

kellerai/repo-a/              # Inherits from central
kellerai/repo-b/              # Inherits from central
kellerai/repo-c/              # Override with local config
    └── .coderabbit.yaml
```

### Configuration Hierarchy (Highest → Lowest)
1. Repository `.coderabbit.yaml` (complete override)
2. Central `coderabbit/.coderabbit.yaml`
3. Repository UI settings
4. Organization UI settings
5. CodeRabbit defaults

### Platform Support
- **GitHub:** `organization/coderabbit`
- **GitLab:** `group/coderabbit` (supports nested groups)
- **Azure DevOps:** `project/coderabbit` (project-level only)
- **Bitbucket Cloud:** `workspace/coderabbit`
- **Bitbucket Server:** Not supported

## TaskMaster AI Integration

### What is TaskMaster?
Project management CLI that parses PRDs into dependency-aware tasks.

### Key Features
- **PRD Parsing:** Convert requirements into executable tasks
- **Dependency Management:** Track task dependencies
- **Task Expansion:** Break complex tasks into subtasks
- **AI Research:** Use Perplexity for enhanced task generation

### Commands
```bash
task-master init                          # Initialize project
task-master parse-prd .taskmaster/docs/prd.txt  # Generate tasks
task-master list                          # Show all tasks
task-master next                          # Get next task
task-master show <id>                     # View task details
task-master set-status --id=<id> --status=done  # Mark complete
```

### RPG Method (Repository Planning Graph)
Structured PRD format that separates:
- **Functional Decomposition:** What the system does (capabilities, features)
- **Structural Decomposition:** How it's organized (modules, files)
- **Dependency Graph:** Explicit dependencies for topological execution
- **Implementation Roadmap:** Phased development plan

### Integration with Claude Code
```markdown
# In CLAUDE.md:
When implementing features:
1. Get task from: task-master next
2. Review requirements: task-master show <id>
3. Implement feature
4. Run coderabbit --prompt-only for review
5. Fix issues found
6. Mark complete: task-master set-status --id=<id> --status=done
```

## Knowledge Base & Learning

### Auto-detected Files
CodeRabbit automatically scans for:
- `.cursorrules` - Cursor AI editor rules
- `CLAUDE.md` - Claude Code configuration (Pro feature)
- `.github/copilot-instructions.md` - GitHub Copilot rules
- `agent.md` - AI agent instructions
- `.rules/` - Generic team rules

### Adaptive Learning System

**Repository-wide Preferences:**
```
@coderabbitai always remember to enforce type hints for all parameters
@coderabbitai we prefer async/await over callbacks
@coderabbitai database migrations must include up and down scripts
```

**Line-specific Context:**
```python
# In PR comment:
@coderabbitai this timeout value is intentionally high for batch ETL
@coderabbitai do not complain about error handling here, it's at middleware level
```

**Learning Scopes:**
- **Local:** Repository-specific learnings
- **Global:** Organization-wide learnings (for private repos)
- **Auto:** Local for public, global for private

## Best Practices

### Incremental Reviews
- Review during development, not just at PR time
- Use `--type uncommitted` for quick checks
- Fix issues immediately while context is fresh

### Background Execution
- Always run CLI reviews in background for Claude Code
- Explicit instruction: "Let it run as long as needed, do NOT timeout"
- Check progress periodically

### Effective Custom Checks
- Be specific and actionable
- Provide clear pass/fail criteria
- Include examples (both passing and failing)
- Define exemptions explicitly
- Use structured format (PASS/FAIL/VERIFICATION/EXEMPTIONS)

### Team Adoption
- Start with warning mode to gather feedback
- Refine checks based on false positives
- Switch to error mode when team is ready
- Regular review cadence (monthly)
- Document override reasons to improve checks
