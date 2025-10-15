# Context7 MCP Server Integration

## Overview

Context7 provides up-to-date library documentation for code reviews, enabling CodeRabbit to validate library usage, check for deprecated methods, and suggest best practices.

## Configuration

The Context7 MCP server is configured in the root `.mcp.json` file:

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "header": "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY}"
    }
  }
}
```

## Environment Variables

Add to your `.env` file:

```bash
# Context7 API Key (obtain from https://context7.com)
CONTEXT7_API_KEY=your_api_key_here
```

## Usage in CodeRabbit

Context7 is automatically invoked when CodeRabbit detects library usage in code reviews. It provides:

1. **Library Documentation Retrieval**: Fetches official documentation for libraries
2. **Deprecated Method Detection**: Identifies outdated APIs and suggests alternatives
3. **Best Practices**: Recommends patterns from official library documentation
4. **Documentation Links**: Provides direct links to relevant docs

## Supported Libraries

### Python
- `fastapi` - Modern web framework
- `requests` - HTTP library
- `pytest` - Testing framework
- `pandas` - Data analysis
- `numpy` - Numerical computing
- `sqlalchemy` - Database ORM
- `pydantic` - Data validation
- `django` - Web framework

### JavaScript/TypeScript
- `react` - UI library
- `express` - Web server
- `axios` - HTTP client
- `jest` - Testing framework
- `lodash` - Utility library

### General
- Database drivers (PostgreSQL, MongoDB, Redis)
- HTTP clients
- Test frameworks
- Popular development tools

## MCP Tools

Context7 provides two MCP tools:

### 1. `resolve-library-id`
Resolves a package/product name to a Context7-compatible library ID.

**Input:**
```json
{
  "libraryName": "fastapi"
}
```

**Output:**
```json
{
  "libraryId": "/tiangolo/fastapi",
  "matches": [
    {
      "id": "/tiangolo/fastapi",
      "name": "FastAPI",
      "description": "Modern, fast web framework for Python",
      "trustScore": 9
    }
  ]
}
```

### 2. `get-library-docs`
Fetches documentation for a specific library.

**Input:**
```json
{
  "context7CompatibleLibraryID": "/tiangolo/fastapi",
  "topic": "async endpoints",
  "tokens": 5000
}
```

**Output:**
Markdown-formatted documentation focused on the requested topic.

## Integration Examples

### Example 1: Validating FastAPI Usage

**Code Under Review:**
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/users/{user_id}")
def get_user(user_id: int):
    # Synchronous function - not ideal for FastAPI
    return {"user_id": user_id}
```

**CodeRabbit Review with Context7:**
```
⚠️ Suggestion: Use async endpoints with FastAPI

Context7 documentation shows that FastAPI is designed for async operations.
Using synchronous functions can reduce performance.

Recommended pattern:
```python
@app.get("/users/{user_id}")
async def get_user(user_id: int):
    return {"user_id": user_id}
```

📚 Reference: https://fastapi.tiangolo.com/async/
```

### Example 2: Detecting Deprecated Methods

**Code Under Review:**
```python
import requests

response = requests.get(
    "https://api.example.com/data",
    verify=False  # Disables SSL verification
)
```

**CodeRabbit Review with Context7:**
```
🚨 Security Issue: SSL verification disabled

Context7 documentation strongly recommends enabling SSL verification.
Setting verify=False exposes the application to man-in-the-middle attacks.

If certificate issues exist, provide a custom CA bundle instead:
```python
response = requests.get(
    "https://api.example.com/data",
    verify="/path/to/certfile"
)
```

📚 Reference: https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification
```

### Example 3: Best Practices Recommendation

**Code Under Review:**
```python
import pandas as pd

# Reading large CSV file
df = pd.read_csv("large_file.csv")
result = df[df['value'] > 100]
```

**CodeRabbit Review with Context7:**
```
💡 Performance Tip: Use chunking for large files

Context7 documentation recommends using chunking for large CSV files
to avoid memory issues.

Recommended pattern:
```python
chunks = pd.read_csv("large_file.csv", chunksize=10000)
result = pd.concat([chunk[chunk['value'] > 100] for chunk in chunks])
```

📚 Reference: https://pandas.pydata.org/docs/user_guide/io.html#iterating-through-files-chunk-by-chunk
```

## Testing the Integration

### Test 1: Basic Library Query

Create a test file with library usage:

```python
# test_context7.py
import requests

def fetch_data(url):
    return requests.get(url).json()
```

Run CodeRabbit review:
```bash
coderabbit review test_context7.py
```

**Expected:** CodeRabbit should reference requests documentation.

### Test 2: Deprecated API Detection

Create a file with deprecated patterns:

```python
# test_deprecated.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # Deprecated in SQLAlchemy 2.0
```

**Expected:** CodeRabbit should flag the deprecated pattern and suggest the modern alternative (`DeclarativeBase`).

### Test 3: Framework-Specific Patterns

Create FastAPI code:

```python
# test_fastapi.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/items")
def get_items():  # Sync function in async framework
    return {"items": []}
```

**Expected:** CodeRabbit should suggest using `async def` for better performance.

## Configuration Options

### Token Limits

Control the amount of documentation retrieved:

```yaml
# In CodeRabbit configuration
context7:
  max_tokens: 5000  # Default
  # Higher = more context, more API usage
  # Lower = less context, faster reviews
```

Recommended values:
- **Quick reviews:** 2000 tokens
- **Standard reviews:** 5000 tokens (default)
- **Detailed reviews:** 10000 tokens

### Topic Focusing

Focus Context7 queries on specific topics:

```yaml
context7:
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

### Timeout Configuration

Set reasonable timeouts to prevent review delays:

```yaml
context7:
  timeout_ms: 5000  # 5 seconds
  retry_attempts: 2
  fallback_behavior: "skip"  # or "cache" or "error"
```

## Troubleshooting

### Issue: No Context7 Results

**Possible Causes:**
- Invalid or missing API key
- Library not in Context7 database
- Network connectivity issues

**Solutions:**
```bash
# Test API key
curl -H "CONTEXT7_API_KEY: $CONTEXT7_API_KEY" \
  https://mcp.context7.com/mcp/health

# Check library support
# Use the Context7 website to search for your library

# Test with a known library (e.g., requests, fastapi)
```

### Issue: Slow Reviews

**Possible Causes:**
- High token limits
- Multiple concurrent Context7 calls
- Network latency

**Solutions:**
- Reduce `max_tokens` to 2000-3000
- Implement request caching (see caching section)
- Set stricter timeouts

### Issue: Irrelevant Documentation

**Possible Causes:**
- Generic topic queries
- Wrong library version
- Broad search terms

**Solutions:**
- Use specific topics: "async database queries" instead of "database"
- Specify library version in queries
- Configure topic triggers for better targeting

## Performance Optimization

### Caching Strategy

Implement caching to reduce API calls and improve review speed:

```python
# Example caching configuration
cache:
  enabled: true
  ttl: 3600  # 1 hour
  max_size: 100  # Cache 100 most recent queries
  strategy: "lru"  # Least Recently Used
```

### Batch Requests

For reviewing multiple files, batch Context7 requests:

```yaml
context7:
  batch_enabled: true
  batch_size: 5
  batch_timeout_ms: 10000
```

### Graceful Degradation

Configure fallback behavior when Context7 is unavailable:

```yaml
context7:
  fallback: "cache"  # Use cached results
  # Other options: "skip", "error"
  cache_expiry: 86400  # 24 hours
```

## Monitoring and Metrics

### Key Metrics to Track

1. **API Call Volume**: Track Context7 API usage
2. **Response Times**: Monitor latency (target: <2s)
3. **Cache Hit Rate**: Measure caching effectiveness
4. **Error Rate**: Track failures and timeouts

### Health Checks

Implement health checks for Context7:

```bash
# Health check endpoint
curl https://mcp.context7.com/mcp/health

# Expected response
{
  "status": "healthy",
  "version": "1.0",
  "uptime": "99.9%"
}
```

## Best Practices

1. **Set Appropriate Timeouts**: 5 seconds max to avoid blocking reviews
2. **Use Caching**: Cache documentation for frequently used libraries
3. **Focus Topics**: Use specific topics to get relevant documentation
4. **Monitor Usage**: Track API calls to stay within rate limits
5. **Implement Fallbacks**: Configure graceful degradation for failures
6. **Version Awareness**: Specify library versions when possible
7. **Test Regularly**: Verify integration with test PRs

## Security Considerations

1. **API Key Management**:
   - Store API key in environment variables, not in code
   - Use secret management (AWS Secrets Manager, HashiCorp Vault)
   - Rotate keys periodically

2. **Network Security**:
   - Use HTTPS for all Context7 API calls
   - Implement request signing if available
   - Monitor for unauthorized access

3. **Data Privacy**:
   - Context7 receives library names and topics only
   - No proprietary code is sent to Context7
   - Review Context7 privacy policy for compliance

## Support and Resources

- **Context7 Documentation**: https://docs.context7.com
- **MCP Protocol Spec**: https://modelcontextprotocol.io
- **CodeRabbit MCP Guide**: https://docs.coderabbit.ai/integrations/mcp
- **Issue Reporting**: Create issues in this repository

## Changelog

### Version 1.0 (2025-10-14)
- Initial Context7 MCP integration
- Support for Python and JavaScript libraries
- Documentation and examples
- Caching and performance optimization guides
