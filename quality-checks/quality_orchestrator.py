"""
Quality Check Orchestrator for CodeRabbit.

This module orchestrates all quality checks and generates comprehensive reports.

Task 11: Custom Pre-merge Quality Checks - Main Orchestrator
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import json

from .security_checks import SecurityValidator, SecurityFinding
from .architecture_checks import ArchitectureValidator, ArchitectureFinding
from .test_coverage_checks import TestCoverageValidator, TestCoverageFinding
from .performance_checks import PerformanceValidator, PerformanceFinding
from .breaking_changes_checks import BreakingChangesValidator, BreakingChangeFinding


@dataclass
class QualityCheckResult:
    """Overall quality check result."""
    passed: bool
    total_issues: int
    critical_issues: int
    high_issues: int
    medium_issues: int
    low_issues: int
    security_findings: List[SecurityFinding]
    architecture_findings: List[ArchitectureFinding]
    test_coverage_findings: List[TestCoverageFinding]
    performance_findings: List[PerformanceFinding]
    breaking_changes_findings: List[BreakingChangeFinding]
    mode: str  # "warning" or "error"
    override_used: bool = False
    override_justification: Optional[str] = None


class QualityCheckOrchestrator:
    """
    Orchestrates all quality checks for CodeRabbit PRs.

    This is the main entry point for running quality checks on pull requests.
    """

    def __init__(self, mode: str = "warning"):
        """
        Initialize quality check orchestrator.

        Args:
            mode: Execution mode - "warning" (allow merge) or "error" (block merge)
        """
        self.mode = mode
        self.security_validator = SecurityValidator()
        self.architecture_validator = ArchitectureValidator()
        self.test_coverage_validator = TestCoverageValidator()
        self.performance_validator = PerformanceValidator()
        self.breaking_changes_validator = BreakingChangesValidator()

    def validate_pr(
        self,
        pr_title: str,
        pr_description: str,
        changed_files: Dict[str, str],
        old_files: Optional[Dict[str, str]] = None
    ) -> QualityCheckResult:
        """
        Run all quality checks on a pull request.

        Args:
            pr_title: Pull request title
            pr_description: Pull request description
            changed_files: Dictionary of changed files (path -> new content)
            old_files: Dictionary of old file versions (path -> old content)

        Returns:
            QualityCheckResult with all findings
        """
        # Initialize old_files if not provided
        if old_files is None:
            old_files = {}

        # Run security checks
        security_results = self.security_validator.validate_pr_changes(changed_files)
        security_findings = []
        for findings in security_results.values():
            security_findings.extend(findings)

        # Run architecture checks
        architecture_results = self.architecture_validator.validate_project(changed_files)
        architecture_findings = []
        for findings in architecture_results.values():
            architecture_findings.extend(findings)

        # Run test coverage checks
        test_coverage_findings = self.test_coverage_validator.validate_pr(
            pr_title,
            pr_description,
            changed_files
        )

        # Run performance checks
        performance_results = self.performance_validator.validate_pr(changed_files)
        performance_findings = []
        for findings in performance_results.values():
            performance_findings.extend(findings)

        # Run breaking changes checks
        breaking_changes_findings = self.breaking_changes_validator.validate_pr(
            changed_files,
            old_files
        )

        # Calculate severity counts
        all_findings = (
            security_findings +
            architecture_findings +
            test_coverage_findings +
            performance_findings +
            breaking_changes_findings
        )

        severity_counts = self._count_severities(all_findings)

        # Determine if checks passed
        passed = self._determine_pass_status(severity_counts)

        return QualityCheckResult(
            passed=passed,
            total_issues=len(all_findings),
            critical_issues=severity_counts['critical'],
            high_issues=severity_counts['high'],
            medium_issues=severity_counts['medium'],
            low_issues=severity_counts['low'],
            security_findings=security_findings,
            architecture_findings=architecture_findings,
            test_coverage_findings=test_coverage_findings,
            performance_findings=performance_findings,
            breaking_changes_findings=breaking_changes_findings,
            mode=self.mode
        )

    def _count_severities(self, findings: List[Any]) -> Dict[str, int]:
        """Count findings by severity level."""
        counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for finding in findings:
            severity = getattr(finding, 'severity', 'medium').lower()
            if severity in counts:
                counts[severity] += 1

        return counts

    def _determine_pass_status(self, severity_counts: Dict[str, int]) -> bool:
        """
        Determine if quality checks passed.

        In "error" mode: Fail if any critical or high severity issues exist
        In "warning" mode: Always pass (issues are warnings only)
        """
        if self.mode == "error":
            return severity_counts['critical'] == 0 and severity_counts['high'] == 0
        else:
            return True  # Warning mode always passes

    def generate_report(self, result: QualityCheckResult) -> str:
        """
        Generate comprehensive quality check report.

        Args:
            result: QualityCheckResult to format

        Returns:
            Formatted markdown report
        """
        report = ["# 🔍 CodeRabbit Quality Check Results\n"]

        # Overall status
        if result.passed:
            status_emoji = "✅"
            status_text = "PASSED"
        else:
            status_emoji = "❌"
            status_text = "FAILED"

        report.append(f"{status_emoji} **Status**: {status_text}")
        report.append(f"**Mode**: {result.mode.upper()}\n")

        # Summary statistics
        report.append("## 📊 Summary\n")
        report.append(f"- **Total Issues**: {result.total_issues}")
        report.append(f"- **Critical**: {result.critical_issues}")
        report.append(f"- **High**: {result.high_issues}")
        report.append(f"- **Medium**: {result.medium_issues}")
        report.append(f"- **Low**: {result.low_issues}\n")

        # Mode explanation
        if result.mode == "warning":
            report.append("ℹ️  **Warning Mode**: Issues reported but PR can be merged. Move to error mode after team training.\n")
        else:
            report.append("🚫 **Error Mode**: Critical and high severity issues block merge.\n")

        # Individual check reports
        if result.security_findings:
            report.append("\n---\n")
            security_report = self.security_validator.format_findings_report(
                self._group_findings_by_file(result.security_findings)
            )
            report.append(security_report)

        if result.architecture_findings:
            report.append("\n---\n")
            report.append(self._format_architecture_findings(result.architecture_findings))

        if result.test_coverage_findings:
            report.append("\n---\n")
            test_report = self.test_coverage_validator.format_findings_report(
                result.test_coverage_findings
            )
            report.append(test_report)

        if result.performance_findings:
            report.append("\n---\n")
            performance_report = self.performance_validator.format_findings_report(
                self._group_findings_by_file(result.performance_findings)
            )
            report.append(performance_report)

        if result.breaking_changes_findings:
            report.append("\n---\n")
            breaking_report = self.breaking_changes_validator.format_findings_report(
                result.breaking_changes_findings
            )
            report.append(breaking_report)

        # Override information
        if result.override_used:
            report.append("\n---\n")
            report.append("## ⚠️  Override Applied\n")
            report.append(f"**Justification**: {result.override_justification}\n")

        # Next steps
        report.append("\n---\n")
        report.append("## 📝 Next Steps\n")

        if not result.passed:
            report.append("1. Review and fix critical and high severity issues above")
            report.append("2. Update code and push new commits")
            report.append("3. Quality checks will re-run automatically")
            report.append("\n**OR**\n")
            report.append("Use override command if issues are false positives:")
            report.append("```")
            report.append("@coderabbitai ignore <check-name> --reason \"Detailed justification (min 50 chars)\"")
            report.append("```")
        else:
            if result.total_issues > 0:
                report.append("- Address warnings before merging (optional but recommended)")
            report.append("- All quality gates passed ✅")
            report.append("- PR is ready for review and merge")

        return "\n".join(report)

    def _group_findings_by_file(self, findings: List[Any]) -> Dict[str, List[Any]]:
        """Group findings by file path."""
        grouped = {}
        for finding in findings:
            file_path = finding.file_path
            if file_path not in grouped:
                grouped[file_path] = []
            grouped[file_path].append(finding)
        return grouped

    def _format_architecture_findings(self, findings: List[ArchitectureFinding]) -> str:
        """Format architecture findings."""
        report = ["## 🏗️  Architecture Check Results\n"]

        severity_counts = {
            'high': len([f for f in findings if f.severity == 'high']),
            'medium': len([f for f in findings if f.severity == 'medium']),
            'low': len([f for f in findings if f.severity == 'low']),
        }

        report.append(
            f"**{severity_counts['high']} HIGH** | "
            f"**{severity_counts['medium']} MEDIUM** | "
            f"**{severity_counts['low']} LOW** severity issues\n"
        )

        # Group by file
        by_file = self._group_findings_by_file(findings)

        for file_path, file_findings in sorted(by_file.items()):
            report.append(f"\n### 📄 {file_path}\n")

            for finding in file_findings:
                emoji = "🔴" if finding.severity == "high" else "🟡" if finding.severity == "medium" else "ℹ️"
                report.append(f"{emoji} **Line {finding.line_number}**: {finding.message}")
                report.append(f"   **Rule**: {finding.violated_rule}")
                if finding.suggested_fix:
                    report.append(f"   💡 **Fix**: {finding.suggested_fix}")
                report.append("")

        return "\n".join(report)

    def export_results_json(self, result: QualityCheckResult) -> str:
        """
        Export results as JSON for programmatic processing.

        Args:
            result: QualityCheckResult to export

        Returns:
            JSON string
        """
        # Convert findings to dictionaries
        result_dict = {
            'passed': result.passed,
            'total_issues': result.total_issues,
            'severity_counts': {
                'critical': result.critical_issues,
                'high': result.high_issues,
                'medium': result.medium_issues,
                'low': result.low_issues,
            },
            'mode': result.mode,
            'override_used': result.override_used,
            'override_justification': result.override_justification,
            'findings': {
                'security': [asdict(f) for f in result.security_findings],
                'architecture': [asdict(f) for f in result.architecture_findings],
                'test_coverage': [asdict(f) for f in result.test_coverage_findings],
                'performance': [asdict(f) for f in result.performance_findings],
                'breaking_changes': [asdict(f) for f in result.breaking_changes_findings],
            }
        }

        return json.dumps(result_dict, indent=2)
