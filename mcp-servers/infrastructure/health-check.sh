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

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Check Context7
echo -n "Context7 MCP:        "
if [ -z "$CONTEXT7_API_KEY" ]; then
    echo -e "${YELLOW}⚠ Not configured${NC}"
else
    if curl -s -f -H "CONTEXT7_API_KEY: ${CONTEXT7_API_KEY}" \
        https://mcp.context7.com/mcp/health > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        FAILED=$((FAILED + 1))
    fi
fi

# Check Confluence
echo -n "Confluence MCP:      "
if [ -z "$CONFLUENCE_API_TOKEN" ]; then
    echo -e "${YELLOW}⚠ Not configured${NC}"
else
    if curl -s -f -u "${CONFLUENCE_USERNAME}:${CONFLUENCE_API_TOKEN}" \
        "${CONFLUENCE_BASE_URL}/rest/api/space?limit=1" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        FAILED=$((FAILED + 1))
    fi
fi

# Check Notion
echo -n "Notion MCP:          "
if [ -z "$NOTION_API_TOKEN" ]; then
    echo -e "${YELLOW}⚠ Not configured${NC}"
else
    if curl -s -f -H "Authorization: Bearer ${NOTION_API_TOKEN}" \
        -H "Notion-Version: 2022-06-28" \
        https://api.notion.com/v1/users/me > /dev/null 2>&1; then
        echo -e "${GREEN}✓ Healthy${NC}"
    else
        echo -e "${RED}✗ Unhealthy${NC}"
        FAILED=$((FAILED + 1))
    fi
fi

# Check KellerAI Standards (file existence)
echo -n "KellerAI Standards:  "
STANDARDS_SERVER="mcp-servers/kellerai-standards/src/server.py"
if [ -f "$STANDARDS_SERVER" ]; then
    echo -e "${GREEN}✓ Healthy${NC}"
else
    echo -e "${RED}✗ Server file not found${NC}"
    FAILED=$((FAILED + 1))
fi

# Check standards data files
echo -n "Standards Data:      "
STANDARDS_YAML="docs/standards/coding-standards.yaml"
if [ -f "$STANDARDS_YAML" ]; then
    echo -e "${GREEN}✓ Present${NC}"
else
    echo -e "${YELLOW}⚠ Missing${NC}"
fi

echo ""
echo "=========================="
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All configured MCP servers healthy ✓${NC}"
    exit 0
else
    echo -e "${RED}${FAILED} server(s) unhealthy ✗${NC}"
    exit 1
fi
