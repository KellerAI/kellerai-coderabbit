"""
Test Suite for Architecture Compliance Checks

Tests for:
- Layer separation validation
- Dependency injection patterns
- Async pattern enforcement
- Circular dependency detection
"""

import pytest
from quality_checks.architecture_checks import (
    ArchitectureValidator,
    LayerSeparationCheck,
    DependencyInjectionCheck,
    AsyncPatternsCheck,
    CircularDependencyCheck,
)


class TestLayerSeparationCheck:
    """Test layer separation validation."""

    def test_repository_importing_controller_fails(self):
        """Repository importing from controller should fail."""
        code = """
from api.controllers import UserController

class UserRepository:
    def get_users(self):
        pass
"""
        check = LayerSeparationCheck()
        findings = check.check("repositories/user_repository.py", code)

        assert len(findings) > 0
        assert any("controller" in f.message.lower() for f in findings)
        assert findings[0].severity in ["high", "medium"]

    def test_repository_importing_service_fails(self):
        """Repository importing from service should fail."""
        code = """
from services.user_service import UserService

class UserRepository:
    def __init__(self):
        self.service = UserService()
"""
        check = LayerSeparationCheck()
        findings = check.check("repositories/user_repository.py", code)

        assert len(findings) > 0
        assert any("service" in f.message.lower() for f in findings)

    def test_model_importing_service_fails(self):
        """Model importing from service should fail."""
        code = """
from services.validation_service import ValidationService

class User:
    def validate(self):
        ValidationService().validate(self)
"""
        check = LayerSeparationCheck()
        findings = check.check("models/user.py", code)

        assert len(findings) > 0

    def test_controller_importing_repository_allowed(self):
        """Controller can import from repository (with DI)."""
        code = """
from repositories.user_repository import UserRepository
from fastapi import Depends

@router.get("/users")
async def get_users(repo: UserRepository = Depends()):
    return repo.get_all()
"""
        check = LayerSeparationCheck()
        findings = check.check("api/user_controller.py", code)

        # Should not fail for correct direction
        assert len([f for f in findings if "prohibited" in f.message.lower()]) == 0

    def test_service_importing_repository_allowed(self):
        """Service can import from repository."""
        code = """
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
"""
        check = LayerSeparationCheck()
        findings = check.check("services/user_service.py", code)

        # Should pass - correct direction
        assert len([f for f in findings if "prohibited" in f.message.lower()]) == 0


class TestDependencyInjectionCheck:
    """Test dependency injection pattern enforcement."""

    def test_fastapi_depends_detected(self):
        """Detect proper use of FastAPI Depends."""
        code = """
from fastapi import Depends
from services.user_service import UserService

@router.post("/users")
async def create_user(
    data: UserCreate,
    service: UserService = Depends(get_user_service)
):
    return await service.create_user(data)
"""
        check = DependencyInjectionCheck()
        findings = check.check("api/users.py", code)

        # Should pass - using Depends
        assert len(findings) == 0

    def test_direct_instantiation_in_controller_fails(self):
        """Direct service instantiation in controller should fail."""
        code = """
from services.user_service import UserService

@router.post("/users")
async def create_user(data: UserCreate):
    service = UserService()  # Direct instantiation!
    return await service.create_user(data)
"""
        check = DependencyInjectionCheck()
        findings = check.check("api/users.py", code)

        assert len(findings) > 0
        assert any("depends" in f.message.lower() for f in findings)

    def test_constructor_injection_in_service_allowed(self):
        """Constructor injection in service is allowed."""
        code = """
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        
    async def create_user(self, data):
        return await self.repo.create(data)
"""
        check = DependencyInjectionCheck()
        findings = check.check("services/user_service.py", code)

        # Constructor injection is fine in services
        assert len(findings) == 0


class TestAsyncPatternsCheck:
    """Test async/await pattern enforcement."""

    def test_sync_requests_in_async_function_fails(self):
        """Using requests library in async function should fail."""
        code = """
import requests

async def fetch_user_data(user_id: int):
    response = requests.get(f"https://api.example.com/users/{user_id}")
    return response.json()
"""
        check = AsyncPatternsCheck()
        findings = check.check("services/user_service.py", code)

        assert len(findings) > 0
        assert any("httpx" in f.suggested_fix.lower() or "async" in f.suggested_fix.lower() for f in findings)

    def test_httpx_in_async_function_passes(self):
        """Using httpx in async function should pass."""
        code = """
import httpx

async def fetch_user_data(user_id: int):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"https://api.example.com/users/{user_id}")
        return response.json()
"""
        check = AsyncPatternsCheck()
        findings = check.check("services/user_service.py", code)

        # Should pass - using async HTTP client
        assert len(findings) == 0

    def test_time_sleep_in_async_function_fails(self):
        """Using time.sleep in async function should fail."""
        code = """
import time

async def process_with_delay():
    time.sleep(1)  # Blocks event loop!
    return "done"
"""
        check = AsyncPatternsCheck()
        findings = check.check("services/processor.py", code)

        assert len(findings) > 0
        assert any("asyncio.sleep" in f.suggested_fix for f in findings)

    def test_asyncio_sleep_in_async_function_passes(self):
        """Using asyncio.sleep in async function should pass."""
        code = """
import asyncio

async def process_with_delay():
    await asyncio.sleep(1)
    return "done"
"""
        check = AsyncPatternsCheck()
        findings = check.check("services/processor.py", code)

        # Should pass - using async sleep
        assert len(findings) == 0


class TestCircularDependencyCheck:
    """Test circular dependency detection."""

    def test_circular_dependency_detected(self):
        """Detect circular dependencies between modules."""
        file_contents = {
            "services/user_service.py": """
from services.order_service import OrderService

class UserService:
    pass
""",
            "services/order_service.py": """
from services.user_service import UserService

class OrderService:
    pass
"""
        }

        check = CircularDependencyCheck()
        findings = check.check_project(file_contents)

        assert len(findings) > 0
        assert any("circular" in f.message.lower() for f in findings)

    def test_no_circular_dependency_passes(self):
        """No circular dependencies should pass."""
        file_contents = {
            "controllers/user_controller.py": """
from services.user_service import UserService
""",
            "services/user_service.py": """
from repositories.user_repository import UserRepository
""",
            "repositories/user_repository.py": """
from models.user import User
""",
            "models/user.py": """
class User:
    pass
"""
        }

        check = CircularDependencyCheck()
        findings = check.check_project(file_contents)

        # Should pass - no circular dependencies
        assert len(findings) == 0


class TestArchitectureValidator:
    """Test the main architecture validator."""

    def test_validate_file_runs_all_checks(self):
        """Validator should run all applicable checks."""
        code = """
from api.controllers import Controller
import requests

async def process():
    response = requests.get("http://example.com")
    return response.json()
"""
        validator = ArchitectureValidator()
        findings = validator.validate_file("repositories/repo.py", code)

        # Should have findings from multiple checks
        assert len(findings) > 0

    def test_validate_project_detects_circular_deps(self):
        """Project validation should detect circular dependencies."""
        file_contents = {
            "services/a.py": "from services.b import B",
            "services/b.py": "from services.a import A",
        }

        validator = ArchitectureValidator()
        all_findings = validator.validate_project(file_contents)

        # Should have findings for circular dependency
        assert len(all_findings) > 0

    def test_clean_architecture_passes(self):
        """Clean architecture with proper layering should pass."""
        code = """
from repositories.user_repository import UserRepository

class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo
        
    async def get_users(self):
        return await self.repo.get_all()
"""
        validator = ArchitectureValidator()
        findings = validator.validate_file("services/user_service.py", code)

        # Clean code should have no critical findings
        critical_findings = [f for f in findings if f.severity == "high"]
        assert len(critical_findings) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
