# Notion MCP Server Configuration

## Overview

Notion MCP server provides access to product requirements, design documents, feature specifications, and team knowledge bases stored in Notion.

## Prerequisites

- Notion workspace (Team or Enterprise plan recommended)
- Admin access to create integrations
- Node.js installed (for MCP server)
- Relevant pages/databases to share with integration

## Installation

### 1. Install Notion MCP Server

```bash
# Global installation
npm install -g @modelcontextprotocol/server-notion

# Or use npx (no installation needed)
npx @modelcontextprotocol/server-notion
```

### 2. Create Notion Integration

**Step-by-step:**

1. Navigate to: https://www.notion.so/my-integrations
2. Click **+ New integration**
3. Configure integration:
   ```
   Name: CodeRabbit MCP
   Associated workspace: [Select your workspace]
   Type: Internal integration
   ```
4. Set capabilities:
   - ✅ **Read content** (required)
   - ✅ **Read comments** (optional, for context)
   - ❌ **Update content** (not needed)
   - ❌ **Insert content** (not needed)
   - ❌ **Read user information** (optional)

5. Click **Submit**
6. Copy the **Internal Integration Token** (starts with `secret_`)
7. Save securely - you'll need this for configuration

### 3. Share Pages with Integration

**Important:** Each page/database must be explicitly shared with the integration.

**For individual pages:**
1. Open the page in Notion
2. Click **Share** in top-right corner
3. Click **Invite**
4. Search for "CodeRabbit MCP"
5. Click integration name to add it
6. Integration now has read access to this page and its children

**For databases:**
1. Open the database
2. Click **•••** (More options)
3. Click **Share**
4. Invite **CodeRabbit MCP** integration
5. Integration can now query this database

**Pro Tip:** Share a parent page to automatically grant access to all child pages.

## Configuration

### Add to `.mcp.json`

```json
{
  "mcpServers": {
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_TOKEN": "${NOTION_API_TOKEN}"
      }
    }
  }
}
```

### Add to `.env`

```bash
# Notion Configuration
NOTION_API_TOKEN=secret_your_integration_token_here

# Optional: Specific database IDs to prioritize
# NOTION_DATABASE_IDS=abc123...,def456...,ghi789...
```

### Add to `.claude/settings.json`

```json
{
  "enableAllProjectMcpServers": true,
  "enabledMcpjsonServers": [
    "notion",
    "confluence",
    "context7"
  ]
}
```

## Available MCP Tools

### 1. `search_pages`

Search across all accessible Notion pages and databases.

**Input:**
```json
{
  "query": "user authentication feature",
  "filter": {
    "property": "Status",
    "status": { "equals": "In Development" }
  },
  "sort": {
    "property": "Last edited",
    "direction": "descending"
  }
}
```

**Output:**
```json
{
  "results": [
    {
      "id": "abc-123-def",
      "title": "PRD: User Authentication Feature",
      "url": "https://notion.so/...",
      "last_edited": "2025-10-14T10:30:00.000Z",
      "properties": {
        "Status": "In Development",
        "Priority": "High"
      }
    }
  ]
}
```

### 2. `get_page`

Retrieve complete page content including all blocks.

**Input:**
```json
{
  "pageId": "abc-123-def"
}
```

**Output:**
Markdown-formatted page content with:
- Page title and metadata
- All text blocks
- Nested content (callouts, quotes, lists)
- Code blocks
- Properties (if database entry)

### 3. `query_database`

Query a specific Notion database with filters and sorts.

**Input:**
```json
{
  "databaseId": "database-id-here",
  "filter": {
    "and": [
      {
        "property": "Status",
        "status": { "equals": "In Development" }
      },
      {
        "property": "Team",
        "select": { "equals": "Engineering" }
      }
    ]
  },
  "sorts": [
    {
      "property": "Priority",
      "direction": "descending"
    }
  ],
  "page_size": 10
}
```

**Output:**
List of database entries with all properties and content.

### 4. `get_block_children`

Retrieve nested blocks (for paginated content).

**Input:**
```json
{
  "blockId": "block-id-here",
  "page_size": 100
}
```

**Output:**
List of child blocks with content.

## Recommended Notion Structure

### Workspace Organization

```
Notion Workspace
│
├── 📋 Engineering Wiki (Database)
│   ├── Development Guidelines
│   ├── Code Review Process
│   ├── Testing Standards
│   └── Deployment Procedures
│
├── 📝 Product Requirements (Database)
│   ├── Template: PRD
│   ├── [PRD] User Authentication
│   ├── [PRD] Payment Integration
│   └── [PRD] Admin Dashboard
│
├── 🎨 Design System (Database)
│   ├── Component Library
│   ├── Design Tokens
│   ├── UI Patterns
│   └── Accessibility Guidelines
│
├── 🗂️ Architecture Decisions (Page with sub-pages)
│   ├── ADR Index
│   ├── ADR-001: Database Selection
│   ├── ADR-002: Auth Strategy
│   └── ADR-003: API Design
│
├── 🔬 Research & Spikes (Database)
│   ├── [Research] GraphQL vs REST
│   ├── [Spike] Performance Testing Tools
│   └── [Research] Cloud Providers
│
└── 📅 Meeting Notes (Database)
    ├── Template: Meeting Notes
    ├── 2025-10-14: Sprint Planning
    ├── 2025-10-13: Tech Decisions
    └── 2025-10-12: Architecture Review
```

### PRD Template

Create a template for Product Requirements Documents:

```markdown
# [PRD] {Feature Name}

**Status:** Draft | In Review | Approved | In Development | Completed
**Owner:** @product-manager
**Engineering Lead:** @tech-lead
**Priority:** High | Medium | Low
**Target Release:** Q1 2025

## Overview

{One paragraph describing the feature and its value}

## Problem Statement

{What problem are we solving? Why now?}

## Goals

- [ ] Goal 1
- [ ] Goal 2
- [ ] Goal 3

## Non-Goals

- Not doing X because Y
- Out of scope: Z

## User Stories

### As a [user type]
- I want to [action]
- So that [benefit]

**Acceptance Criteria:**
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## Technical Requirements

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/v1/users` | GET | List users |
| `/api/v1/users/:id` | GET | Get user |

### Database Schema

```sql
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Dependencies

- Library X for Y functionality
- Service Z for integration

## Design Mockups

[Embed Figma links or screenshots]

## Security Considerations

- Authentication required for all endpoints
- Data encryption at rest and in transit
- Rate limiting: 100 requests/minute

## Performance Requirements

- API response time: < 200ms (P95)
- Database queries: < 50ms
- Page load time: < 2s

## Testing Strategy

- Unit tests: 80%+ coverage
- Integration tests for all endpoints
- E2E tests for critical user flows
- Performance testing under load

## Rollout Plan

**Phase 1:** Internal testing (Week 1-2)
**Phase 2:** Beta users (Week 3-4)
**Phase 3:** General availability (Week 5)

## Success Metrics

- Metric 1: Target value
- Metric 2: Target value
- Metric 3: Target value

## Open Questions

- [ ] Question 1?
- [ ] Question 2?

## Related Documents

- [Link to design doc]
- [Link to architecture decision]
- [Link to technical spec]
```

### Database Properties

**For PRD Database:**
```
Properties:
- Title (Text)
- Status (Select: Draft, In Review, Approved, In Development, Completed)
- Owner (Person)
- Engineering Lead (Person)
- Priority (Select: High, Medium, Low)
- Target Release (Date)
- Team (Select: Frontend, Backend, Mobile, DevOps)
- Tags (Multi-select: authentication, api, database, ui, performance)
```

**For Engineering Wiki:**
```
Properties:
- Title (Text)
- Category (Select: Guidelines, Process, Standards, Tools)
- Last Updated (Last edited time)
- Owner (Person)
- Status (Select: Draft, Active, Deprecated)
```

## Usage in CodeRabbit Reviews

### Example 1: Feature Requirements Validation

**Code Change:**
```python
@app.post("/api/users")
async def create_user(email: str):
    # Create user without password
    return {"email": email}
```

**CodeRabbit with Notion:**
```
⚠️ Missing Requirements from PRD

Notion reference: "[PRD] User Authentication"

According to the PRD, user creation must include:
1. Email validation
2. Password (hashed with bcrypt)
3. Email verification token
4. Created timestamp

Current implementation missing:
- Password field
- Email validation
- Verification token generation

📚 https://notion.so/kellerai/PRD-User-Authentication-abc123
```

### Example 2: Design System Compliance

**Code Change:**
```jsx
<button style={{backgroundColor: "#FF5733"}}>
  Click Me
</button>
```

**CodeRabbit with Notion:**
```
🎨 Design System Violation

Notion reference: "Design System > Design Tokens"

Custom colors should not be hardcoded. Use design tokens from our system:

Correct usage:
```jsx
import { colors } from '@/design-system'

<Button variant="primary">Click Me</Button>
```

Available button variants: primary, secondary, danger, ghost

📚 https://notion.so/kellerai/Design-Tokens-def456
```

### Example 3: Acceptance Criteria Check

**Code Change:**
```python
# User login endpoint
@app.post("/api/login")
async def login(email: str, password: str):
    user = authenticate(email, password)
    return {"token": create_token(user)}
```

**CodeRabbit with Notion:**
```
✅ Partial Implementation

Notion reference: "[PRD] User Authentication > User Stories"

Acceptance criteria status:
- [x] Accept email and password
- [x] Authenticate user
- [x] Return JWT token
- [ ] Rate limiting (100 req/min) ← Missing
- [ ] Failed login tracking ← Missing
- [ ] Account lockout after 5 failures ← Missing

Remaining work needed for full acceptance.

📚 https://notion.so/kellerai/PRD-User-Auth-ghi789#user-stories
```

## Testing the Integration

### Test 1: Connection Test

```bash
# Test Notion API connection
curl https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer ${NOTION_API_TOKEN}" \
  -H "Notion-Version: 2022-06-28"

# Expected: JSON response with integration info
```

### Test 2: Search Test

In Claude Code or testing environment:

```
Use Notion MCP to search for "authentication" across all shared pages
```

**Expected Output:**
- List of pages/databases containing "authentication"
- Page titles and URLs
- Property values (if database entries)

### Test 3: Database Query

```
Query the "Product Requirements" database for all PRDs with status "In Development"
```

**Expected Output:**
- Filtered list of PRDs
- All properties (Status, Owner, Priority, etc.)
- Page URLs

### Test 4: Page Retrieval

```
Get the full content of the PRD titled "User Authentication Feature"
```

**Expected Output:**
- Complete page content in Markdown
- All sections and subsections
- Embedded content
- Metadata

## Performance Optimization

### Caching Strategy

```yaml
notion:
  cache:
    enabled: true
    search_results_ttl: 180  # 3 minutes
    page_content_ttl: 600    # 10 minutes
    database_query_ttl: 300  # 5 minutes
    max_cache_size: 50       # Cache 50 items
```

### Request Optimization

```yaml
notion:
  request:
    timeout_ms: 5000         # 5 second timeout
    retry_attempts: 2        # Retry failed requests twice
    concurrent_max: 3        # Max 3 concurrent requests (rate limit)
    page_size: 100          # Max results per request
```

### Rate Limiting

```yaml
notion:
  rate_limit:
    requests_per_second: 3   # Notion limit
    burst_allowance: 5       # Allow short bursts
    backoff_strategy: "exponential"
    respect_retry_after: true
```

## Troubleshooting

### Issue: Integration Token Invalid

**Error:**
```
401 Unauthorized: invalid_token
```

**Solutions:**
1. Verify token starts with `secret_`
2. Check token hasn't been revoked
3. Regenerate integration token if needed
4. Confirm workspace hasn't changed

### Issue: Page Not Accessible

**Error:**
```
404 Not Found: Could not find page
```

**Solutions:**
1. Verify page is shared with integration
2. Check page hasn't been deleted or archived
3. Share parent page for automatic child access
4. Confirm page ID is correct

### Issue: Rate Limit Exceeded

**Error:**
```
429 Too Many Requests: rate_limited
```

**Solutions:**
1. Respect `Retry-After` header
2. Reduce concurrent requests (max 3)
3. Implement exponential backoff
4. Add caching to reduce API calls
5. Consider upgrading to Enterprise plan for higher limits

### Issue: Partial Content Retrieved

**Symptom:**
- Large pages cut off
- Missing nested blocks

**Solutions:**
1. Use `get_block_children` for paginated content
2. Check `has_more` flag in responses
3. Make additional requests for nested content
4. Increase `page_size` parameter (max 100)

## Security Best Practices

### 1. Token Management

```bash
# ✅ GOOD: Store in environment variables or secrets manager
export NOTION_API_TOKEN=$(aws secretsmanager get-secret-value --secret-id notion-token --query SecretString --output text)

# ❌ BAD: Hardcode in files
NOTION_API_TOKEN="secret_actual_token_here"  # Never do this!
```

### 2. Access Control

- Create integration-specific workspace if needed
- Share only necessary pages/databases
- Use least privilege principle
- Regularly audit shared pages
- Remove access when no longer needed

### 3. Content Filtering

```yaml
notion:
  security:
    filter_sensitive: true    # Filter out sensitive data
    allowed_databases: ["PRD", "Engineering Wiki"]  # Whitelist
    exclude_private_pages: true
    redact_personal_info: true
```

### 4. Audit Logging

Track integration usage:
- Page access patterns
- Search queries performed
- Failed authentication attempts
- Unusual request patterns

## Monitoring and Metrics

### Key Metrics

1. **API Call Volume**: Track Notion API usage
2. **Response Times**: Monitor latency (target: <1.5s)
3. **Error Rate**: Track failed requests
4. **Cache Hit Rate**: Measure caching effectiveness
5. **Content Coverage**: % of reviews with Notion context

### Health Checks

```bash
# Notion health check
curl https://api.notion.com/v1/users/me \
  -H "Authorization: Bearer ${NOTION_API_TOKEN}" \
  -H "Notion-Version: 2022-06-28"

# Should return 200 OK
```

### Alerting Thresholds

```yaml
alerts:
  error_rate_threshold: 5      # Alert if >5% requests fail
  response_time_p95: 2000      # Alert if P95 >2s
  cache_hit_rate_min: 70       # Alert if cache hit rate <70%
  rate_limit_threshold: 80     # Alert at 80% of rate limit
```

## Support Resources

- **Notion API Docs**: https://developers.notion.com
- **MCP Server Docs**: https://github.com/modelcontextprotocol/servers
- **Notion Support**: https://notion.so/help
- **Community**: https://notion.so/community
- **Internal Issues**: Create issue in this repository

## Changelog

### Version 1.0 (2025-10-14)
- Initial Notion MCP configuration
- PRD template and structure guidelines
- Security and performance recommendations
- Troubleshooting guide
- Integration examples
