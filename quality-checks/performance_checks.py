"""
Performance quality checks for CodeRabbit.

This module implements performance checks to detect:
- N+1 query patterns
- Missing database indexes
- Algorithm complexity issues
- Inefficient data structures
- Memory leaks

Task 11.4: Performance and Breaking Changes Checks
"""

import re
from typing import List, Dict
from dataclasses import dataclass


@dataclass
class PerformanceFinding:
    """Represents a performance issue finding."""
    check_name: str
    severity: str
    file_path: str
    line_number: int
    line_content: str
    message: str
    impact: str
    suggested_fix: str = ""


class NPlusOneQueryCheck:
    """Detect N+1 query patterns."""

    # ORM query patterns that might indicate N+1 issues
    QUERY_PATTERNS = [
        r'\.(get|filter|query|select|find)\s*\(',
        r'\.get_object_or_404\s*\(',
        r'\.objects\.',
    ]

    # Loop patterns
    LOOP_PATTERNS = [
        r'for\s+\w+\s+in\s+',
        r'\[.*for\s+.*in\s+.*\]',  # List comprehension
    ]

    def check(self, file_path: str, content: str) -> List[PerformanceFinding]:
        """
        Check for N+1 query patterns.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of performance findings
        """
        findings = []
        lines = content.split('\n')

        # Check if file uses ORM (SQLAlchemy, Django, etc.)
        has_orm = any(
            pattern in content
            for pattern in ['sqlalchemy', 'django.db', 'peewee', 'tortoise']
        )

        if not has_orm:
            return findings

        # Look for loops with database queries inside
        for i, line in enumerate(lines):
            line_num = i + 1

            # Check if line starts a loop
            is_loop = any(re.search(pattern, line) for pattern in self.LOOP_PATTERNS)

            if is_loop:
                # Check next few lines for database queries
                look_ahead = min(20, len(lines) - i)
                for j in range(1, look_ahead):
                    next_line = lines[i + j]

                    # Check for database query
                    has_query = any(
                        re.search(pattern, next_line)
                        for pattern in self.QUERY_PATTERNS
                    )

                    if has_query:
                        findings.append(PerformanceFinding(
                            check_name="n_plus_one_queries",
                            severity="high",
                            file_path=file_path,
                            line_number=line_num,
                            line_content=line.strip(),
                            message="Potential N+1 query detected: database query inside loop",
                            impact="O(n) database queries - severe performance degradation with large datasets",
                            suggested_fix="Use eager loading: SQLAlchemy joinedload()/selectinload(), Django select_related()/prefetch_related()"
                        ))
                        break  # Only report once per loop

        return findings


class DatabaseIndexCheck:
    """Check for proper database index usage."""

    FOREIGN_KEY_PATTERNS = [
        (r'ForeignKey\s*\([^)]*\)', r'index=True|db_index=True', 'ForeignKey'),
        (r'relationship\s*\([^)]*\)', r'index=True', 'Relationship'),
    ]

    FREQUENTLY_QUERIED_PATTERNS = [
        (r'\.filter\((\w+)=', 'filter field'),
        (r'WHERE\s+(\w+)\s*=', 'WHERE clause field'),
    ]

    def check(self, file_path: str, content: str) -> List[PerformanceFinding]:
        """
        Check for missing database indexes.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of performance findings
        """
        findings = []

        # Only check model files
        if not ('models/' in file_path or 'model.py' in file_path):
            return findings

        lines = content.split('\n')

        # Check foreign keys for indexes
        for line_num, line in enumerate(lines, 1):
            for fk_pattern, index_pattern, fk_type in self.FOREIGN_KEY_PATTERNS:
                if re.search(fk_pattern, line):
                    # Check if this line or nearby lines have index=True
                    context_start = max(0, line_num - 2)
                    context_end = min(len(lines), line_num + 2)
                    context = '\n'.join(lines[context_start:context_end])

                    if not re.search(index_pattern, context):
                        findings.append(PerformanceFinding(
                            check_name="missing_database_indexes",
                            severity="medium",
                            file_path=file_path,
                            line_number=line_num,
                            line_content=line.strip(),
                            message=f"{fk_type} without database index",
                            impact="Slow query performance on joins and lookups",
                            suggested_fix=f"Add index=True or db_index=True to the {fk_type} definition"
                        ))

        return findings


class AlgorithmComplexityCheck:
    """Check for high complexity algorithms."""

    def check(self, file_path: str, content: str) -> List[PerformanceFinding]:
        """
        Check for algorithm complexity issues.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of performance findings
        """
        findings = []

        # Skip test files
        if 'test_' in file_path or '/tests/' in file_path:
            return findings

        lines = content.split('\n')

        # Detect nested loops (O(n²) or worse)
        findings.extend(self._check_nested_loops(file_path, lines))

        # Detect inefficient list operations
        findings.extend(self._check_inefficient_list_ops(file_path, lines))

        # Detect redundant computations in loops
        findings.extend(self._check_loop_invariants(file_path, lines))

        return findings

    def _check_nested_loops(self, file_path: str, lines: List[str]) -> List[PerformanceFinding]:
        """Detect nested loops."""
        findings = []
        indent_stack = []

        for line_num, line in enumerate(lines, 1):
            # Calculate indentation level
            indent = len(line) - len(line.lstrip())

            # Check if this is a for loop
            if re.match(r'\s*for\s+\w+\s+in\s+', line):
                # Pop stack if we've dedented
                while indent_stack and indent_stack[-1][1] >= indent:
                    indent_stack.pop()

                # If stack is not empty, we have a nested loop
                if indent_stack:
                    findings.append(PerformanceFinding(
                        check_name="algorithm_complexity",
                        severity="medium",
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message="Nested loops detected - potential O(n²) complexity",
                        impact="Performance degrades quadratically with input size",
                        suggested_fix="Consider using more efficient algorithms or data structures (dict, set for lookups)"
                    ))

                indent_stack.append((line_num, indent))

        return findings

    def _check_inefficient_list_ops(self, file_path: str, lines: List[str]) -> List[PerformanceFinding]:
        """Detect inefficient list operations."""
        findings = []

        inefficient_patterns = [
            (r'(\w+)\s*in\s*range\(len\((\w+)\)\)', "Use enumerate() instead of range(len())"),
            (r'(\w+)\.append\(.*\)\s*#.*loop', "Consider list comprehension for better performance"),
        ]

        for line_num, line in enumerate(lines, 1):
            for pattern, suggestion in inefficient_patterns:
                if re.search(pattern, line):
                    findings.append(PerformanceFinding(
                        check_name="algorithm_complexity",
                        severity="low",
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message="Inefficient list operation",
                        impact="Minor performance overhead",
                        suggested_fix=suggestion
                    ))

        return findings

    def _check_loop_invariants(self, file_path: str, lines: List[str]) -> List[PerformanceFinding]:
        """Detect computations that should be moved outside loops."""
        findings = []
        in_loop = False
        loop_start = 0

        function_call_pattern = r'(\w+)\s*\([^)]*\)'

        for line_num, line in enumerate(lines, 1):
            if re.match(r'\s*for\s+\w+\s+in\s+', line):
                in_loop = True
                loop_start = line_num
            elif in_loop and (not line.strip() or not line[0].isspace()):
                in_loop = False

            # Check for expensive operations in loop
            if in_loop and re.search(r'len\(\w+\)', line):
                # len() called in loop - might be invariant
                findings.append(PerformanceFinding(
                    check_name="algorithm_complexity",
                    severity="low",
                    file_path=file_path,
                    line_number=line_num,
                    line_content=line.strip(),
                    message="len() called inside loop - consider moving outside if list doesn't change",
                    impact="Repeated function calls add overhead",
                    suggested_fix="Store len() result before loop if the collection size is invariant"
                ))

        return findings


class MemoryLeakCheck:
    """Check for potential memory leak patterns."""

    LEAK_PATTERNS = [
        (r'global\s+\w+\s*=\s*\[\]', "Global mutable collection can grow unbounded"),
        (r'cache\s*=\s*\{\}', "Unbounded cache can cause memory issues"),
        (r'\.append\(.*\)\s*#.*never.*clear', "Append without clear can accumulate memory"),
    ]

    def check(self, file_path: str, content: str) -> List[PerformanceFinding]:
        """
        Check for potential memory leaks.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of performance findings
        """
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, issue in self.LEAK_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(PerformanceFinding(
                        check_name="memory_leak",
                        severity="medium",
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message=f"Potential memory leak: {issue}",
                        impact="Memory usage grows over time, causing OOM errors",
                        suggested_fix="Use LRU cache, implement size limits, or periodic cleanup"
                    ))

        return findings


class PerformanceValidator:
    """Main performance validator."""

    def __init__(self):
        """Initialize performance checks."""
        self.checks = [
            NPlusOneQueryCheck(),
            DatabaseIndexCheck(),
            AlgorithmComplexityCheck(),
            MemoryLeakCheck(),
        ]

    def validate_file(self, file_path: str, content: str) -> List[PerformanceFinding]:
        """
        Run all performance checks on a file.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of all performance findings
        """
        all_findings = []
        for check in self.checks:
            findings = check.check(file_path, content)
            all_findings.extend(findings)
        return all_findings

    def validate_pr(self, changed_files: Dict[str, str]) -> Dict[str, List[PerformanceFinding]]:
        """
        Validate performance across all changed files.

        Args:
            changed_files: Dictionary mapping file paths to contents

        Returns:
            Dictionary mapping file paths to their findings
        """
        results = {}
        for file_path, content in changed_files.items():
            findings = self.validate_file(file_path, content)
            if findings:
                results[file_path] = findings
        return results

    def format_findings_report(self, findings: Dict[str, List[PerformanceFinding]]) -> str:
        """
        Format performance findings as a readable report.

        Args:
            findings: Dictionary of findings by file path

        Returns:
            Formatted report string
        """
        if not findings:
            return "✅ No performance issues detected."

        report = ["## ⚡ Performance Check Results\n"]

        severity_counts = {
            'high': 0,
            'medium': 0,
            'low': 0,
        }

        for file_findings in findings.values():
            for finding in file_findings:
                severity_counts[finding.severity] += 1

        report.append(
            f"**{severity_counts['high']} HIGH** | "
            f"**{severity_counts['medium']} MEDIUM** | "
            f"**{severity_counts['low']} LOW** severity issues\n"
        )

        for file_path, file_findings in sorted(findings.items()):
            report.append(f"\n### 📄 {file_path}\n")

            for finding in sorted(file_findings, key=lambda f: f.line_number):
                emoji = "🔴" if finding.severity == "high" else "🟡" if finding.severity == "medium" else "ℹ️"
                report.append(f"{emoji} **Line {finding.line_number}**: {finding.message}")
                report.append("   ```python")
                report.append(f"   {finding.line_content}")
                report.append("   ```")
                report.append(f"   📊 **Impact**: {finding.impact}")
                if finding.suggested_fix:
                    report.append(f"   💡 **Fix**: {finding.suggested_fix}")
                report.append("")

        return "\n".join(report)
