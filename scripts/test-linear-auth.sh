#!/bin/bash
# Linear API Authentication Test Script
# Task 10.2 - Configure API Authentication and Permissions

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Load environment variables
if [ -f "$PROJECT_ROOT/.env" ]; then
  export $(cat "$PROJECT_ROOT/.env" | grep -v '^#' | grep -v '^$' | xargs)
fi

# Check LINEAR_PAT is set
if [ -z "$LINEAR_PAT" ]; then
  echo -e "${RED}✗ LINEAR_PAT not set${NC}"
  echo ""
  echo "Please set LINEAR_PAT environment variable or add to .env file:"
  echo "  export LINEAR_PAT='lin_api_your_token_here'"
  echo "  OR"
  echo "  echo 'LINEAR_PAT=lin_api_your_token_here' >> .env"
  echo ""
  exit 1
fi

# Header
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Linear API Authentication Test Suite${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Project: KellerAI CodeRabbit Integration"
echo "Task: 10.2 - Configure API Authentication"
echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# Test counter
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test 1: Basic Authentication
echo -e "${BLUE}Test 1: Basic Authentication${NC}"
echo "Testing viewer query to verify token validity..."
TESTS_RUN=$((TESTS_RUN + 1))

RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email admin } }"}')

if echo "$RESPONSE" | grep -q '"data"'; then
  echo -e "${GREEN}✓ PASSED${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))

  VIEWER_NAME=$(echo "$RESPONSE" | grep -o '"name":"[^"]*' | cut -d'"' -f4)
  VIEWER_EMAIL=$(echo "$RESPONSE" | grep -o '"email":"[^"]*' | cut -d'"' -f4)
  IS_ADMIN=$(echo "$RESPONSE" | grep -o '"admin":[^,}]*' | cut -d':' -f2)

  echo "  • Authenticated as: $VIEWER_NAME"
  echo "  • Email: $VIEWER_EMAIL"
  echo "  • Admin: $IS_ADMIN"
else
  echo -e "${RED}✗ FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  Response: $RESPONSE"
fi
echo ""

# Test 2: Team Query
echo -e "${BLUE}Test 2: Team Configuration Query${NC}"
echo "Testing team access and configuration..."
TESTS_RUN=$((TESTS_RUN + 1))

RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id key name } } }"}')

if echo "$RESPONSE" | grep -q '"data"'; then
  echo -e "${GREEN}✓ PASSED${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))

  TEAM_COUNT=$(echo "$RESPONSE" | grep -o '"key"' | wc -l | tr -d ' ')
  echo "  • Found $TEAM_COUNT team(s)"

  # Extract team keys for display
  TEAM_KEYS=$(echo "$RESPONSE" | grep -o '"key":"[^"]*' | cut -d'"' -f4 | paste -sd ',' -)
  if [ -n "$TEAM_KEYS" ]; then
    echo "  • Team keys: $TEAM_KEYS"
    echo ""
    echo "  ${YELLOW}Note:${NC} Update .coderabbit.yaml with these team keys:"
    echo "    knowledge_base:"
    echo "      linear:"
    echo "        team_keys:"
    for key in $(echo "$TEAM_KEYS" | tr ',' '\n'); do
      echo "          - $key"
    done
  fi
else
  echo -e "${RED}✗ FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  Response: $RESPONSE"
fi
echo ""

# Test 3: Write Permission Test (create test issue)
echo -e "${BLUE}Test 3: Write Permission (Create Test Issue)${NC}"
echo "Testing write access by creating a test issue..."
TESTS_RUN=$((TESTS_RUN + 1))

# Get first team ID for test issue
TEAM_RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { id key } } }"}')

TEAM_ID=$(echo "$TEAM_RESPONSE" | grep -o '"id":"[^"]*' | head -1 | cut -d'"' -f4)

if [ -n "$TEAM_ID" ]; then
  CREATE_RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
    -H "Authorization: Bearer $LINEAR_PAT" \
    -H "Content-Type: application/json" \
    -d "{\"query\": \"mutation { issueCreate(input: { title: \\\"[TEST] API Auth Verification - $(date +%s)\\\", description: \\\"Automated test issue from CodeRabbit integration setup. Safe to delete.\\\", teamId: \\\"$TEAM_ID\\\" }) { success issue { id identifier url } } }\"}")

  if echo "$CREATE_RESPONSE" | grep -q '"success":true'; then
    echo -e "${GREEN}✓ PASSED${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))

    ISSUE_ID=$(echo "$CREATE_RESPONSE" | grep -o '"identifier":"[^"]*' | cut -d'"' -f4)
    ISSUE_URL=$(echo "$CREATE_RESPONSE" | grep -o '"url":"[^"]*' | cut -d'"' -f4)

    echo "  • Created test issue: $ISSUE_ID"
    echo "  • URL: $ISSUE_URL"
    echo "  • ${YELLOW}Note:${NC} You can delete this test issue manually"
  else
    echo -e "${RED}✗ FAILED${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    echo "  Could not create test issue"
    echo "  Response: $CREATE_RESPONSE"
  fi
else
  echo -e "${YELLOW}⚠ SKIPPED${NC}"
  echo "  No team ID found - skipping write test"
fi
echo ""

# Test 4: Rate Limit Check
echo -e "${BLUE}Test 4: Rate Limit Status${NC}"
echo "Checking API rate limit status..."
TESTS_RUN=$((TESTS_RUN + 1))

RESPONSE=$(curl -s -i -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}' 2>&1)

RATE_LIMIT=$(echo "$RESPONSE" | grep -i "x-ratelimit-limit" | cut -d' ' -f2 | tr -d '\r' | tr -d ' ')
RATE_REMAINING=$(echo "$RESPONSE" | grep -i "x-ratelimit-remaining" | cut -d' ' -f2 | tr -d '\r' | tr -d ' ')
RATE_RESET=$(echo "$RESPONSE" | grep -i "x-ratelimit-reset" | cut -d' ' -f2 | tr -d '\r' | tr -d ' ')

if [ -n "$RATE_REMAINING" ]; then
  echo -e "${GREEN}✓ PASSED${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))

  echo "  • Limit: $RATE_LIMIT requests/hour"
  echo "  • Remaining: $RATE_REMAINING requests"

  if [ -n "$RATE_RESET" ]; then
    RESET_TIME=$(date -r "$RATE_RESET" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || echo "N/A")
    echo "  • Resets at: $RESET_TIME"
  fi

  # Warning if running low
  USAGE_PERCENT=$((100 - (RATE_REMAINING * 100 / RATE_LIMIT)))
  if [ "$USAGE_PERCENT" -gt 80 ]; then
    echo "  ${YELLOW}⚠ Warning:${NC} Rate limit ${USAGE_PERCENT}% consumed"
  fi
else
  echo -e "${YELLOW}⚠ WARNING${NC}"
  echo "  Rate limit headers not found (may not be available)"
fi
echo ""

# Test 5: GraphQL Schema Introspection
echo -e "${BLUE}Test 5: API Schema Validation${NC}"
echo "Testing GraphQL schema introspection..."
TESTS_RUN=$((TESTS_RUN + 1))

RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { queryType { name } mutationType { name } } }"}')

if echo "$RESPONSE" | grep -q '"queryType"'; then
  echo -e "${GREEN}✓ PASSED${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
  echo "  • GraphQL schema accessible"
  echo "  • Query and mutation types available"
else
  echo -e "${RED}✗ FAILED${NC}"
  TESTS_FAILED=$((TESTS_FAILED + 1))
  echo "  Could not access GraphQL schema"
fi
echo ""

# Summary
echo -e "${BLUE}================================================${NC}"
echo -e "${BLUE}Test Summary${NC}"
echo -e "${BLUE}================================================${NC}"
echo ""
echo "Total Tests: $TESTS_RUN"
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
if [ $TESTS_FAILED -gt 0 ]; then
  echo -e "${RED}Failed: $TESTS_FAILED${NC}"
else
  echo -e "${GREEN}Failed: $TESTS_FAILED${NC}"
fi
echo ""

# Final verdict
if [ $TESTS_FAILED -eq 0 ]; then
  echo -e "${GREEN}✓ All tests passed!${NC}"
  echo ""
  echo "Linear API authentication is configured correctly."
  echo ""
  echo "Next steps:"
  echo "  1. Update .coderabbit.yaml with Linear team keys (see Test 2 output)"
  echo "  2. Configure webhook in Linear Settings → API → Webhooks"
  echo "  3. Set LINEAR_WEBHOOK_SECRET in .env file"
  echo "  4. Create test PR with issue reference (e.g., 'Closes ENG-123')"
  echo "  5. Proceed to Subtask 10.3: Implement Bidirectional Sync Logic"
  echo ""
  exit 0
else
  echo -e "${RED}✗ Some tests failed${NC}"
  echo ""
  echo "Please review the failed tests above and:"
  echo "  1. Verify LINEAR_PAT is correct and not expired"
  echo "  2. Check your Linear workspace permissions"
  echo "  3. Ensure you have Member or Admin role"
  echo "  4. Review Linear API documentation: https://developers.linear.app"
  echo ""
  exit 1
fi
