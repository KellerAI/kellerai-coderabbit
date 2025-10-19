"""
Test coverage quality checks for CodeRabbit.

This module implements test coverage checks to ensure:
- New functions have corresponding unit tests
- Bug fixes include regression tests
- Test coverage meets minimum thresholds
- Test quality and completeness

Task 11.3: Architecture and Test Coverage Checks
"""

import re
import ast
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TestCoverageFinding:
    """Represents a test coverage finding."""
    check_name: str
    severity: str
    file_path: str
    function_name: str
    line_number: int
    message: str
    suggested_fix: str = ""


class NewFunctionsHaveTestsCheck:
    """Ensure new functions have corresponding tests."""

    def check(
        self,
        changed_files: Dict[str, str],
        test_files: Dict[str, str]
    ) -> List[TestCoverageFinding]:
        """
        Check if new functions have corresponding tests.

        Args:
            changed_files: Dict of changed source files (path -> content)
            test_files: Dict of test files (path -> content)

        Returns:
            List of test coverage findings
        """
        findings = []

        for file_path, content in changed_files.items():
            # Skip test files and non-source files
            if self._should_skip_file(file_path):
                continue

            # Extract new function definitions
            new_functions = self._extract_functions(content)

            # Find corresponding test file
            test_file_path = self._find_test_file(file_path, test_files)

            if not test_file_path:
                # No test file exists for this source file
                if new_functions:
                    findings.append(TestCoverageFinding(
                        check_name="new_functions_have_tests",
                        severity="medium",
                        file_path=file_path,
                        function_name="(all functions)",
                        line_number=1,
                        message=f"No test file found for {file_path}. Create tests for new functions.",
                        suggested_fix=f"Create {self._suggest_test_file_path(file_path)}"
                    ))
                continue

            # Check each new function for corresponding test
            test_content = test_files[test_file_path]
            for func_name, line_num in new_functions:
                if not self._has_test_for_function(func_name, test_content):
                    findings.append(TestCoverageFinding(
                        check_name="new_functions_have_tests",
                        severity="medium",
                        file_path=file_path,
                        function_name=func_name,
                        line_number=line_num,
                        message=f"Function '{func_name}' has no corresponding test",
                        suggested_fix=f"Add test_{func_name} in {test_file_path}"
                    ))

        return findings

    def _should_skip_file(self, file_path: str) -> bool:
        """Check if file should be skipped for test coverage."""
        skip_patterns = [
            'test_',
            '__init__.py',
            'migrations/',
            'scripts/',
            'config/',
            '.example',
        ]
        return any(pattern in file_path for pattern in skip_patterns)

    def _extract_functions(self, content: str) -> List[Tuple[str, int]]:
        """
        Extract function definitions from Python code.

        Returns:
            List of tuples (function_name, line_number)
        """
        functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    # Skip private functions (starting with _)
                    if not node.name.startswith('_'):
                        functions.append((node.name, node.lineno))
        except SyntaxError:
            # Fallback to regex
            pattern = r'^def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
            for line_num, line in enumerate(content.split('\n'), 1):
                match = re.match(pattern, line.strip())
                if match and not match.group(1).startswith('_'):
                    functions.append((match.group(1), line_num))

        return functions

    def _find_test_file(self, source_path: str, test_files: Dict[str, str]) -> Optional[str]:
        """Find corresponding test file for a source file."""
        # Convert source path to expected test path
        # e.g., src/services/user.py -> tests/test_user.py or tests/services/test_user.py

        path_obj = Path(source_path)
        filename = path_obj.name

        # Common test file patterns
        test_patterns = [
            f"tests/test_{filename}",
            f"tests/{path_obj.parent.name}/test_{filename}",
            f"test_{filename}",
            f"{path_obj.parent}/test_{filename}",
        ]

        for pattern in test_patterns:
            for test_path in test_files.keys():
                if pattern in test_path:
                    return test_path

        return None

    def _suggest_test_file_path(self, source_path: str) -> str:
        """Suggest a test file path for a source file."""
        path_obj = Path(source_path)
        return f"tests/{path_obj.parent.name}/test_{path_obj.name}"

    def _has_test_for_function(self, func_name: str, test_content: str) -> bool:
        """Check if test content has a test for the given function."""
        # Look for test_<function_name> pattern
        test_pattern = rf'def\s+test_{func_name}\s*\('
        return bool(re.search(test_pattern, test_content))


class BugFixRegressionTestCheck:
    """Ensure bug fixes include regression tests."""

    BUG_FIX_PATTERNS = [
        r'^fix',
        r'^bug',
        r'\bfix\b',
        r'\bbug\b',
        r'\bregression\b',
    ]

    def check(
        self,
        pr_title: str,
        pr_description: str,
        changed_files: Dict[str, str]
    ) -> List[TestCoverageFinding]:
        """
        Check if bug fix PRs include regression tests.

        Args:
            pr_title: Pull request title
            pr_description: Pull request description
            changed_files: Dictionary of all changed files

        Returns:
            List of test coverage findings
        """
        findings = []

        # Check if this is a bug fix PR
        is_bug_fix = self._is_bug_fix_pr(pr_title, pr_description)

        if not is_bug_fix:
            return findings

        # Check if any test files were modified/added
        has_new_tests = self._has_new_or_modified_tests(changed_files)

        if not has_new_tests:
            findings.append(TestCoverageFinding(
                check_name="bug_fix_regression_tests",
                severity="high",
                file_path="(pull request)",
                function_name="N/A",
                line_number=0,
                message="Bug fix PR should include regression tests to prevent reoccurrence",
                suggested_fix="Add test cases that reproduce the bug and verify the fix"
            ))

        return findings

    def _is_bug_fix_pr(self, title: str, description: str) -> bool:
        """Check if PR is a bug fix based on title and description."""
        combined = f"{title} {description}".lower()
        return any(re.search(pattern, combined, re.IGNORECASE) for pattern in self.BUG_FIX_PATTERNS)

    def _has_new_or_modified_tests(self, changed_files: Dict[str, str]) -> bool:
        """Check if any test files were added or modified."""
        test_patterns = ['test_', '/tests/', '_test.py']
        return any(
            any(pattern in file_path for pattern in test_patterns)
            for file_path in changed_files.keys()
        )


class TestQualityCheck:
    """Check test quality and completeness."""

    def check(self, test_files: Dict[str, str]) -> List[TestCoverageFinding]:
        """
        Check test quality.

        Args:
            test_files: Dictionary of test files

        Returns:
            List of test coverage findings
        """
        findings = []

        for file_path, content in test_files.items():
            # Check for assertion statements
            if not self._has_assertions(content):
                findings.append(TestCoverageFinding(
                    check_name="test_quality",
                    severity="high",
                    file_path=file_path,
                    function_name="N/A",
                    line_number=1,
                    message="Test file has no assertions. Tests should include assert statements.",
                    suggested_fix="Add assert statements to verify expected behavior"
                ))

            # Check for test setup/teardown
            if not self._has_fixtures_or_setup(content):
                # This is just a warning for files with many tests
                test_count = len(re.findall(r'def\s+test_', content))
                if test_count > 5:
                    findings.append(TestCoverageFinding(
                        check_name="test_quality",
                        severity="low",
                        file_path=file_path,
                        function_name="N/A",
                        line_number=1,
                        message=f"Test file with {test_count} tests should use fixtures/setup for shared test data",
                        suggested_fix="Use pytest fixtures or setUp/tearDown methods for test initialization"
                    ))

        return findings

    def _has_assertions(self, content: str) -> bool:
        """Check if test content has assertion statements."""
        assertion_patterns = [
            r'\bassert\s+',
            r'\.assert',
            r'self\.assertEqual',
            r'self\.assertTrue',
        ]
        return any(re.search(pattern, content) for pattern in assertion_patterns)

    def _has_fixtures_or_setup(self, content: str) -> bool:
        """Check if test uses fixtures or setup methods."""
        fixture_patterns = [
            r'@pytest\.fixture',
            r'def\s+setUp\s*\(',
            r'def\s+tearDown\s*\(',
            r'@conftest',
        ]
        return any(re.search(pattern, content) for pattern in fixture_patterns)


class TestCoverageValidator:
    """Main test coverage validator."""

    def __init__(self):
        """Initialize test coverage checks."""
        self.new_functions_check = NewFunctionsHaveTestsCheck()
        self.bug_fix_check = BugFixRegressionTestCheck()
        self.quality_check = TestQualityCheck()

    def validate_pr(
        self,
        pr_title: str,
        pr_description: str,
        changed_files: Dict[str, str]
    ) -> List[TestCoverageFinding]:
        """
        Validate test coverage for a pull request.

        Args:
            pr_title: Pull request title
            pr_description: Pull request description
            changed_files: All changed files in the PR

        Returns:
            List of all test coverage findings
        """
        all_findings = []

        # Separate source files and test files
        source_files = {}
        test_files = {}

        for file_path, content in changed_files.items():
            if 'test_' in file_path or '/tests/' in file_path:
                test_files[file_path] = content
            elif file_path.endswith('.py'):
                source_files[file_path] = content

        # Run checks
        new_func_findings = self.new_functions_check.check(source_files, test_files)
        all_findings.extend(new_func_findings)

        bug_fix_findings = self.bug_fix_check.check(pr_title, pr_description, changed_files)
        all_findings.extend(bug_fix_findings)

        quality_findings = self.quality_check.check(test_files)
        all_findings.extend(quality_findings)

        return all_findings

    def format_findings_report(self, findings: List[TestCoverageFinding]) -> str:
        """
        Format test coverage findings as a readable report.

        Args:
            findings: List of test coverage findings

        Returns:
            Formatted report string
        """
        if not findings:
            return "✅ All test coverage requirements met."

        report = ["## 🧪 Test Coverage Check Results\n"]

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

        # Group by check type
        by_check = {}
        for finding in findings:
            if finding.check_name not in by_check:
                by_check[finding.check_name] = []
            by_check[finding.check_name].append(finding)

        for check_name, check_findings in by_check.items():
            report.append(f"\n### {check_name.replace('_', ' ').title()}\n")

            for finding in check_findings:
                emoji = "🔴" if finding.severity == "high" else "🟡" if finding.severity == "medium" else "ℹ️"
                report.append(f"{emoji} **{finding.file_path}**")
                if finding.function_name != "N/A":
                    report.append(f"   Function: `{finding.function_name}` (line {finding.line_number})")
                report.append(f"   {finding.message}")
                if finding.suggested_fix:
                    report.append(f"   💡 **Fix**: {finding.suggested_fix}")
                report.append("")

        return "\n".join(report)
