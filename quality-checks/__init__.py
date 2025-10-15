"""
Quality Checks Module for CodeRabbit.

This module provides comprehensive pre-merge quality validation including:
- Security checks (hardcoded credentials, SQL injection, sensitive data logging)
- Architecture compliance (layered architecture, dependency injection, async patterns)
- Test coverage validation (new functions have tests, bug fix regression tests)
- Performance checks (N+1 queries, algorithm complexity, memory leaks)
- Breaking changes detection (API changes, removed methods, CHANGELOG requirements)

Task 11: Custom Pre-merge Quality Checks
"""

from .security_checks import SecurityValidator, SecurityFinding
from .architecture_checks import ArchitectureValidator, ArchitectureFinding
from .test_coverage_checks import TestCoverageValidator, TestCoverageFinding
from .performance_checks import PerformanceValidator, PerformanceFinding
from .breaking_changes_checks import BreakingChangesValidator, BreakingChangeFinding
from .quality_orchestrator import QualityCheckOrchestrator

__all__ = [
    'SecurityValidator',
    'SecurityFinding',
    'ArchitectureValidator',
    'ArchitectureFinding',
    'TestCoverageValidator',
    'TestCoverageFinding',
    'PerformanceValidator',
    'PerformanceFinding',
    'BreakingChangesValidator',
    'BreakingChangeFinding',
    'QualityCheckOrchestrator',
]

__version__ = '1.0.0'
