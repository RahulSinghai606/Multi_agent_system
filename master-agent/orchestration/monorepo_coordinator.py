"""
Monorepo Coordinator

Expert in managing monorepo patterns:
- Turborepo integration and optimization
- Nx workspace coordination
- Lerna/pnpm workspace support
- Package interdependencies
- Unified build and test orchestration
- Workspace-aware deployments
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class WorkspaceInfo:
    """Information about a workspace/package in monorepo"""

    name: str
    path: Path
    type: str  # "app", "package", "library", "service"
    dependencies: List[str] = field(default_factory=list)
    dev_dependencies: List[str] = field(default_factory=list)
    scripts: Dict[str, str] = field(default_factory=dict)
    version: Optional[str] = None
    private: bool = False


@dataclass
class MonorepoConfig:
    """Monorepo configuration"""

    type: str  # "turborepo", "nx", "lerna", "pnpm", "yarn"
    root: Path
    workspaces: List[str]  # Workspace patterns
    build_system: str  # "turborepo", "nx", "npm", "pnpm"
    cache_enabled: bool = True
    remote_cache_url: Optional[str] = None
    pipeline_config: Dict[str, Any] = field(default_factory=dict)


class MonorepoCoordinator:
    """
    Monorepo coordination and orchestration

    Supports:
    - Turborepo: High-performance build system
    - Nx: Smart monorepo tool with affected project detection
    - Lerna: Multi-package repository management
    - pnpm workspaces: Fast, disk-efficient package manager
    - Yarn workspaces: Dependency hoisting and linking

    Capabilities:
    - Workspace discovery and mapping
    - Dependency graph construction
    - Affected project detection
    - Parallel build orchestration
    - Cache-aware task execution
    - Selective testing and deployment
    """

    def __init__(self, config: MonorepoConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.MonorepoCoordinator")
        self.workspaces: Dict[str, WorkspaceInfo] = {}
        self.dependency_graph: Dict[str, Set[str]] = {}

    def discover_workspaces(self) -> Dict[str, WorkspaceInfo]:
        """
        Discover all workspaces in monorepo

        Returns:
            Dictionary of workspace_name -> WorkspaceInfo
        """
        self.logger.info(f"Discovering workspaces in {self.config.root}")

        if self.config.type == "turborepo":
            workspaces = self._discover_turborepo_workspaces()
        elif self.config.type == "nx":
            workspaces = self._discover_nx_workspaces()
        elif self.config.type in ["lerna", "pnpm", "yarn"]:
            workspaces = self._discover_npm_workspaces()
        else:
            raise ValueError(f"Unsupported monorepo type: {self.config.type}")

        self.workspaces = workspaces
        self.logger.info(f"Discovered {len(workspaces)} workspaces")

        return workspaces

    def build_dependency_graph(self) -> Dict[str, Set[str]]:
        """
        Build dependency graph between workspaces

        Returns:
            Dictionary of workspace_name -> set of dependent workspace names
        """
        self.logger.info("Building dependency graph")

        graph = {}

        for name, workspace in self.workspaces.items():
            dependencies = set()

            # Check workspace dependencies
            for dep in workspace.dependencies + workspace.dev_dependencies:
                if dep in self.workspaces:
                    dependencies.add(dep)

            graph[name] = dependencies

        self.dependency_graph = graph
        self.logger.info(f"Built dependency graph with {len(graph)} nodes")

        return graph

    def get_affected_workspaces(
        self,
        changed_files: Optional[List[str]] = None,
        base_ref: str = "main"
    ) -> List[str]:
        """
        Get workspaces affected by changes

        Args:
            changed_files: List of changed file paths (optional)
            base_ref: Git reference to compare against

        Returns:
            List of affected workspace names
        """
        self.logger.info(f"Detecting affected workspaces (base: {base_ref})")

        if self.config.type == "turborepo":
            affected = self._get_turborepo_affected(base_ref)
        elif self.config.type == "nx":
            affected = self._get_nx_affected(base_ref)
        else:
            # Fallback: detect from git changes
            affected = self._get_affected_from_git(changed_files, base_ref)

        self.logger.info(f"Found {len(affected)} affected workspaces: {affected}")

        return affected

    def run_task(
        self,
        task: str,
        workspaces: Optional[List[str]] = None,
        parallel: bool = True,
        cache: bool = True
    ) -> Dict[str, Any]:
        """
        Run task across workspaces

        Args:
            task: Task name (e.g., "build", "test", "lint")
            workspaces: Specific workspaces to run on (None = all)
            parallel: Run in parallel
            cache: Use cache if available

        Returns:
            Execution results
        """
        self.logger.info(f"Running task '{task}' on workspaces: {workspaces or 'all'}")

        if self.config.type == "turborepo":
            result = self._run_turborepo_task(task, workspaces, parallel, cache)
        elif self.config.type == "nx":
            result = self._run_nx_task(task, workspaces, parallel, cache)
        else:
            result = self._run_npm_task(task, workspaces, parallel)

        return result

    def get_build_order(self, workspaces: Optional[List[str]] = None) -> List[str]:
        """
        Get topologically sorted build order

        Args:
            workspaces: Specific workspaces to order (None = all)

        Returns:
            Ordered list of workspace names
        """
        if not self.dependency_graph:
            self.build_dependency_graph()

        target_workspaces = set(workspaces) if workspaces else set(self.workspaces.keys())

        # Topological sort
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)

            # Visit dependencies first
            for dep in self.dependency_graph.get(name, set()):
                if dep in target_workspaces:
                    visit(dep)

            order.append(name)

        for workspace in target_workspaces:
            visit(workspace)

        self.logger.info(f"Build order: {order}")

        return order

    # Turborepo-specific methods
    def _discover_turborepo_workspaces(self) -> Dict[str, WorkspaceInfo]:
        """Discover Turborepo workspaces"""
        workspaces = {}

        # Read turbo.json
        turbo_config = self.config.root / "turbo.json"
        if not turbo_config.exists():
            self.logger.warning("turbo.json not found")
            return workspaces

        # Read package.json for workspaces
        package_json = self.config.root / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                data = json.load(f)
                workspace_patterns = data.get("workspaces", [])

                # Find all packages matching patterns
                for pattern in workspace_patterns:
                    pattern_path = self.config.root / pattern
                    for pkg_dir in pattern_path.parent.glob(pattern_path.name):
                        if (pkg_dir / "package.json").exists():
                            ws_info = self._parse_package_json(pkg_dir)
                            if ws_info:
                                workspaces[ws_info.name] = ws_info

        return workspaces

    def _discover_nx_workspaces(self) -> Dict[str, WorkspaceInfo]:
        """Discover Nx workspaces"""
        workspaces = {}

        # Read nx.json
        nx_config = self.config.root / "nx.json"
        if not nx_config.exists():
            self.logger.warning("nx.json not found")
            return workspaces

        # Read workspace.json or project.json files
        workspace_config = self.config.root / "workspace.json"
        if workspace_config.exists():
            with open(workspace_config) as f:
                data = json.load(f)
                projects = data.get("projects", {})

                for name, project_config in projects.items():
                    project_path = self.config.root / project_config
                    if isinstance(project_config, str):
                        # Path to project
                        ws_info = self._create_workspace_info(name, project_path)
                    else:
                        # Inline config
                        ws_info = self._create_workspace_info(
                            name,
                            self.config.root / project_config.get("root", name)
                        )

                    if ws_info:
                        workspaces[name] = ws_info

        # Also check for standalone project.json files
        for project_json in self.config.root.rglob("project.json"):
            if project_json.parent != self.config.root:
                name = project_json.parent.name
                if name not in workspaces:
                    ws_info = self._create_workspace_info(name, project_json.parent)
                    if ws_info:
                        workspaces[name] = ws_info

        return workspaces

    def _discover_npm_workspaces(self) -> Dict[str, WorkspaceInfo]:
        """Discover npm/pnpm/yarn workspaces"""
        workspaces = {}

        # Read package.json
        package_json = self.config.root / "package.json"
        if not package_json.exists():
            self.logger.warning("package.json not found")
            return workspaces

        with open(package_json) as f:
            data = json.load(f)
            workspace_patterns = data.get("workspaces", [])

            # Handle both array and object formats
            if isinstance(workspace_patterns, dict):
                workspace_patterns = workspace_patterns.get("packages", [])

            # Find all packages matching patterns
            for pattern in workspace_patterns:
                pattern_path = self.config.root / pattern
                for pkg_dir in pattern_path.parent.glob(pattern_path.name):
                    if (pkg_dir / "package.json").exists():
                        ws_info = self._parse_package_json(pkg_dir)
                        if ws_info:
                            workspaces[ws_info.name] = ws_info

        return workspaces

    def _parse_package_json(self, pkg_dir: Path) -> Optional[WorkspaceInfo]:
        """Parse package.json and create WorkspaceInfo"""
        package_json = pkg_dir / "package.json"

        try:
            with open(package_json) as f:
                data = json.load(f)

                # Determine workspace type
                ws_type = "package"
                if "main" in data or "module" in data:
                    ws_type = "library"
                if "dependencies" in data and ("react" in data.get("dependencies", {}) or "next" in data.get("dependencies", {})):
                    ws_type = "app"

                return WorkspaceInfo(
                    name=data.get("name", pkg_dir.name),
                    path=pkg_dir,
                    type=ws_type,
                    dependencies=list(data.get("dependencies", {}).keys()),
                    dev_dependencies=list(data.get("devDependencies", {}).keys()),
                    scripts=data.get("scripts", {}),
                    version=data.get("version"),
                    private=data.get("private", False)
                )
        except Exception as e:
            self.logger.warning(f"Error parsing {package_json}: {e}")
            return None

    def _create_workspace_info(self, name: str, path: Path) -> Optional[WorkspaceInfo]:
        """Create WorkspaceInfo from path"""
        # Try package.json first
        if (path / "package.json").exists():
            return self._parse_package_json(path)

        # Fallback: basic info
        return WorkspaceInfo(
            name=name,
            path=path,
            type="package"
        )

    # Task execution methods
    def _run_turborepo_task(
        self,
        task: str,
        workspaces: Optional[List[str]],
        parallel: bool,
        cache: bool
    ) -> Dict[str, Any]:
        """Run Turborepo task"""
        cmd = ["npx", "turbo", "run", task]

        if workspaces:
            cmd.extend(["--filter", ",".join(workspaces)])

        if not cache:
            cmd.append("--force")

        if not parallel:
            cmd.append("--concurrency=1")

        self.logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.root,
                capture_output=True,
                text=True,
                timeout=600
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Task execution timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }

    def _run_nx_task(
        self,
        task: str,
        workspaces: Optional[List[str]],
        parallel: bool,
        cache: bool
    ) -> Dict[str, Any]:
        """Run Nx task"""
        if workspaces:
            # Run on specific projects
            cmd = ["npx", "nx", "run-many", "--target", task, "--projects", ",".join(workspaces)]
        else:
            # Run on all projects
            cmd = ["npx", "nx", "run-many", "--target", task, "--all"]

        if not cache:
            cmd.append("--skip-nx-cache")

        if not parallel:
            cmd.extend(["--parallel", "1"])

        self.logger.info(f"Executing: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.root,
                capture_output=True,
                text=True,
                timeout=600
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Task execution timeout",
                "returncode": -1
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "returncode": -1
            }

    def _run_npm_task(
        self,
        task: str,
        workspaces: Optional[List[str]],
        parallel: bool
    ) -> Dict[str, Any]:
        """Run npm/pnpm/yarn workspace task"""
        results = {}

        target_workspaces = workspaces or list(self.workspaces.keys())

        for ws_name in target_workspaces:
            workspace = self.workspaces.get(ws_name)
            if not workspace:
                continue

            # Check if task exists in scripts
            if task not in workspace.scripts:
                self.logger.warning(f"Task '{task}' not found in {ws_name}")
                continue

            # Determine package manager
            if self.config.type == "pnpm":
                cmd = ["pnpm", "--filter", ws_name, "run", task]
            elif self.config.type == "yarn":
                cmd = ["yarn", "workspace", ws_name, "run", task]
            else:
                cmd = ["npm", "run", task, "--workspace", ws_name]

            self.logger.info(f"Running {task} on {ws_name}: {' '.join(cmd)}")

            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.config.root,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                results[ws_name] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except Exception as e:
                results[ws_name] = {
                    "success": False,
                    "error": str(e),
                    "returncode": -1
                }

        return {
            "success": all(r.get("success", False) for r in results.values()),
            "results": results
        }

    # Affected detection methods
    def _get_turborepo_affected(self, base_ref: str) -> List[str]:
        """Get affected workspaces using Turborepo"""
        # Turborepo uses --filter with git refs
        cmd = ["npx", "turbo", "run", "build", "--dry-run", "--filter", f"...[{base_ref}]"]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.root,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Parse output to extract affected packages
            affected = []
            for line in result.stdout.split('\n'):
                if "•" in line or "●" in line:
                    # Extract package name
                    parts = line.split()
                    if len(parts) > 1:
                        affected.append(parts[1].strip(':'))

            return affected
        except Exception as e:
            self.logger.warning(f"Failed to get Turborepo affected: {e}")
            return []

    def _get_nx_affected(self, base_ref: str) -> List[str]:
        """Get affected workspaces using Nx"""
        cmd = ["npx", "nx", "affected:apps", "--base", base_ref, "--plain"]

        try:
            result = subprocess.run(
                cmd,
                cwd=self.config.root,
                capture_output=True,
                text=True,
                timeout=30
            )

            affected = result.stdout.strip().split()
            return affected
        except Exception as e:
            self.logger.warning(f"Failed to get Nx affected: {e}")
            return []

    def _get_affected_from_git(
        self,
        changed_files: Optional[List[str]],
        base_ref: str
    ) -> List[str]:
        """Determine affected workspaces from git changes"""
        if not changed_files:
            # Get changed files from git
            cmd = ["git", "diff", "--name-only", base_ref]

            try:
                result = subprocess.run(
                    cmd,
                    cwd=self.config.root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                changed_files = result.stdout.strip().split('\n')
            except Exception as e:
                self.logger.warning(f"Failed to get git changes: {e}")
                return []

        # Map changed files to workspaces
        affected = set()

        for file_path in changed_files:
            file_full_path = self.config.root / file_path

            # Find which workspace owns this file
            for ws_name, workspace in self.workspaces.items():
                try:
                    file_full_path.relative_to(workspace.path)
                    affected.add(ws_name)
                    break
                except ValueError:
                    continue

        # Add dependent workspaces
        if self.dependency_graph:
            all_affected = set(affected)
            for ws in affected:
                # Find workspaces that depend on this one
                for name, deps in self.dependency_graph.items():
                    if ws in deps:
                        all_affected.add(name)

            return list(all_affected)

        return list(affected)

    def generate_report(self) -> Dict[str, Any]:
        """Generate monorepo coordination report"""
        return {
            "type": self.config.type,
            "root": str(self.config.root),
            "total_workspaces": len(self.workspaces),
            "workspaces": {
                name: {
                    "path": str(ws.path.relative_to(self.config.root)),
                    "type": ws.type,
                    "dependencies": ws.dependencies,
                    "version": ws.version
                }
                for name, ws in self.workspaces.items()
            },
            "dependency_graph": {
                name: list(deps)
                for name, deps in self.dependency_graph.items()
            }
        }
