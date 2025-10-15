#!/usr/bin/env python3
"""
Generate weekly quality gate compliance report.
Reads from .quality-gate-metrics/ and .coderabbit-overrides.log
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
import sys

def load_metrics(days=7):
    """Load quality gate events from last N days"""
    metrics_dir = Path('.quality-gate-metrics')
    events = []
    
    if not metrics_dir.exists():
        print(f"Warning: Metrics directory not found: {metrics_dir}")
        return events
    
    for day in range(days):
        date = (datetime.now() - timedelta(days=day)).strftime('%Y-%m-%d')
        metrics_file = metrics_dir / f"{date}.jsonl"
        
        if metrics_file.exists():
            try:
                with open(metrics_file) as f:
                    events.extend([json.loads(line) for line in f])
            except Exception as e:
                print(f"Error loading {metrics_file}: {e}")
    
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
        print(f"Warning: Override log not found: {overrides_file}")
        return {
            'total': 0,
            'by_level': defaultdict(int),
            'by_check': defaultdict(int)
        }
    
    cutoff = datetime.now() - timedelta(days=days)
    overrides = []
    
    try:
        with open(overrides_file) as f:
            for line in f:
                try:
                    override = json.loads(line)
                    timestamp = datetime.fromisoformat(override['timestamp'].replace('Z', '+00:00'))
                    if timestamp > cutoff:
                        overrides.append(override)
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid JSON line: {e}")
    except Exception as e:
        print(f"Error loading overrides: {e}")
    
    by_level = defaultdict(int)
    by_check = defaultdict(int)
    
    for override in overrides:
        by_level[override.get('override_level', 'unknown')] += 1
        by_check[override.get('check_name', 'unknown')] += 1
    
    return {
        'total': len(overrides),
        'by_level': by_level,
        'by_check': by_check
    }

def generate_report():
    """Generate complete compliance report"""
    events = load_metrics(days=7)
    compliance_rate = calculate_compliance_rate(events)
    failing_checks = top_failing_checks(events)
    overrides = override_summary(days=7)
    
    # Calculate status
    if compliance_rate >= 95:
        status = '✅ ON TRACK'
    elif compliance_rate >= 85:
        status = '⚠️ BELOW TARGET'
    else:
        status = '🚨 CRITICAL'
    
    report = f"""# Weekly Quality Gate Compliance Report

**Period:** {(datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')} to {datetime.now().strftime('%Y-%m-%d')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Executive Summary

- **Total PRs Analyzed:** {len(events)}
- **Compliance Rate:** {compliance_rate:.1f}%
- **Target:** 95%
- **Status:** {status}

---

## Top Failing Checks

"""
    
    if failing_checks:
        report += "| Check Name | Failures | Percentage |\n"
        report += "|------------|----------|------------|\n"
        
        for check, count in failing_checks:
            percentage = (count / len(events)) * 100 if events else 0
            report += f"| {check} | {count} | {percentage:.1f}% |\n"
    else:
        report += "*No check failures in this period* ✅\n"
    
    report += f"""
---

## Override Usage

- **Total Overrides:** {overrides['total']}
- **Self-Service:** {overrides['by_level'].get('self-service', 0)}
- **Tech Lead Approved:** {overrides['by_level'].get('tech-lead', 0)}
- **Security Team:** {overrides['by_level'].get('security-team', 0)}
- **Emergency:** {overrides['by_level'].get('emergency', 0)}

"""
    
    if overrides['by_check']:
        report += "### Most Overridden Checks\n\n"
        top_overridden = sorted(overrides['by_check'].items(), key=lambda x: x[1], reverse=True)[:5]
        for check, count in top_overridden:
            report += f"- **{check}**: {count} override(s)\n"
    
    report += "\n---\n\n## Recommendations\n\n"
    
    recommendations = []
    
    if compliance_rate < 95:
        recommendations.append("1. **Increase Focus:** Compliance below target. Review top failing checks for patterns.")
    
    if overrides['total'] > 20:
        recommendations.append(f"2. **High Override Volume:** {overrides['total']} overrides this week. Investigate false positive patterns.")
    
    if overrides['by_level'].get('emergency', 0) > 0:
        recommendations.append(f"3. **Emergency Overrides:** {overrides['by_level']['emergency']} emergency override(s). Review post-incident reports.")
    
    if not failing_checks and compliance_rate >= 95:
        recommendations.append("1. **Excellent Performance:** Quality gates are working effectively. Continue current practices.")
    
    if recommendations:
        report += "\n".join(recommendations)
    else:
        report += "*No specific recommendations at this time.*"
    
    report += """

---

## Actions Required

- [ ] Review top failing checks with engineering team
- [ ] Update check patterns to reduce false positives
- [ ] Conduct training for common failure scenarios
"""
    
    if overrides['by_level'].get('emergency', 0) > 0:
        report += "- [ ] Review emergency override post-incident reports\n"
    
    report += """
---

## Resources

- [Quality Gates Quick Reference](../docs/QUALITY_GATES_QUICK_REFERENCE.md)
- [Override Process Guide](../docs/workflows/override-process-guide.md)
- [Escalation Procedures](../docs/workflows/escalation-procedures.md)

---

*Automated report generated by quality-gate-compliance-monitoring*
"""
    
    return report, compliance_rate

def main():
    """Main entry point"""
    print("Generating weekly compliance report...")
    
    try:
        report, compliance_rate = generate_report()
        
        # Create reports directory
        reports_dir = Path('compliance-reports')
        reports_dir.mkdir(exist_ok=True)
        
        # Save report
        report_file = reports_dir / f"weekly-{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(report_file, 'w') as f:
            f.write(report)
        
        print(f"✅ Report generated: {report_file}")
        print(f"📊 Compliance Rate: {compliance_rate:.1f}%")
        
        # Print report to stdout
        print("\n" + "="*80)
        print(report)
        print("="*80)
        
        # Exit with appropriate code
        if compliance_rate < 85:
            print("\n🚨 CRITICAL: Compliance rate below 85%")
            sys.exit(2)
        elif compliance_rate < 95:
            print("\n⚠️ WARNING: Compliance rate below target (95%)")
            sys.exit(1)
        else:
            print("\n✅ SUCCESS: Compliance rate meets target")
            sys.exit(0)
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(3)

if __name__ == '__main__':
    main()
