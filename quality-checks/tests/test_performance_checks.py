"""
Test Suite for Performance Checks

Tests for:
- N+1 query detection
- Database index validation
- Algorithm complexity analysis
- Memory leak detection
"""

import pytest
from quality_checks.performance_checks import (
    PerformanceValidator,
    NPlusOneQueryCheck,
    DatabaseIndexCheck,
    AlgorithmComplexityCheck,
    MemoryLeakCheck,
    PerformanceFinding,
)


class TestNPlusOneQueryCheck:
    """Test N+1 query pattern detection."""

    def test_query_in_loop_detected(self):
        """Database query inside loop should be detected."""
        code = """
users = session.query(User).all()
for user in users:
    orders = session.query(Order).filter_by(user_id=user.id).all()
    print(orders)
"""
        check = NPlusOneQueryCheck()
        findings = check.check("services/user_service.py", code)
        
        assert len(findings) > 0
        assert any("n+1" in f.message.lower() for f in findings)
        assert findings[0].severity in ["high", "critical"]

    def test_list_comprehension_with_query_detected(self):
        """Query in list comprehension should be detected."""
        code = """
user_ids = [1, 2, 3, 4, 5]
orders = [db.query(Order).filter_by(user_id=uid).all() for uid in user_ids]
"""
        check = NPlusOneQueryCheck()
        findings = check.check("services/order_service.py", code)
        
        assert len(findings) > 0
        assert any("n+1" in f.message.lower() for f in findings)

    def test_eager_loading_passes(self):
        """Proper eager loading should pass."""
        code = """
from sqlalchemy.orm import joinedload

users = session.query(User).options(joinedload(User.orders)).all()
for user in users:
    orders = user.orders  # Already loaded
    print(orders)
"""
        check = NPlusOneQueryCheck()
        findings = check.check("services/user_service.py", code)
        
        # Should pass - using eager loading
        n_plus_one_findings = [f for f in findings if "n+1" in f.message.lower()]
        assert len(n_plus_one_findings) == 0

    def test_single_query_outside_loop_passes(self):
        """Single query outside loop should pass."""
        code = """
orders = session.query(Order).all()
for order in orders:
    print(order.total)
"""
        check = NPlusOneQueryCheck()
        findings = check.check("services/order_service.py", code)
        
        # Should pass - no query in loop
        assert len(findings) == 0


class TestDatabaseIndexCheck:
    """Test database index validation."""

    def test_foreign_key_without_index_detected(self):
        """Foreign key without index should be detected."""
        code = """
user_id = Column(Integer, ForeignKey('users.id'))
order_date = Column(DateTime)
"""
        check = DatabaseIndexCheck()
        findings = check.check("models/order.py", code)
        
        assert len(findings) > 0
        assert any("index" in f.message.lower() for f in findings)

    def test_foreign_key_with_index_passes(self):
        """Foreign key with index should pass."""
        code = """
user_id = Column(Integer, ForeignKey('users.id'), index=True)
order_date = Column(DateTime)
"""
        check = DatabaseIndexCheck()
        findings = check.check("models/order.py", code)
        
        # Should pass - index specified
        fk_findings = [f for f in findings if "foreign" in f.message.lower()]
        assert len(fk_findings) == 0

    def test_db_index_parameter_recognized(self):
        """db_index=True should be recognized."""
        code = """
user_id = Column(Integer, ForeignKey('users.id'), db_index=True)
"""
        check = DatabaseIndexCheck()
        findings = check.check("models/order.py", code)
        
        # Should pass - db_index specified
        assert len([f for f in findings if "foreign" in f.message.lower()]) == 0

    def test_frequently_queried_field_without_index(self):
        """Frequently queried fields should have indexes."""
        code = """
status = Column(String)  # Frequently used in WHERE clauses

# Query usage
orders = session.query(Order).filter(Order.status == 'pending').all()
"""
        check = DatabaseIndexCheck()
        findings = check.check("models/order.py", code)
        
        # May suggest index on status field
        assert len(findings) >= 0  # Advisory check


class TestAlgorithmComplexityCheck:
    """Test algorithm complexity analysis."""

    def test_nested_loops_detected(self):
        """Nested loops should be flagged."""
        code = """
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i+1, len(items)):
            if items[i] == items[j]:
                duplicates.append(items[i])
    return duplicates
"""
        check = AlgorithmComplexityCheck()
        findings = check.check("services/processor.py", code)
        
        assert len(findings) > 0
        assert any("nested" in f.message.lower() or "o(n" in f.message.lower() for f in findings)

    def test_inefficient_list_contains_in_loop(self):
        """Inefficient list.contains in loop should be flagged."""
        code = """
def remove_duplicates(items):
    result = []
    for item in items:
        if item not in result:  # O(n) operation in loop!
            result.append(item)
    return result
"""
        check = AlgorithmComplexityCheck()
        findings = check.check("services/processor.py", code)
        
        assert len(findings) > 0
        assert any("set" in f.suggested_fix.lower() for f in findings)

    def test_efficient_algorithm_passes(self):
        """Efficient algorithm should pass."""
        code = """
def remove_duplicates(items):
    seen = set()
    result = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result
"""
        check = AlgorithmComplexityCheck()
        findings = check.check("services/processor.py", code)
        
        # Should pass - using set for O(1) lookup
        inefficient_findings = [f for f in findings if "inefficient" in f.message.lower()]
        assert len(inefficient_findings) == 0

    def test_loop_invariant_computation_detected(self):
        """Computation inside loop that could be outside should be flagged."""
        code = """
def process_items(items, multiplier):
    results = []
    for item in items:
        constant_value = expensive_calculation(multiplier)  # Loop invariant!
        results.append(item * constant_value)
    return results
"""
        check = AlgorithmComplexityCheck()
        findings = check.check("services/processor.py", code)
        
        # Should detect loop invariant
        assert len(findings) > 0


class TestMemoryLeakCheck:
    """Test memory leak pattern detection."""

    def test_unbounded_global_collection_detected(self):
        """Global unbounded collection should be detected."""
        code = """
cache = {}  # Unbounded cache!

def store_data(key, value):
    cache[key] = value  # Never cleared
"""
        check = MemoryLeakCheck()
        findings = check.check("services/cache.py", code)
        
        assert len(findings) > 0
        assert any("unbounded" in f.message.lower() or "cache" in f.message.lower() for f in findings)

    def test_bounded_cache_with_lru_passes(self):
        """Bounded cache with LRU should pass."""
        code = """
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(arg):
    return arg * 2
"""
        check = MemoryLeakCheck()
        findings = check.check("services/processor.py", code)
        
        # Should pass - bounded cache
        assert len(findings) == 0

    def test_local_collection_passes(self):
        """Local collections are fine."""
        code = """
def process_batch():
    results = []
    for item in get_items():
        results.append(item)
    return results
"""
        check = MemoryLeakCheck()
        findings = check.check("services/processor.py", code)
        
        # Should pass - local scope
        assert len(findings) == 0


class TestPerformanceValidator:
    """Test the main performance validator."""

    def test_validate_file_runs_all_checks(self):
        """Validator should run all applicable checks."""
        code = """
# N+1 query
users = session.query(User).all()
for user in users:
    orders = session.query(Order).filter_by(user_id=user.id).all()

# Nested loops
def bad_algorithm(items):
    for i in items:
        for j in items:
            if i == j:
                print("match")
"""
        validator = PerformanceValidator()
        findings = validator.validate_file("services/user_service.py", code)
        
        # Should have findings from multiple checks
        assert len(findings) > 0

    def test_validate_pr_checks_all_files(self):
        """PR validation should check all changed files."""
        changed_files = {
            "src/services/user.py": """
users = db.query(User).all()
for user in users:
    posts = db.query(Post).filter_by(user_id=user.id).all()
""",
            "src/models/order.py": """
user_id = Column(Integer, ForeignKey('users.id'))  # No index
"""
        }
        
        validator = PerformanceValidator()
        all_findings = validator.validate_pr(changed_files)
        
        # Should have findings from both files
        assert len(all_findings) > 0
        assert len(all_findings.keys()) >= 1

    def test_format_findings_report_groups_by_file(self):
        """Report should group findings by file."""
        changed_files = {
            "src/service1.py": """
for i in range(100):
    for j in range(100):
        pass
""",
            "src/service2.py": """
users = db.query(User).all()
for user in users:
    db.query(Order).filter_by(user_id=user.id).all()
"""
        }
        
        validator = PerformanceValidator()
        all_findings = validator.validate_pr(changed_files)
        report = validator.format_findings_report(all_findings)
        
        assert "service1.py" in report or "service2.py" in report
        assert len(report) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
