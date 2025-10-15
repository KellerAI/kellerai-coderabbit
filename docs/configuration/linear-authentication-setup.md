# Linear API Authentication Setup Guide

**Document Version:** 1.0
**Last Updated:** 2025-10-14
**Task:** Subtask 10.2 - Configure API Authentication and Permissions
**Status:** Implementation Complete

---

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Generate Linear Personal Access Token](#generate-linear-personal-access-token)
4. [Configure Environment Variables](#configure-environment-variables)
5. [Update CodeRabbit Configuration](#update-coderabbit-configuration)
6. [Permission Scopes](#permission-scopes)
7. [Webhook Configuration](#webhook-configuration)
8. [Security Best Practices](#security-best-practices)
9. [Testing Authentication](#testing-authentication)
10. [Troubleshooting](#troubleshooting)
11. [Credential Rotation](#credential-rotation)

---

## Overview

This guide provides step-by-step instructions for configuring Linear API authentication to enable CodeRabbit integration with bidirectional synchronization capabilities.

### What You'll Configure

- **Linear Personal Access Token (PAT)** for API authentication
- **Environment variables** for secure credential storage
- **CodeRabbit .yaml configuration** for Linear integration
- **Webhook endpoints** for real-time bidirectional sync
- **Permission scopes** for appropriate access levels

### Estimated Setup Time

- **Initial Setup:** 15-30 minutes
- **Testing and Validation:** 15 minutes
- **Total:** 30-45 minutes

---

## Prerequisites

### Required Access

- [ ] **Linear Account** with workspace access
- [ ] **Admin or Member permissions** in Linear workspace
- [ ] **GitHub repository access** for CodeRabbit configuration
- [ ] **CodeRabbit account** (completed in Task #4)

### Required Tools

- [ ] Text editor (VS Code, vim, etc.)
- [ ] Git command line tools
- [ ] curl or API testing tool (for validation)

### Completed Dependencies

- [x] Task #4: CodeRabbit Organization Account Setup
- [x] Task #5: GitHub App Integration
- [x] Subtask 10.1: Issue Tracking System Evaluation (Linear selected)

---

## Generate Linear Personal Access Token

### Step 1: Access Linear Settings

1. **Log in to Linear**
   ```
   https://linear.app/kellerai
   ```

2. **Navigate to Settings**
   - Click your workspace avatar (bottom-left corner)
   - Select **Settings** from the menu
   - Navigate to **API** section in the left sidebar

### Step 2: Create Personal API Key

1. **Click "Create new API Key"**

2. **Configure the API Key**
   - **Label:** `CodeRabbit Integration - Production`
   - **Description:** `API key for CodeRabbit bidirectional sync integration`
   - **Expires:** Select appropriate expiration (recommend: 1 year)

3. **Generate and Copy Token**
   - Click **Create** button
   - **IMPORTANT:** Copy the token immediately - it will only be shown once
   - Format: `lin_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

4. **Secure Storage (Temporary)**
   - Store in password manager immediately
   - Do NOT commit to version control
   - Do NOT share in chat/email

### Step 3: Document Token Metadata

Create a secure record with:
```
Token Label: CodeRabbit Integration - Production
Created Date: 2025-10-14
Created By: [Your Name]
Expiration: 2026-10-14
Purpose: CodeRabbit Linear integration for PR-issue bidirectional sync
Scopes: read, write (default for PAT)
Last Rotated: 2025-10-14
```

---

## Configure Environment Variables

### Production Environment (.env)

Create or update `.env` file in the project root:

```bash
# Linear API Configuration
LINEAR_PAT=lin_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Linear Workspace Configuration
LINEAR_WORKSPACE_ID=kellerai
LINEAR_WORKSPACE_NAME="KellerAI"

# Integration Settings
LINEAR_SYNC_ENABLED=true
LINEAR_WEBHOOK_SECRET=<generate-secure-secret>
```

### Generate Webhook Secret

Use a cryptographically secure random string:

```bash
# On macOS/Linux
openssl rand -hex 32

# Or use Node.js
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

**Example Output:**
```
a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
```

### Environment-Specific Configuration

#### Development (.env.development)
```bash
LINEAR_PAT=lin_api_dev_xxxxxxxxxxxxxxxxxxxxxxxx
LINEAR_WORKSPACE_ID=kellerai-dev
LINEAR_SYNC_ENABLED=true
LINEAR_WEBHOOK_SECRET=<dev-webhook-secret>
```

#### Staging (.env.staging)
```bash
LINEAR_PAT=lin_api_staging_xxxxxxxxxxxxxxxxxxxxxxxx
LINEAR_WORKSPACE_ID=kellerai-staging
LINEAR_SYNC_ENABLED=true
LINEAR_WEBHOOK_SECRET=<staging-webhook-secret>
```

### Secure .env Files

Ensure `.env` files are gitignored:

```bash
# Check .gitignore includes
cat .gitignore | grep -E '^\.env'

# Expected output:
# .env
# .env.*
# !.env.example
```

---

## Update CodeRabbit Configuration

### Update .coderabbit.yaml

Add Linear configuration to your `.coderabbit.yaml`:

```yaml
# Knowledge Base - Linear Integration
knowledge_base:
  linear:
    usage: "auto"  # Disable for public repositories, enable for private
    team_keys:
      - ENG        # Engineering team
      - PROD       # Product team
      - INFRA      # Infrastructure team

# Chat Integrations (if using CodeRabbit chat features)
chat:
  integrations:
    linear:
      usage: "auto"

# Reviews - Enable issue linking validation
reviews:
  request_changes_workflow: true
  issue_linking:
    enabled: true
    required: true  # Require issue links on all PRs
    validation:
      scope_check: true  # Validate PR scope against issue
```

### Configuration Options Explained

#### `usage: "auto"`
- Enables integration for **private repositories only**
- Disables for public repositories (security)
- Alternative: `"enabled"` (always on) or `"disabled"` (always off)

#### `team_keys`
- Array of Linear team identifiers
- Issues are scoped to specific teams
- Format: Team key prefix (e.g., `ENG` for issues like `ENG-123`)

#### `issue_linking.required`
- `true`: Enforces issue links on all PRs
- `false`: Issue links are optional but validated when present
- Recommendation: Start with `false`, enforce after team adoption

#### `scope_check`
- Validates PR changes against linked issue description
- Flags out-of-scope changes
- Helps prevent scope creep

### Find Your Linear Team Keys

To identify team keys for your workspace:

1. **Via Linear UI:**
   - Go to Settings → Teams
   - Each team shows its **Key** (e.g., `ENG`, `PROD`)

2. **Via API Query:**
```bash
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ teams { nodes { key name } } }"
  }'
```

**Example Response:**
```json
{
  "data": {
    "teams": {
      "nodes": [
        {"key": "ENG", "name": "Engineering"},
        {"key": "PROD", "name": "Product"},
        {"key": "INFRA", "name": "Infrastructure"}
      ]
    }
  }
}
```

---

## Permission Scopes

### Linear PAT Default Permissions

Personal Access Tokens have **full access** to the workspace with these capabilities:

#### Read Permissions
- ✅ Read all issues, projects, and cycles
- ✅ Read user information
- ✅ Read team configuration
- ✅ Read comments and attachments
- ✅ Read issue relationships and history

#### Write Permissions
- ✅ Create and update issues
- ✅ Change issue status and assignees
- ✅ Add and remove labels
- ✅ Create and update comments
- ✅ Manage issue relationships

#### Administrative (Member+ only)
- ⚠️ Create webhooks (requires Member or Admin)
- ⚠️ Manage projects (requires appropriate team role)

### Required Permissions for CodeRabbit Integration

| Feature | Required Permission | Notes |
|---------|-------------------|-------|
| **Read issues** | Read | Required for all features |
| **Link issues to PRs** | Read | PR description parsing |
| **Update issue status** | Write | Bidirectional sync |
| **Add comments** | Write | PR status updates in Linear |
| **Create webhooks** | Member+ | Real-time sync notifications |
| **Validate scope** | Read | Compare PR changes to issue |

### Permission Verification

Test your token permissions:

```bash
# Test Read Permission
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}'

# Test Write Permission (create a test comment)
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { commentCreate(input: { issueId: \"TEST_ISSUE_ID\", body: \"API test\" }) { success } }"
  }'
```

---

## Webhook Configuration

### Overview

Webhooks enable **real-time bidirectional synchronization** between Linear and GitHub PRs via CodeRabbit.

### Step 1: Determine Webhook Endpoint

Your webhook endpoint depends on deployment model:

#### CodeRabbit Cloud (Recommended)
```
https://app.coderabbit.ai/webhooks/linear
```

#### Self-Hosted CodeRabbit
```
https://your-coderabbit-instance.com/webhooks/linear
```

### Step 2: Create Webhook in Linear

1. **Access Linear Settings**
   - Settings → API → Webhooks
   - Click **Create new webhook**

2. **Configure Webhook**
   ```
   Label: CodeRabbit Integration
   URL: https://app.coderabbit.ai/webhooks/linear
   Secret: <your-webhook-secret-from-env>
   ```

3. **Select Event Types**

   Select these events for bidirectional sync:

   **Issue Events:**
   - [x] Issue created
   - [x] Issue updated
   - [x] Issue deleted
   - [x] Issue status changed

   **Comment Events:**
   - [x] Comment created
   - [x] Comment updated

   **Project Events (Optional):**
   - [ ] Project created
   - [ ] Project updated

   **Cycle Events (Optional):**
   - [ ] Cycle created
   - [ ] Cycle updated

4. **Enable Webhook**
   - Toggle **Enabled** to ON
   - Click **Create webhook**

### Step 3: Webhook Security

Linear webhooks include security features:

#### Signature Verification

Linear signs all webhook payloads with HMAC SHA256:

```javascript
// Example verification (Node.js)
const crypto = require('crypto');

function verifyLinearWebhook(payload, signature, secret) {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = hmac.update(JSON.stringify(payload)).digest('hex');
  return signature === digest;
}
```

#### Headers Sent by Linear

```
X-Linear-Signature: sha256=<signature>
X-Linear-Event: Issue
X-Linear-Delivery: <unique-delivery-id>
Content-Type: application/json
```

### Step 4: Test Webhook Delivery

1. **Create a test issue in Linear:**
   ```
   Title: Webhook Test - CodeRabbit Integration
   Team: ENG
   Description: Testing webhook delivery
   ```

2. **Check webhook delivery logs in Linear:**
   - Settings → API → Webhooks
   - Click on webhook → View deliveries
   - Verify successful delivery (200 status code)

3. **Expected webhook payload:**
   ```json
   {
     "action": "create",
     "type": "Issue",
     "data": {
       "id": "abc123...",
       "title": "Webhook Test - CodeRabbit Integration",
       "team": {
         "key": "ENG"
       },
       "state": {
         "name": "Todo",
         "type": "backlog"
       }
     }
   }
   ```

---

## Security Best Practices

### Token Storage

#### ✅ DO
- Store tokens in environment variables
- Use password managers for backups
- Encrypt tokens at rest in production
- Rotate tokens annually or on compromise
- Limit token access to necessary personnel

#### ❌ DON'T
- Commit tokens to version control
- Share tokens in chat/email
- Use same token across environments
- Log tokens in application logs
- Store tokens in client-side code

### Environment Variable Security

#### Production Deployment

Use secure secret management:

**AWS Systems Manager Parameter Store:**
```bash
aws ssm put-parameter \
  --name "/kellerai/coderabbit/linear-pat" \
  --value "$LINEAR_PAT" \
  --type SecureString
```

**HashiCorp Vault:**
```bash
vault kv put secret/coderabbit/linear \
  pat="$LINEAR_PAT" \
  webhook_secret="$LINEAR_WEBHOOK_SECRET"
```

**GitHub Secrets (for GitHub Actions):**
```bash
gh secret set LINEAR_PAT --body "$LINEAR_PAT"
gh secret set LINEAR_WEBHOOK_SECRET --body "$LINEAR_WEBHOOK_SECRET"
```

### Network Security

#### Webhook Endpoint Protection

1. **IP Allowlisting (if self-hosted):**
   - Linear webhook IPs are dynamic
   - Rely on signature verification instead

2. **HTTPS Required:**
   - Linear only sends webhooks to HTTPS endpoints
   - TLS 1.2+ required

3. **Rate Limiting:**
   - Implement rate limiting on webhook endpoint
   - Protect against accidental loops

### Access Control

#### Token Access Logging

Maintain audit log:
```
Date: 2025-10-14
Action: Token Created
User: admin@kellerai.com
Token ID: lin_api_prod_xxx
Purpose: CodeRabbit Integration

Date: 2025-10-15
Action: Token Used
Service: CodeRabbit
API Call: GetIssue(ENG-123)
Result: Success
```

---

## Testing Authentication

### Test 1: Verify Token Authentication

```bash
# Set environment variable
export LINEAR_PAT="lin_api_xxxxxxxx"

# Test GraphQL API access
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ viewer { id name email admin } }"
  }'
```

**Expected Success Response:**
```json
{
  "data": {
    "viewer": {
      "id": "user-id-123",
      "name": "Your Name",
      "email": "you@kellerai.com",
      "admin": false
    }
  }
}
```

**Common Error Responses:**

**401 Unauthorized:**
```json
{
  "errors": [
    {
      "message": "Authentication required",
      "extensions": {
        "code": "UNAUTHENTICATED"
      }
    }
  ]
}
```
**Fix:** Verify LINEAR_PAT is correct and not expired

**403 Forbidden:**
```json
{
  "errors": [
    {
      "message": "Insufficient permissions",
      "extensions": {
        "code": "FORBIDDEN"
      }
    }
  ]
}
```
**Fix:** Verify workspace access and token permissions

### Test 2: Query Team Configuration

```bash
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ teams { nodes { id key name } } }"
  }'
```

**Expected Success Response:**
```json
{
  "data": {
    "teams": {
      "nodes": [
        {"id": "team-1", "key": "ENG", "name": "Engineering"},
        {"id": "team-2", "key": "PROD", "name": "Product"}
      ]
    }
  }
}
```

### Test 3: Create Test Issue (Write Permission)

```bash
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { issueCreate(input: { title: \"API Auth Test\", teamId: \"team-1\" }) { success issue { id identifier } } }"
  }'
```

**Expected Success Response:**
```json
{
  "data": {
    "issueCreate": {
      "success": true,
      "issue": {
        "id": "issue-abc123",
        "identifier": "ENG-456"
      }
    }
  }
}
```

### Test 4: CodeRabbit Integration Test

1. **Update .env file:**
   ```bash
   echo "LINEAR_PAT=$LINEAR_PAT" >> .env
   ```

2. **Update .coderabbit.yaml:**
   ```yaml
   knowledge_base:
     linear:
       team_keys:
         - ENG
   ```

3. **Create test PR with issue reference:**
   ```bash
   git checkout -b test/linear-integration
   echo "# Test" > test-file.md
   git add test-file.md
   git commit -m "Test Linear integration"
   git push origin test/linear-integration

   gh pr create --title "Test: Linear Integration" \
     --body "Testing Linear integration\n\nCloses ENG-456"
   ```

4. **Verify CodeRabbit comment:**
   - Check PR for CodeRabbit review
   - Confirm Linear issue link is recognized
   - Verify issue details appear in review context

---

## Troubleshooting

### Issue: "Authentication required" error

**Symptoms:**
```json
{
  "errors": [{"message": "Authentication required"}]
}
```

**Solutions:**
1. Verify `LINEAR_PAT` environment variable is set
2. Check token format: should start with `lin_api_`
3. Confirm token hasn't expired
4. Test with different API client (curl vs. application)

### Issue: "Insufficient permissions" error

**Symptoms:**
```json
{
  "errors": [{"message": "Insufficient permissions"}]
}
```

**Solutions:**
1. Verify your Linear workspace role (need Member or Admin)
2. Check if workspace has restricted API access
3. Confirm token was created with current account
4. Test with read-only query first

### Issue: Webhook not delivering

**Symptoms:**
- Webhook shows failed deliveries in Linear
- No webhook events received by CodeRabbit

**Solutions:**

1. **Check webhook URL:**
   ```bash
   # Verify endpoint is accessible
   curl -I https://app.coderabbit.ai/webhooks/linear
   ```

2. **Verify webhook secret matches:**
   - Check `.env` file: `LINEAR_WEBHOOK_SECRET`
   - Compare with Linear webhook configuration

3. **Review webhook delivery logs:**
   - Linear Settings → API → Webhooks → View deliveries
   - Check HTTP status code and response body

4. **Test webhook manually:**
   ```bash
   # Send test webhook payload
   curl -X POST https://app.coderabbit.ai/webhooks/linear \
     -H "Content-Type: application/json" \
     -H "X-Linear-Signature: sha256=test" \
     -H "X-Linear-Event: Issue" \
     -d '{"type":"Issue","action":"create","data":{}}'
   ```

### Issue: Rate Limiting

**Symptoms:**
```json
{
  "errors": [
    {
      "message": "Rate limit exceeded",
      "extensions": {
        "code": "RATE_LIMITED"
      }
    }
  ]
}
```

**Solutions:**
1. Implement exponential backoff
2. Cache frequently accessed data
3. Reduce polling frequency
4. Use webhooks instead of polling

**Linear Rate Limits:**
- **1,500 requests per hour** per workspace
- Burst allowance for short spikes
- Headers indicate limit status:
  ```
  X-RateLimit-Limit: 1500
  X-RateLimit-Remaining: 1450
  X-RateLimit-Reset: 1697654400
  ```

---

## Credential Rotation

### When to Rotate

Rotate Linear PAT:
- **Annually** (scheduled maintenance)
- **On suspected compromise** (immediate)
- **Team member departure** (if they had access)
- **After security audit** (as recommended)

### Rotation Procedure

#### Step 1: Create New Token

1. Generate new Linear PAT (follow [Generation Steps](#generate-linear-personal-access-token))
2. Label: `CodeRabbit Integration - Production (Rotated YYYY-MM-DD)`
3. Store securely in password manager

#### Step 2: Update Environment Variables

**Development/Staging:**
```bash
# Update .env.development
LINEAR_PAT=lin_api_new_token_here

# Test integration
curl -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}'
```

**Production:**
```bash
# Update production secrets (example with AWS)
aws ssm put-parameter \
  --name "/kellerai/coderabbit/linear-pat" \
  --value "$NEW_LINEAR_PAT" \
  --type SecureString \
  --overwrite

# Or with environment variables
export LINEAR_PAT="lin_api_new_token_here"

# Restart services to pick up new token
kubectl rollout restart deployment/coderabbit-integration
```

#### Step 3: Verify New Token

Run full authentication test suite:
```bash
# Run test script
./scripts/test-linear-auth.sh

# Expected output:
# ✓ Authentication successful
# ✓ Team query successful
# ✓ Issue creation successful
# ✓ Webhook delivery successful
```

#### Step 4: Revoke Old Token

1. Login to Linear → Settings → API
2. Find old token in list
3. Click **Revoke** button
4. Confirm revocation

#### Step 5: Update Documentation

Update this document's rotation log:
```markdown
## Rotation History

- **2025-10-14:** Initial token creation
- **2026-10-14:** Scheduled annual rotation (planned)
```

---

## Appendix A: Environment Variable Reference

### Complete .env Template

```bash
# ============================================
# Linear API Configuration
# ============================================

# Linear Personal Access Token (Required)
# Generate: Linear Settings → API → Create new API Key
# Format: lin_api_xxxxxxxxxxxxxxxxxxxxxxxx
LINEAR_PAT=lin_api_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Linear Workspace Configuration
LINEAR_WORKSPACE_ID=kellerai
LINEAR_WORKSPACE_NAME="KellerAI"

# Integration Settings
LINEAR_SYNC_ENABLED=true
LINEAR_BIDIRECTIONAL_SYNC=true

# Webhook Configuration
LINEAR_WEBHOOK_URL=https://app.coderabbit.ai/webhooks/linear
LINEAR_WEBHOOK_SECRET=<generate-with-openssl-rand-hex-32>

# Polling Configuration (fallback if webhooks fail)
LINEAR_POLL_INTERVAL_SECONDS=300
LINEAR_POLL_ENABLED=false

# Rate Limiting
LINEAR_MAX_REQUESTS_PER_MINUTE=25
LINEAR_BURST_ALLOWANCE=50

# Retry Configuration
LINEAR_MAX_RETRIES=3
LINEAR_RETRY_DELAY_MS=1000
LINEAR_RETRY_BACKOFF_MULTIPLIER=2

# Logging
LINEAR_LOG_LEVEL=info
LINEAR_LOG_API_CALLS=false

# Feature Flags
LINEAR_SCOPE_VALIDATION_ENABLED=true
LINEAR_AUTO_STATUS_UPDATE=true
LINEAR_COMMENT_SYNC_ENABLED=true
```

---

## Appendix B: API Testing Script

Save as `scripts/test-linear-auth.sh`:

```bash
#!/bin/bash
# Linear API Authentication Test Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
  export $(cat .env | grep -v '^#' | xargs)
fi

# Check LINEAR_PAT is set
if [ -z "$LINEAR_PAT" ]; then
  echo -e "${RED}✗ LINEAR_PAT not set${NC}"
  echo "Set LINEAR_PAT environment variable or add to .env file"
  exit 1
fi

echo "Linear API Authentication Test"
echo "=============================="
echo ""

# Test 1: Basic Authentication
echo -n "Test 1: Basic Authentication... "
RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id name email } }"}')

if echo "$RESPONSE" | grep -q '"data"'; then
  echo -e "${GREEN}✓ PASSED${NC}"
  VIEWER_NAME=$(echo "$RESPONSE" | grep -o '"name":"[^"]*' | cut -d'"' -f4)
  echo "  Authenticated as: $VIEWER_NAME"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "  Response: $RESPONSE"
  exit 1
fi

# Test 2: Team Query
echo -n "Test 2: Team Query... "
RESPONSE=$(curl -s -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ teams { nodes { key name } } }"}')

if echo "$RESPONSE" | grep -q '"data"'; then
  echo -e "${GREEN}✓ PASSED${NC}"
  TEAM_COUNT=$(echo "$RESPONSE" | grep -o '"key"' | wc -l | xargs)
  echo "  Found $TEAM_COUNT team(s)"
else
  echo -e "${RED}✗ FAILED${NC}"
  echo "  Response: $RESPONSE"
  exit 1
fi

# Test 3: Rate Limit Check
echo -n "Test 3: Rate Limit Check... "
RESPONSE=$(curl -s -I -X POST https://api.linear.app/graphql \
  -H "Authorization: Bearer $LINEAR_PAT" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ viewer { id } }"}')

RATE_LIMIT=$(echo "$RESPONSE" | grep -i "x-ratelimit-remaining" | cut -d' ' -f2 | tr -d '\r')
if [ -n "$RATE_LIMIT" ]; then
  echo -e "${GREEN}✓ PASSED${NC}"
  echo "  Remaining requests: $RATE_LIMIT / 1500"
else
  echo -e "${YELLOW}⚠ WARNING${NC}"
  echo "  Rate limit header not found"
fi

echo ""
echo -e "${GREEN}All tests passed!${NC}"
echo ""
echo "Next steps:"
echo "1. Update .coderabbit.yaml with Linear configuration"
echo "2. Configure webhook in Linear settings"
echo "3. Create test PR with issue reference"
```

Make script executable:
```bash
chmod +x scripts/test-linear-auth.sh
```

---

## Appendix C: Webhook Testing Payload

Example webhook payload for testing:

```json
{
  "action": "update",
  "type": "Issue",
  "createdAt": "2025-10-14T21:00:00.000Z",
  "data": {
    "id": "abc123-def456-ghi789",
    "createdAt": "2025-10-14T20:00:00.000Z",
    "updatedAt": "2025-10-14T21:00:00.000Z",
    "number": 123,
    "title": "Implement Linear integration",
    "priority": 1,
    "boardOrder": 0,
    "sortOrder": -1000,
    "startedAt": "2025-10-14T20:30:00.000Z",
    "teamId": "team-abc123",
    "previousIdentifiers": [],
    "creatorId": "user-123",
    "stateId": "state-in-progress",
    "priorityLabel": "High",
    "identifier": "ENG-123",
    "url": "https://linear.app/kellerai/issue/ENG-123",
    "team": {
      "id": "team-abc123",
      "key": "ENG",
      "name": "Engineering"
    },
    "state": {
      "id": "state-in-progress",
      "name": "In Progress",
      "color": "#f2c94c",
      "type": "started"
    },
    "assignee": {
      "id": "user-123",
      "name": "Developer Name",
      "email": "dev@kellerai.com"
    },
    "labels": [
      {
        "id": "label-123",
        "name": "integration",
        "color": "#4ea7fc"
      }
    ]
  },
  "organizationId": "org-kellerai",
  "webhookTimestamp": 1697654400000,
  "webhookId": "webhook-abc123"
}
```

---

**Document Status:** Complete and ready for implementation
**Next Steps:** Proceed to Subtask 10.3 - Implement Bidirectional Synchronization Logic
