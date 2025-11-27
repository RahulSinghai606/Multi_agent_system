"""
Dependency Tracker

Unified dependency tracking across monorepo and multi-repo setups:
- Package dependencies (npm, pip, poetry, etc.)
- Workspace/repository interdependencies
- Version constraint management
- Dependency graph visualization
- Circular dependency detection
- Security vulnerability tracking
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class DependencyType(Enum):
    """Type of dependency relationship"""
    PRODUCTION = "production"
    DEVELOPMENT = "development"
    PEER = "peer"
    OPTIONAL = "optional"
    WORKSPACE = "workspace"  # Internal workspace/repo dependency


@dataclass
class Dependency:
    """Dependency information"""

    name: str
    version: str
    type: DependencyType
    source: str  # Which package/workspace declares this dependency
    resolved_version: Optional[str] = None
    is_internal: bool = False  # True if dependency is another workspace/repo
    vulnerabilities: List[Dict[str, Any]] = field(default_factory=list)


class DependencyTracker:
    """
    Unified dependency tracking system

    Capabilities:
    - Extract dependencies from package.json, requirements.txt, etc.
    - Build comprehensive dependency graphs
    - Detect circular dependencies
    - Find version conflicts
    - Track security vulnerabilities
    - Generate dependency reports
    - Suggest dependency updates
    """

    def __init__(self, root: Path):
        self.root = root
        self.logger = logging.getLogger(f"{__name__}.DependencyTracker")
        self.dependencies: Dict[str, List[Dependency]] = {}  # source -> dependencies
        self.graph: Dict[str, Set[str]] = {}  # dependency graph
        self.reverse_graph: Dict[str, Set[str]] = {}  # reverse dependency graph

    def scan_dependencies(self, workspaces: Dict[str, Any]) -> Dict[str, List[Dependency]]:
        """
        Scan dependencies across all workspaces

        Args:
            workspaces: Dictionary of workspace_name -> workspace_info

        Returns:
            Dictionary of source -> list of dependencies
        """
        self.logger.info("Scanning dependencies across workspaces")

        for name, workspace in workspaces.items():
            deps = self._extract_dependencies(name, workspace.get("path", Path(name)))
            self.dependencies[name] = deps

        self.logger.info(f"Found dependencies in {len(self.dependencies)} workspaces")

        return self.dependencies

    def build_graph(self) -> Dict[str, Set[str]]:
        """
        Build dependency graph

        Returns:
            Dependency graph (source -> set of dependencies)
        """
        self.logger.info("Building dependency graph")

        graph = {}
        reverse_graph = {}

        for source, deps in self.dependencies.items():
            graph[source] = set()

            for dep in deps:
                graph[source].add(dep.name)

                # Build reverse graph
                if dep.name not in reverse_graph:
                    reverse_graph[dep.name] = set()
                reverse_graph[dep.name].add(source)

        self.graph = graph
        self.reverse_graph = reverse_graph

        self.logger.info(f"Built graph with {len(graph)} nodes")

        return graph

    def detect_circular_dependencies(self) -> List[List[str]]:
        """
        Detect circular dependencies

        Returns:
            List of circular dependency chains
        """
        self.logger.info("Detecting circular dependencies")

        if not self.graph:
            self.build_graph()

        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in self.graph.get(node, set()):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in self.graph:
            if node not in visited:
                dfs(node)

        if cycles:
            self.logger.warning(f"Found {len(cycles)} circular dependencies")
        else:
            self.logger.info("No circular dependencies detected")

        return cycles

    def find_version_conflicts(self) -> List[Dict[str, Any]]:
        """
        Find version conflicts where same dependency has multiple versions

        Returns:
            List of conflicts with details
        """
        self.logger.info("Finding version conflicts")

        # Group dependencies by name
        dep_versions: Dict[str, List[Tuple[str, str]]] = {}  # dep_name -> [(source, version)]

        for source, deps in self.dependencies.items():
            for dep in deps:
                if dep.name not in dep_versions:
                    dep_versions[dep.name] = []
                dep_versions[dep.name].append((source, dep.version))

        # Find conflicts
        conflicts = []

        for dep_name, versions in dep_versions.items():
            unique_versions = set(v for _, v in versions)

            if len(unique_versions) > 1:
                conflicts.append({
                    "dependency": dep_name,
                    "versions": list(unique_versions),
                    "sources": [
                        {"source": source, "version": version}
                        for source, version in versions
                    ]
                })

        if conflicts:
            self.logger.warning(f"Found {len(conflicts)} version conflicts")
        else:
            self.logger.info("No version conflicts detected")

        return conflicts

    def get_dependency_tree(self, source: str, max_depth: int = 10) -> Dict[str, Any]:
        """
        Get dependency tree for specific source

        Args:
            source: Source workspace/package
            max_depth: Maximum depth to traverse

        Returns:
            Dependency tree structure
        """
        visited = set()

        def build_tree(node: str, depth: int = 0) -> Dict[str, Any]:
            if depth >= max_depth or node in visited:
                return {"name": node, "truncated": True}

            visited.add(node)

            tree = {
                "name": node,
                "dependencies": []
            }

            for dep_name in self.graph.get(node, set()):
                tree["dependencies"].append(build_tree(dep_name, depth + 1))

            return tree

        return build_tree(source)

    def get_dependents(self, dependency: str) -> List[str]:
        """
        Get list of workspaces that depend on given dependency

        Args:
            dependency: Dependency name

        Returns:
            List of dependent workspace names
        """
        if not self.reverse_graph:
            self.build_graph()

        return list(self.reverse_graph.get(dependency, set()))

    def find_unused_dependencies(self) -> Dict[str, List[str]]:
        """
        Find declared dependencies that are not used (simple heuristic)

        Returns:
            Dictionary of source -> list of potentially unused dependencies
        """
        unused = {}

        for source, deps in self.dependencies.items():
            source_path = self.root / source

            # Get all code files
            code_files = []
            for ext in ['.js', '.ts', '.tsx', '.jsx', '.py']:
                code_files.extend(source_path.rglob(f'*{ext}'))

            # Check if dependency is imported/required
            source_unused = []

            for dep in deps:
                if dep.is_internal:
                    continue  # Skip internal workspace dependencies

                dep_found = False

                for code_file in code_files:
                    try:
                        content = code_file.read_text()

                        # Check for import/require
                        if (f"from '{dep.name}'" in content or
                            f'from "{dep.name}"' in content or
                            f"require('{dep.name}')" in content or
                            f'require("{dep.name}")' in content or
                            f"import {dep.name}" in content):
                            dep_found = True
                            break
                    except Exception:
                        pass

                if not dep_found:
                    source_unused.append(dep.name)

            if source_unused:
                unused[source] = source_unused

        return unused

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive dependency report"""

        total_deps = sum(len(deps) for deps in self.dependencies.values())

        # Count by type
        type_counts = {t.value: 0 for t in DependencyType}
        for deps in self.dependencies.values():
            for dep in deps:
                type_counts[dep.type.value] = type_counts.get(dep.type.value, 0) + 1

        # Count internal vs external
        internal_count = 0
        external_count = 0
        for deps in self.dependencies.values():
            for dep in deps:
                if dep.is_internal:
                    internal_count += 1
                else:
                    external_count += 1

        # Detect issues
        circular = self.detect_circular_dependencies()
        conflicts = self.find_version_conflicts()

        return {
            "summary": {
                "total_dependencies": total_deps,
                "internal_dependencies": internal_count,
                "external_dependencies": external_count,
                "by_type": type_counts,
                "circular_dependencies": len(circular),
                "version_conflicts": len(conflicts)
            },
            "dependencies_by_source": {
                source: [
                    {
                        "name": dep.name,
                        "version": dep.version,
                        "type": dep.type.value,
                        "is_internal": dep.is_internal
                    }
                    for dep in deps
                ]
                for source, deps in self.dependencies.items()
            },
            "issues": {
                "circular_dependencies": circular,
                "version_conflicts": conflicts
            },
            "graph_stats": {
                "nodes": len(self.graph),
                "edges": sum(len(deps) for deps in self.graph.values())
            }
        }

    # Private helper methods
    def _extract_dependencies(self, source: str, path: Path) -> List[Dependency]:
        """Extract dependencies from workspace/package"""
        dependencies = []

        # JavaScript/TypeScript - package.json
        package_json = path / "package.json"
        if package_json.exists():
            dependencies.extend(self._extract_npm_dependencies(source, package_json))

        # Python - requirements.txt
        requirements = path / "requirements.txt"
        if requirements.exists():
            dependencies.extend(self._extract_pip_dependencies(source, requirements))

        # Python - pyproject.toml (Poetry)
        pyproject = path / "pyproject.toml"
        if pyproject.exists():
            dependencies.extend(self._extract_poetry_dependencies(source, pyproject))

        return dependencies

    def _extract_npm_dependencies(self, source: str, package_json: Path) -> List[Dependency]:
        """Extract dependencies from package.json"""
        dependencies = []

        try:
            with open(package_json) as f:
                data = json.load(f)

                # Production dependencies
                for name, version in data.get("dependencies", {}).items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.PRODUCTION,
                        source=source,
                        is_internal=name in self.dependencies  # Check if internal workspace
                    ))

                # Dev dependencies
                for name, version in data.get("devDependencies", {}).items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.DEVELOPMENT,
                        source=source,
                        is_internal=name in self.dependencies
                    ))

                # Peer dependencies
                for name, version in data.get("peerDependencies", {}).items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.PEER,
                        source=source,
                        is_internal=name in self.dependencies
                    ))

                # Optional dependencies
                for name, version in data.get("optionalDependencies", {}).items():
                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.OPTIONAL,
                        source=source,
                        is_internal=name in self.dependencies
                    ))

        except Exception as e:
            self.logger.warning(f"Error reading {package_json}: {e}")

        return dependencies

    def _extract_pip_dependencies(self, source: str, requirements: Path) -> List[Dependency]:
        """Extract dependencies from requirements.txt"""
        dependencies = []

        try:
            content = requirements.read_text()

            for line in content.split('\n'):
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse dependency
                # Format: package==version or package>=version, etc.
                if '==' in line:
                    name, version = line.split('==', 1)
                elif '>=' in line:
                    name, version = line.split('>=', 1)
                elif '<=' in line:
                    name, version = line.split('<=', 1)
                else:
                    name = line
                    version = "*"

                dependencies.append(Dependency(
                    name=name.strip(),
                    version=version.strip(),
                    type=DependencyType.PRODUCTION,
                    source=source,
                    is_internal=name.strip() in self.dependencies
                ))

        except Exception as e:
            self.logger.warning(f"Error reading {requirements}: {e}")

        return dependencies

    def _extract_poetry_dependencies(self, source: str, pyproject: Path) -> List[Dependency]:
        """Extract dependencies from pyproject.toml (Poetry)"""
        dependencies = []

        try:
            # Simple TOML parsing (basic implementation)
            content = pyproject.read_text()

            in_dependencies = False
            in_dev_dependencies = False

            for line in content.split('\n'):
                line = line.strip()

                if line == "[tool.poetry.dependencies]":
                    in_dependencies = True
                    in_dev_dependencies = False
                    continue
                elif line == "[tool.poetry.dev-dependencies]":
                    in_dependencies = False
                    in_dev_dependencies = True
                    continue
                elif line.startswith('['):
                    in_dependencies = False
                    in_dev_dependencies = False
                    continue

                if (in_dependencies or in_dev_dependencies) and '=' in line:
                    parts = line.split('=', 1)
                    name = parts[0].strip()
                    version = parts[1].strip().strip('"').strip("'")

                    if name == "python":
                        continue  # Skip Python version

                    dependencies.append(Dependency(
                        name=name,
                        version=version,
                        type=DependencyType.DEVELOPMENT if in_dev_dependencies else DependencyType.PRODUCTION,
                        source=source,
                        is_internal=name in self.dependencies
                    ))

        except Exception as e:
            self.logger.warning(f"Error reading {pyproject}: {e}")

        return dependencies

    def export_graph_dot(self, output_path: Path):
        """Export dependency graph as DOT format for visualization"""

        if not self.graph:
            self.build_graph()

        dot_content = "digraph Dependencies {\n"
        dot_content += "    rankdir=LR;\n"
        dot_content += "    node [shape=box];\n\n"

        # Add nodes
        for node in self.graph.keys():
            dot_content += f'    "{node}";\n'

        dot_content += "\n"

        # Add edges
        for source, deps in self.graph.items():
            for dep in deps:
                dot_content += f'    "{source}" -> "{dep}";\n'

        dot_content += "}\n"

        with open(output_path, 'w') as f:
            f.write(dot_content)

        self.logger.info(f"Dependency graph exported to {output_path}")
        self.logger.info("Visualize with: dot -Tpng output.dot -o output.png")
