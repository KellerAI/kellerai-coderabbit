# CodeRabbit Performance & Compliance Dashboard Setup

**Version:** 2.0
**Date:** 2025-10-14  
**Purpose:** Configure comprehensive monitoring for CodeRabbit performance metrics, quality gates, and continuous improvement tracking

---

## Overview

This guide covers setting up comprehensive monitoring for the CodeRabbit integration, including performance metrics, quality gate compliance, cross-repository learning effectiveness, and automated alerting.

**Metrics Tracked:**
- ✅ **Performance**: Review time, issue detection rate, developer satisfaction
- ✅ **Quality Gates**: Pass/fail rates, override frequency, escalation response times
- ✅ **MCP Optimization**: Query efficiency, cache hit rates, context relevance
- ✅ **Cross-Repository Learning**: Pattern suggestions, acceptance rates
- ✅ **System Health**: Uptime, error rates, response times

---

## Table of Contents

1. [Metrics Collection](#metrics-collection)
2. [Dashboard Configuration](#dashboard-configuration)
3. [Automated Reporting](#automated-reporting)
4. [Compliance Metrics](#compliance-metrics)
5. [Alert Configuration](#alert-configuration)

---

## Metrics Collection

### Data Sources

**1. Quality Gate Events**
- **Location:** `.quality-gate-metrics/*.jsonl`
- **Format:** JSON Lines (one event per line)
- **Retention:** 90 days in GitHub Actions artifacts
- **Collection:** Automatic via quality-gate-notifications.yml workflow

**Example Event:**
```json
{
  "timestamp": "2025-10-14T14:30:00Z",
  "event_type": "pull_request_review",
  "pr_number": 456,
  "status": "changes_requested",
  "repository": "kellerai-api",
  "checks_run": ["security", "architecture", "testing"],
  "checks_failed": ["layer-separation"],
  "checks_passed": ["security", "testing"]
}
```

**2. Override Audit Log**
- **Location:** `.coderabbit-overrides.log`
- **Format:** JSON Lines
- **Retention:** Unlimited (version controlled)
- **Collection:** Automatic via CodeRabbit integration

**Example Override:**
```json
{
  "timestamp": "2025-10-14T14:30:00Z",
  "pr_number": 456,
  "check_name": "layer-separation",
  "override_level": "self-service",
  "requested_by": "developer-name",
  "justification_length": 267,
  "ticket_reference": "TECH-456",
  "risk_level": "low"
}
```

**3. Escalation Metrics**
- **Location:** GitHub Issues with labels
- **Labels:** `escalation:tech-lead-approval`, `escalation:security-review`, `escalation:emergency`
- **Tracking:** Response time, resolution time, approval/rejection

---

## Dashboard Configuration

### Compliance Metrics Dashboard (JSON)

**File:** `.quality-gate-compliance-config.json`

```json
{
  "dashboard": {
    "title": "CodeRabbit Quality Gate Compliance",
    "refresh_interval": "5m",
    "time_range": "30d",
    "panels": [
      {
        "id": "quality-gate-pass-rate",
        "title": "Quality Gate Pass Rate",
        "type": "stat",
        "description": "Percentage of PRs passing all quality gates",
        "query": {
          "metric": "quality_gate_events",
          "filter": "event_type=pull_request_review",
          "aggregation": "count(status=approved) / count(total) * 100"
        },
        "thresholds": {
          "green": 95,
          "yellow": 85,
          "red": 75
        },
        "target": 95
      },
      {
        "id": "failed-checks-breakdown",
        "title": "Failed Checks by Type",
        "type": "pie",
        "description": "Distribution of check failures",
        "query": {
          "metric": "quality_gate_events",
          "filter": "checks_failed.length > 0",
          "group_by": "checks_failed",
          "aggregation": "count"
        }
      },
      {
        "id": "override-frequency",
        "title": "Override Usage Trend",
        "type": "line",
        "description": "Override requests over time",
        "query": {
          "metric": "override_audit_log",
          "time_series": "1d",
          "group_by": "override_level",
          "aggregation": "count"
        }
      },
      {
        "id": "top-failing-checks",
        "title": "Top 5 Failing Checks",
        "type": "table",
        "description": "Checks with highest failure rates",
        "query": {
          "metric": "quality_gate_events",
          "filter": "status=changes_requested",
          "group_by": "check_name",
          "aggregation": "count",
          "order_by": "count DESC",
          "limit": 5
        },
        "columns": ["Check Name", "Failures", "Pass Rate", "Override Rate"]
      },
      {
        "id": "escalation-response-times",
        "title": "Escalation Response Times",
        "type": "bar",
        "description": "Average time to escalation resolution",
        "query": {
          "metric": "github_issues",
          "filter": "labels contains escalation",
          "group_by": "escalation_type",
          "aggregation": "avg(resolution_time)"
        },
        "sla_lines": {
          "tech-lead": 4,
          "security-team": 8,
          "emergency": 0.25
        }
      },
      {
        "id": "compliance-trend",
        "title": "7-Day Compliance Trend",
        "type": "line",
        "description": "Daily compliance percentage",
        "query": {
          "metric": "quality_gate_events",
          "time_series": "1d",
          "time_range": "7d",
          "aggregation": "count(status=approved) / count(total) * 100"
        },
        "target_line": 95
      },
      {
        "id": "override-justification-quality",
        "title": "Override Justification Quality",
        "type": "histogram",
        "description": "Distribution of justification lengths",
        "query": {
          "metric": "override_audit_log",
          "field": "justification_length",
          "buckets": [50, 100, 150, 200, 250, 300],
          "aggregation": "count"
        }
      },
      {
        "id": "false-positive-rate",
        "title": "False Positive Rate by Check",
        "type": "table",
        "description": "Checks with high override rates (potential false positives)",
        "query": {
          "metric": "combined",
          "calculation": "(overrides / failures) * 100",
          "filter": "failures > 10",
          "group_by": "check_name",
          "order_by": "false_positive_rate DESC"
        }
      },
      {
        "id": "emergency-overrides",
        "title": "Emergency Override Usage",
        "type": "timeline",
        "description": "Emergency overrides with incident references",
        "query": {
          "metric": "override_audit_log",
          "filter": "override_level=emergency",
          "fields": ["timestamp", "pr_number", "incident_id", "approved_by"],
          "order_by": "timestamp DESC",
          "limit": 20
        }
      },
      {
        "id": "developer-compliance",
        "title": "Developer Compliance Scores",
        "type": "leaderboard",
        "description": "Developers ranked by quality gate pass rate",
        "query": {
          "metric": "quality_gate_events",
          "group_by": "pr_author",
          "aggregation": "count(status=approved) / count(total) * 100",
          "order_by": "compliance_rate DESC",
          "limit": 10
        }
      }
    ]
  },
  "alerts": [
    {
      "name": "Compliance Below Target",
      "condition": "quality_gate_pass_rate < 85",
      "severity": "warning",
      "notify": ["#engineering-leadership"],
      "message": "Quality gate pass rate dropped below 85% (current: {{value}}%)"
    },
    {
      "name": "High Override Frequency",
      "condition": "override_count_24h > 10",
      "severity": "info",
      "notify": ["#code-reviews"],
      "message": "Unusual override volume detected: {{value}} overrides in 24 hours"
    },
    {
      "name": "Escalation SLA Breach",
      "condition": "escalation_response_time > sla_threshold",
      "severity": "critical",
      "notify": ["#engineering-escalations"],
      "message": "Escalation SLA breached: {{escalation_id}} pending for {{duration}} hours"
    }
  ]
}
```

### Visualization Examples

**Panel 1: Quality Gate Pass Rate (Stat)**
```
┌─────────────────────────────────┐
│  Quality Gate Pass Rate         │
│                                 │
│           92.5%                 │
│        ↑ 2.3% from last week    │
│                                 │
│  ████████████████░░░ 95% target │
└─────────────────────────────────┘
```

**Panel 2: Failed Checks Breakdown (Pie Chart)**
```
┌─────────────────────────────────┐
│  Failed Checks by Type          │
│                                 │
│   Security:      35% ██████████ │
│   Architecture:  25% ███████    │
│   Testing:       20% ██████     │
│   Performance:   15% ████       │
│   Documentation:  5% ██         │
└─────────────────────────────────┘
```

**Panel 3: Top 5 Failing Checks (Table)**
```
┌──────────────────────────────────────────────────────┐
│ Check Name            Failures  Pass Rate  Override  │
├──────────────────────────────────────────────────────┤
│ layer-separation         42      75%        15%      │
│ new-functions-tests      38      78%        20%      │
│ docstring-coverage       35      80%        25%      │
│ n-plus-one              28      85%        10%      │
│ algorithm-complexity     22      88%         8%      │
└──────────────────────────────────────────────────────┘
```

---

## Automated Reporting

### Weekly Compliance Report

**Script:** `.github/scripts/generate-compliance-report.py`

```python
#!/usr/bin/env python3
"""
Generate weekly quality gate compliance report.
Reads from .quality-gate-metrics/ and .coderabbit-overrides.log
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

def load_metrics(days=7):
    """Load quality gate events from last N days"""
    metrics_dir = Path('.quality-gate-metrics')
    events = []
    
    for day in range(days):
        date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        metrics_file = metrics_dir / f"{date}.jsonl"
        
        if metrics_file.exists():
            with open(metrics_file) as f:
                events.extend([json.loads(line) for line in f])
    
    return events

def calculate_compliance_rate(events):
    """Calculate overall compliance percentage"""
    total = len(events)
    if total == 0:
        return 0
    
    passed = sum(1 for e in events if e.get('status') == 'approved')
    return (passed / total) * 100

def top_failing_checks(events, limit=5):
    """Get top N failing checks"""
    failures = defaultdict(int)
    
    for event in events:
        for check in event.get('checks_failed', []):
            failures[check] += 1
    
    return sorted(failures.items(), key=lambda x: x[1], reverse=True)[:limit]

def override_summary(days=7):
    """Summarize override usage"""
    overrides_file = Path('.coderabbit-overrides.log')
    if not overrides_file.exists():
        return {}
    
    cutoff = datetime.now() - timedelta(days=days)
    overrides = []
    
    with open(overrides_file) as f:
        for line in f:
            override = json.loads(line)
            if datetime.fromisoformat(override['timestamp'].replace('Z', '+00:00')) > cutoff:
                overrides.append(override)
    
    from collections import Counter
    
    return {
        'total': len(overrides),
        'by_level': Counter(o['override_level'] for o in overrides),
        'by_check': Counter(o['check_name'] for o in overrides)
    }

def generate_report():
    """Generate complete compliance report"""
    events = load_metrics(days=7)
    compliance_rate = calculate_compliance_rate(events)
    failing_checks = top_failing_checks(events)
    overrides = override_summary(days=7)
    
    report = f"""
# Weekly Quality Gate Compliance Report
**Period:** {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

- **Total PRs Analyzed:** {len(events)}
- **Compliance Rate:** {compliance_rate:.1f}%
- **Target:** 95%
- **Status:** {'✅ ON TRACK' if compliance_rate >= 95 else '⚠️ BELOW TARGET' if compliance_rate >= 85 else '🚨 CRITICAL'}

---

## Top Failing Checks

| Check Name | Failures | Percentage |
|------------|----------|------------|
"""
    
    for check, count in failing_checks:
        percentage = (count / len(events)) * 100 if events else 0
        report += f"| {check} | {count} | {percentage:.1f}% |\n"
    
    report += f"""
---

## Override Usage

- **Total Overrides:** {overrides['total']}
- **Self-Service:** {overrides['by_level'].get('self-service', 0)}
- **Tech Lead Approved:** {overrides['by_level'].get('tech-lead', 0)}
- **Security Team:** {overrides['by_level'].get('security-team', 0)}
- **Emergency:** {overrides['by_level'].get('emergency', 0)}

---

## Recommendations

"""
    
    if compliance_rate < 95:
        report += "1. **Increase Focus:** Compliance below target. Review top failing checks for patterns.\n"
    
    if overrides['total'] > 20:
        report += f"2. **High Override Volume:** {overrides['total']} overrides this week. Investigate false positive patterns.\n"
    
    if overrides['by_level'].get('emergency', 0) > 0:
        report += f"3. **Emergency Overrides:** {overrides['by_level']['emergency']} emergency overrides. Review post-incident reports.\n"
    
    report += """
---

## Actions Required

- [ ] Review top failing checks with engineering team
- [ ] Update check patterns to reduce false positives
- [ ] Conduct training for common failure scenarios
- [ ] Review emergency override post-incident reports

---

*Automated report generated by quality-gate-compliance-monitoring*
"""
    
    return report

if __name__ == '__main__':
    report = generate_report()
    
    # Save report
    reports_dir = Path('compliance-reports')
    reports_dir.mkdir(exist_ok=True)
    
    report_file = reports_dir / f"weekly-{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"Report generated: {report_file}")
    print("\n" + report)
```

### Automated Report Workflow

**File:** `.github/workflows/compliance-reporting.yml`

```yaml
name: Quality Gate Compliance Reporting

on:
  schedule:
    # Run every Monday at 9:00 AM PST (17:00 UTC)
    - cron: '0 17 * * 1'
  workflow_dispatch:  # Manual trigger

permissions:
  contents: write
  issues: write

jobs:
  generate-weekly-report:
    name: Generate Weekly Compliance Report
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for metrics

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Download metrics artifacts
        uses: actions/download-artifact@v4
        with:
          pattern: quality-gate-metrics-*
          path: .quality-gate-metrics/
          merge-multiple: true

      - name: Generate compliance report
        run: |
          python .github/scripts/generate-compliance-report.py

      - name: Commit report
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"
          git add compliance-reports/
          git commit -m "docs: add weekly compliance report $(date +%Y-%m-%d)" || echo "No changes"
          git push

      - name: Post to Slack
        if: env.SLACK_WEBHOOK_URL != ''
        env:
          SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
        uses: slackapi/slack-github-action@v1.25.0
        with:
          payload-file-path: ./compliance-reports/weekly-$(date +%Y-%m-%d).json

      - name: Create GitHub issue if below target
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const reportPath = `compliance-reports/weekly-${new Date().toISOString().split('T')[0]}.md`;
            const report = fs.readFileSync(reportPath, 'utf8');
            
            // Check if compliance is below target
            const complianceMatch = report.match(/\*\*Compliance Rate:\*\* ([\d.]+)%/);
            if (complianceMatch) {
              const rate = parseFloat(complianceMatch[1]);
              
              if (rate < 95) {
                await github.rest.issues.create({
                  owner: context.repo.owner,
                  repo: context.repo.repo,
                  title: `⚠️ Quality Gate Compliance Below Target: ${rate}%`,
                  body: report,
                  labels: ['quality-gates', 'compliance', 'needs-attention']
                });
              }
            }
```

---

## Compliance Metrics

### Key Performance Indicators

**1. Quality Gate Pass Rate**
- **Formula:** `(Approved PRs / Total PRs) × 100`
- **Target:** ≥ 95%
- **Warning Threshold:** < 90%
- **Critical Threshold:** < 85%

**2. Override Frequency**
- **Formula:** `(Overrides / Total PR Reviews) × 100`
- **Target:** < 10%
- **Warning Threshold:** > 15%
- **Critical Threshold:** > 20%

**3. False Positive Rate**
- **Formula:** `(Overrides / Failures) × 100` (per check)
- **Target:** < 15%
- **Warning Threshold:** > 25%
- **Action Required:** > 30% (refine check pattern)

**4. Escalation Response Time**
- **Tech Lead SLA:** 4 hours (business hours)
- **Security Team SLA:** 8 hours (business hours)
- **Emergency SLA:** 15 minutes (24/7)
- **Target Compliance:** ≥ 90% within SLA

**5. Emergency Override Usage**
- **Target:** < 1 per month
- **Warning:** > 2 per month
- **Review Required:** Any emergency override

---

## Alert Configuration

### Alert Rules

**1. Compliance Drop Alert**
```yaml
alert: ComplianceBelowTarget
condition: quality_gate_pass_rate < 90%
severity: warning
notify:
  - slack: "#engineering-leadership"
  - email: "tech-leads@kellerai.com"
message: |
  Quality gate pass rate dropped to {{value}}% (target: 95%)
  Review compliance report: {{report_url}}
```

**2. High Override Volume**
```yaml
alert: HighOverrideVolume
condition: override_count_7d > 50
severity: info
notify:
  - slack: "#code-reviews"
message: |
  High override volume detected: {{value}} overrides in 7 days
  Consider reviewing check patterns for false positives
```

**3. Escalation SLA Breach**
```yaml
alert: EscalationSLABreach
condition: escalation_open_time > sla_threshold
severity: critical
notify:
  - slack: "#engineering-escalations"
  - pagerduty: "escalation-sla-breach"
message: |
  Escalation SLA breached: {{escalation_id}}
  Open for: {{duration}} hours (SLA: {{sla}} hours)
  Action required: {{escalation_url}}
```

---

## Summary

**Compliance Monitoring System Provides:**

✅ **Real-time metrics** on quality gate performance  
✅ **Automated weekly reports** delivered to engineering leadership  
✅ **False positive detection** for check refinement  
✅ **Override usage tracking** with audit trail  
✅ **Escalation SLA monitoring** with alerts  
✅ **Trend analysis** for continuous improvement  

**Next Steps:**
1. Deploy dashboard configuration
2. Set up automated reporting workflow
3. Configure alerts for critical thresholds
4. Train team on metrics interpretation
5. Establish monthly review cadence

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-14  
**Owner:** Platform Engineering  
**Status:** Active
