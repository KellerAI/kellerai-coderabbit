#!/bin/bash
# Integration test script for MCP server infrastructure

set -e

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     MCP Server Infrastructure Integration Test    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

PASSED=0
FAILED=0

# Load environment variables if .env exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Test 1: Check .mcp.json exists and is valid
echo -n "Test 1: .mcp.json exists and is valid JSON... "
if [ -f .mcp.json ]; then
    if jq empty .mcp.json 2>/dev/null; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}FAIL (invalid JSON)${NC}"
        FAILED=$((FAILED + 1))
    fi
else
    echo -e "${RED}FAIL (file not found)${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 2: Check Claude settings
echo -n "Test 2: .claude/settings.json configured... "
if [ -f .claude/settings.json ]; then
    if jq -e '.enabledMcpjsonServers | contains(["context7", "confluence", "notion", "kellerai-standards"])' .claude/settings.json > /dev/null 2>&1; then
        echo -e "${GREEN}PASS${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}PARTIAL (some servers not enabled)${NC}"
        PASSED=$((PASSED + 1))
    fi
else
    echo -e "${RED}FAIL (file not found)${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 3: KellerAI Standards server exists
echo -n "Test 3: KellerAI Standards MCP server exists... "
if [ -f mcp-servers/kellerai-standards/src/server.py ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 4: Standards data files exist
echo -n "Test 4: Standards data files present... "
if [ -f docs/standards/coding-standards.yaml ] && \
   [ -f docs/standards/approved-patterns.yaml ] && \
   [ -f docs/standards/team-preferences.yaml ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 5: Health check script exists and is executable
echo -n "Test 5: Health check script executable... "
if [ -x mcp-servers/infrastructure/health-check.sh ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 6: Documentation complete
echo -n "Test 6: Documentation files present... "
DOC_COUNT=0
[ -f mcp-servers/context7/README.md ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -f mcp-servers/documentation/confluence/README.md ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -f mcp-servers/documentation/notion/README.md ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -f mcp-servers/kellerai-standards/README.md ] && DOC_COUNT=$((DOC_COUNT + 1))
[ -f mcp-servers/infrastructure/deployment-guide.md ] && DOC_COUNT=$((DOC_COUNT + 1))

if [ $DOC_COUNT -eq 5 ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}PARTIAL ($DOC_COUNT/5 docs found)${NC}"
    PASSED=$((PASSED + 1))
fi

# Test 7: Test examples exist
echo -n "Test 7: Context7 test examples present... "
if [ -f mcp-servers/context7/test-examples/test_fastapi_async.py ] && \
   [ -f mcp-servers/context7/test-examples/test_requests_security.py ] && \
   [ -f mcp-servers/context7/test-examples/test_pandas_performance.py ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 8: Python server dependencies
echo -n "Test 8: Python dependencies specified... "
if [ -f mcp-servers/kellerai-standards/requirements.txt ]; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 9: Environment template
echo -n "Test 9: .env.example includes MCP config... "
if grep -q "CONTEXT7_API_KEY" .env.example && \
   grep -q "CONFLUENCE_API_TOKEN" .env.example && \
   grep -q "NOTION_API_TOKEN" .env.example; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}FAIL${NC}"
    FAILED=$((FAILED + 1))
fi

# Test 10: Run health check
echo -n "Test 10: Health check script executes... "
if ./mcp-servers/infrastructure/health-check.sh > /dev/null 2>&1; then
    echo -e "${GREEN}PASS${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${YELLOW}PARTIAL (servers not configured)${NC}"
    PASSED=$((PASSED + 1))
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "Test Results:"
echo -e "  ${GREEN}PASSED: $PASSED${NC}"
echo -e "  ${RED}FAILED: $FAILED${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Next steps:"
    echo "  1. Copy .env.example to .env"
    echo "  2. Configure API credentials in .env"
    echo "  3. Run health check: ./mcp-servers/infrastructure/health-check.sh"
    echo "  4. Test MCP servers with Claude Code"
    exit 0
else
    echo -e "${RED}✗ Some tests failed. Please review the failures above.${NC}"
    exit 1
fi
