# MCP Server Infrastructure Deployment Guide

## Overview

This guide covers deploying MCP servers for the KellerAI CodeRabbit integration with comprehensive monitoring, health checks, and operational procedures.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    CodeRabbit (MCP Client)                  │
└────────────┬────────────────────────────────────────────────┘
             │
             ├─── MCP Protocol (stdio/HTTP) ───┐
             │                                  │
    ┌────────▼────────┐              ┌────────▼────────┐
    │   Context7 MCP  │              │  Confluence MCP │
    │   (HTTP)        │              │  (stdio)        │
    └────────┬────────┘              └────────┬────────┘
             │                                 │
    ┌────────▼────────┐              ┌────────▼────────┐
    │   Notion MCP    │              │ KellerAI Custom │
    │   (stdio)       │              │  MCP (stdio)    │
    └─────────────────┘              └─────────────────┘
             │                                 │
    ┌────────▼─────────────────────────────────▼────────┐
    │            Monitoring & Logging                   │
    │  - Health Checks                                  │
    │  - Metrics Collection                             │
    │  - Error Tracking                                 │
    └───────────────────────────────────────────────────┘
```

## Deployment Options

### Option 1: Local Development (Claude Code)

**Use Case:** Individual developer workflows with Claude Code

**Setup:**
1. Install MCP servers locally
2. Configure `.mcp.json` with local paths
3. Set environment variables in `.env`
4. Enable in `.claude/settings.json`

**Pros:**
- Simple setup
- Fast iteration
- No infrastructure needed

**Cons:**
- No centralized monitoring
- Each developer maintains own config
- No shared caching

### Option 2: Shared Development Server

**Use Case:** Team development with shared MCP servers

**Infrastructure:**
- Dedicated VM or container
- Run MCP servers as system services
- Shared cache (Redis)
- Centralized logging

**Pros:**
- Consistent configuration
- Shared caching improves performance
- Centralized monitoring
- Reduced API costs

**Cons:**
- Requires infrastructure maintenance
- Single point of failure (mitigate with redundancy)
- Network latency

### Option 3: Production (CodeRabbit Integration)

**Use Case:** Production CodeRabbit integration (when supported)

**Infrastructure:**
- Containerized MCP servers (Docker/Kubernetes)
- Load balancing and auto-scaling
- Redis for caching
- Comprehensive monitoring
- High availability setup

**Pros:**
- Scalable
- Highly available
- Production-grade monitoring
- Optimal performance

**Cons:**
- Complex setup
- Higher operational overhead
- Infrastructure costs

## Deployment Configuration

### MCP Server Configurations

#### Update `.mcp.json`

```json
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "header": "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY}",
      "timeout": 5000,
      "retries": 2
    },
    "confluence": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-confluence"],
      "env": {
        "CONFLUENCE_BASE_URL": "${CONFLUENCE_BASE_URL}",
        "CONFLUENCE_USERNAME": "${CONFLUENCE_USERNAME}",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}",
        "CONFLUENCE_SPACES": "ENG,TECH,ARCH,SEC,API"
      },
      "timeout": 5000
    },
    "notion": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-notion"],
      "env": {
        "NOTION_API_TOKEN": "${NOTION_API_TOKEN}"
      },
      "timeout": 5000
    },
    "kellerai-standards": {
      "type": "stdio",
      "command": "python",
      "args": ["${KELLERAI_REPO}/mcp-servers/kellerai-standards/src/server.py"],
      "env": {
        "KELLERAI_REPO_ROOT": "${KELLERAI_REPO}"
      },
      "timeout": 2000
    }
  }
}
```

### Environment Variables

Create `.env` file:

```bash
# Context7
CONTEXT7_API_KEY=your_context7_api_key

# Confluence
CONFLUENCE_BASE_URL=https://kellerai.atlassian.net/wiki
CONFLUENCE_USERNAME=engineering@kellerai.com
CONFLUENCE_API_TOKEN=your_confluence_token

# Notion
NOTION_API_TOKEN=secret_your_notion_token

# KellerAI
KELLERAI_REPO=/path/to/kellerai/repository

# Optional: Monitoring
SENTRY_DSN=your_sentry_dsn
DATADOG_API_KEY=your_datadog_key
```

## Health Checks

### Health Check Script

Create `mcp-servers/infrastructure/health-check.sh`:

```bash
#!/bin/bash
# Health check script for MCP servers

set -e

FAILED=0

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🏥 MCP Server Health Check"
echo "=========================="
echo ""

# Check Context7
echo -n "Context7 MCP:        "
if curl -s -f -H "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY}" \
    https://mcp.context7.com/mcp/health > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    FAILED=$((FAILED + 1))
fi

# Check Confluence
echo -n "Confluence MCP:      "
if curl -s -f -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
    "${CONFLUENCE_BASE_URL}/rest/api/space?limit=1" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    FAILED=$((FAILED + 1))
fi

# Check Notion
echo -n "Notion MCP:          "
if curl -s -f -H "Authorization: Bearer ${NOTION_API_TOKEN}" \
    -H "Notion-Version: 2022-06-28" \
    https://api.notion.com/v1/users/me > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Unhealthy${NC}"
    FAILED=$((FAILED + 1))
fi

# Check KellerAI Standards (file existence)
echo -n "KellerAI Standards:  "
if [ -f "${KELLERAI_REPO}/mcp-servers/kellerai-standards/src/server.py" ]; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Server file not found${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "=========================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All MCP servers healthy ✓${NC}"
    exit 0
else
    echo -e "${RED}${FAILED} server(s) unhealthy ✗${NC}"
    exit 1
fi
```

Make executable:
```bash
chmod +x mcp-servers/infrastructure/health-check.sh
```

### Automated Health Checks

#### Cron Job (Linux/Mac)

```bash
# Add to crontab: Run health check every 5 minutes
*/5 * * * * /path/to/mcp-servers/infrastructure/health-check.sh >> /var/log/mcp-health.log 2>&1
```

#### SystemD Timer (Linux)

Create `/etc/systemd/system/mcp-health-check.service`:

```ini
[Unit]
Description=MCP Server Health Check
After=network.target

[Service]
Type=oneshot
EnvironmentFile=/path/to/.env
ExecStart=/path/to/mcp-servers/infrastructure/health-check.sh
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/mcp-health-check.timer`:

```ini
[Unit]
Description=MCP Server Health Check Timer
Requires=mcp-health-check.service

[Timer]
OnBootSec=5min
OnUnitActiveSec=5min
Unit=mcp-health-check.service

[Install]
WantedBy=timers.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable mcp-health-check.timer
sudo systemctl start mcp-health-check.timer
```

## Monitoring

### Metrics to Track

1. **Availability**
   - Uptime percentage
   - Health check pass rate
   - Error rate by server

2. **Performance**
   - Response time (P50, P95, P99)
   - Request volume
   - Timeout rate

3. **Resource Usage**
   - CPU usage
   - Memory usage
   - Network I/O

4. **API Usage**
   - API call volume by server
   - Rate limit proximity
   - API error rate

### Monitoring Tools

#### Option 1: Simple Logging

Create `mcp-servers/infrastructure/monitor.py`:

```python
#!/usr/bin/env python3
"""Simple monitoring script for MCP servers"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path
import requests
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('mcp-monitor.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('mcp-monitor')

def check_context7():
    """Check Context7 MCP health"""
    try:
        response = requests.get(
            'https://mcp.context7.com/mcp/health',
            headers={'CONTEXT7_API_KEY': os.getenv('CONTEXT7_API_KEY')},
            timeout=5
        )
        return {
            'server': 'context7',
            'status': 'healthy' if response.ok else 'unhealthy',
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'server': 'context7',
            'status': 'error',
            'error': str(e)
        }

def check_confluence():
    """Check Confluence MCP health"""
    try:
        response = requests.get(
            f"{os.getenv('CONFLUENCE_BASE_URL')}/rest/api/space",
            auth=(os.getenv('CONFLUENCE_USERNAME'), os.getenv('CONFLUENCE_API_TOKEN')),
            params={'limit': 1},
            timeout=5
        )
        return {
            'server': 'confluence',
            'status': 'healthy' if response.ok else 'unhealthy',
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'server': 'confluence',
            'status': 'error',
            'error': str(e)
        }

def check_notion():
    """Check Notion MCP health"""
    try:
        response = requests.get(
            'https://api.notion.com/v1/users/me',
            headers={
                'Authorization': f"Bearer {os.getenv('NOTION_API_TOKEN')}",
                'Notion-Version': '2022-06-28'
            },
            timeout=5
        )
        return {
            'server': 'notion',
            'status': 'healthy' if response.ok else 'unhealthy',
            'response_time_ms': response.elapsed.total_seconds() * 1000,
            'status_code': response.status_code
        }
    except Exception as e:
        return {
            'server': 'notion',
            'status': 'error',
            'error': str(e)
        }

def check_kellerai_standards():
    """Check KellerAI Standards MCP health"""
    try:
        server_path = Path(os.getenv('KELLERAI_REPO')) / 'mcp-servers/kellerai-standards/src/server.py'
        return {
            'server': 'kellerai-standards',
            'status': 'healthy' if server_path.exists() else 'unhealthy',
            'file_exists': server_path.exists()
        }
    except Exception as e:
        return {
            'server': 'kellerai-standards',
            'status': 'error',
            'error': str(e)
        }

def run_health_checks():
    """Run all health checks and log results"""
    timestamp = datetime.now().isoformat()
    results = {
        'timestamp': timestamp,
        'checks': [
            check_context7(),
            check_confluence(),
            check_notion(),
            check_kellerai_standards()
        ]
    }
    
    # Log results
    for check in results['checks']:
        if check['status'] == 'healthy':
            logger.info(f"{check['server']}: ✓ Healthy ({check.get('response_time_ms', 0):.0f}ms)")
        elif check['status'] == 'unhealthy':
            logger.warning(f"{check['server']}: ⚠ Unhealthy (status {check.get('status_code')})")
        else:
            logger.error(f"{check['server']}: ✗ Error - {check.get('error')}")
    
    # Write to metrics file
    metrics_file = Path('mcp-metrics.jsonl')
    with metrics_file.open('a') as f:
        f.write(json.dumps(results) + '\n')
    
    return results

if __name__ == '__main__':
    logger.info("Starting MCP server monitoring...")
    
    while True:
        try:
            run_health_checks()
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
        
        # Wait 5 minutes
        time.sleep(300)
```

Run with:
```bash
python mcp-servers/infrastructure/monitor.py
```

#### Option 2: Prometheus + Grafana (Production)

**Install Prometheus exporter:**

```python
# mcp-servers/infrastructure/prometheus-exporter.py
from prometheus_client import start_http_server, Gauge, Counter
import time
import requests
import os

# Metrics
health_gauge = Gauge('mcp_server_health', 'MCP server health status', ['server'])
response_time_gauge = Gauge('mcp_server_response_time_ms', 'Response time in ms', ['server'])
error_counter = Counter('mcp_server_errors', 'Error count', ['server'])

def collect_metrics():
    # Context7
    try:
        r = requests.get('https://mcp.context7.com/mcp/health', timeout=5)
        health_gauge.labels(server='context7').set(1 if r.ok else 0)
        response_time_gauge.labels(server='context7').set(r.elapsed.total_seconds() * 1000)
    except Exception:
        error_counter.labels(server='context7').inc()
        health_gauge.labels(server='context7').set(0)
    
    # Add other servers...

if __name__ == '__main__':
    start_http_server(8000)  # Prometheus scrapes this
    while True:
        collect_metrics()
        time.sleep(60)
```

**Grafana Dashboard:**
- Import `mcp-servers/infrastructure/grafana-dashboard.json`
- Visualize health, response times, errors

## Operational Runbooks

### Runbook: MCP Server Down

**Symptoms:**
- Health check fails
- CodeRabbit reviews missing context
- Error logs show connection failures

**Diagnosis:**
1. Check health check script output
2. Review error logs
3. Verify API credentials
4. Test API endpoints manually

**Resolution:**
1. **Context7 Down:**
   - Check Context7 status page
   - Verify API key validity
   - Fall back to cached data
   - Contact Context7 support if outage

2. **Confluence Down:**
   - Check Atlassian status page
   - Verify credentials not expired
   - Check network connectivity
   - Regenerate API token if needed

3. **Notion Down:**
   - Check Notion status page
   - Verify integration token valid
   - Check page sharing permissions
   - Recreate integration if needed

4. **KellerAI Standards:**
   - Check file paths correct
   - Verify Python environment
   - Check YAML syntax in standards files
   - Review server logs for errors

### Runbook: Slow Response Times

**Symptoms:**
- Response times > 5 seconds
- Timeout errors
- Review delays

**Diagnosis:**
1. Check response time metrics
2. Identify slow server
3. Check API rate limits
4. Review cache hit rates

**Resolution:**
1. Increase timeout limits temporarily
2. Implement/improve caching
3. Reduce concurrent requests
4. Contact API provider for rate limit increase
5. Optimize queries (smaller result sets, specific filters)

### Runbook: High API Usage

**Symptoms:**
- Approaching rate limits
- Increased API costs
- Rate limit errors

**Diagnosis:**
1. Review API usage metrics
2. Identify high-usage patterns
3. Check cache effectiveness
4. Review unnecessary calls

**Resolution:**
1. Implement aggressive caching
2. Reduce search scopes
3. Batch requests where possible
4. Set up request throttling
5. Upgrade API tier if justified

## Disaster Recovery

### Backup Strategy

**Configuration Backups:**
```bash
# Backup .mcp.json and .env daily
0 2 * * * tar -czf /backups/mcp-config-$(date +\%Y\%m\%d).tar.gz \
    .mcp.json .env .claude/settings.json
```

**Standards Backups:**
```bash
# Backup standards files (they're in git, but extra backup doesn't hurt)
0 2 * * * tar -czf /backups/mcp-standards-$(date +\%Y\%m\%d).tar.gz \
    docs/standards/ docs/architecture/decisions/
```

### Recovery Procedures

**MCP Server Failure:**
1. Switch to fallback/cached data
2. Notify team of degraded functionality
3. Restore from backup if corruption
4. Restart servers
5. Verify health checks pass
6. Resume normal operations

**Data Loss:**
1. Restore from git (standards files)
2. Restore from backup (.mcp.json, .env)
3. Regenerate API tokens if compromised
4. Update configurations
5. Test all servers
6. Document incident

## Deployment Checklist

- [ ] Environment variables configured
- [ ] `.mcp.json` created and validated
- [ ] `.claude/settings.json` updated
- [ ] All API tokens generated and stored securely
- [ ] Health check script installed
- [ ] Monitoring set up
- [ ] Logging configured
- [ ] Backup procedures in place
- [ ] Runbooks accessible to team
- [ ] Team trained on operational procedures
- [ ] Disaster recovery tested
- [ ] Documentation complete

## Support and Escalation

**Level 1: Team Developer**
- Check health checks
- Review logs
- Restart servers
- Verify credentials

**Level 2: DevOps/SRE**
- Infrastructure issues
- Monitoring setup
- Performance optimization
- Scaling decisions

**Level 3: Vendor Support**
- Context7: support@context7.com
- Atlassian: https://support.atlassian.com
- Notion: https://notion.so/help

**Emergency Contact:**
- On-call rotation
- Slack: #mcp-infrastructure
- PagerDuty: MCP Services

## Changelog

### Version 1.0 (2025-10-14)
- Initial deployment guide
- Health check implementation
- Monitoring setup
- Operational runbooks
- Disaster recovery procedures
