"""
Multi-Repo Coordinator

Expert in managing multi-repository patterns:
- Git submodules coordination
- Git subtrees management
- Cross-repo dependency tracking
- Atomic operations across repositories
- Version synchronization
- Unified workflow orchestration
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import subprocess
import logging

logger = logging.getLogger(__name__)


@dataclass
class RepoConfig:
    """Configuration for a repository in multi-repo setup"""

    name: str
    path: Path
    remote_url: str
    branch: str = "main"
    type: str = "submodule"  # "submodule", "subtree", "independent"
    dependencies: List[str] = field(default_factory=list)
    version: Optional[str] = None
    sync_strategy: str = "manual"  # "manual", "auto", "on_change"


@dataclass
class DependencyGraph:
    """Cross-repository dependency graph"""

    nodes: Dict[str, Set[str]] = field(default_factory=dict)  # repo -> dependent repos
    versions: Dict[str, str] = field(default_factory=dict)  # repo -> version
    conflicts: List[Tuple[str, str, str]] = field(default_factory=list)  # (repo, version1, version2)


class MultiRepoCoordinator:
    """
    Multi-repository coordination and orchestration

    Supports:
    - Git submodules: Nested repositories
    - Git subtrees: Embedded repositories
    - Independent repos: Linked via configuration

    Capabilities:
    - Repository discovery and mapping
    - Cross-repo dependency tracking
    - Atomic update operations
    - Version conflict detection
    - Unified build and test orchestration
    - Selective repository operations
    - Branch synchronization
    """

    def __init__(self, root: Path):
        self.root = root
        self.logger = logging.getLogger(f"{__name__}.MultiRepoCoordinator")
        self.repos: Dict[str, RepoConfig] = {}
        self.dependency_graph = DependencyGraph()

    def discover_repositories(self) -> Dict[str, RepoConfig]:
        """
        Discover all repositories in multi-repo setup

        Returns:
            Dictionary of repo_name -> RepoConfig
        """
        self.logger.info(f"Discovering repositories in {self.root}")

        repos = {}

        # Discover git submodules
        submodules = self._discover_submodules()
        repos.update(submodules)

        # Discover from config file if exists
        config_repos = self._discover_from_config()
        repos.update(config_repos)

        self.repos = repos
        self.logger.info(f"Discovered {len(repos)} repositories")

        return repos

    def build_dependency_graph(self) -> DependencyGraph:
        """
        Build cross-repository dependency graph

        Returns:
            DependencyGraph with nodes, versions, and conflicts
        """
        self.logger.info("Building cross-repo dependency graph")

        graph = DependencyGraph()

        for name, repo in self.repos.items():
            # Get dependencies from repo
            deps = self._extract_repo_dependencies(repo)
            graph.nodes[name] = set(deps)

            # Get version
            version = self._get_repo_version(repo)
            if version:
                graph.versions[name] = version

        # Detect version conflicts
        conflicts = self._detect_version_conflicts(graph)
        graph.conflicts = conflicts

        self.dependency_graph = graph
        self.logger.info(f"Built dependency graph with {len(graph.nodes)} repositories")

        if conflicts:
            self.logger.warning(f"Detected {len(conflicts)} version conflicts")

        return graph

    def sync_repository(
        self,
        repo_name: str,
        branch: Optional[str] = None,
        recursive: bool = False
    ) -> Dict[str, Any]:
        """
        Sync specific repository

        Args:
            repo_name: Repository to sync
            branch: Target branch (None = repo's default)
            recursive: Sync dependencies recursively

        Returns:
            Sync results
        """
        repo = self.repos.get(repo_name)
        if not repo:
            return {"success": False, "error": f"Repository {repo_name} not found"}

        self.logger.info(f"Syncing repository: {repo_name}")

        target_branch = branch or repo.branch

        if repo.type == "submodule":
            result = self._sync_submodule(repo, target_branch)
        elif repo.type == "subtree":
            result = self._sync_subtree(repo, target_branch)
        else:
            result = self._sync_independent_repo(repo, target_branch)

        # Recursively sync dependencies if requested
        if recursive and result.get("success"):
            for dep_name in repo.dependencies:
                if dep_name in self.repos:
                    self.sync_repository(dep_name, branch, recursive=True)

        return result

    def sync_all_repositories(
        self,
        branch: Optional[str] = None,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Sync all repositories

        Args:
            branch: Target branch for all repos (None = each repo's default)
            parallel: Sync in parallel (experimental)

        Returns:
            Sync results for all repositories
        """
        self.logger.info("Syncing all repositories")

        results = {}

        # Get topological order
        order = self._get_sync_order()

        for repo_name in order:
            result = self.sync_repository(repo_name, branch)
            results[repo_name] = result

            if not result.get("success"):
                self.logger.error(f"Failed to sync {repo_name}, stopping")
                break

        return {
            "success": all(r.get("success", False) for r in results.values()),
            "results": results
        }

    def run_command(
        self,
        command: str,
        repos: Optional[List[str]] = None,
        sequential: bool = True
    ) -> Dict[str, Any]:
        """
        Run command across repositories

        Args:
            command: Command to execute
            repos: Specific repositories (None = all)
            sequential: Run sequentially in dependency order

        Returns:
            Command execution results
        """
        target_repos = repos or list(self.repos.keys())

        if sequential:
            order = self._get_sync_order(target_repos)
        else:
            order = target_repos

        results = {}

        for repo_name in order:
            repo = self.repos.get(repo_name)
            if not repo:
                continue

            self.logger.info(f"Running '{command}' in {repo_name}")

            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                results[repo_name] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "returncode": result.returncode
                }
            except subprocess.TimeoutExpired:
                results[repo_name] = {
                    "success": False,
                    "error": "Command timeout",
                    "returncode": -1
                }
            except Exception as e:
                results[repo_name] = {
                    "success": False,
                    "error": str(e),
                    "returncode": -1
                }

        return {
            "success": all(r.get("success", False) for r in results.values()),
            "results": results
        }

    def create_release_branch(
        self,
        branch_name: str,
        base_branch: str = "main"
    ) -> Dict[str, Any]:
        """
        Create release branch across all repositories

        Args:
            branch_name: Name of release branch
            base_branch: Base branch to branch from

        Returns:
            Branch creation results
        """
        self.logger.info(f"Creating release branch '{branch_name}' from '{base_branch}'")

        results = {}

        for repo_name, repo in self.repos.items():
            cmd = f"git checkout {base_branch} && git pull && git checkout -b {branch_name} && git push -u origin {branch_name}"

            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                results[repo_name] = {
                    "success": result.returncode == 0,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except Exception as e:
                results[repo_name] = {
                    "success": False,
                    "error": str(e)
                }

        return {
            "success": all(r.get("success", False) for r in results.values()),
            "results": results
        }

    def get_repository_status(self, repo_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get git status of repositories

        Args:
            repo_name: Specific repository (None = all)

        Returns:
            Repository status information
        """
        if repo_name:
            repos_to_check = {repo_name: self.repos[repo_name]} if repo_name in self.repos else {}
        else:
            repos_to_check = self.repos

        status = {}

        for name, repo in repos_to_check.items():
            try:
                # Get git status
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                changes = result.stdout.strip().split('\n') if result.stdout.strip() else []

                # Get current branch
                branch_result = subprocess.run(
                    ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                current_branch = branch_result.stdout.strip()

                # Get latest commit
                commit_result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                commit_hash = commit_result.stdout.strip()

                status[name] = {
                    "branch": current_branch,
                    "commit": commit_hash,
                    "clean": len(changes) == 0,
                    "changes": changes,
                    "change_count": len(changes)
                }
            except Exception as e:
                status[name] = {
                    "error": str(e)
                }

        return status

    # Private helper methods
    def _discover_submodules(self) -> Dict[str, RepoConfig]:
        """Discover git submodules"""
        repos = {}

        try:
            # Check if .gitmodules exists
            gitmodules = self.root / ".gitmodules"
            if not gitmodules.exists():
                return repos

            # Read .gitmodules
            result = subprocess.run(
                ["git", "config", "--file", ".gitmodules", "--get-regexp", "path"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=10
            )

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                # Parse: submodule.name.path value
                parts = line.split()
                if len(parts) < 2:
                    continue

                # Extract submodule name
                config_key = parts[0]  # e.g., "submodule.backend.path"
                submodule_path = parts[1]

                # Get submodule name
                name_parts = config_key.split('.')
                if len(name_parts) >= 2:
                    name = name_parts[1]
                else:
                    name = submodule_path

                # Get remote URL
                url_result = subprocess.run(
                    ["git", "config", "--file", ".gitmodules", f"submodule.{name}.url"],
                    cwd=self.root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                remote_url = url_result.stdout.strip()

                # Get branch
                branch_result = subprocess.run(
                    ["git", "config", "--file", ".gitmodules", f"submodule.{name}.branch"],
                    cwd=self.root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                branch = branch_result.stdout.strip() or "main"

                repos[name] = RepoConfig(
                    name=name,
                    path=self.root / submodule_path,
                    remote_url=remote_url,
                    branch=branch,
                    type="submodule"
                )

        except Exception as e:
            self.logger.warning(f"Error discovering submodules: {e}")

        return repos

    def _discover_from_config(self) -> Dict[str, RepoConfig]:
        """Discover repositories from multi-repo.json config"""
        repos = {}

        config_file = self.root / "multi-repo.json"
        if not config_file.exists():
            return repos

        try:
            with open(config_file) as f:
                data = json.load(f)

                for repo_data in data.get("repositories", []):
                    name = repo_data.get("name")
                    if not name:
                        continue

                    repos[name] = RepoConfig(
                        name=name,
                        path=self.root / repo_data.get("path", name),
                        remote_url=repo_data.get("remote_url", ""),
                        branch=repo_data.get("branch", "main"),
                        type=repo_data.get("type", "independent"),
                        dependencies=repo_data.get("dependencies", []),
                        version=repo_data.get("version"),
                        sync_strategy=repo_data.get("sync_strategy", "manual")
                    )

        except Exception as e:
            self.logger.warning(f"Error reading multi-repo.json: {e}")

        return repos

    def _extract_repo_dependencies(self, repo: RepoConfig) -> List[str]:
        """Extract dependencies from repository"""
        dependencies = set(repo.dependencies)

        # Check package.json for JavaScript projects
        package_json = repo.path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)

                    for dep in list(data.get("dependencies", {}).keys()):
                        # Check if dependency is another repo in our setup
                        if dep in self.repos:
                            dependencies.add(dep)

            except Exception:
                pass

        # Check requirements.txt for Python projects
        requirements = repo.path / "requirements.txt"
        if requirements.exists():
            try:
                content = requirements.read_text()
                for line in content.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Extract package name
                        pkg_name = line.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        if pkg_name in self.repos:
                            dependencies.add(pkg_name)
            except Exception:
                pass

        return list(dependencies)

    def _get_repo_version(self, repo: RepoConfig) -> Optional[str]:
        """Get repository version"""
        if repo.version:
            return repo.version

        # Try to get version from package.json
        package_json = repo.path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    data = json.load(f)
                    return data.get("version")
            except Exception:
                pass

        # Try to get version from git tag
        try:
            result = subprocess.run(
                ["git", "describe", "--tags", "--abbrev=0"],
                cwd=repo.path,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return None

    def _detect_version_conflicts(self, graph: DependencyGraph) -> List[Tuple[str, str, str]]:
        """Detect version conflicts in dependency graph"""
        conflicts = []

        # Check if multiple repos depend on different versions of same repo
        version_requirements: Dict[str, Set[str]] = {}

        for repo_name, deps in graph.nodes.items():
            for dep in deps:
                if dep in graph.versions:
                    version = graph.versions[dep]
                    if dep not in version_requirements:
                        version_requirements[dep] = set()
                    version_requirements[dep].add(version)

        # Find conflicts
        for repo, versions in version_requirements.items():
            if len(versions) > 1:
                versions_list = list(versions)
                conflicts.append((repo, versions_list[0], versions_list[1]))

        return conflicts

    def _get_sync_order(self, repos: Optional[List[str]] = None) -> List[str]:
        """Get topologically sorted sync order"""
        if not self.dependency_graph.nodes:
            self.build_dependency_graph()

        target_repos = set(repos) if repos else set(self.repos.keys())

        # Topological sort
        visited = set()
        order = []

        def visit(name: str):
            if name in visited:
                return
            visited.add(name)

            # Visit dependencies first
            for dep in self.dependency_graph.nodes.get(name, set()):
                if dep in target_repos:
                    visit(dep)

            order.append(name)

        for repo in target_repos:
            visit(repo)

        return order

    def _sync_submodule(self, repo: RepoConfig, branch: str) -> Dict[str, Any]:
        """Sync git submodule"""
        try:
            # Initialize submodule if needed
            init_result = subprocess.run(
                ["git", "submodule", "init", str(repo.path.relative_to(self.root))],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=30
            )

            # Update submodule
            update_result = subprocess.run(
                ["git", "submodule", "update", "--remote", "--merge", str(repo.path.relative_to(self.root))],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=60
            )

            # Checkout specific branch if needed
            if branch != repo.branch:
                checkout_result = subprocess.run(
                    ["git", "checkout", branch],
                    cwd=repo.path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

            return {
                "success": update_result.returncode == 0,
                "stdout": update_result.stdout,
                "stderr": update_result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _sync_subtree(self, repo: RepoConfig, branch: str) -> Dict[str, Any]:
        """Sync git subtree"""
        try:
            # Pull subtree changes
            result = subprocess.run(
                ["git", "subtree", "pull", "--prefix", str(repo.path.relative_to(self.root)),
                 repo.remote_url, branch, "--squash"],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _sync_independent_repo(self, repo: RepoConfig, branch: str) -> Dict[str, Any]:
        """Sync independent repository"""
        try:
            # Fetch and pull
            cmd = f"git fetch origin && git checkout {branch} && git pull origin {branch}"

            result = subprocess.run(
                cmd,
                shell=True,
                cwd=repo.path,
                capture_output=True,
                text=True,
                timeout=60
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def generate_report(self) -> Dict[str, Any]:
        """Generate multi-repo coordination report"""
        return {
            "root": str(self.root),
            "total_repositories": len(self.repos),
            "repositories": {
                name: {
                    "path": str(repo.path.relative_to(self.root)),
                    "type": repo.type,
                    "branch": repo.branch,
                    "remote_url": repo.remote_url,
                    "dependencies": repo.dependencies,
                    "version": repo.version
                }
                for name, repo in self.repos.items()
            },
            "dependency_graph": {
                "nodes": {
                    name: list(deps)
                    for name, deps in self.dependency_graph.nodes.items()
                },
                "versions": self.dependency_graph.versions,
                "conflicts": [
                    {"repo": repo, "version1": v1, "version2": v2}
                    for repo, v1, v2 in self.dependency_graph.conflicts
                ]
            }
        }

    def save_config(self, filename: str = "multi-repo.json"):
        """Save multi-repo configuration"""
        config_path = self.root / filename

        config = {
            "repositories": [
                {
                    "name": repo.name,
                    "path": str(repo.path.relative_to(self.root)),
                    "remote_url": repo.remote_url,
                    "branch": repo.branch,
                    "type": repo.type,
                    "dependencies": repo.dependencies,
                    "version": repo.version,
                    "sync_strategy": repo.sync_strategy
                }
                for repo in self.repos.values()
            ]
        }

        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        self.logger.info(f"Configuration saved to {config_path}")
