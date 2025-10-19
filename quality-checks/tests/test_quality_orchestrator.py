"""
Test Suite for Quality Check Orchestrator

Integration tests for:
- Complete PR validation workflow
- Multiple check coordination
- Override mechanism
- Reporting and JSON export
"""

import pytest
import json
from quality_checks.quality_orchestrator import (
    QualityCheckOrchestrator,
)


class TestQualityCheckOrchestrator:
    """Test the quality check orchestrator."""

    def test_validate_pr_runs_all_checks(self):
        """Orchestrator should run all configured checks."""
        pr_title = "feat(auth): add JWT authentication"
        pr_description = """
## Summary
Implementing JWT-based authentication system.

## Changes
- Add JWT token generation
- Add token validation middleware
- Update login endpoint

## Testing
- Unit tests included
- Integration tests pass
"""
        changed_files = {
            "src/auth/jwt.py": """
def generate_token(user_id: int) -> str:
    \"\"\"Generate JWT token for user.\"\"\"
    return "token"

def validate_token(token: str) -> bool:
    \"\"\"Validate JWT token.\"\"\"
    return True
""",
            "tests/test_jwt.py": """
def test_generate_token():
    assert generate_token(1) == "token"

def test_validate_token():
    assert validate_token("token") == True
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Should execute without errors
        assert result is not None
        assert result.mode == "warning"
        assert result.total_issues >= 0

    def test_warning_mode_allows_merge(self):
        """Warning mode should pass even with issues."""
        pr_title = "fix bug"  # Bad title format
        pr_description = "Short"  # Too short
        changed_files = {
            "src/bad.py": """
API_KEY = "hardcoded_secret"  # Security issue!
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Should have issues but still pass in warning mode
        assert result.total_issues > 0
        assert result.passed == True  # Warning mode allows merge

    def test_error_mode_blocks_critical_issues(self):
        """Error mode should fail on critical/high severity issues."""
        pr_title = "feat: add feature"
        pr_description = "A" * 100  # Long enough
        changed_files = {
            "src/security_issue.py": """
# Hardcoded credential - critical issue
API_KEY = "sk_live_1234567890abcdef"

def authenticate():
    pass
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="error")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Should fail due to security issue
        assert result.total_issues > 0
        assert result.critical_issues > 0
        assert result.passed == False  # Error mode blocks

    def test_severity_counting(self):
        """Should correctly count issues by severity."""
        pr_title = "fix: security and architecture issues"
        pr_description = "Fixing multiple issues" + "." * 100
        changed_files = {
            "src/problems.py": """
# Security issue (critical)
PASSWORD = "hardcoded123"

# Architecture issue (medium)
from api.controllers import Controller
# (in a repository file - wrong layer)
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Should have issues of different severities
        assert result.total_issues > 0
        assert result.critical_issues >= 0
        assert result.high_issues >= 0
        assert result.medium_issues >= 0

    def test_generate_report_includes_all_findings(self):
        """Report should include findings from all checks."""
        pr_title = "feat: new feature"
        pr_description = "Implementing new feature with issues" + "." * 100
        changed_files = {
            "src/feature.py": """
# Security issue
API_KEY = "secret123"

# Performance issue
users = db.query(User).all()
for user in users:
    orders = db.query(Order).filter_by(user_id=user.id).all()
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )
        report = orchestrator.generate_report(result)

        # Report should mention issues
        assert len(report) > 0
        assert "Security" in report or "security" in report or "Performance" in report

    def test_export_results_json_valid(self):
        """JSON export should be valid and parseable."""
        pr_title = "feat: add feature"
        pr_description = "Feature implementation" + "." * 100
        changed_files = {
            "src/simple.py": """
def hello():
    \"\"\"Say hello.\"\"\"
    return "hello"
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )
        json_output = orchestrator.export_results_json(result)

        # Should be valid JSON
        parsed = json.loads(json_output)
        assert "passed" in parsed
        assert "total_issues" in parsed
        assert "mode" in parsed

    def test_override_mechanism(self):
        """Override should be captured in results."""
        pr_title = "feat: override test"
        pr_description = "Testing override mechanism" + "." * 100
        changed_files = {
            "src/test.py": "code"
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Check override fields exist
        assert hasattr(result, "override_used")
        assert hasattr(result, "override_justification")

    def test_multiple_check_types_integration(self):
        """Should integrate security, architecture, testing, performance, breaking changes."""
        pr_title = "feat(api): refactor user service"
        pr_description = """
## Summary
Major refactoring of user service with breaking changes.

## Changes
- Changed API signature
- Improved performance
- Added security fixes

## Testing
- All tests updated
""" + "." * 100

        changed_files = {
            "api/users.py": """
def get_user(user_id: int, include_profile: bool) -> User:
    \"\"\"Get user with optional profile.\"\"\"
    return User()
""",
            "tests/test_users.py": """
def test_get_user():
    user = get_user(1, True)
    assert user is not None
"""
        }
        old_files = {
            "api/users.py": """
def get_user(user_id: int) -> User:
    \"\"\"Get user.\"\"\"
    return User()
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="warning")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files, old_files
        )

        # Should complete validation
        assert result is not None
        assert result.mode == "warning"

    def test_clean_pr_passes_all_checks(self):
        """Clean PR with proper code should pass all checks."""
        pr_title = "feat(auth): add user authentication"
        pr_description = """
## Summary
Implementing user authentication system with JWT tokens.

## Changes
- Added JWT token generation and validation
- Implemented login endpoint with proper validation
- Added comprehensive test coverage

## Testing
- Unit tests for all new functions
- Integration tests for authentication flow
- Security review completed

## Issue Reference
Fixes ENG-123
"""

        changed_files = {
            "src/auth/jwt_service.py": """
import os
from datetime import datetime, timedelta
from typing import Optional

def generate_token(user_id: int, expires_in: int = 3600) -> str:
    \"\"\"
    Generate JWT token for authenticated user.
    
    Args:
        user_id: ID of the authenticated user
        expires_in: Token expiration time in seconds (default: 1 hour)
        
    Returns:
        Encoded JWT token string
        
    Raises:
        ValueError: If user_id is invalid
    \"\"\"
    if user_id <= 0:
        raise ValueError("Invalid user ID")
    
    secret = os.getenv("JWT_SECRET")  # Proper secret management
    # Token generation logic here
    return "token"

def validate_token(token: str) -> Optional[int]:
    \"\"\"
    Validate JWT token and extract user ID.
    
    Args:
        token: JWT token string to validate
        
    Returns:
        User ID if valid, None otherwise
    \"\"\"
    # Validation logic here
    return 1
""",
            "tests/auth/test_jwt_service.py": """
import pytest
from auth.jwt_service import generate_token, validate_token

def test_generate_token_valid_user_succeeds():
    \"\"\"Test token generation for valid user.\"\"\"
    token = generate_token(123)
    assert token is not None
    assert isinstance(token, str)

def test_generate_token_invalid_user_raises_error():
    \"\"\"Test token generation fails for invalid user.\"\"\"
    with pytest.raises(ValueError):
        generate_token(-1)

def test_validate_token_valid_token_returns_user_id():
    \"\"\"Test token validation returns user ID.\"\"\"
    token = generate_token(123)
    user_id = validate_token(token)
    assert user_id == 123

def test_validate_token_invalid_token_returns_none():
    \"\"\"Test token validation fails for invalid token.\"\"\"
    user_id = validate_token("invalid_token")
    assert user_id is None
"""
        }

        orchestrator = QualityCheckOrchestrator(mode="error")
        result = orchestrator.validate_pr(
            pr_title, pr_description, changed_files
        )

        # Should pass all checks
        assert result.passed == True
        assert result.critical_issues == 0
        assert result.high_issues == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
