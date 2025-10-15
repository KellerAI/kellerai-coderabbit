"""
Tests for security quality checks.

Task 11.2: Security Validation Custom Check - Testing
"""

import pytest
from quality_checks.security_checks import (
    HardcodedCredentialsCheck,
    SQLInjectionCheck,
    SensitiveDataLoggingCheck,
    UnsafeDeserializationCheck,
    SecurityValidator,
)


class TestHardcodedCredentialsCheck:
    """Test hardcoded credentials detection."""

    def test_detects_api_key(self):
        """Test detection of hardcoded API keys."""
        code = '''
        API_KEY = "sk-1234567890abcdef"
        api_key = "live_1234567890"
        '''
        checker = HardcodedCredentialsCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 2
        assert any("API key" in f.message for f in findings)

    def test_detects_password(self):
        """Test detection of hardcoded passwords."""
        code = '''
        password = "my_secret_pass"
        DB_PASSWORD = "super_secret"
        '''
        checker = HardcodedCredentialsCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 2
        assert any("Password" in f.message or "password" in f.message.lower() for f in findings)

    def test_detects_aws_credentials(self):
        """Test detection of AWS credentials."""
        code = '''
        aws_access_key_id = "AKIA1234567890"
        aws_secret_access_key = "abcdef1234567890"
        '''
        checker = HardcodedCredentialsCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 2
        assert any("AWS" in f.message for f in findings)

    def test_ignores_test_data(self):
        """Test that test data is ignored."""
        code = '''
        test_api_key = "test_key_12345"
        example_password = "example_pass"
        mock_token = "mock_token_xxxxx"
        '''
        checker = HardcodedCredentialsCheck()
        findings = checker.check("test.py", code)

        # Should ignore all of these (test/example/mock patterns)
        assert len(findings) == 0

    def test_ignores_env_var_usage(self):
        """Test that environment variable usage is not flagged."""
        code = '''
        import os
        API_KEY = os.getenv("API_KEY")
        password = os.environ.get("PASSWORD")
        '''
        checker = HardcodedCredentialsCheck()
        findings = checker.check("test.py", code)

        assert len(findings) == 0


class TestSQLInjectionCheck:
    """Test SQL injection detection."""

    def test_detects_f_string_in_query(self):
        """Test detection of f-strings in SQL queries."""
        code = '''
        user_id = request.args.get('id')
        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        '''
        checker = SQLInjectionCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1
        assert any("SQL injection" in f.message for f in findings)

    def test_detects_string_format_in_query(self):
        """Test detection of .format() in SQL queries."""
        code = '''
        query = "SELECT * FROM users WHERE email = '{}'".format(user_email)
        cursor.execute(query)
        '''
        checker = SQLInjectionCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1

    def test_allows_parameterized_queries(self):
        """Test that parameterized queries are not flagged."""
        code = '''
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        '''
        checker = SQLInjectionCheck()
        findings = checker.check("test.py", code)

        # Parameterized queries should not be flagged
        assert len(findings) == 0


class TestSensitiveDataLoggingCheck:
    """Test sensitive data logging detection."""

    def test_detects_password_logging(self):
        """Test detection of password logging."""
        code = '''
        logger.info(f"User password: {user.password}")
        log.debug(f"Credentials: {password}")
        '''
        checker = SensitiveDataLoggingCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 2
        assert any("password" in f.message.lower() for f in findings)

    def test_detects_token_logging(self):
        """Test detection of token logging."""
        code = '''
        logger.info(f"Auth token: {auth_token}")
        '''
        checker = SensitiveDataLoggingCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1
        assert any("token" in f.message.lower() for f in findings)

    def test_detects_pii_logging(self):
        """Test detection of PII logging."""
        code = '''
        logger.debug(f"User SSN: {ssn}")
        log.info(f"Credit card: {credit_card_number}")
        '''
        checker = SensitiveDataLoggingCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 2


class TestUnsafeDeserializationCheck:
    """Test unsafe deserialization detection."""

    def test_detects_pickle_loads(self):
        """Test detection of pickle.loads."""
        code = '''
        import pickle
        data = pickle.loads(untrusted_data)
        '''
        checker = UnsafeDeserializationCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1
        assert any("pickle" in f.message.lower() for f in findings)

    def test_detects_eval(self):
        """Test detection of eval()."""
        code = '''
        result = eval(user_input)
        '''
        checker = UnsafeDeserializationCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1
        assert any("eval" in f.message.lower() for f in findings)

    def test_detects_unsafe_yaml_load(self):
        """Test detection of yaml.load without Loader."""
        code = '''
        import yaml
        data = yaml.load(file_content)
        '''
        checker = UnsafeDeserializationCheck()
        findings = checker.check("test.py", code)

        assert len(findings) >= 1


class TestSecurityValidator:
    """Test the main security validator."""

    def test_validates_multiple_issues(self):
        """Test validation of file with multiple security issues."""
        code = '''
        API_KEY = "sk-12345"
        password = "secret123"

        cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
        logger.info(f"User password: {password}")
        data = pickle.loads(untrusted)
        '''

        validator = SecurityValidator()
        findings = validator.validate_file("test.py", code)

        # Should find multiple issues
        assert len(findings) >= 5

    def test_generates_report(self):
        """Test report generation."""
        code = '''
        API_KEY = "sk-12345"
        '''

        validator = SecurityValidator()
        results = validator.validate_pr_changes({"test.py": code})
        report = validator.format_findings_report(results)

        assert "Security Check Results" in report
        assert "CRITICAL" in report
        assert "test.py" in report
