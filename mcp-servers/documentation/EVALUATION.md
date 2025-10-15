# Documentation MCP Server Evaluation

## Purpose

Evaluate Confluence and Notion MCP servers to determine the optimal solution for KellerAI's internal documentation access in CodeRabbit reviews.

## Evaluation Criteria

### 1. Feature Completeness
- Search functionality
- Page/document retrieval
- Content formatting
- Metadata access
- Version history

### 2. Performance
- Response times
- Caching capabilities
- Rate limiting
- Concurrent requests

### 3. Authentication & Security
- OAuth support
- API token management
- Permission handling
- Audit logging

### 4. Integration Ease
- MCP protocol compliance
- Configuration complexity
- Documentation quality
- Community support

### 5. Maintenance
- Update frequency
- Bug fixes
- Breaking changes
- Long-term viability

## Option A: Confluence MCP Server

### Overview
Official MCP server for Atlassian Confluence, providing access to wiki pages, spaces, and documentation.

### Key Features

**Supported:**
- ✅ Full-text search across spaces
- ✅ Page retrieval by ID or title
- ✅ Space listing and navigation
- ✅ Rich content formatting (Confluence markup → Markdown)
- ✅ Attachment handling
- ✅ Label/tag filtering
- ✅ Page versioning access

**Limitations:**
- ❌ No comment retrieval
- ❌ Limited inline image support
- ⚠️ Complex nested page structures require multiple calls

### Technical Specifications

**Package:** `@modelcontextprotocol/server-confluence`

**Installation:**
```bash
npm install -g @modelcontextprotocol/server-confluence
```

**Configuration:**
```json
{
  "mcpServers": {
    "confluence": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-confluence"],
      "env": {
        "CONFLUENCE_BASE_URL": "https://company.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}",
        "CONFLUENCE_SPACES": "ENG,TECH,ARCH,SEC"
      }
    }
  }
}
```

**Available MCP Tools:**

| Tool | Description | Priority |
|------|-------------|----------|
| `search_pages` | Search across specified spaces | High |
| `get_page` | Retrieve page by ID | High |
| `get_page_by_title` | Find page by exact title | Medium |
| `list_spaces` | List accessible spaces | Low |
| `get_page_children` | Get child pages | Medium |
| `get_labels` | Get page labels | Low |

### Authentication

**API Token Generation:**
1. Navigate to https://id.atlassian.com/manage/api-tokens
2. Click "Create API token"
3. Name: "CodeRabbit MCP Integration"
4. Copy and store securely

**Permissions Required:**
- Read access to relevant spaces
- Search permissions
- No write permissions needed

### Performance Characteristics

**Response Times (estimated):**
- Search query: 500ms - 2s
- Page retrieval: 200ms - 800ms
- Space listing: 100ms - 500ms

**Rate Limits:**
- Confluence Cloud: ~200 requests/minute per user
- Confluence Data Center: Configurable

**Caching Strategy:**
- Cache search results: 5 minutes
- Cache page content: 15 minutes
- Cache space list: 1 hour

### Pros

✅ **Official Support**: Maintained by Atlassian  
✅ **Rich Search**: Full-text search with relevance ranking  
✅ **Structured Content**: Well-organized spaces and hierarchies  
✅ **Enterprise Ready**: Used by large organizations  
✅ **Version Control**: Access to page history  
✅ **Label System**: Easy content categorization  

### Cons

❌ **Complex Setup**: Requires API token and space configuration  
❌ **Confluence-Specific**: Tied to Atlassian ecosystem  
❌ **Markup Conversion**: May lose formatting fidelity  
❌ **No Real-time Updates**: Cache invalidation needed  
❌ **Cost**: Confluence Cloud can be expensive  

### Use Cases for KellerAI

**Best For:**
- Architecture Decision Records (ADRs)
- Technical specifications
- API documentation
- Security policies
- Engineering standards
- Team runbooks

**Content Types:**
- `/wiki/spaces/ENG/pages/*` - Engineering docs
- `/wiki/spaces/ARCH/pages/*` - Architecture decisions
- `/wiki/spaces/SEC/pages/*` - Security guidelines
- `/wiki/spaces/API/pages/*` - API specifications

### Example Queries

**Search ADRs:**
```
Tool: search_pages
Query: "authentication database migration"
Spaces: ["ARCH"]
Limit: 5
```

**Get Security Policy:**
```
Tool: get_page_by_title
Title: "Secure Coding Guidelines"
Space: "SEC"
```

### Cost Analysis

**Confluence Cloud Pricing:**
- Free: Up to 10 users
- Standard: $5.75/user/month (up to 10,000 users)
- Premium: $11/user/month
- Enterprise: Custom pricing

**API Usage:**
- Included in subscription
- No per-request costs
- Rate limits apply

---

## Option B: Notion MCP Server

### Overview
Community-maintained MCP server for Notion, providing access to pages, databases, and wikis.

### Key Features

**Supported:**
- ✅ Page search across workspace
- ✅ Database queries
- ✅ Block content retrieval
- ✅ Rich formatting support
- ✅ Property access (metadata)
- ✅ Relation and rollup support
- ✅ Inline databases

**Limitations:**
- ❌ No file attachment retrieval
- ❌ Limited search filtering
- ⚠️ Block-level pagination required for large pages
- ⚠️ Community-maintained (not official)

### Technical Specifications

**Package:** `@modelcontextprotocol/server-notion`

**Installation:**
```bash
npm install -g @modelcontextprotocol/server-notion
```

**Configuration:**
```json
{
  "mcpServers": {
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_TOKEN": "${NOTION_API_TOKEN}",
        "NOTION_DATABASE_IDS": "${NOTION_DATABASE_IDS}"
      }
    }
  }
}
```

**Available MCP Tools:**

| Tool | Description | Priority |
|------|-------------|----------|
| `search_pages` | Search all accessible pages | High |
| `get_page` | Retrieve page content | High |
| `query_database` | Query Notion database | High |
| `get_block_children` | Get nested blocks | Medium |
| `get_page_property` | Access page metadata | Low |

### Authentication

**Integration Token Generation:**
1. Go to https://www.notion.so/my-integrations
2. Click "New integration"
3. Name: "CodeRabbit MCP"
4. Select workspace
5. Set capabilities:
   - ✅ Read content
   - ✅ Read comments
   - ❌ Update content (not needed)
   - ❌ Insert content (not needed)
6. Copy "Internal Integration Token"

**Page Sharing:**
Each page/database must be explicitly shared with the integration:
1. Open page in Notion
2. Click "Share"
3. Invite "CodeRabbit MCP" integration

### Performance Characteristics

**Response Times (estimated):**
- Search query: 300ms - 1.5s
- Page retrieval: 150ms - 600ms
- Database query: 400ms - 2s

**Rate Limits:**
- Free/Personal: ~3 requests/second
- Team: ~3 requests/second (per workspace)
- Enterprise: ~10 requests/second

**Caching Strategy:**
- Cache search results: 3 minutes
- Cache page content: 10 minutes
- Cache database queries: 5 minutes

### Pros

✅ **Modern Interface**: Clean, intuitive documentation  
✅ **Flexible Structure**: Databases and pages combined  
✅ **Rich Metadata**: Properties and relations  
✅ **Easy Sharing**: Simple integration setup  
✅ **Real-time Sync**: Faster content updates  
✅ **Lower Cost**: More affordable than Confluence  
✅ **Better UX**: Team prefers Notion interface  

### Cons

❌ **Community Support**: Not officially maintained by Notion  
❌ **Manual Sharing**: Each page requires explicit integration access  
❌ **Limited Search**: Less powerful than Confluence search  
❌ **Block Pagination**: Large pages require multiple requests  
❌ **No Spaces**: Flat hierarchy vs Confluence spaces  

### Use Cases for KellerAI

**Best For:**
- Product requirements (PRDs)
- Design documents
- Meeting notes with decisions
- Project wikis
- Team knowledge bases
- Feature specifications

**Content Types:**
- Engineering Wiki database
- PRD database
- Design System pages
- Meeting Notes database
- Project Tracker

### Example Queries

**Search PRDs:**
```
Tool: search_pages
Query: "user authentication feature"
```

**Query PRD Database:**
```
Tool: query_database
Database ID: "abc123..."
Filter: {
  "property": "Status",
  "status": { "equals": "In Development" }
}
```

### Cost Analysis

**Notion Pricing:**
- Free: Individual use (limited features)
- Plus: $10/user/month
- Business: $18/user/month
- Enterprise: Custom pricing

**API Usage:**
- Included in subscription
- No per-request costs
- Rate limits apply (more restrictive)

---

## Recommendation: Hybrid Approach

### Strategy

**Use Both MCP Servers** for comprehensive documentation coverage:

1. **Confluence MCP** for:
   - Architecture Decision Records (ADRs)
   - Technical specifications
   - API documentation
   - Security policies
   - Engineering standards

2. **Notion MCP** for:
   - Product Requirements Documents (PRDs)
   - Design documents
   - Feature specifications
   - Meeting notes
   - Team wikis

### Rationale

**Why Hybrid:**
- **Best of Both**: Leverage strengths of each platform
- **Current Usage**: KellerAI likely uses both already
- **Different Purposes**: Different doc types suit different tools
- **Fallback**: If one fails, other provides context
- **Flexibility**: Teams can choose preferred platform

**Implementation Priority:**
1. **Start with Confluence** (Week 1-2)
   - More structured
   - Better for technical docs
   - Easier search

2. **Add Notion** (Week 3-4)
   - After Confluence validated
   - Complementary content
   - Team preference for some docs

### Configuration

**Combined MCP Config:**
```json
{
  "mcpServers": {
    "confluence": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-confluence"],
      "env": {
        "CONFLUENCE_BASE_URL": "https://kellerai.atlassian.net/wiki",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}",
        "CONFLUENCE_SPACES": "ENG,TECH,ARCH,SEC,API"
      }
    },
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

**Usage Guidance for CodeRabbit:**
```markdown
## Documentation MCP Usage

**Confluence** - Check for:
- Architecture decisions (ADRs) when reviewing structural changes
- Security policies for authentication/authorization code
- API specifications when modifying endpoints
- Technical standards for code patterns

**Notion** - Check for:
- Product requirements when implementing features
- Design documents for UI/UX changes
- Feature specifications for acceptance criteria
- Meeting decisions for context on "why"

**Search Priority:**
1. If architectural change → Confluence ADRs
2. If new feature → Notion PRDs
3. If security-related → Confluence security policies
4. If API change → Confluence API specs
5. If UI change → Notion design docs
```

### Success Metrics

**Confluence:**
- ADR references in 40%+ of architectural reviews
- Security policy checks in 60%+ of auth code reviews
- API spec validation in 70%+ of endpoint changes

**Notion:**
- PRD references in 50%+ of feature implementations
- Design doc checks in 60%+ of UI reviews
- Meeting context in 30%+ of complex reviews

### Fallback Strategy

If one MCP server fails:
1. Log error (don't block review)
2. Attempt other server
3. Use cached results if available
4. Continue review with reduced context
5. Alert team of MCP failure

---

## Decision: Implement Hybrid Approach

**Selected Solution:** Both Confluence and Notion MCP servers

**Implementation Order:**
1. ✅ Confluence MCP (Primary) - Week 1-2
2. ✅ Notion MCP (Secondary) - Week 3-4

**Next Steps:**
1. Configure Confluence MCP server
2. Set up authentication and permissions
3. Test with sample queries
4. Document usage patterns
5. Add Notion MCP server
6. Create unified usage guide

**Decision Date:** 2025-10-14  
**Decision Maker:** AI Integration Agent  
**Status:** Approved for Implementation
