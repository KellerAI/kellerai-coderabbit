"""
Test Suite for Test Coverage Checks

Tests for:
- New functions have corresponding tests
- Bug fix regression tests
- Test quality validation
"""

import pytest
from quality_checks.test_coverage_checks import (
    TestCoverageValidator,
    NewFunctionsHaveTestsCheck,
    BugFixRegressionTestCheck,
    TestQualityCheck,
    TestCoverageFinding,
)


class TestNewFunctionsHaveTestsCheck:
    """Test new function coverage validation."""

    def test_new_function_without_test_fails(self):
        """New function without test should fail."""
        changed_files = {
            "src/services/payment.py": """
def process_payment(amount: float) -> bool:
    \"\"\"Process payment transaction.\"\"\"
    return True
"""
        }
        test_files = {}

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        assert len(findings) > 0
        assert any("process_payment" in f.function_name for f in findings)
        assert any("test" in f.message.lower() for f in findings)

    def test_new_function_with_test_passes(self):
        """New function with corresponding test should pass."""
        changed_files = {
            "src/services/payment.py": """
def process_payment(amount: float) -> bool:
    \"\"\"Process payment transaction.\"\"\"
    return True
"""
        }
        test_files = {
            "tests/services/test_payment.py": """
def test_process_payment_valid_amount_succeeds():
    assert process_payment(100.0) == True

def test_process_payment_zero_amount_fails():
    assert process_payment(0) == False
"""
        }

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        # Should pass - test exists
        assert len(findings) == 0

    def test_private_function_skipped(self):
        """Private functions (_prefix) should not require tests."""
        changed_files = {
            "src/services/payment.py": """
def _internal_calculation(amount: float) -> float:
    return amount * 1.1
"""
        }
        test_files = {}

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        # Should skip private functions
        assert len(findings) == 0

    def test_test_file_itself_skipped(self):
        """Test files themselves should not require tests."""
        changed_files = {
            "tests/test_payment.py": """
def test_something():
    pass
"""
        }
        test_files = {}

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        # Should skip test files
        assert len(findings) == 0

    def test_init_file_skipped(self):
        """__init__.py files should not require tests."""
        changed_files = {
            "src/__init__.py": """
def helper_function():
    pass
"""
        }
        test_files = {}

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        # Should skip __init__ files
        assert len(findings) == 0

    def test_multiple_functions_some_missing_tests(self):
        """Should detect which functions are missing tests."""
        changed_files = {
            "src/calculator.py": """
def add(a: int, b: int) -> int:
    return a + b

def subtract(a: int, b: int) -> int:
    return a - b

def multiply(a: int, b: int) -> int:
    return a * b
"""
        }
        test_files = {
            "tests/test_calculator.py": """
def test_add():
    assert add(2, 3) == 5

def test_multiply():
    assert multiply(2, 3) == 6
"""
        }

        check = NewFunctionsHaveTestsCheck()
        findings = check.check(changed_files, test_files)

        # Should find subtract missing test
        assert len(findings) == 1
        assert findings[0].function_name == "subtract"


class TestBugFixRegressionTestCheck:
    """Test bug fix regression test validation."""

    def test_bug_fix_pr_without_tests_fails(self):
        """Bug fix PR without new tests should fail."""
        pr_title = "fix: resolve memory leak in cache"
        pr_description = "Fixed memory leak by clearing cache properly"
        changed_files = {
            "src/cache.py": "# Fixed code"
        }

        check = BugFixRegressionTestCheck()
        findings = check.check(pr_title, pr_description, changed_files)

        assert len(findings) > 0
        assert any("regression" in f.message.lower() for f in findings)

    def test_bug_fix_pr_with_tests_passes(self):
        """Bug fix PR with regression tests should pass."""
        pr_title = "fix: resolve memory leak in cache"
        pr_description = "Fixed memory leak by clearing cache properly"
        changed_files = {
            "src/cache.py": "# Fixed code",
            "tests/test_cache.py": """
def test_cache_clears_properly():
    # Regression test for memory leak
    pass
"""
        }

        check = BugFixRegressionTestCheck()
        findings = check.check(pr_title, pr_description, changed_files)

        # Should pass - test file included
        assert len(findings) == 0

    def test_feature_pr_without_tests_passes(self):
        """Feature PR without 'fix' keyword should not require regression test."""
        pr_title = "feat: add new payment method"
        pr_description = "Added credit card payment support"
        changed_files = {
            "src/payment.py": "# New code"
        }

        check = BugFixRegressionTestCheck()
        findings = check.check(pr_title, pr_description, changed_files)

        # Should pass - not a bug fix
        assert len(findings) == 0

    def test_bug_keyword_in_description_detected(self):
        """Bug fix mentioned in description should require tests."""
        pr_title = "Update payment processing"
        pr_description = "This PR fixes a bug in the payment validation logic"
        changed_files = {
            "src/payment.py": "# Fixed code"
        }

        check = BugFixRegressionTestCheck()
        findings = check.check(pr_title, pr_description, changed_files)

        assert len(findings) > 0

    def test_modified_test_file_counts(self):
        """Modified existing test file should count as adding tests."""
        pr_title = "fix: validation error"
        pr_description = "Fixed validation bug"
        changed_files = {
            "src/validator.py": "# Fixed code",
            "tests/test_validator.py": "# Added regression test"
        }

        check = BugFixRegressionTestCheck()
        findings = check.check(pr_title, pr_description, changed_files)

        # Should pass - test file modified
        assert len(findings) == 0


class TestTestQualityCheck:
    """Test quality validation."""

    def test_test_without_assertions_fails(self):
        """Test without assertions should fail."""
        test_files = {
            "tests/test_user.py": """
def test_create_user():
    user = create_user("test")
    # No assertion!
"""
        }

        check = TestQualityCheck()
        findings = check.check(test_files)

        assert len(findings) > 0
        assert any("assertion" in f.message.lower() for f in findings)

    def test_test_with_assertions_passes(self):
        """Test with proper assertions should pass."""
        test_files = {
            "tests/test_user.py": """
def test_create_user():
    user = create_user("test")
    assert user.name == "test"
    assert user.is_active == True
"""
        }

        check = TestQualityCheck()
        findings = check.check(test_files)

        # Should pass - has assertions
        assert len(findings) == 0

    def test_pytest_raises_counts_as_assertion(self):
        """pytest.raises should count as assertion."""
        test_files = {
            "tests/test_validator.py": """
def test_invalid_input_raises_error():
    with pytest.raises(ValueError):
        validate_input("")
"""
        }

        check = TestQualityCheck()
        findings = check.check(test_files)

        # Should pass - pytest.raises is valid
        assert len(findings) == 0

    def test_empty_test_file_skipped(self):
        """Empty or import-only test files should be skipped."""
        test_files = {
            "tests/__init__.py": "",
            "tests/conftest.py": "import pytest"
        }

        check = TestQualityCheck()
        findings = check.check(test_files)

        # Should not flag special files
        assert len(findings) == 0


class TestTestCoverageValidator:
    """Test the main test coverage validator."""

    def test_validate_pr_runs_all_checks(self):
        """Validator should run all applicable checks."""
        pr_title = "fix: payment bug"
        pr_description = "Fixed payment processing bug"
        changed_files = {
            "src/payment.py": """
def process_payment(amount):
    return True
""",
            # No test file!
        }

        validator = TestCoverageValidator()
        findings = validator.validate_pr(pr_title, pr_description, changed_files)

        # Should have findings from multiple checks
        assert len(findings) > 0

    def test_validate_pr_complete_coverage_passes(self):
        """PR with complete test coverage should pass."""
        pr_title = "fix: validation bug"
        pr_description = "Fixed validation logic"
        changed_files = {
            "src/validator.py": """
def validate_email(email: str) -> bool:
    return '@' in email
""",
            "tests/test_validator.py": """
def test_validate_email_valid():
    assert validate_email("test@example.com") == True

def test_validate_email_invalid():
    assert validate_email("invalid") == False
"""
        }

        validator = TestCoverageValidator()
        findings = validator.validate_pr(pr_title, pr_description, changed_files)

        # Should pass - complete coverage
        assert len(findings) == 0

    def test_format_findings_report_includes_details(self):
        """Report should include clear findings."""
        findings = [
            TestCoverageFinding(
                check_name="new_functions_tests",
                severity="medium",
                file_path="src/payment.py",
                function_name="process_payment",
                line_number=10,
                message="No test found for new function",
                suggested_fix="Create tests/test_payment.py with test_process_payment"
            )
        ]

        validator = TestCoverageValidator()
        report = validator.format_findings_report(findings)

        assert "process_payment" in report
        assert "src/payment.py" in report
        assert "test_payment.py" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
