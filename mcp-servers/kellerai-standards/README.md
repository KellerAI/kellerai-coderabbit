# KellerAI Custom MCP Server

## Overview

Custom Model Context Protocol (MCP) server that provides KellerAI-specific organizational standards, architecture decisions, and team preferences to CodeRabbit for enhanced code reviews.

## Features

- **Coding Standards**: Retrieve organizational coding standards by category
- **ADR Search**: Search Architecture Decision Records by keyword
- **Team Preferences**: Get language-specific code review preferences
- **Pattern Validation**: Check if code patterns are approved/discouraged/prohibited
- **API Design Validation**: Validate REST API endpoint design against standards

## Installation

### Prerequisites

- Python 3.9 or higher
- pip package manager
- MCP SDK: `pip install mcp`
- PyYAML: `pip install pyyaml`

### Install Dependencies

```bash
cd mcp-servers/kellerai-standards
pip install -r requirements.txt
```

### Set Environment Variable

```bash
# Set repository root (defaults to current directory)
export KELLERAI_REPO_ROOT=/path/to/kellerai/repository
```

## Configuration

### Add to `.mcp.json`

```json
{
  "mcpServers": {
    "kellerai-standards": {
      "type": "stdio",
      "command": "python",
      "args": ["/path/to/mcp-servers/kellerai-standards/src/server.py"],
      "env": {
        "KELLERAI_REPO_ROOT": "/path/to/kellerai/repository"
      }
    }
  }
}
```

### Add to `.claude/settings.json`

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "kellerai-standards",
    "context7",
    "confluence",
    "notion"
  ]
}
```

## Directory Structure

```
kellerai-repository/
├── docs/
│   ├── standards/
│   │   ├── coding-standards.yaml       # Organizational coding standards
│   │   ├── approved-patterns.yaml      # Pattern approval status
│   │   └── team-preferences.yaml       # Team code review preferences
│   └── architecture/
│       └── decisions/                  # Architecture Decision Records (ADRs)
│           ├── ADR-001-database-selection.md
│           ├── ADR-002-authentication-strategy.md
│           └── ADR-003-api-design.md
```

## MCP Tools

### 1. `get_coding_standards`

Retrieve KellerAI coding standards by category.

**Input:**
```json
{
  "category": "security"  // "architecture", "performance", "testing", "documentation", or "all"
}
```

**Output:**
YAML-formatted standards for the specified category.

**Example Usage:**
```
Get security coding standards from KellerAI
```

### 2. `search_adr`

Search Architecture Decision Records.

**Input:**
```json
{
  "query": "database migration",
  "status": "accepted",  // "proposed", "deprecated", "superseded", or "all"
  "limit": 5
}
```

**Output:**
Matching ADRs with metadata and content excerpts.

**Example Usage:**
```
Search KellerAI ADRs for "authentication strategy"
```

### 3. `get_team_preferences`

Get team code review preferences.

**Input:**
```json
{
  "language": "python"  // "javascript", "typescript", or "all"
}
```

**Output:**
YAML-formatted team preferences for the specified language.

**Example Usage:**
```
Get Python coding preferences for KellerAI
```

### 4. `check_pattern_approval`

Check if a code pattern is approved.

**Input:**
```json
{
  "pattern": "singleton",
  "context": "database connections"  // Optional
}
```

**Output:**
Approval status with guidance and recommendations.

**Example Usage:**
```
Check if the singleton pattern is approved at KellerAI
```

### 5. `validate_api_design`

Validate REST API endpoint design.

**Input:**
```json
{
  "endpoint": "/api/v1/users/{id}",
  "method": "GET",
  "description": "Retrieve user by ID"
}
```

**Output:**
Validation results with issues and recommendations.

**Example Usage:**
```
Validate this API endpoint: POST /users/create
```

## Sample Standards Files

### coding-standards.yaml

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

security:
  authentication:
    method: "JWT tokens"
    algorithm: "HS256"
    expiry: "24 hours"
  
  sensitive_data:
    passwords: "bcrypt hashing"
    api_keys: "environment variables only"
    secrets: "AWS Secrets Manager"

performance:
  database:
    connections: "Connection pooling (10-20 pool size)"
    queries: "Eager loading to avoid N+1"
    indexes: "Required for all foreign keys"
  
  api:
    pagination: "Required for list endpoints"
    rate_limiting: "100 requests/minute per user"

testing:
  framework: "pytest"
  coverage:
    minimum: 80
    critical_paths: 90
  naming: "test_<function>_<scenario>"
```

### approved-patterns.yaml

```yaml
approved:
  - name: "dependency injection"
    description: "Inject dependencies via constructor or function parameters"
  
  - name: "async/await"
    description: "Use async/await for I/O operations"
  
  - name: "type hints"
    description: "Required for all public APIs and functions"

discouraged:
  - name: "global state"
    description: "Avoid mutable global variables; use dependency injection"
  
  - name: "synchronous I/O in async context"
    description: "Use async I/O operations in async functions"

prohibited:
  - name: "eval"
    description: "Security risk - never use eval() on untrusted input"
  
  - name: "hardcoded credentials"
    description: "Always use environment variables or secrets manager"
  
  - name: "SQL injection patterns"
    description: "Use parameterized queries; never string concatenation"
```

### team-preferences.yaml

```yaml
python:
  naming:
    functions: "snake_case"
    classes: "PascalCase"
    constants: "UPPER_SNAKE_CASE"
    private: "_leading_underscore"
  
  async: "Required for all I/O operations"
  type_hints: "Required for public APIs"
  docstrings: "Google style, required for all public functions"
  
  testing:
    framework: "pytest"
    coverage: "80% minimum"
    naming: "test_<function>_<scenario>"

javascript:
  naming:
    functions: "camelCase"
    classes: "PascalCase"
    constants: "UPPER_SNAKE_CASE"
  
  async: "Use async/await, avoid callbacks"
  modules: "ES6 modules (import/export)"
  formatting: "Prettier with 2-space indents"
```

## Sample ADR Template

```markdown
# ADR-{number}: {Title}

**Status:** Accepted
**Date:** 2025-10-14
**Deciders:** @tech-lead, @architecture-team

## Context

What is the issue we're facing? What factors are driving this decision?

## Decision

What decision have we made? What are we going to do?

## Consequences

### Positive
- Benefit 1
- Benefit 2

### Negative
- Trade-off 1
- Trade-off 2

## Alternatives Considered

### Option A
**Pros:** ...
**Cons:** ...
**Decision:** Not selected because...

## References
- Link to research
- Link to related docs
```

## Usage in CodeRabbit

When CodeRabbit reviews code, it will reference KellerAI standards:

### Example 1: Architectural Pattern Validation

**Code:**
```python
# Controller directly accessing database
@app.get("/users")
def get_users():
    conn = db.connect()
    users = conn.execute("SELECT * FROM users")
    return {"users": users}
```

**CodeRabbit with KellerAI Standards:**
```
❌ Architecture Violation

KellerAI standards require layered architecture:
Controller → Service → Repository → Model

This controller directly accesses the database, violating the
dependency flow rule. 

Recommended structure:
```python
@app.get("/users")
async def get_users(user_service: UserService = Depends()):
    users = await user_service.get_all_users()
    return {"users": users}
```

📚 Reference: KellerAI Coding Standards > Architecture > Layered Architecture
```

### Example 2: Security Pattern Check

**Code:**
```python
import hashlib

def hash_password(password: str) -> str:
    return hashlib.md5(password.encode()).hexdigest()
```

**CodeRabbit with KellerAI Standards:**
```
🚫 Prohibited Pattern Detected

KellerAI security standards PROHIBIT MD5 for password hashing.

Required pattern: bcrypt hashing

Correct implementation:
```python
import bcrypt

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

📚 Reference: KellerAI Coding Standards > Security > Passwords
```

### Example 3: ADR Compliance

**Code:**
```python
# Using MongoDB for new feature
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client.myapp
```

**CodeRabbit with KellerAI Standards:**
```
⚠️ Conflicts with Architecture Decision

ADR-001: Database Selection decided on PostgreSQL for ACID compliance.

Using MongoDB for this feature conflicts with the established architecture.

If NoSQL is genuinely needed:
1. Discuss with architecture team
2. Create new ADR documenting the exception
3. Document why PostgreSQL is unsuitable for this use case

📚 Reference: ADR-001: Database Selection
```

## Testing the Server

### Test 1: Run Server Locally

```bash
python src/server.py
```

Server should start and wait for MCP protocol messages on stdin.

### Test 2: Test with MCP Client

In Claude Code or testing environment:

```
Use KellerAI standards MCP to get security coding standards
```

**Expected:** Security section from coding-standards.yaml

### Test 3: Search ADRs

```
Search KellerAI ADRs for "database"
```

**Expected:** List of ADRs mentioning "database" with metadata

### Test 4: Pattern Validation

```
Check if "dependency injection" is approved at KellerAI
```

**Expected:** ✅ Approved status with guidance

## Troubleshooting

### Issue: Server Won't Start

**Error:**
```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:**
```bash
pip install mcp pyyaml
```

### Issue: Standards File Not Found

**Error:**
```
Standards file not found at: /path/to/coding-standards.yaml
```

**Solutions:**
1. Create the standards file at the expected location
2. Set `KELLERAI_REPO_ROOT` environment variable
3. Use sample standards from this README

### Issue: No ADRs Found

**Error:**
```
ADR directory not found
```

**Solutions:**
1. Create `docs/architecture/decisions/` directory
2. Add ADR markdown files
3. Use sample ADR template from this README

## Performance

- **Response Time**: < 100ms for standards retrieval
- **ADR Search**: < 500ms for full-text search
- **Memory Usage**: ~50MB for server process
- **Caching**: Results cached for 5 minutes

## Security

- **Read-Only**: Server only reads files, never writes
- **Sandboxed**: Only accesses files in configured repository
- **No External Calls**: All data local, no network requests
- **Validation**: Input validation on all tool parameters

## Support

- **GitHub Issues**: Report bugs and feature requests
- **Documentation**: See `/docs/architecture/mcp-servers.md`
- **Team Channel**: #code-quality on Slack

## Changelog

### Version 1.0 (2025-10-14)
- Initial KellerAI standards MCP server
- 5 MCP tools: standards, ADR search, preferences, patterns, API validation
- Sample standards and ADR templates
- Documentation and examples
