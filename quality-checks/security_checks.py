"""
Security validation quality checks for CodeRabbit.

This module implements security checks to detect:
- Hardcoded credentials (API keys, passwords, tokens)
- SQL injection vulnerabilities
- Sensitive data logging (PII, credentials)
- Unsafe deserialization patterns
- Input sanitization issues

Task 11.2: Security Validation Custom Check
"""

import re
from typing import List, Dict
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Severity levels for security findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SecurityFinding:
    """Represents a security vulnerability finding."""
    check_name: str
    severity: Severity
    file_path: str
    line_number: int
    line_content: str
    message: str
    pattern_matched: str
    suggested_fix: str = ""


class HardcodedCredentialsCheck:
    """Detect hardcoded credentials in code."""

    # Pattern definitions for various credential types
    CREDENTIAL_PATTERNS = [
        # API keys
        (r'api[_-]?key\s*[=:]\s*["\'][^"\']+["\']', "API key"),
        (r'apikey\s*[=:]\s*["\'][^"\']+["\']', "API key"),

        # AWS credentials
        (r'aws[_-]?access[_-]?key[_-]?id\s*[=:]\s*["\'][^"\']+["\']', "AWS access key"),
        (r'aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*["\'][^"\']+["\']', "AWS secret key"),

        # Passwords
        (r'password\s*[=:]\s*["\'][^"\']+["\']', "Password"),
        (r'passwd\s*[=:]\s*["\'][^"\']+["\']', "Password"),
        (r'pwd\s*[=:]\s*["\'][^"\']+["\']', "Password"),

        # Tokens
        (r'token\s*[=:]\s*["\'][^"\']+["\']', "Token"),
        (r'auth[_-]?token\s*[=:]\s*["\'][^"\']+["\']', "Auth token"),
        (r'bearer\s*[=:]\s*["\'][^"\']+["\']', "Bearer token"),

        # Private keys
        (r'-----BEGIN (RSA|DSA|EC|OPENSSH) PRIVATE KEY-----', "Private key"),

        # Database credentials
        (r'db[_-]?password\s*[=:]\s*["\'][^"\']+["\']', "Database password"),
        (r'database[_-]?url\s*[=:]\s*["\'].*:[^@]+@.*["\']', "Database connection string"),

        # OAuth/JWT secrets
        (r'client[_-]?secret\s*[=:]\s*["\'][^"\']+["\']', "Client secret"),
        (r'jwt[_-]?secret\s*[=:]\s*["\'][^"\']+["\']', "JWT secret"),
    ]

    # Patterns that are safe to ignore (test data, examples)
    EXCLUDE_PATTERNS = [
        r'test[_-]?',
        r'example',
        r'sample',
        r'demo',
        r'fake',
        r'mock',
        r'placeholder',
        r'xxx+',
        r'<[^>]+>',  # Placeholder syntax
    ]

    def check(self, file_path: str, content: str) -> List[SecurityFinding]:
        """
        Check for hardcoded credentials in file content.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of security findings
        """
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip comments (basic implementation)
            if line.strip().startswith('#') or line.strip().startswith('//'):
                continue

            for pattern, cred_type in self.CREDENTIAL_PATTERNS:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Check if this is an excluded pattern (test data, etc.)
                    if self._is_excluded(match.group()):
                        continue

                    findings.append(SecurityFinding(
                        check_name="hardcoded_credentials",
                        severity=Severity.CRITICAL,
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message=f"Hardcoded {cred_type} detected. Use environment variables or AWS Secrets Manager.",
                        pattern_matched=pattern,
                        suggested_fix="Use: value = os.getenv('VARIABLE_NAME')"
                    ))

        return findings

    def _is_excluded(self, matched_text: str) -> bool:
        """Check if matched text should be excluded (test data, placeholders)."""
        for exclude_pattern in self.EXCLUDE_PATTERNS:
            if re.search(exclude_pattern, matched_text, re.IGNORECASE):
                return True
        return False


class SQLInjectionCheck:
    """Detect SQL injection vulnerabilities."""

    SQL_INJECTION_PATTERNS = [
        # String concatenation in SQL
        (r'execute\s*\(\s*["\'].*\{\}.*["\'].*\.format', "String formatting in SQL query"),
        (r'execute\s*\(\s*f["\'].*\{.*\}.*["\']', "F-string in SQL query"),
        (r'execute\s*\(\s*["\'].*%s.*["\'].*%\s*[^(]', "Old-style string formatting in SQL"),

        # Raw SQL with variables
        (r'raw\s*\(\s*f["\']', "F-string in raw SQL"),
        (r'cursor\.execute\s*\(\s*f["\']', "F-string in cursor.execute"),

        # Direct string concatenation
        (r'(SELECT|INSERT|UPDATE|DELETE).*\+\s*\w+', "String concatenation in SQL"),
    ]

    def check(self, file_path: str, content: str) -> List[SecurityFinding]:
        """
        Check for SQL injection vulnerabilities.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of security findings
        """
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, vuln_type in self.SQL_INJECTION_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        check_name="sql_injection",
                        severity=Severity.CRITICAL,
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message=f"Potential SQL injection: {vuln_type}. Use parameterized queries.",
                        pattern_matched=pattern,
                        suggested_fix="Use: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))"
                    ))

        return findings


class SensitiveDataLoggingCheck:
    """Detect logging of sensitive data."""

    SENSITIVE_PATTERNS = [
        # Credentials
        (r'log.*password', "password", Severity.HIGH),
        (r'log.*token', "authentication token", Severity.HIGH),
        (r'log.*secret', "secret", Severity.HIGH),
        (r'log.*api[_-]?key', "API key", Severity.HIGH),

        # PII
        (r'log.*ssn', "SSN", Severity.CRITICAL),
        (r'log.*social[_-]?security', "social security number", Severity.CRITICAL),
        (r'log.*credit[_-]?card', "credit card", Severity.CRITICAL),
        (r'log.*cvv', "CVV", Severity.CRITICAL),
        (r'log.*driver[_-]?license', "driver's license", Severity.HIGH),

        # Other sensitive data
        (r'log.*auth', "authentication data", Severity.MEDIUM),
        (r'log.*session', "session data", Severity.MEDIUM),
    ]

    def check(self, file_path: str, content: str) -> List[SecurityFinding]:
        """
        Check for logging of sensitive data.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of security findings
        """
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, data_type, severity in self.SENSITIVE_PATTERNS:
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(SecurityFinding(
                        check_name="sensitive_data_logging",
                        severity=severity,
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message=f"Potential logging of {data_type}. Redact sensitive fields before logging.",
                        pattern_matched=pattern,
                        suggested_fix=f"Redact {data_type} or use structured logging with field exclusion"
                    ))

        return findings


class UnsafeDeserializationCheck:
    """Detect unsafe deserialization patterns."""

    UNSAFE_PATTERNS = [
        (r'pickle\.loads?\s*\(', "pickle.load", "Use json.loads or safe serialization"),
        (r'yaml\.load\s*\([^,)]*\)', "yaml.load without Loader", "Use yaml.safe_load"),
        (r'eval\s*\(', "eval()", "Avoid eval; use ast.literal_eval for literals"),
        (r'exec\s*\(', "exec()", "Redesign to avoid dynamic code execution"),
        (r'__import__\s*\(', "__import__()", "Use importlib.import_module with validation"),
    ]

    def check(self, file_path: str, content: str) -> List[SecurityFinding]:
        """
        Check for unsafe deserialization patterns.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of security findings
        """
        findings = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, unsafe_func, suggested_fix in self.UNSAFE_PATTERNS:
                if re.search(pattern, line):
                    findings.append(SecurityFinding(
                        check_name="unsafe_deserialization",
                        severity=Severity.CRITICAL,
                        file_path=file_path,
                        line_number=line_num,
                        line_content=line.strip(),
                        message=f"Unsafe deserialization: {unsafe_func}. This allows arbitrary code execution.",
                        pattern_matched=pattern,
                        suggested_fix=suggested_fix
                    ))

        return findings


class SecurityValidator:
    """Main security validator that runs all security checks."""

    def __init__(self):
        """Initialize security checks."""
        self.checks = [
            HardcodedCredentialsCheck(),
            SQLInjectionCheck(),
            SensitiveDataLoggingCheck(),
            UnsafeDeserializationCheck(),
        ]

    def validate_file(self, file_path: str, content: str) -> List[SecurityFinding]:
        """
        Run all security checks on a file.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of all security findings from all checks
        """
        all_findings = []
        for check in self.checks:
            findings = check.check(file_path, content)
            all_findings.extend(findings)
        return all_findings

    def validate_pr_changes(self, changed_files: Dict[str, str]) -> Dict[str, List[SecurityFinding]]:
        """
        Validate all changed files in a PR.

        Args:
            changed_files: Dictionary mapping file paths to file contents

        Returns:
            Dictionary mapping file paths to their security findings
        """
        results = {}
        for file_path, content in changed_files.items():
            findings = self.validate_file(file_path, content)
            if findings:
                results[file_path] = findings
        return results

    def format_findings_report(self, findings: Dict[str, List[SecurityFinding]]) -> str:
        """
        Format security findings as a readable report.

        Args:
            findings: Dictionary of findings by file path

        Returns:
            Formatted report string
        """
        if not findings:
            return "✅ No security issues detected."

        report = ["## 🔒 Security Check Results\n"]

        total_critical = sum(
            len([f for f in file_findings if f.severity == Severity.CRITICAL])
            for file_findings in findings.values()
        )
        total_high = sum(
            len([f for f in file_findings if f.severity == Severity.HIGH])
            for file_findings in findings.values()
        )

        report.append(f"**{total_critical} CRITICAL** | **{total_high} HIGH** severity issues found\n")

        for file_path, file_findings in sorted(findings.items()):
            report.append(f"\n### 📄 {file_path}\n")

            for finding in sorted(file_findings, key=lambda f: f.severity.value):
                emoji = "🔴" if finding.severity == Severity.CRITICAL else "🟡"
                report.append(f"{emoji} **Line {finding.line_number}**: {finding.message}")
                report.append("   ```")
                report.append(f"   {finding.line_content}")
                report.append("   ```")
                report.append(f"   💡 **Fix**: {finding.suggested_fix}\n")

        return "\n".join(report)
