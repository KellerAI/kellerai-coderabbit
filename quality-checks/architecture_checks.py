"""
Architecture compliance quality checks for CodeRabbit.

This module implements architecture checks to validate:
- Layered architecture compliance (Controller → Service → Repository → Model)
- Dependency flow patterns
- Dependency injection usage
- Async/await patterns for I/O operations

Task 11.3: Architecture and Test Coverage Checks
"""

import re
import ast
from typing import List, Dict, Set, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ArchitectureFinding:
    """Represents an architecture violation finding."""
    check_name: str
    severity: str
    file_path: str
    line_number: int
    message: str
    violated_rule: str
    suggested_fix: str = ""


class LayerSeparationCheck:
    """Validate layered architecture compliance."""

    # Define layer hierarchy and allowed dependencies
    LAYERS = {
        'controller': {
            'paths': ['api/', 'controllers/'],
            'allowed_dependencies': ['service', 'model'],
            'prohibited_dependencies': ['repository'],
        },
        'service': {
            'paths': ['services/', 'business/'],
            'allowed_dependencies': ['repository', 'model'],
            'prohibited_dependencies': ['controller', 'api'],
        },
        'repository': {
            'paths': ['repositories/', 'data/'],
            'allowed_dependencies': ['model'],
            'prohibited_dependencies': ['controller', 'api', 'service'],
        },
        'model': {
            'paths': ['models/', 'entities/'],
            'allowed_dependencies': [],
            'prohibited_dependencies': ['controller', 'api', 'service', 'repository'],
        },
    }

    def check(self, file_path: str, content: str) -> List[ArchitectureFinding]:
        """
        Check for layer separation violations.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of architecture findings
        """
        findings = []

        # Determine which layer this file belongs to
        current_layer = self._identify_layer(file_path)
        if not current_layer:
            return findings  # Not in a defined layer

        # Extract imports from the file
        imports = self._extract_imports(content)

        # Check for prohibited dependencies
        prohibited = self.LAYERS[current_layer]['prohibited_dependencies']
        for import_stmt in imports:
            for prohibited_layer in prohibited:
                if self._import_references_layer(import_stmt, prohibited_layer):
                    findings.append(ArchitectureFinding(
                        check_name="layer_separation",
                        severity="medium",
                        file_path=file_path,
                        line_number=import_stmt['line'],
                        message=f"{current_layer.title()} layer must not depend on {prohibited_layer} layer",
                        violated_rule=f"{current_layer} → {prohibited_layer} (prohibited)",
                        suggested_fix=f"Use dependency injection to invert the dependency or refactor to use {self.LAYERS[current_layer]['allowed_dependencies']}"
                    ))

        return findings

    def _identify_layer(self, file_path: str) -> Optional[str]:
        """Identify which layer a file belongs to based on its path."""
        for layer, config in self.LAYERS.items():
            for path_pattern in config['paths']:
                if path_pattern in file_path:
                    return layer
        return None

    def _extract_imports(self, content: str) -> List[Dict]:
        """Extract import statements from Python code."""
        imports = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append({
                            'type': 'import',
                            'module': alias.name,
                            'line': node.lineno
                        })
                elif isinstance(node, ast.ImportFrom):
                    imports.append({
                        'type': 'from',
                        'module': node.module or '',
                        'line': node.lineno
                    })
        except SyntaxError:
            # If we can't parse, try regex fallback
            import_pattern = r'(?:from|import)\s+([\w.]+)'
            for line_num, line in enumerate(content.split('\n'), 1):
                match = re.search(import_pattern, line)
                if match:
                    imports.append({
                        'type': 'import',
                        'module': match.group(1),
                        'line': line_num
                    })
        return imports

    def _import_references_layer(self, import_stmt: Dict, layer: str) -> bool:
        """Check if an import statement references a specific layer."""
        module = import_stmt['module'].lower()
        layer_indicators = self.LAYERS[layer]['paths']
        for indicator in layer_indicators:
            indicator_clean = indicator.strip('/')
            if indicator_clean in module:
                return True
        return False


class DependencyInjectionCheck:
    """Ensure dependency injection is used in controllers/API routes."""

    def check(self, file_path: str, content: str) -> List[ArchitectureFinding]:
        """
        Check for dependency injection usage.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of architecture findings
        """
        findings = []

        # Only check controller/API files
        if not ('api/' in file_path or 'controllers/' in file_path):
            return findings

        # Check if FastAPI Depends is used
        has_depends = bool(re.search(r'from\s+fastapi\s+import.*Depends', content))
        has_depends_usage = bool(re.search(r'Depends\s*\(', content))

        if not has_depends or not has_depends_usage:
            # Check for route definitions
            route_patterns = [
                r'@app\.(get|post|put|delete|patch)',
                r'@router\.(get|post|put|delete|patch)',
            ]
            has_routes = any(re.search(pattern, content) for pattern in route_patterns)

            if has_routes:
                # Find route function definitions
                for line_num, line in enumerate(content.split('\n'), 1):
                    if re.search(r'@(app|router)\.\w+', line):
                        findings.append(ArchitectureFinding(
                            check_name="dependency_injection",
                            severity="medium",
                            file_path=file_path,
                            line_number=line_num,
                            message="Use FastAPI Depends() for dependency injection in API routes",
                            violated_rule="Missing dependency injection pattern",
                            suggested_fix="from fastapi import Depends\n\ndef get_service() -> MyService:\n    return MyService()\n\n@app.get('/endpoint')\ndef endpoint(service: MyService = Depends(get_service)):"
                        ))
                        break  # Report once per file

        return findings


class AsyncPatternsCheck:
    """Ensure async/await is used properly for I/O operations."""

    SYNC_LIBRARIES = {
        'requests': {
            'pattern': r'requests\.(get|post|put|delete|patch|head|options)',
            'alternative': 'httpx.AsyncClient',
            'message': 'Use httpx.AsyncClient instead of requests in async functions',
        },
        'psycopg2': {
            'pattern': r'import\s+psycopg2',
            'alternative': 'asyncpg',
            'message': 'Use asyncpg instead of psycopg2 in async functions',
        },
        'pymongo': {
            'pattern': r'import\s+pymongo',
            'alternative': 'motor',
            'message': 'Use motor (async MongoDB driver) instead of pymongo in async functions',
        },
        'redis': {
            'pattern': r'import\s+redis\b',
            'alternative': 'aioredis',
            'message': 'Use aioredis instead of redis in async functions',
        },
    }

    def check(self, file_path: str, content: str) -> List[ArchitectureFinding]:
        """
        Check for proper async/await usage.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of architecture findings
        """
        findings = []

        # Find async function definitions
        async_functions = self._find_async_functions(content)

        if not async_functions:
            return findings

        # Check for sync library usage in async functions
        for lib_name, lib_config in self.SYNC_LIBRARIES.items():
            pattern = lib_config['pattern']
            for match in re.finditer(pattern, content):
                line_num = content[:match.start()].count('\n') + 1

                # Check if this line is inside an async function
                if self._is_in_async_function(line_num, async_functions):
                    findings.append(ArchitectureFinding(
                        check_name="async_patterns",
                        severity="medium",
                        file_path=file_path,
                        line_number=line_num,
                        message=lib_config['message'],
                        violated_rule=f"Sync library '{lib_name}' in async context",
                        suggested_fix=f"Use {lib_config['alternative']} for async I/O operations"
                    ))

        return findings

    def _find_async_functions(self, content: str) -> List[tuple]:
        """
        Find all async function definitions.

        Returns:
            List of tuples (start_line, end_line, function_name)
        """
        async_functions = []
        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.AsyncFunctionDef):
                    async_functions.append((
                        node.lineno,
                        node.end_lineno or node.lineno,
                        node.name
                    ))
        except SyntaxError:
            # Fallback to regex
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if re.match(r'async\s+def\s+(\w+)', line):
                    # Estimate end of function (simple heuristic)
                    async_functions.append((i, i + 20, 'unknown'))

        return async_functions

    def _is_in_async_function(self, line_num: int, async_functions: List[tuple]) -> bool:
        """Check if a line number is inside an async function."""
        for start, end, _ in async_functions:
            if start <= line_num <= end:
                return True
        return False


class CircularDependencyCheck:
    """Detect circular dependencies between modules."""

    def check_project(self, file_contents: Dict[str, str]) -> List[ArchitectureFinding]:
        """
        Check for circular dependencies across the project.

        Args:
            file_contents: Dictionary mapping file paths to their contents

        Returns:
            List of architecture findings
        """
        findings = []
        dependency_graph = self._build_dependency_graph(file_contents)

        # Detect cycles
        cycles = self._find_cycles(dependency_graph)

        for cycle in cycles:
            cycle_str = ' → '.join(cycle + [cycle[0]])
            findings.append(ArchitectureFinding(
                check_name="circular_dependency",
                severity="high",
                file_path=cycle[0],
                line_number=1,
                message=f"Circular dependency detected: {cycle_str}",
                violated_rule="No circular dependencies allowed",
                suggested_fix="Refactor to use dependency inversion or extract shared dependencies to a common module"
            ))

        return findings

    def _build_dependency_graph(self, file_contents: Dict[str, str]) -> Dict[str, Set[str]]:
        """Build a dependency graph from file imports."""
        graph = {}

        for file_path, content in file_contents.items():
            module_name = self._path_to_module(file_path)
            graph[module_name] = set()

            # Extract imports
            import_pattern = r'from\s+([\w.]+)\s+import|import\s+([\w.]+)'
            for match in re.finditer(import_pattern, content):
                imported = match.group(1) or match.group(2)
                if imported:
                    graph[module_name].add(imported.split('.')[0])

        return graph

    def _path_to_module(self, file_path: str) -> str:
        """Convert file path to module name."""
        return file_path.replace('/', '.').replace('.py', '')

    def _find_cycles(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find cycles in dependency graph using DFS."""
        cycles = []
        visited = set()
        rec_stack = []

        def dfs(node: str):
            visited.add(node)
            rec_stack.append(node)

            if node in graph:
                for neighbor in graph[node]:
                    if neighbor not in visited:
                        dfs(neighbor)
                    elif neighbor in rec_stack:
                        # Found a cycle
                        cycle_start = rec_stack.index(neighbor)
                        cycles.append(rec_stack[cycle_start:])

            rec_stack.pop()

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles


class ArchitectureValidator:
    """Main architecture validator that runs all architecture checks."""

    def __init__(self):
        """Initialize architecture checks."""
        self.checks = [
            LayerSeparationCheck(),
            DependencyInjectionCheck(),
            AsyncPatternsCheck(),
        ]

    def validate_file(self, file_path: str, content: str) -> List[ArchitectureFinding]:
        """
        Run all architecture checks on a file.

        Args:
            file_path: Path to the file being checked
            content: File content to analyze

        Returns:
            List of all architecture findings
        """
        all_findings = []
        for check in self.checks:
            findings = check.check(file_path, content)
            all_findings.extend(findings)
        return all_findings

    def validate_project(self, file_contents: Dict[str, str]) -> Dict[str, List[ArchitectureFinding]]:
        """
        Validate architecture across entire project.

        Args:
            file_contents: Dictionary mapping file paths to contents

        Returns:
            Dictionary mapping file paths to their findings
        """
        results = {}

        # Run per-file checks
        for file_path, content in file_contents.items():
            findings = self.validate_file(file_path, content)
            if findings:
                results[file_path] = findings

        # Run project-wide checks
        circular_dep_check = CircularDependencyCheck()
        circular_findings = circular_dep_check.check_project(file_contents)
        for finding in circular_findings:
            if finding.file_path not in results:
                results[finding.file_path] = []
            results[finding.file_path].append(finding)

        return results
