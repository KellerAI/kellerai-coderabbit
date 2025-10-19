"""
Test Suite for Breaking Changes Checks

Tests for:
- API signature changes detection
- Removed public methods/classes
- CHANGELOG requirement validation
- Database schema change detection
"""

import pytest
from quality_checks.breaking_changes_checks import (
    BreakingChangesValidator,
    APISignatureChangeCheck,
    RemovedPublicMethodsCheck,
    ChangelogRequirementCheck,
    DatabaseSchemaChangeCheck,
    BreakingChangeFinding,
)


class TestAPISignatureChangeCheck:
    """Test API signature change detection."""

    def test_added_parameter_detected(self):
        """Adding required parameter is breaking change."""
        old_code = """
def authenticate(username: str) -> Token:
    pass
"""
        new_code = """
def authenticate(username: str, email: str) -> Token:
    pass
"""
        check = APISignatureChangeCheck()
        findings = check.check("api/auth.py", old_code, new_code)

        assert len(findings) > 0
        assert any("parameter" in f.message.lower() for f in findings)
        assert findings[0].requires_changelog

    def test_added_optional_parameter_not_breaking(self):
        """Adding optional parameter with default is not breaking."""
        old_code = """
def authenticate(username: str) -> Token:
    pass
"""
        new_code = """
def authenticate(username: str, remember_me: bool = False) -> Token:
    pass
"""
        check = APISignatureChangeCheck()
        findings = check.check("api/auth.py", old_code, new_code)

        # Should pass - optional parameter
        breaking_findings = [f for f in findings if f.severity == "high"]
        assert len(breaking_findings) == 0

    def test_changed_return_type_detected(self):
        """Changing return type is breaking change."""
        old_code = """
def get_user(user_id: int) -> User:
    pass
"""
        new_code = """
def get_user(user_id: int) -> Optional[User]:
    pass
"""
        check = APISignatureChangeCheck()
        findings = check.check("api/users.py", old_code, new_code)

        assert len(findings) > 0
        assert any("return" in f.message.lower() for f in findings)

    def test_renamed_parameter_detected(self):
        """Renaming parameter is breaking change."""
        old_code = """
def create_order(user_id: int, total: float) -> Order:
    pass
"""
        new_code = """
def create_order(customer_id: int, total: float) -> Order:
    pass
"""
        check = APISignatureChangeCheck()
        findings = check.check("api/orders.py", old_code, new_code)

        assert len(findings) > 0
        assert findings[0].change_type in ["signature_change", "parameter_change"]

    def test_no_changes_passes(self):
        """No signature changes should pass."""
        old_code = """
def get_user(user_id: int) -> User:
    pass
"""
        new_code = """
def get_user(user_id: int) -> User:
    # Implementation changed but signature same
    return User.query.get(user_id)
"""
        check = APISignatureChangeCheck()
        findings = check.check("api/users.py", old_code, new_code)

        # Should pass - no signature change
        assert len(findings) == 0


class TestRemovedPublicMethodsCheck:
    """Test removed public method/class detection."""

    def test_removed_public_function_detected(self):
        """Removing public function is breaking change."""
        old_code = """
def get_user(user_id: int) -> User:
    pass

def delete_user(user_id: int) -> bool:
    pass
"""
        new_code = """
def get_user(user_id: int) -> User:
    pass

# delete_user removed!
"""
        check = RemovedPublicMethodsCheck()
        findings = check.check("api/users.py", old_code, new_code)

        assert len(findings) > 0
        assert any("delete_user" in f.element_name for f in findings)
        assert findings[0].severity == "critical"

    def test_removed_public_class_detected(self):
        """Removing public class is breaking change."""
        old_code = """
class User:
    pass

class Order:
    pass
"""
        new_code = """
class User:
    pass

# Order class removed!
"""
        check = RemovedPublicMethodsCheck()
        findings = check.check("models/entities.py", old_code, new_code)

        assert len(findings) > 0
        assert any("Order" in f.element_name for f in findings)

    def test_removed_private_function_allowed(self):
        """Removing private function (_prefix) is not breaking."""
        old_code = """
def get_user(user_id: int) -> User:
    return _fetch_from_db(user_id)

def _fetch_from_db(user_id: int) -> User:
    pass
"""
        new_code = """
def get_user(user_id: int) -> User:
    return User.query.get(user_id)

# _fetch_from_db removed - OK, it's private
"""
        check = RemovedPublicMethodsCheck()
        findings = check.check("services/user_service.py", old_code, new_code)

        # Should pass - private method
        assert len(findings) == 0

    def test_renamed_function_detected_as_removal(self):
        """Renaming is detected as removal + addition."""
        old_code = """
def authenticate(username: str) -> Token:
    pass
"""
        new_code = """
def login(username: str) -> Token:
    pass
"""
        check = RemovedPublicMethodsCheck()
        findings = check.check("api/auth.py", old_code, new_code)

        # Should detect authenticate removal
        assert len(findings) > 0
        assert any("authenticate" in f.element_name for f in findings)


class TestChangelogRequirementCheck:
    """Test CHANGELOG.md requirement validation."""

    def test_breaking_changes_without_changelog_fails(self):
        """Breaking changes without CHANGELOG update should fail."""
        changed_files = {
            "api/users.py": "code with breaking changes"
        }
        breaking_changes = [
            BreakingChangeFinding(
                check_name="api_signature",
                severity="high",
                file_path="api/users.py",
                line_number=10,
                change_type="signature_change",
                element_name="get_user",
                message="Parameter added",
                requires_changelog=True,
                suggested_changelog_entry="Changed get_user signature"
            )
        ]

        check = ChangelogRequirementCheck()
        findings = check.check(changed_files, breaking_changes)

        assert len(findings) > 0
        assert any("CHANGELOG" in f.message for f in findings)

    def test_breaking_changes_with_changelog_passes(self):
        """Breaking changes with CHANGELOG update should pass."""
        changed_files = {
            "api/users.py": "code with breaking changes",
            "CHANGELOG.md": """
## [Unreleased]

### Breaking Changes
- Changed get_user API signature to require email parameter
"""
        }
        breaking_changes = [
            BreakingChangeFinding(
                check_name="api_signature",
                severity="high",
                file_path="api/users.py",
                line_number=10,
                change_type="signature_change",
                element_name="get_user",
                message="Parameter added",
                requires_changelog=True,
                suggested_changelog_entry="Changed get_user signature"
            )
        ]

        check = ChangelogRequirementCheck()
        findings = check.check(changed_files, breaking_changes)

        # Should pass - CHANGELOG updated
        assert len(findings) == 0

    def test_no_breaking_changes_passes(self):
        """No breaking changes should not require CHANGELOG."""
        changed_files = {
            "services/user_service.py": "internal refactoring"
        }
        breaking_changes = []

        check = ChangelogRequirementCheck()
        findings = check.check(changed_files, breaking_changes)

        # Should pass - no breaking changes
        assert len(findings) == 0

    def test_changelog_format_validation(self):
        """CHANGELOG should have proper format."""
        changed_files = {
            "api/users.py": "breaking change",
            "CHANGELOG.md": """
Just some random notes
No proper format
"""
        }
        breaking_changes = [
            BreakingChangeFinding(
                check_name="api_signature",
                severity="high",
                file_path="api/users.py",
                line_number=10,
                change_type="signature_change",
                element_name="get_user",
                message="Breaking change",
                requires_changelog=True,
                suggested_changelog_entry="API change"
            )
        ]

        check = ChangelogRequirementCheck()
        findings = check.check(changed_files, breaking_changes)

        # Should fail - improper format
        assert len(findings) > 0


class TestDatabaseSchemaChangeCheck:
    """Test database schema change detection."""

    def test_removed_column_detected(self):
        """Removing database column is breaking change."""
        code = """
def downgrade():
    op.drop_column('users', 'legacy_field')
"""
        check = DatabaseSchemaChangeCheck()
        findings = check.check("migrations/remove_column.py", code)

        assert len(findings) > 0
        assert any("column" in f.message.lower() for f in findings)
        assert findings[0].requires_changelog

    def test_non_nullable_column_detected(self):
        """Adding non-nullable column without default is breaking."""
        code = """
def upgrade():
    op.add_column('users', sa.Column('required_field', sa.String(), nullable=False))
"""
        check = DatabaseSchemaChangeCheck()
        findings = check.check("migrations/add_required_field.py", code)

        assert len(findings) > 0
        assert any("nullable" in f.message.lower() or "default" in f.message.lower() for f in findings)

    def test_nullable_column_allowed(self):
        """Adding nullable column is not breaking."""
        code = """
def upgrade():
    op.add_column('users', sa.Column('optional_field', sa.String(), nullable=True))
"""
        check = DatabaseSchemaChangeCheck()
        findings = check.check("migrations/add_optional_field.py", code)

        # Should pass - nullable column
        breaking_findings = [f for f in findings if f.severity == "critical"]
        assert len(breaking_findings) == 0

    def test_dropped_table_detected(self):
        """Dropping table is critical breaking change."""
        code = """
def downgrade():
    op.drop_table('old_users')
"""
        check = DatabaseSchemaChangeCheck()
        findings = check.check("migrations/drop_table.py", code)

        assert len(findings) > 0
        assert any("table" in f.message.lower() for f in findings)
        assert findings[0].severity == "critical"


class TestBreakingChangesValidator:
    """Test the main breaking changes validator."""

    def test_validate_pr_detects_multiple_changes(self):
        """Validator should detect all types of breaking changes."""
        changed_files = {
            "api/users.py": """
def get_user(user_id: int, include_orders: bool) -> User:  # Added param
    pass
""",
            "migrations/schema.py": """
op.drop_column('users', 'legacy_id')
"""
        }
        old_files = {
            "api/users.py": """
def get_user(user_id: int) -> User:
    pass
"""
        }

        validator = BreakingChangesValidator()
        findings = validator.validate_pr(changed_files, old_files)

        # Should have findings from multiple checks
        assert len(findings) > 0

    def test_validate_pr_requires_changelog(self):
        """PR with breaking changes should require CHANGELOG."""
        changed_files = {
            "api/auth.py": """
def authenticate(email: str) -> Token:  # Changed from username
    pass
"""
        }
        old_files = {
            "api/auth.py": """
def authenticate(username: str) -> Token:
    pass
"""
        }

        validator = BreakingChangesValidator()
        findings = validator.validate_pr(changed_files, old_files)

        # Should require CHANGELOG
        assert any(f.requires_changelog for f in findings)

    def test_format_findings_report_includes_changelog_template(self):
        """Report should include suggested CHANGELOG entries."""
        findings = [
            BreakingChangeFinding(
                check_name="api_signature",
                severity="high",
                file_path="api/users.py",
                line_number=10,
                change_type="signature_change",
                element_name="get_user",
                message="Added required parameter",
                requires_changelog=True,
                suggested_changelog_entry="Changed get_user to require email parameter"
            )
        ]

        validator = BreakingChangesValidator()
        report = validator.format_findings_report(findings)

        assert "CHANGELOG" in report
        assert "get_user" in report
        assert "email parameter" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
