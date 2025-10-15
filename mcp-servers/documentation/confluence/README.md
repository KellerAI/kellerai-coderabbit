# Confluence MCP Server Configuration

## Overview

Confluence MCP server provides access to internal documentation, ADRs, technical specifications, and engineering standards stored in Atlassian Confluence.

## Prerequisites

- Confluence Cloud or Data Center instance
- Admin access to create API tokens
- Node.js installed (for MCP server)
- Access to relevant Confluence spaces

## Installation

### 1. Install Confluence MCP Server

```bash
# Global installation
npm install -g @modelcontextprotocol/server-confluence

# Or use npx (no installation needed)
npx @modelcontextprotocol/server-confluence
```

### 2. Generate Confluence API Token

**For Confluence Cloud:**

1. Navigate to: https://id.atlassian.com/manage/api-tokens
2. Click **Create API token**
3. Name: `CodeRabbit MCP Integration`
4. Copy the token (save securely - only shown once)

**For Confluence Data Center:**

1. Go to Profile → Personal Access Tokens
2. Create new token
3. Set permissions: Read access to relevant spaces
4. Copy token

### 3. Find Confluence Details

You'll need these values for configuration:

```bash
# Base URL (Confluence Cloud)
CONFLUENCE_BASE_URL=https://your-company.atlassian.net/wiki

# Base URL (Confluence Data Center)
CONFLUENCE_BASE_URL=https://confluence.your-company.com

# Username (your email for Cloud)
CONFLUENCE_USERNAME=your-email@company.com

# API Token (from step 2)
CONFLUENCE_API_TOKEN=your-generated-token

# Space Keys (comma-separated list of spaces to search)
CONFLUENCE_SPACES=ENG,TECH,ARCH,SEC,API
```

**To find space keys:**
1. Open Confluence
2. Navigate to a space
3. Look at URL: `https://company.atlassian.net/wiki/spaces/ENG/`
4. Space key is the segment after `/spaces/` (e.g., `ENG`)

## Configuration

### Add to `.mcp.json`

```json
{
  "mcpServers": {
    "confluence": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-confluence"],
      "env": {
        "CONFLUENCE_BASE_URL": "${CONFLUENCE_BASE_URL}",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}",
        "CONFLUENCE_SPACES": "ENG,TECH,ARCH,SEC,API"
      }
    }
  }
}
```

### Add to `.env`

```bash
# Confluence Configuration
CONFLUENCE_BASE_URL=https://kellerai.atlassian.net/wiki
CONFLUENCE_USERNAME=engineering@kellerai.com
CONFLUENCE_API_TOKEN=your_actual_token_here
```

**CRITICAL - Security Best Practices:**

1. **Never Commit Secrets:**
   - Add `.env` to `.gitignore` immediately
   - Use `.env.example` template without real credentials
   - Never commit API tokens or passwords to version control

2. **Production Deployment:**
   - Use secrets manager (AWS Secrets Manager, HashiCorp Vault, etc.)
   - Set environment variables via CI/CD pipeline or container orchestration
   - Never store production credentials in `.env` files

3. **API Token Management:**
   - Rotate tokens every 90 days minimum
   - Use separate tokens for dev/staging/production environments
   - Revoke tokens immediately when team members leave
   - Monitor token usage via Atlassian admin console

4. **Access Control:**
   - Grant minimum required Confluence permissions (read-only if possible)
   - Use service accounts, not personal accounts for API access
   - Document which spaces/pages each token can access

**Example `.env.example` Template:**
```bash
# Confluence Configuration (DO NOT commit real values)
CONFLUENCE_BASE_URL=https://your-domain.atlassian.net/wiki
CONFLUENCE_USERNAME=your-service-account@company.com
CONFLUENCE_API_TOKEN=your_token_here_get_from_secrets_manager
```

### Add to `.claude/settings.json`

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "confluence",
    "context7"
  ]
}
```

## Available MCP Tools

### 1. `search_pages`

Search for pages across configured spaces.

**Input:**
```json
{
  "query": "authentication security",
  "spaceKeys": ["SEC", "ARCH"],
  "limit": 5
}
```

**Output:**
```json
{
  "results": [
    {
      "id": "123456",
      "title": "Authentication Security Guidelines",
      "space": "SEC",
      "url": "https://company.atlassian.net/wiki/spaces/SEC/pages/123456",
      "excerpt": "...guidelines for implementing authentication..."
    }
  ]
}
```

### 2. `get_page`

Retrieve a specific page by ID.

**Input:**
```json
{
  "pageId": "123456"
}
```

**Output:**
Markdown-formatted page content with metadata.

### 3. `get_page_by_title`

Find a page by exact title match.

**Input:**
```json
{
  "title": "Database Migration Policy",
  "spaceKey": "ARCH"
}
```

**Output:**
Page content if found, error if not found or multiple matches.

### 4. `list_spaces`

List all accessible Confluence spaces.

**Input:**
```json
{}
```

**Output:**
```json
{
  "spaces": [
    {"key": "ENG", "name": "Engineering"},
    {"key": "ARCH", "name": "Architecture"},
    {"key": "SEC", "name": "Security"}
  ]
}
```

## Recommended Confluence Structure

### Space Organization

```
Confluence Workspace
├── ENG (Engineering)
│   ├── Development Standards
│   ├── Code Review Guidelines
│   ├── Testing Best Practices
│   └── Deployment Procedures
│
├── ARCH (Architecture)
│   ├── ADRs/
│   │   ├── ADR-001: Database Selection
│   │   ├── ADR-002: Authentication Strategy
│   │   └── ADR-003: Microservices Pattern
│   ├── System Architecture
│   └── Integration Patterns
│
├── SEC (Security)
│   ├── Security Policies
│   ├── Secure Coding Guidelines
│   ├── Authentication Standards
│   ├── Data Protection
│   └── Incident Response
│
├── API (API Documentation)
│   ├── REST API Specifications
│   ├── GraphQL Schemas
│   ├── API Versioning Policy
│   └── Authentication & Authorization
│
└── OPS (Operations)
    ├── Runbooks
    ├── Monitoring Guidelines
    └── Disaster Recovery
```

### ADR Template

Create a template for Architecture Decision Records:

```markdown
# ADR-{number}: {Title}

**Status:** {Proposed | Accepted | Deprecated | Superseded}
**Date:** YYYY-MM-DD
**Deciders:** @team-leads
**Tags:** #architecture #database #authentication

## Context

{What is the issue we're facing? What factors are driving this decision?}

## Decision

{What decision have we made? What are we going to do?}

## Consequences

### Positive

- {Benefit 1}
- {Benefit 2}

### Negative

- {Trade-off 1}
- {Trade-off 2}

### Neutral

- {Neutral consequence 1}

## Alternatives Considered

### Option A: {Alternative}

**Pros:**
- {Pro 1}

**Cons:**
- {Con 1}

**Decision:** Not selected because {reason}

## References

- {Link to related docs}
- {Link to research}
```

## Usage in CodeRabbit Reviews

When CodeRabbit reviews code, it can reference Confluence documentation:

### Example 1: Architecture Decision Validation

**Code Change:**
```python
# New database connection using PostgreSQL
DATABASE_URL = "postgresql://..."
```

**CodeRabbit with Confluence:**
```
✅ This aligns with ADR-001: Database Selection

Confluence reference: "Architecture/ADR-001-database-selection"

The decision to use PostgreSQL was made due to:
- ACID compliance requirements
- Complex query needs
- Strong community support

Ensure you follow the connection pooling guidelines from the ADR.

📚 https://company.atlassian.net/wiki/spaces/ARCH/pages/123456
```

### Example 2: Security Policy Enforcement

**Code Change:**
```python
def authenticate_user(username, password):
    # Hash password with MD5
    hashed = hashlib.md5(password.encode()).hexdigest()
```

**CodeRabbit with Confluence:**
```
🚨 Security Policy Violation

Confluence reference: "Security/Secure-Coding-Guidelines"

Our security policy requires bcrypt for password hashing, not MD5.
MD5 is cryptographically broken and unsuitable for passwords.

Required pattern per security guidelines:
```python
import bcrypt
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
```

📚 https://company.atlassian.net/wiki/spaces/SEC/pages/789012
```

### Example 3: API Specification Compliance

**Code Change:**
```python
@app.get("/api/users/{user_id}")
def get_user(user_id: int):
    return {"id": user_id}
```

**CodeRabbit with Confluence:**
```
⚠️ API Specification Compliance

Confluence reference: "API/REST-API-Specifications"

According to our API standards, all endpoints must:
1. Use async handlers for I/O operations
2. Include proper error responses (404, 500)
3. Return standardized response format
4. Include rate limiting headers

Suggested implementation:
```python
@app.get("/api/v1/users/{user_id}")
async def get_user(user_id: int):
    if not user_exists(user_id):
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "data": {"id": user_id},
        "meta": {"version": "1.0"}
    }
```

📚 https://company.atlassian.net/wiki/spaces/API/pages/345678
```

## Testing the Integration

### Test 1: Connection Test

```bash
# Test Confluence API connection
curl -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
  "${CONFLUENCE_BASE_URL}/rest/api/space"

# Expected: JSON response with list of spaces
```

### Test 2: Search Test

In Claude Code or testing environment:

```
Use Confluence MCP to search for "authentication" in the SEC space
```

**Expected Output:**
- List of security pages about authentication
- Page titles, excerpts, and URLs
- Links to full content

### Test 3: Page Retrieval

```
Get the Confluence page titled "Database Migration Policy" from ARCH space
```

**Expected Output:**
- Full page content in Markdown
- Metadata (author, last updated, labels)
- Page URL

### Test 4: CodeRabbit Integration

When CodeRabbit supports MCP (future):

1. Create test PR with architectural change
2. Comment: `@coderabbitai Check if this follows our architecture decisions`
3. Verify CodeRabbit references relevant ADRs from Confluence

## Performance Optimization

### Caching Strategy

```yaml
confluence:
  cache:
    enabled: true
    search_results_ttl: 300  # 5 minutes
    page_content_ttl: 900    # 15 minutes
    space_list_ttl: 3600     # 1 hour
    max_cache_size: 100      # Cache 100 items
```

### Request Optimization

```yaml
confluence:
  request:
    timeout_ms: 5000         # 5 second timeout
    retry_attempts: 2        # Retry failed requests twice
    concurrent_max: 3        # Max 3 concurrent requests
    batch_enabled: false     # Batch not supported by Confluence API
```

### Rate Limiting

```yaml
confluence:
  rate_limit:
    requests_per_minute: 180  # Stay under 200/min limit
    burst_allowance: 10       # Allow short bursts
    backoff_strategy: "exponential"
```

## Troubleshooting

### Issue: Authentication Failed

**Error:**
```
401 Unauthorized: Invalid credentials
```

**Solutions:**
1. Verify API token is correct and not expired
2. Check username matches token owner
3. Regenerate API token if needed
4. Confirm base URL is correct (Cloud vs Data Center)

### Issue: Space Not Found

**Error:**
```
404 Not Found: Space 'XYZ' does not exist
```

**Solutions:**
1. Verify space key is correct (case-sensitive)
2. Check user has access to the space
3. Confirm space exists in Confluence
4. Update `CONFLUENCE_SPACES` environment variable

### Issue: Rate Limit Exceeded

**Error:**
```
429 Too Many Requests
```

**Solutions:**
1. Reduce concurrent requests
2. Implement request caching
3. Increase delay between requests
4. Contact Atlassian for rate limit increase (Enterprise)

### Issue: Slow Response Times

**Symptoms:**
- Searches taking >5 seconds
- Page retrieval timing out

**Solutions:**
1. Reduce search scope (fewer spaces)
2. Implement more aggressive caching
3. Use specific page IDs instead of title searches
4. Check network latency to Confluence instance
5. Consider Confluence Data Center for better performance

## Security Best Practices

### 1. API Token Management

```bash
# ✅ GOOD: Store in environment variables
export CONFLUENCE_API_TOKEN=$(aws secretsmanager get-secret-value --secret-id confluence-token --query SecretString --output text)

# ❌ BAD: Hardcode in files
CONFLUENCE_API_TOKEN="actual-token-here"  # Never do this!
```

### 2. Permission Scoping

- Grant MCP integration **read-only** access
- Limit to specific spaces (not all spaces)
- Review access permissions quarterly
- Rotate API tokens every 90 days

### 3. Audit Logging

Enable Confluence audit logs to track:
- API token usage
- Page access patterns
- Failed authentication attempts
- Unusual search patterns

### 4. Network Security

```yaml
confluence:
  security:
    ssl_verify: true           # Always verify SSL certificates
    allowed_spaces: ["ENG", "ARCH", "SEC"]  # Whitelist spaces
    content_filtering: true    # Filter sensitive content
```

## Monitoring and Metrics

### Key Metrics

1. **API Call Volume**: Track Confluence API usage
2. **Response Times**: Monitor latency (target: <2s)
3. **Error Rate**: Track failed requests
4. **Cache Hit Rate**: Measure caching effectiveness
5. **Space Coverage**: % of reviews with Confluence context

### Health Checks

```bash
# Confluence health check endpoint
curl -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
  "${CONFLUENCE_BASE_URL}/rest/api/space?limit=1"

# Should return 200 OK with space list
```

### Alerting Thresholds

```yaml
alerts:
  error_rate_threshold: 5      # Alert if >5% requests fail
  response_time_p95: 3000      # Alert if P95 >3s
  cache_hit_rate_min: 60       # Alert if cache hit rate <60%
  api_quota_threshold: 80      # Alert at 80% of rate limit
```

## Support Resources

- **Confluence API Docs**: https://developer.atlassian.com/cloud/confluence/rest/
- **MCP Server Docs**: https://github.com/modelcontextprotocol/servers
- **Atlassian Support**: https://support.atlassian.com
- **Internal Issues**: Create issue in this repository

## Changelog

### Version 1.0 (2025-10-14)
- Initial Confluence MCP configuration
- Documentation and examples
- Security and performance guidelines
- Troubleshooting guide
