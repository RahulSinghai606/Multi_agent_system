"""
Multi-Repo Coordination System

Handles:
- Monorepo patterns (Turborepo, Nx)
- Multi-repo patterns (Git submodules, Git subtrees)
- Cross-repo dependency tracking
- Unified workflow orchestration
- Atomic operations across repositories

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Master Agent Orchestration Team"

from .monorepo_coordinator import MonorepoCoordinator, MonorepoConfig, WorkspaceInfo
from .multi_repo_coordinator import MultiRepoCoordinator, RepoConfig, DependencyGraph
from .dependency_tracker import DependencyTracker, Dependency, DependencyType

__all__ = [
    "MonorepoCoordinator",
    "MonorepoConfig",
    "WorkspaceInfo",
    "MultiRepoCoordinator",
    "RepoConfig",
    "DependencyGraph",
    "DependencyTracker",
    "Dependency",
    "DependencyType",
]
