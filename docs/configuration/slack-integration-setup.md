# Slack Integration Setup for Quality Gate Notifications

**Version:** 1.0  
**Date:** 2025-10-14  
**Purpose:** Configure Slack integration for quality gate notifications and escalation alerts

---

## Overview

This guide covers setting up Slack integration for the CodeRabbit quality gate system to enable:
- ✅ Real-time PR blocking notifications
- ✅ Escalation alerts to tech leads and security team
- ✅ Daily compliance summaries
- ✅ Emergency incident notifications

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Slack Workspace Setup](#slack-workspace-setup)
3. [Webhook Configuration](#webhook-configuration)
4. [GitHub Secrets Setup](#github-secrets-setup)
5. [Channel Configuration](#channel-configuration)
6. [Notification Templates](#notification-templates)
7. [Testing](#testing)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

**Requirements:**
- Slack workspace admin access
- GitHub repository admin access
- CodeRabbit quality gate system deployed
- GitHub Actions enabled

**Slack Channels to Create:**
- `#code-reviews` - Standard quality gate notifications
- `#security-alerts` - Security escalations (private)
- `#engineering-escalations` - Tech lead escalations

---

## Slack Workspace Setup

### Step 1: Create Slack App

1. **Navigate to Slack API**
   - Go to https://api.slack.com/apps
   - Click "Create New App"
   - Choose "From scratch"

2. **Configure App**
   - **App Name:** `CodeRabbit Quality Gates`
   - **Workspace:** Select your workspace
   - Click "Create App"

3. **Enable Incoming Webhooks**
   - In app settings, navigate to "Incoming Webhooks"
   - Toggle "Activate Incoming Webhooks" to **ON**
   - Click "Add New Webhook to Workspace"

### Step 2: Configure Webhook URLs

**For Each Channel:**

1. **#code-reviews Channel**
   - Click "Add New Webhook to Workspace"
   - Select `#code-reviews` channel
   - Authorize the app
   - **Copy webhook URL** (starts with `https://hooks.slack.com/services/...`)
   - Save as: `SLACK_WEBHOOK_URL`

2. **#security-alerts Channel**
   - Repeat process for `#security-alerts`
   - Save as: `SLACK_SECURITY_WEBHOOK_URL`

3. **#engineering-escalations Channel**
   - Repeat process for `#engineering-escalations`
   - Save as: `SLACK_ESCALATION_WEBHOOK_URL`

### Step 3: Configure App Permissions

**Optional - For Advanced Features:**

1. Navigate to "OAuth & Permissions"
2. Add Bot Token Scopes:
   - `chat:write` - Send messages
   - `chat:write.customize` - Customize message appearance
   - `users:read` - Map GitHub usernames to Slack users
3. Install app to workspace
4. Copy "Bot User OAuth Token"
5. Save as: `SLACK_BOT_TOKEN`

---

## Webhook Configuration

### Webhook URL Format

```
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
                                 ↑         ↑         ↑
                            Workspace   Channel   Secret
```

**Security Notes:**
- ⚠️ Webhook URLs are **secrets** - never commit to version control
- ✅ Store in GitHub Secrets only
- ✅ Rotate webhooks if accidentally exposed
- ✅ Use separate webhooks per channel for isolation

### Webhook Testing

**Test with cURL:**

```bash
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "Test message from CodeRabbit Quality Gates",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "✅ Slack integration is working correctly!"
        }
      }
    ]
  }' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

**Expected Response:**
```
ok
```

---

## GitHub Secrets Setup

### Step 1: Add Repository Secrets

1. **Navigate to Repository Settings**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions

2. **Add Secrets**
   
   Click "New repository secret" for each:

   | Name | Value | Description |
   |------|-------|-------------|
   | `SLACK_WEBHOOK_URL` | `https://hooks.slack.com/services/...` | Main notifications (#code-reviews) |
   | `SLACK_SECURITY_WEBHOOK_URL` | `https://hooks.slack.com/services/...` | Security alerts (#security-alerts) |
   | `SLACK_ESCALATION_WEBHOOK_URL` | `https://hooks.slack.com/services/...` | Escalations (#engineering-escalations) |
   | `SLACK_BOT_TOKEN` | `xoxb-...` | (Optional) For advanced features |

### Step 2: Verify Secrets

**Check secrets are available:**

```yaml
# In GitHub Actions workflow
- name: Verify Slack secrets
  run: |
    if [ -z "${{ secrets.SLACK_WEBHOOK_URL }}" ]; then
      echo "❌ SLACK_WEBHOOK_URL not set"
      exit 1
    fi
    echo "✅ Slack webhook configured"
```

---

## Channel Configuration

### #code-reviews Channel

**Purpose:** Standard quality gate notifications

**Message Types:**
- PR blocked by quality gates
- Quality gate status updates
- Override requests (Level 1 self-service)

**Configuration:**
```yaml
# In .coderabbit.yaml
notifications:
  slack:
    enabled: true
    webhook_url: "${SLACK_WEBHOOK_URL}"
    channel: "#code-reviews"
    notify_on:
      - blocked_pr
      - quality_check_failure
      - override_used
```

**Channel Settings:**
- Public channel (visible to all engineers)
- Notifications: Standard (not @channel unless critical)
- Retention: 90 days
- Pinned messages: Quality gates quick reference

### #security-alerts Channel

**Purpose:** Security escalations and critical alerts

**Message Types:**
- Security check failures (critical severity)
- Security override requests (Level 3)
- Incident-related security issues

**Configuration:**
```yaml
# In .coderabbit.yaml
notifications:
  slack:
    security_alerts:
      enabled: true
      webhook_url: "${SLACK_SECURITY_WEBHOOK_URL}"
      channel: "#security-alerts"
      notify_on:
        - security_check_failure
        - security_override_request
        - incident_security_issue
      mention: "@security-team"
```

**Channel Settings:**
- **Private channel** (security-team only)
- Notifications: @channel for critical alerts
- Retention: Unlimited
- Compliance: Audit log enabled

### #engineering-escalations Channel

**Purpose:** Tech lead escalations and approvals

**Message Types:**
- Tech lead override requests (Level 2)
- Emergency override notifications (Level 4)
- Escalation timeout warnings

**Configuration:**
```yaml
# In .coderabbit.yaml
notifications:
  slack:
    escalations:
      enabled: true
      webhook_url: "${SLACK_ESCALATION_WEBHOOK_URL}"
      channel: "#engineering-escalations"
      notify_on:
        - tech_lead_override_request
        - emergency_override
        - escalation_timeout
      mention: "@tech-leads"
```

**Channel Settings:**
- Private channel (tech-leads, engineering-leadership)
- Notifications: @channel for urgent escalations
- Retention: 90 days
- SLA tracking: 4-hour response time

---

## Notification Templates

### Blocked PR Notification

**Channel:** #code-reviews

**Template:**
```json
{
  "text": "⚠️ Quality Gate Failure - PR Blocked",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "⚠️ Quality Gate Failure - PR Blocked"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*PR:*\n<{{PR_URL}}|#{{PR_NUMBER}} - {{PR_TITLE}}>"
        },
        {
          "type": "mrkdwn",
          "text": "*Author:*\n@{{AUTHOR}}"
        },
        {
          "type": "mrkdwn",
          "text": "*Failed Checks:*\n{{FAILED_CHECKS_COUNT}}"
        },
        {
          "type": "mrkdwn",
          "text": "*Severity:*\n{{SEVERITY_LEVEL}}"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Failed Checks:*\n{{FAILED_CHECKS_LIST}}"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View PR"
          },
          "url": "{{PR_URL}}",
          "style": "primary"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Quality Gates Guide"
          },
          "url": "{{DOCS_URL}}"
        }
      ]
    }
  ]
}
```

### Security Escalation

**Channel:** #security-alerts

**Template:**
```json
{
  "text": "🔒 SECURITY: Override Review Required",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🔒 Security Override Review Required"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "<!subteam^S12345678|@security-team> - Security check override requested"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*PR:*\n<{{PR_URL}}|#{{PR_NUMBER}}>"
        },
        {
          "type": "mrkdwn",
          "text": "*Requested By:*\n@{{REQUESTER}}"
        },
        {
          "type": "mrkdwn",
          "text": "*Check Failed:*\n{{CHECK_NAME}} ({{SEVERITY}})"
        },
        {
          "type": "mrkdwn",
          "text": "*SLA:*\n8 hours (expires {{SLA_DEADLINE}})"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Claimed False Positive:*\n{{JUSTIFICATION}}"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Review Request"
          },
          "url": "{{COMMENT_URL}}",
          "style": "danger"
        }
      ]
    }
  ]
}
```

### Emergency Override

**Channel:** #engineering-escalations

**Template:**
```json
{
  "text": "🚨 EMERGENCY: Quality Gate Override Requested",
  "blocks": [
    {
      "type": "header",
      "text": {
        "type": "plain_text",
        "text": "🚨 EMERGENCY: Quality Gate Override Requested"
      }
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "<!here> Production incident requires immediate override approval"
      }
    },
    {
      "type": "section",
      "fields": [
        {
          "type": "mrkdwn",
          "text": "*Incident:*\n{{INCIDENT_ID}} ({{SEVERITY}})"
        },
        {
          "type": "mrkdwn",
          "text": "*PR:*\n<{{PR_URL}}|#{{PR_NUMBER}}>"
        },
        {
          "type": "mrkdwn",
          "text": "*Impact:*\n{{CUSTOMER_IMPACT}}"
        },
        {
          "type": "mrkdwn",
          "text": "*On-Call Engineer:*\n@{{ENGINEER}}"
        }
      ]
    },
    {
      "type": "section",
      "text": {
        "type": "mrkdwn",
        "text": "*Justification:*\n{{EMERGENCY_JUSTIFICATION}}"
      }
    },
    {
      "type": "actions",
      "elements": [
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "Approve Override"
          },
          "url": "{{PR_URL}}",
          "style": "danger"
        },
        {
          "type": "button",
          "text": {
            "type": "plain_text",
            "text": "View Incident"
          },
          "url": "{{INCIDENT_URL}}"
        }
      ]
    }
  ]
}
```

---

## Testing

### Test Workflow

1. **Test Basic Notification**
   
   ⚠️ **WARNING**: This example is for testing only. Never commit real API keys to repositories. Always use test/sandbox credentials and follow your organization's security policies.
   
   ```bash
   # Create test PR with quality gate failure
   git checkout -b test/quality-gate-notification
   
   # Add intentional security issue (using FAKE test key)
   echo 'API_KEY = "sk_test_FAKE_DO_NOT_USE_REAL_KEYS"' >> test_file.py
   
   git add test_file.py
   git commit -m "test: trigger quality gate notification"
   git push origin test/quality-gate-notification
   
   # Create PR
   gh pr create --title "test: quality gate notification" \
     --body "Testing Slack notification for blocked PR"
   ```

2. **Verify Slack Notification**
   - Check `#code-reviews` channel for notification
   - Verify PR link works
   - Verify failed checks list is populated

3. **Test Security Escalation**
   ```markdown
   # In PR comment:
   @kellerai/security-team - Security check false positive review request
   
   **Check:** hardcoded-credentials
   [Rest of security review template]
   ```
   
   - Check `#security-alerts` channel for notification
   - Verify @security-team mention
   - Verify comment link works

4. **Test Emergency Override**
   ```markdown
   # In PR comment:
   🚨 **EMERGENCY OVERRIDE REQUEST** 🚨
   
   **Incident:** INCIDENT-TEST
   [Rest of emergency template]
   
   @kellerai/admins
   ```
   
   - Check `#engineering-escalations` channel
   - Verify @here mention (or @channel)
   - Verify incident details displayed

### Validation Checklist

- [ ] Webhook URLs correctly configured in GitHub Secrets
- [ ] Notifications arrive in correct Slack channels
- [ ] PR links in notifications are clickable and correct
- [ ] User mentions (@author, @team) work correctly
- [ ] Button actions link to correct URLs
- [ ] Message formatting renders correctly
- [ ] @channel/@here mentions work for escalations
- [ ] Security alerts go to private channel only

---

## Troubleshooting

### Issue: No Notifications Received

**Possible Causes:**
1. Webhook URL not configured in GitHub Secrets
2. Workflow not triggered
3. Slack app webhook deactivated

**Resolution:**
```bash
# Check GitHub Secrets
# Repository Settings → Secrets → Actions
# Verify SLACK_WEBHOOK_URL exists

# Test webhook manually
curl -X POST \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test"}' \
  $SLACK_WEBHOOK_URL

# Check GitHub Actions logs
# Actions tab → quality-gate-notifications workflow
```

### Issue: Messages Not Formatted Correctly

**Cause:** Invalid JSON in notification payload

**Resolution:**
- Validate JSON syntax in workflow file
- Check for unescaped special characters
- Review Slack Block Kit Builder: https://api.slack.com/block-kit/building

### Issue: @mentions Not Working

**Causes:**
- User group ID incorrect
- Bot lacks permissions

**Resolution:**
```bash
# Get user group ID
# Slack → Manage Apps → Your App → User Groups
# Use <!subteam^GROUP_ID|handle> format

# Example:
# <!subteam^S12345678|@security-team>
```

### Issue: Too Many Notifications

**Solution:** Configure notification filters

```yaml
# In .github/workflows/quality-gate-notifications.yml
jobs:
  notify-blocked-pr:
    if: |
      steps.failed_checks.outputs.failed_checks_count > 0 &&
      steps.notification_level.outputs.level == 'critical'
```

---

## Next Steps

1. **Configure Metrics Dashboard**
   - Use Slack metrics API to track notification volume
   - Set up alerts for unusual patterns

2. **User Mapping**
   - Map GitHub usernames to Slack user IDs
   - Enable @mentions for PR authors

3. **Custom Workflows**
   - Add reaction-based workflows (approve with 👍)
   - Implement slash commands for override approvals

4. **Compliance Reporting**
   - Daily summary of quality gate compliance
   - Weekly escalation usage report

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Platform Engineering  
**Status:** Active
