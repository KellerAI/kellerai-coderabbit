"""
Breaking changes quality checks for CodeRabbit.

This module implements checks to detect and require documentation of:
- API signature changes
- Removed public methods/classes
- Changed return types
- Deprecated features
- Database schema changes

Task 11.4: Breaking Changes and Performance Checks
"""

import re
import ast
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class BreakingChangeFinding:
    """Represents a breaking change finding."""
    check_name: str
    severity: str
    file_path: str
    line_number: int
    change_type: str
    element_name: str
    message: str
    requires_changelog: bool = True
    suggested_changelog_entry: str = ""


class APISignatureChangeCheck:
    """Detect changes to public API signatures."""

    def check(
        self,
        file_path: str,
        old_content: Optional[str],
        new_content: str
    ) -> List[BreakingChangeFinding]:
        """
        Check for API signature changes.

        Args:
            file_path: Path to the file being checked
            old_content: Previous version of the file (None if new file)
            new_content: New version of the file

        Returns:
            List of breaking change findings
        """
        findings = []

        # Only check API files
        path_parts = Path(file_path).parts
        if not ('api' in path_parts or 'controllers' in path_parts):
            return findings

        if old_content is None:
            return findings  # New file, no breaking changes

        # Extract function signatures
        old_signatures = self._extract_signatures(old_content)
        new_signatures = self._extract_signatures(new_content)

        # Check for modified signatures
        for func_name, old_sig in old_signatures.items():
            if func_name in new_signatures:
                new_sig = new_signatures[func_name]
                if old_sig != new_sig:
                    findings.append(BreakingChangeFinding(
                        check_name="api_signature_changes",
                        severity="high",
                        file_path=file_path,
                        line_number=new_sig['line'],
                        change_type="modified",
                        element_name=func_name,
                        message=f"API signature changed for '{func_name}'",
                        requires_changelog=True,
                        suggested_changelog_entry=f"- **CHANGED**: `{func_name}` signature modified. Old: {old_sig['signature']}, New: {new_sig['signature']}"
                    ))

        # Check for removed functions
        removed_functions = set(old_signatures.keys()) - set(new_signatures.keys())
        for func_name in removed_functions:
            findings.append(BreakingChangeFinding(
                check_name="api_signature_changes",
                severity="critical",
                file_path=file_path,
                line_number=1,
                change_type="deleted",
                element_name=func_name,
                message=f"Public API function '{func_name}' was removed",
                requires_changelog=True,
                suggested_changelog_entry=f"- **REMOVED**: `{func_name}` (BREAKING CHANGE)"
            ))

        return findings

    def _extract_signatures(self, content: str) -> Dict[str, Dict]:
        """Extract function signatures from Python code."""
        signatures = {}

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Only track public functions (not starting with _)
                    if not node.name.startswith('_'):
                        # Extract parameter names and types
                        params = []
                        for arg in node.args.args:
                            param_str = arg.arg
                            if arg.annotation:
                                param_str += f": {ast.unparse(arg.annotation)}"
                            params.append(param_str)

                        # Extract return type
                        return_type = ""
                        if node.returns:
                            return_type = f" -> {ast.unparse(node.returns)}"

                        signature = f"({', '.join(params)}){return_type}"

                        signatures[node.name] = {
                            'signature': signature,
                            'line': node.lineno,
                            'params': params,
                            'return_type': return_type,
                        }
        except SyntaxError:
            pass  # Can't parse, skip

        return signatures


class RemovedPublicMethodsCheck:
    """Detect removal of public methods and classes."""

    def check(
        self,
        file_path: str,
        old_content: Optional[str],
        new_content: Optional[str]
    ) -> List[BreakingChangeFinding]:
        """
        Check for removed public methods and classes.

        Args:
            file_path: Path to the file being checked
            old_content: Previous version of the file
            new_content: New version of the file (None if deleted)

        Returns:
            List of breaking change findings
        """
        findings = []

        # File was deleted entirely
        if old_content and new_content is None:
            public_elements = self._extract_public_elements(old_content)
            if public_elements['classes'] or public_elements['functions']:
                findings.append(BreakingChangeFinding(
                    check_name="removed_public_methods",
                    severity="critical",
                    file_path=file_path,
                    line_number=1,
                    change_type="deleted_file",
                    element_name=file_path,
                    message=f"File with {len(public_elements['classes'])} public classes and {len(public_elements['functions'])} public functions was deleted",
                    requires_changelog=True,
                    suggested_changelog_entry=f"- **BREAKING CHANGE**: Removed {file_path} with public APIs"
                ))
            return findings

        if old_content is None or new_content is None:
            return findings

        # Extract public elements
        old_elements = self._extract_public_elements(old_content)
        new_elements = self._extract_public_elements(new_content)

        # Check for removed classes
        removed_classes = set(old_elements['classes']) - set(new_elements['classes'])
        for class_name in removed_classes:
            findings.append(BreakingChangeFinding(
                check_name="removed_public_methods",
                severity="critical",
                file_path=file_path,
                line_number=1,
                change_type="deleted_class",
                element_name=class_name,
                message=f"Public class '{class_name}' was removed",
                requires_changelog=True,
                suggested_changelog_entry=f"- **BREAKING CHANGE**: Removed class `{class_name}`"
            ))

        # Check for removed functions
        removed_functions = set(old_elements['functions']) - set(new_elements['functions'])
        for func_name in removed_functions:
            findings.append(BreakingChangeFinding(
                check_name="removed_public_methods",
                severity="critical",
                file_path=file_path,
                line_number=1,
                change_type="deleted_function",
                element_name=func_name,
                message=f"Public function '{func_name}' was removed",
                requires_changelog=True,
                suggested_changelog_entry=f"- **BREAKING CHANGE**: Removed function `{func_name}`"
            ))

        return findings

    def _extract_public_elements(self, content: str) -> Dict[str, Set[str]]:
        """Extract public classes and functions from Python code."""
        elements = {
            'classes': set(),
            'functions': set(),
        }

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Public classes start with capital letter, not _
                    if node.name[0].isupper() and not node.name.startswith('_'):
                        elements['classes'].add(node.name)
                elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Public functions don't start with _
                    if not node.name.startswith('_'):
                        elements['functions'].add(node.name)
        except SyntaxError:
            pass

        return elements


class ChangelogRequirementCheck:
    """Check if CHANGELOG.md is updated for breaking changes."""

    def check(
        self,
        changed_files: Dict[str, str],
        breaking_changes: List[BreakingChangeFinding]
    ) -> List[BreakingChangeFinding]:
        """
        Check if CHANGELOG.md exists and is updated.

        Args:
            changed_files: All changed files in the PR
            breaking_changes: List of detected breaking changes

        Returns:
            List of findings about missing CHANGELOG updates
        """
        findings = []

        # If no breaking changes, no CHANGELOG needed
        if not breaking_changes:
            return findings

        # Check if CHANGELOG.md exists in changed files
        import os
        has_changelog = any(os.path.basename(path) == 'CHANGELOG.md' for path in changed_files.keys())

        if not has_changelog:
            findings.append(BreakingChangeFinding(
                check_name="changelog_required",
                severity="critical",
                file_path="CHANGELOG.md",
                line_number=1,
                change_type="missing_changelog",
                element_name="CHANGELOG.md",
                message=f"Breaking changes detected ({len(breaking_changes)} issues) but CHANGELOG.md not updated",
                requires_changelog=True,
                suggested_changelog_entry=self._generate_changelog_template(breaking_changes)
            ))
        else:
            # Verify CHANGELOG has proper format
            import os
            changelog_content = next(
                (content for path, content in changed_files.items() if os.path.basename(path) == 'CHANGELOG.md'),
                None
            )

            if changelog_content:
                if not self._has_proper_changelog_format(changelog_content):
                    findings.append(BreakingChangeFinding(
                        check_name="changelog_format",
                        severity="medium",
                        file_path="CHANGELOG.md",
                        line_number=1,
                        change_type="invalid_format",
                        element_name="CHANGELOG.md",
                        message="CHANGELOG.md does not follow proper format (should have ## [Unreleased] or ## [version] sections)",
                        requires_changelog=True,
                        suggested_changelog_entry="Add section: ## [Unreleased] or ## [X.Y.Z] with ### BREAKING CHANGES subsection"
                    ))

        return findings

    def _has_proper_changelog_format(self, content: str) -> bool:
        """Check if CHANGELOG has proper Keep a Changelog format."""
        # Check for version headers
        version_pattern = r'## \[(Unreleased|\d+\.\d+\.\d+)\]'
        return bool(re.search(version_pattern, content))

    def _generate_changelog_template(self, breaking_changes: List[BreakingChangeFinding]) -> str:
        """Generate CHANGELOG template from breaking changes."""
        template = [
            "## [Unreleased]",
            "",
            "### BREAKING CHANGES",
            "",
        ]

        for change in breaking_changes:
            if change.suggested_changelog_entry:
                template.append(change.suggested_changelog_entry)

        return "\n".join(template)


class DatabaseSchemaChangeCheck:
    """Detect database schema changes that might be breaking."""

    SCHEMA_CHANGE_PATTERNS = [
        (r'Column\([^)]*nullable=False', 'non_nullable_column', 'Adding non-nullable column requires default value or migration'),
        (r'drop_column|remove_column', 'removed_column', 'Removing column is a breaking change'),
        (r'alter_column.*type', 'changed_column_type', 'Changing column type may break existing code'),
        (r'drop_table|remove_table', 'removed_table', 'Removing table is a breaking change'),
    ]

    def check(self, file_path: str, content: str) -> List[BreakingChangeFinding]:
        """
        Check for database schema changes.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of breaking change findings
        """
        findings = []

        # Only check migration files and model files
        path_parts = Path(file_path).parts
        if not ('migrations' in path_parts or 'models' in path_parts):
            return findings

        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, change_type, message in self.SCHEMA_CHANGE_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(BreakingChangeFinding(
                        check_name="database_schema_changes",
                        severity="high",
                        file_path=file_path,
                        line_number=line_num,
                        change_type=change_type,
                        element_name=change_type,
                        message=message,
                        requires_changelog=True,
                        suggested_changelog_entry=f"- **BREAKING CHANGE**: {message}"
                    ))

        return findings


class BreakingChangesValidator:
    """Main breaking changes validator."""

    def __init__(self):
        """Initialize breaking changes checks."""
        self.api_signature_check = APISignatureChangeCheck()
        self.removed_methods_check = RemovedPublicMethodsCheck()
        self.changelog_check = ChangelogRequirementCheck()
        self.schema_change_check = DatabaseSchemaChangeCheck()

    def validate_pr(
        self,
        changed_files: Dict[str, str],
        old_files: Dict[str, Optional[str]]
    ) -> List[BreakingChangeFinding]:
        """
        Validate breaking changes for a pull request.

        Args:
            changed_files: New/modified files (path -> content)
            old_files: Previous versions of files (path -> content or None)

        Returns:
            List of all breaking change findings
        """
        all_findings = []

        # Run per-file checks
        for file_path, new_content in changed_files.items():
            old_content = old_files.get(file_path)

            # API signature changes
            sig_findings = self.api_signature_check.check(file_path, old_content, new_content)
            all_findings.extend(sig_findings)

            # Removed public methods
            removal_findings = self.removed_methods_check.check(file_path, old_content, new_content)
            all_findings.extend(removal_findings)

            # Database schema changes
            schema_findings = self.schema_change_check.check(file_path, new_content)
            all_findings.extend(schema_findings)

        # Check for CHANGELOG updates
        changelog_findings = self.changelog_check.check(changed_files, all_findings)
        all_findings.extend(changelog_findings)

        return all_findings

    def format_findings_report(self, findings: List[BreakingChangeFinding]) -> str:
        """
        Format breaking changes findings as a readable report.

        Args:
            findings: List of breaking change findings

        Returns:
            Formatted report string
        """
        if not findings:
            return "✅ No breaking changes detected."

        report = ["## 💥 Breaking Changes Check Results\n"]

        critical_count = len([f for f in findings if f.severity == "critical"])
        high_count = len([f for f in findings if f.severity == "high"])

        report.append(f"**{critical_count} CRITICAL** | **{high_count} HIGH** severity issues\n")
        report.append("⚠️  **All breaking changes must be documented in CHANGELOG.md**\n")

        # Group by change type
        by_type = {}
        for finding in findings:
            if finding.change_type not in by_type:
                by_type[finding.change_type] = []
            by_type[finding.change_type].append(finding)

        for change_type, type_findings in by_type.items():
            report.append(f"\n### {change_type.replace('_', ' ').title()}\n")

            for finding in type_findings:
                emoji = "🔴" if finding.severity == "critical" else "🟡"
                report.append(f"{emoji} **{finding.file_path}** - {finding.element_name}")
                report.append(f"   {finding.message}")

                if finding.suggested_changelog_entry:
                    report.append("   ```markdown")
                    report.append(f"   {finding.suggested_changelog_entry}")
                    report.append("   ```")
                report.append("")

        return "\n".join(report)
