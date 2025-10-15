# CodeRabbit Integration Documentation

This directory contains comprehensive documentation for KellerAI's CodeRabbit integration.

## Directory Structure

```
docs/
├── README.md (this file)
├── architecture/
│   ├── central-config.md
│   ├── integration-overview.md
│   └── mcp-servers.md
├── workflows/
│   ├── cli-integration.md
│   └── pr-review-process.md
├── quality-gates/
│   └── premerge-checks.md
├── guides/
│   ├── setup-guide.md
│   ├── team-onboarding.md
│   └── troubleshooting.md
└── research/
    ├── best-practices.md
    └── language-configs.md
```

## Documentation Index

### Architecture Documentation
- **Central Configuration** - Organization-wide CodeRabbit configuration strategy
- **Integration Overview** - Complete integration architecture for KellerAI
- **MCP Servers** - Model Context Protocol server setup and configuration

### Workflow Documentation
- **CLI Integration** - Claude Code + CodeRabbit CLI workflows
- **PR Review Process** - Pull request review workflows and patterns

### Quality Gates
- **Pre-merge Checks** - Quality gate specifications and enforcement

### Guides
- **Setup Guide** - Step-by-step installation and configuration
- **Team Onboarding** - Onboarding new team members
- **Troubleshooting** - Common issues and solutions

### Research
- **Best Practices** - Research findings and recommendations
- **Language Configs** - Language-specific configuration patterns

## Quick Links

- [Project Overview](../README.md)
- [TaskMaster Integration](../.taskmaster/CLAUDE.md)
- [Example PRD Template](../.taskmaster/templates/example_prd_rpg.txt)

## Getting Started

1. Read [Integration Overview](architecture/integration-overview.md)
2. Follow [Setup Guide](guides/setup-guide.md)
3. Review [CLI Integration](workflows/cli-integration.md)
4. Configure [Pre-merge Checks](quality-gates/premerge-checks.md)

## Contributing

When adding new documentation:
1. Place in appropriate subdirectory
2. Update this README index
3. Follow markdown standards
4. Include code examples where relevant
