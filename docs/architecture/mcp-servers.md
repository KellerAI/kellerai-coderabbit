# CodeRabbit MCP Server Configuration Guide

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Step-by-step guide for setting up MCP servers with CodeRabbit

---

## Table of Contents

1. [MCP Overview](#mcp-overview)
2. [Context7 MCP Setup](#context7-mcp-setup)
3. [Documentation MCP Servers](#documentation-mcp-servers)
4. [Custom KellerAI MCP Server](#custom-kellerai-mcp-server)
5. [Testing and Validation](#testing-and-validation)
6. [Troubleshooting](#troubleshooting)

---

## 1. MCP Overview

### What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol for connecting AI systems to external data sources. CodeRabbit acts as an MCP **client**, consuming data from MCP **servers** you configure.

### CodeRabbit as MCP Client

```
External Tools                  CodeRabbit                  Reviews
─────────────────              ────────────                ────────
                              
[Context7]  ──┐               ┌─────────────┐             ┌──────────┐
[Notion]    ──┼──MCP Proto──→ │ CodeRabbit  │──Enhanced──→│  Better  │
[Confluence]──┤               │ (MCP Client)│   Context   │ Reviews  │
[Custom]    ──┘               └─────────────┘             └──────────┘
```

### Benefits for Code Reviews

1. **Technical Context**: Library docs, API references, dependencies
2. **Business Context**: Requirements, user stories, acceptance criteria
3. **Organizational Context**: Decisions, conventions, institutional knowledge

---

## 2. Context7 MCP Setup

### Overview

Context7 provides up-to-date library documentation for code reviews. Essential for validating library usage, checking deprecated methods, and suggesting best practices.

### Prerequisites

- CodeRabbit Pro account
- Access to CodeRabbit dashboard
- Admin permissions

### Setup Steps

#### Step 1: Access MCP Integrations

1. Log into CodeRabbit dashboard: `https://app.coderabbit.ai`
2. Navigate to: **Settings → Integrations**
3. Click on **MCP Servers** tab
4. Click **Add MCP Integration** button

#### Step 2: Configure Context7

**Basic Configuration:**

```yaml
Name: Context7
Server Type: context7-mcp
Description: Library documentation for code reviews
```

**Server Connection:**
- Context7 is a pre-configured MCP server
- Select **Context7** from the available server list
- No authentication required (public documentation)

#### Step 3: Configure Usage Guidance

Add this usage guidance to help CodeRabbit use Context7 effectively:

```markdown
## Context7 Usage Guidance

Use Context7 to:
1. Validate library API usage against official documentation
2. Check for deprecated methods and suggest alternatives
3. Verify correct parameter types and return values
4. Recommend best practices from library documentation
5. Provide links to relevant documentation sections

When to call Context7:
- When reviewing code that imports external libraries
- When suggesting improvements to library usage
- When API calls look unusual or deprecated
- When better alternatives might exist in newer versions

Libraries to prioritize:
- Python: FastAPI, requests, pytest, pandas, numpy, django
- JavaScript: React, Express, axios, lodash
- General: Database drivers, HTTP clients, test frameworks
```

#### Step 4: Enable Specific Tools

Context7 provides these MCP tools:

| Tool | Purpose | Enable? |
|------|---------|---------|
| `resolve-library-id` | Find library documentation ID | ✅ Yes |
| `get-library-docs` | Fetch library documentation | ✅ Yes |

**To enable/disable tools:**
1. Click on the Context7 integration
2. View available tools list
3. Toggle checkboxes for each tool
4. Click **Save Changes**

#### Step 5: Test Context7 Integration

**Test Method 1: Create Test PR**

Create a PR with this test file:

```python
# test_context7.py
import requests

def fetch_user_data(user_id):
    # Using deprecated method
    response = requests.get(
        f"https://api.example.com/users/{user_id}",
        auth=("user", "pass")  # Basic auth (older pattern)
    )
    return response.json()
```

**Expected CodeRabbit Response:**
```
✅ Context7 detected deprecated authentication pattern.
   Official requests documentation recommends using HTTPBasicAuth 
   for better security and clarity.
   
   See: [requests.auth documentation]
```

**Test Method 2: Use Chat Command**

In any PR, comment:
```
@coderabbitai Check if our FastAPI usage follows best practices 
according to the official docs
```

CodeRabbit should reference Context7 documentation in its response.

### Library Configuration

#### Common Libraries for KellerAI

**Python Libraries:**
```yaml
libraries:
  - name: fastapi
    versions: [0.100+, latest]
  - name: requests
    versions: [latest]
  - name: pytest
    versions: [7.0+, latest]
  - name: pandas
    versions: [1.5+, latest]
  - name: sqlalchemy
    versions: [2.0+, latest]
  - name: pydantic
    versions: [2.0+, latest]
```

**JavaScript Libraries:**
```yaml
libraries:
  - name: react
    versions: [18.0+, latest]
  - name: express
    versions: [4.0+, latest]
  - name: axios
    versions: [latest]
```

#### Version-Specific Documentation

Context7 can provide version-specific docs:

```
# In CodeRabbit review context:
"Check FastAPI 0.95+ documentation for async database patterns"

# Context7 will fetch:
/fastapi/fastapi/v0.95 (or nearest version)
```

### Advanced Configuration

#### Topic Focusing

Configure Context7 to focus on specific topics:

```yaml
context7_config:
  default_topics:
    - "API endpoints"
    - "async patterns"
    - "error handling"
    - "best practices"
  
  topic_triggers:
    security: ["auth", "password", "token", "encryption"]
    performance: ["query", "cache", "async", "batch"]
    testing: ["test", "mock", "fixture", "pytest"]
```

#### Token Limits

Control Context7 documentation size:

```yaml
context7_config:
  max_tokens: 5000  # Default
  # Higher values = more context, more token usage
  # Lower values = less context, faster reviews
```

For detailed code reviews: `max_tokens: 10000`  
For quick reviews: `max_tokens: 2000`

---

## 3. Documentation MCP Servers

### Option A: Confluence MCP Server

#### Prerequisites

- Confluence Cloud or Data Center instance
- Admin access to create API tokens
- Node.js installed (for MCP server)

#### Installation

**1. Install Confluence MCP Server:**

```bash
# Global installation
npm install -g @modelcontextprotocol/server-confluence

# Or use npx (no installation)
npx @modelcontextprotocol/server-confluence
```

**2. Generate Confluence API Token:**

1. Go to: https://id.atlassian.com/manage/api-tokens
2. Click **Create API token**
3. Name: `CodeRabbit MCP Integration`
4. Copy token (save securely)

**3. Find Your Confluence Details:**

```
Base URL: https://your-company.atlassian.net/wiki
Username: your-email@company.com
API Token: [token from step 2]
Space Keys: [list of spaces to search, e.g., "ENG,TECH,ARCH"]
```

#### CodeRabbit Configuration

**In CodeRabbit Dashboard:**

1. Navigate to: **Settings → Integrations → MCP Servers**
2. Click: **Add MCP Integration**
3. Fill in:

```yaml
Name: Internal Documentation
Server Type: Custom MCP Server
Command: npx @modelcontextprotocol/server-confluence
```

**Environment Variables:**

```bash
CONFLUENCE_BASE_URL=https://your-company.atlassian.net/wiki
CONFLUENCE_USERNAME=your-email@company.com
CONFLUENCE_API_TOKEN=your-api-token-here
CONFLUENCE_SPACES=ENG,TECH,ARCH
```

**Usage Guidance:**

```markdown
## Confluence Documentation Usage

Use this MCP server to access internal documentation including:
- Architecture Decision Records (ADRs)
- Technical specifications
- API documentation
- Design documents
- Team standards and guidelines

Search strategy:
1. Check for ADRs when architectural questions arise
2. Reference API specs when reviewing endpoint changes
3. Validate against security guidelines for auth/data handling
4. Look up team conventions for style and pattern questions

Confluence spaces to prioritize:
- ENG: Engineering documentation
- TECH: Technical specifications
- ARCH: Architecture decisions
- SEC: Security policies
```

#### Available Tools

| Tool | Purpose | Enable? |
|------|---------|---------|
| `search_pages` | Search Confluence pages | ✅ Yes |
| `get_page` | Retrieve specific page content | ✅ Yes |
| `get_page_by_title` | Find page by exact title | ✅ Yes |
| `list_spaces` | List accessible spaces | ⚠️ Optional |

#### Testing Confluence Integration

**Test Search:**

Create a PR that changes authentication logic, then comment:

```
@coderabbitai Check if this authentication pattern follows 
our security guidelines in Confluence
```

**Expected Behavior:**
- CodeRabbit searches Confluence for "authentication security guidelines"
- Finds relevant page in SEC space
- References specific security policy in review
- Provides Confluence page link

**Test Specific Page:**

```
@coderabbitai Review this database migration against 
our "Database Change Policy" document
```

### Option B: Notion MCP Server

#### Prerequisites

- Notion workspace
- Admin access to create integrations
- Node.js installed

#### Installation

**1. Create Notion Integration:**

1. Go to: https://www.notion.so/my-integrations
2. Click: **New integration**
3. Name: `CodeRabbit MCP`
4. Select workspace
5. Set capabilities:
   - ✅ Read content
   - ✅ Read comments
   - ❌ Update content (not needed)
   - ❌ Insert content (not needed)
6. Click: **Submit**
7. Copy **Internal Integration Token**

**2. Share Pages with Integration:**

1. Open Notion page/database to share
2. Click **Share** in top-right
3. Search for **CodeRabbit MCP** integration
4. Click **Invite**
5. Repeat for all relevant pages

**3. Install Notion MCP Server:**

```bash
npm install -g @modelcontextprotocol/server-notion
```

#### CodeRabbit Configuration

```yaml
Name: Notion Documentation
Server Type: Custom MCP Server
Command: npx @modelcontextprotocol/server-notion

Environment Variables:
  NOTION_API_TOKEN: your-integration-token-here
  NOTION_DATABASE_IDS: comma-separated-database-ids (optional)
```

**Usage Guidance:**

```markdown
## Notion Documentation Usage

Access internal Notion documentation including:
- Product requirements (PRDs)
- Feature specifications
- Design documents
- Meeting notes with decisions
- Project wikis

Search approach:
1. Look up PRD when reviewing feature implementation
2. Reference design docs for UI/UX changes
3. Check meeting notes for context on decisions
4. Validate against project wiki standards

Prioritize these databases:
- Engineering Wiki
- Product Requirements
- Design System
- Architecture Decisions
```

#### Available Tools

| Tool | Purpose | Enable? |
|------|---------|---------|
| `search_pages` | Search all accessible pages | ✅ Yes |
| `get_page` | Get specific page content | ✅ Yes |
| `query_database` | Query Notion database | ✅ Yes |
| `get_block_children` | Get nested content | ⚠️ Optional |

---

## 4. Custom KellerAI MCP Server

### Purpose

Create a custom MCP server to serve KellerAI-specific standards, conventions, and knowledge to CodeRabbit reviews.

### Architecture

```
KellerAI Repository                Custom MCP Server            CodeRabbit
──────────────────                ───────────────────          ──────────

/docs/standards.yaml  ─┐
/docs/architecture/   ─┤           ┌─────────────┐            ┌──────────┐
/.cursorrules         ─┼──Read by─→│   KellerAI  │─MCP Proto─→│CodeRabbit│
/CLAUDE.md            ─┤           │ MCP Server  │            │ Reviews  │
/docs/adr/            ─┘           └─────────────┘            └──────────┘
```

### Implementation

**File: `kellerai_mcp_server.py`**

```python
#!/usr/bin/env python3
"""
KellerAI Custom MCP Server for CodeRabbit Integration
Serves organizational standards, ADRs, and team preferences
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional
from mcp.server import MCPServer
from mcp.types import Tool, TextContent

# Initialize MCP server
server = MCPServer("kellerai-standards")

# Configuration
REPO_ROOT = Path(os.environ.get('KELLERAI_REPO_ROOT', '~/kellerai')).expanduser()
STANDARDS_FILE = REPO_ROOT / 'docs' / 'standards.yaml'
ADR_DIR = REPO_ROOT / 'docs' / 'architecture' / 'decisions'
CLAUDE_MD = REPO_ROOT / 'CLAUDE.md'


@server.list_tools()
def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="get_coding_standards",
            description="Retrieve KellerAI coding standards by category",
            input_schema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "enum": ["architecture", "security", "performance", 
                                "testing", "documentation", "all"],
                        "description": "Category of standards to retrieve"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="search_adr",
            description="Search Architecture Decision Records",
            input_schema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search term (e.g., 'database', 'authentication')"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_team_preferences",
            description="Get team code review preferences and conventions",
            input_schema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="check_pattern_approval",
            description="Check if a code pattern is approved or prohibited",
            input_schema={
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "Code pattern to check (e.g., 'singleton', 'global state')"
                    }
                },
                "required": ["pattern"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict) -> List[TextContent]:
    """Handle MCP tool calls"""
    
    if name == "get_coding_standards":
        category = arguments.get("category", "all")
        return [TextContent(
            type="text",
            text=get_coding_standards(category)
        )]
    
    elif name == "search_adr":
        query = arguments["query"]
        return [TextContent(
            type="text",
            text=search_architecture_decisions(query)
        )]
    
    elif name == "get_team_preferences":
        return [TextContent(
            type="text",
            text=get_team_preferences()
        )]
    
    elif name == "check_pattern_approval":
        pattern = arguments["pattern"]
        return [TextContent(
            type="text",
            text=check_pattern_approval(pattern)
        )]
    
    else:
        return [TextContent(
            type="text",
            text=f"Unknown tool: {name}"
        )]


def get_coding_standards(category: str = "all") -> str:
    """Retrieve coding standards from YAML file"""
    try:
        with open(STANDARDS_FILE) as f:
            standards = yaml.safe_load(f)
        
        if category == "all":
            return yaml.dump(standards, default_flow_style=False)
        else:
            return yaml.dump(
                standards.get(category, {}),
                default_flow_style=False
            )
    except FileNotFoundError:
        return f"Standards file not found: {STANDARDS_FILE}"
    except Exception as e:
        return f"Error loading standards: {str(e)}"


def search_architecture_decisions(query: str) -> str:
    """Search ADRs for relevant decisions"""
    try:
        results = []
        query_lower = query.lower()
        
        for adr_file in ADR_DIR.glob("*.md"):
            content = adr_file.read_text()
            
            # Check if query matches filename or content
            if (query_lower in adr_file.name.lower() or 
                query_lower in content.lower()):
                
                results.append(f"""
## {adr_file.name}

{content}

---
""")
        
        if results:
            return "\n".join(results)
        else:
            return f"No ADRs found matching '{query}'"
    
    except FileNotFoundError:
        return f"ADR directory not found: {ADR_DIR}"
    except Exception as e:
        return f"Error searching ADRs: {str(e)}"


def get_team_preferences() -> str:
    """Get team preferences from various sources"""
    preferences = {
        "naming_conventions": {
            "functions": "snake_case",
            "classes": "PascalCase",
            "constants": "UPPER_SNAKE_CASE",
            "private_members": "_leading_underscore",
            "protected_members": "_single_underscore"
        },
        "code_organization": {
            "max_function_lines": 50,
            "max_file_lines": 500,
            "imports_order": ["stdlib", "third_party", "local"],
            "directory_structure": "layered architecture (api/services/repositories)"
        },
        "documentation": {
            "docstring_style": "Google",
            "type_hints": "required for public APIs",
            "inline_comments": "explain why, not what",
            "minimum_coverage": "80%"
        },
        "testing": {
            "framework": "pytest",
            "naming_convention": "test_<function>_<scenario>",
            "coverage_threshold": 80,
            "required_for": ["new_features", "bug_fixes", "refactors"]
        },
        "async_patterns": {
            "io_operations": "always async",
            "database_calls": "use async drivers",
            "http_requests": "prefer httpx over requests",
            "cpu_bound": "use ProcessPoolExecutor"
        },
        "error_handling": {
            "exceptions": "custom exceptions for business errors",
            "global_handler": "at API boundary",
            "logging": "structured logging (JSON)",
            "bare_except": "prohibited"
        }
    }
    
    # Try to load from CLAUDE.md
    try:
        if CLAUDE_MD.exists():
            claude_content = CLAUDE_MD.read_text()
            preferences["claude_md_standards"] = "See CLAUDE.md for detailed standards"
    except Exception:
        pass
    
    return yaml.dump(preferences, default_flow_style=False)


def check_pattern_approval(pattern: str) -> str:
    """Check if a pattern is approved, discouraged, or prohibited"""
    patterns = {
        "approved": [
            "dependency injection",
            "async/await",
            "type hints",
            "dataclasses",
            "context managers",
            "generators",
            "list comprehensions",
            "f-strings"
        ],
        "discouraged": [
            "global state",
            "synchronous I/O in async context",
            "bare except",
            "mutable default arguments",
            "string concatenation in loops"
        ],
        "prohibited": [
            "eval",
            "exec",
            "hardcoded credentials",
            "SQL injection patterns",
            "pickle for untrusted data"
        ]
    }
    
    pattern_lower = pattern.lower()
    
    for category, pattern_list in patterns.items():
        if any(p in pattern_lower for p in pattern_list):
            if category == "approved":
                return f"✅ Pattern '{pattern}' is APPROVED for use at KellerAI"
            elif category == "discouraged":
                return f"⚠️  Pattern '{pattern}' is DISCOURAGED at KellerAI. Consider alternatives."
            elif category == "prohibited":
                return f"🚫 Pattern '{pattern}' is PROHIBITED at KellerAI for security/safety reasons."
    
    return f"ℹ️  Pattern '{pattern}' not explicitly listed. Use best judgment and seek code review."


if __name__ == "__main__":
    # Run MCP server
    server.run()
```

### Standards File Structure

**File: `docs/standards.yaml`**

```yaml
architecture:
  pattern: "Layered Architecture"
  layers:
    - controller: "API endpoints and request handling"
    - service: "Business logic and orchestration"
    - repository: "Data access and persistence"
    - model: "Domain entities and value objects"
  
  dependencies:
    rule: "Dependencies flow inward"
    allowed: "Controller → Service → Repository → Model"
    prohibited: "Repository → Controller"
  
  async_required: true
  di_framework: "FastAPI Depends"

security:
  authentication:
    method: "JWT tokens"
    algorithm: "HS256"
    expiry: "24 hours"
    refresh_tokens: true
  
  authorization:
    method: "Role-based (RBAC)"
    decorator: "@require_auth"
    admin_check: "@require_role('admin')"
  
  sensitive_data:
    passwords: "bcrypt hashing"
    api_keys: "environment variables only"
    secrets: "AWS Secrets Manager"
    logging: "never log passwords, tokens, or PII"
  
  sql_injection:
    method: "Parameterized queries only"
    orm: "SQLAlchemy with ORM patterns"
    prohibited: "String concatenation in queries"

performance:
  database:
    connections: "Connection pooling (10-20 pool size)"
    queries: "Eager loading to avoid N+1"
    indexes: "Required for all foreign keys and frequent queries"
    caching: "Redis for hot data"
  
  api:
    pagination: "Required for list endpoints"
    rate_limiting: "100 requests/minute per user"
    timeout: "30 seconds maximum"
  
  algorithms:
    complexity: "O(n log n) or better for hot paths"
    avoid: "Nested loops on large datasets"

testing:
  framework: "pytest"
  structure:
    unit: "tests/unit/"
    integration: "tests/integration/"
    e2e: "tests/e2e/"
  
  naming: "test_<function_name>_<scenario>"
  coverage:
    minimum: 80
    critical_paths: 90
  
  fixtures: "conftest.py in each test directory"
  mocking: "pytest-mock for external services"

documentation:
  docstrings:
    required_for:
      - public_functions
      - classes
      - modules
    style: "Google format"
    content:
      - summary: "One-line description"
      - args: "Parameter descriptions with types"
      - returns: "Return value description with type"
      - raises: "Exception types and conditions"
      - examples: "Usage examples for complex functions"
  
  type_hints:
    required: true
    style: "Python 3.10+ syntax"
    generics: "Use typing.Generic for generic classes"
  
  inline_comments:
    when: "Explain why, not what"
    avoid: "Obvious comments"
    prefer: "Self-documenting code"
```

### Deployment

**1. Install Dependencies:**

```bash
pip install mcp pyyaml
```

**2. Set Environment Variable:**

```bash
export KELLERAI_REPO_ROOT=/Users/username/kellerai
```

**3. Test Locally:**

```bash
python kellerai_mcp_server.py
```

**4. Configure in CodeRabbit:**

```yaml
Name: KellerAI Standards
Server Type: Custom MCP Server
Command: python /path/to/kellerai_mcp_server.py
Environment Variables:
  KELLERAI_REPO_ROOT: /Users/username/kellerai

Usage Guidance: |
  Use this MCP server to validate code against KellerAI organizational 
  standards, check architecture decisions, and enforce team conventions.
  
  Available tools:
  - get_coding_standards: Retrieve standards by category
  - search_adr: Search Architecture Decision Records
  - get_team_preferences: Get code review preferences
  - check_pattern_approval: Verify if pattern is approved/prohibited
  
  Call these tools when:
  - Reviewing architectural changes
  - Validating security patterns
  - Checking performance considerations
  - Enforcing testing requirements
  - Verifying documentation standards
```

---

## 5. Testing and Validation

### Test Checklist

#### Context7 Testing

- [ ] Library documentation retrieval works
- [ ] Deprecated method detection
- [ ] Alternative suggestions provided
- [ ] Documentation links included

**Test PR:**
```python
# Use deprecated API
import requests
requests.get(url, verify=False)  # Should flag SSL verification disabled
```

#### Documentation MCP Testing

- [ ] Can search Confluence/Notion
- [ ] Retrieves relevant pages
- [ ] References in review comments
- [ ] Page links work

**Test PR:**
```python
# Make architectural change
# Should reference ADR from Confluence
```

#### Custom MCP Testing

- [ ] Standards retrieval works
- [ ] ADR search functional
- [ ] Team preferences loaded
- [ ] Pattern approval checking

**Test Commands:**
```bash
# Test each tool directly
curl -X POST http://localhost:3000/mcp \
  -d '{"tool": "get_coding_standards", "args": {"category": "security"}}'
```

### Validation Criteria

**Successful Integration:**
1. ✅ MCP server shows as "Connected" in dashboard
2. ✅ Tools list populated
3. ✅ Test searches return results
4. ✅ CodeRabbit references MCP data in reviews
5. ✅ Performance acceptable (< 2s per MCP call)

**Review Quality Indicators:**
1. ✅ Context mentions "Referenced [Source]"
2. ✅ Links to external documentation
3. ✅ Specific standard/policy citations
4. ✅ Actionable recommendations

---

## 6. Troubleshooting

### Common Issues

#### Issue: MCP Server Shows "Disconnected"

**Possible Causes:**
- Server not running
- Incorrect command/path
- Authentication failure
- Network issues

**Solutions:**
```bash
# Test server manually
python your_mcp_server.py

# Check logs
tail -f ~/.coderabbit/mcp-logs/your-server.log

# Verify credentials
echo $CONFLUENCE_API_TOKEN  # Should not be empty
```

#### Issue: No Results from MCP Searches

**Possible Causes:**
- Incorrect search scope
- Permission issues
- Empty databases

**Solutions:**
1. Check server has access to documents
2. Verify search permissions
3. Test with known document titles

#### Issue: Slow Review Times

**Possible Causes:**
- Too many MCP calls
- Large document retrieval
- Network latency

**Solutions:**
```yaml
# Reduce MCP call frequency
mcp_config:
  max_calls_per_review: 3
  timeout: 5000  # 5 seconds
  
# Cache frequently accessed documents
cache_ttl: 3600  # 1 hour
```

#### Issue: Authentication Errors

**Confluence:**
```bash
# Test API token
curl -u your-email@company.com:your-api-token \
  https://your-company.atlassian.net/wiki/rest/api/space
```

**Notion:**
```bash
# Test integration token
curl https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer your-integration-token" \
  -H "Notion-Version: 2022-06-28"
```

### Getting Help

1. **CodeRabbit Support**
   - Email: support@coderabbit.ai
   - Discord: https://discord.gg/coderabbit
   - Docs: https://docs.coderabbit.ai

2. **MCP Community**
   - GitHub: https://github.com/modelcontextprotocol
   - Issues: Report server-specific issues

3. **Internal**
   - Tech lead review
   - Team Slack channel
   - Documentation updates

---

## Summary

This guide covered:
1. ✅ Context7 MCP setup for library documentation
2. ✅ Confluence/Notion MCP configuration
3. ✅ Custom KellerAI MCP server creation
4. ✅ Testing and validation procedures
5. ✅ Troubleshooting common issues

**Next Steps:**
1. Set up Context7 (easiest, highest value)
2. Configure documentation MCP (Confluence or Notion)
3. Build custom KellerAI server (longer-term)
4. Test with real PRs
5. Iterate based on team feedback

**Success Metrics:**
- 60%+ reviews reference external context
- MCP calls complete in < 2 seconds
- Team satisfaction 4.5/5 with context quality
- Documentation links in 80%+ of reviews

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Integration & Tooling Research Agent
