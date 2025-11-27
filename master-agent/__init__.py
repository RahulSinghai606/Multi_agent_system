"""
Master Agent - SDLC Orchestration System

Complete orchestration framework for software development lifecycle:
- Dynamic workflow generation (no hardcoding)
- Human-in-the-loop gates at all phases
- Multi-repo support (monorepo and multi-repo patterns)
- CLI fallback (Gemini, Copilot, Qwen, Universal)
- Graphiti knowledge graph integration
- Serena project memory integration
- SOC2 compliance automation
- World-class 3D glassmorphism UI generation

Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Master Agent Development Team"

from pathlib import Path

# Core components
from .core.orchestrator import MasterOrchestrator, SDLCPhase, ProjectState
from .state.state_manager import StateManager, GraphitiEpisode
from .workflows.workflow_generator import (
    WorkflowGenerator,
    BRDAnalyzer,
    ProjectType,
    ComplexityLevel,
    WorkflowConfig
)
from .gates.gate_manager import (
    GateManager,
    GateDecision,
    GateStatus,
    GateConfig,
    create_standard_gates
)
from .cli_adapters.adapter_factory import AdapterFactory, CLIAdapter

__all__ = [
    # Core
    "MasterOrchestrator",
    "SDLCPhase",
    "ProjectState",

    # State Management
    "StateManager",
    "GraphitiEpisode",

    # Workflow Generation
    "WorkflowGenerator",
    "BRDAnalyzer",
    "ProjectType",
    "ComplexityLevel",
    "WorkflowConfig",

    # Gates
    "GateManager",
    "GateDecision",
    "GateStatus",
    "GateConfig",
    "create_standard_gates",

    # CLI Adapters
    "AdapterFactory",
    "CLIAdapter",
]


def get_project_root() -> Path:
    """Get project root directory"""
    return Path(__file__).parent.parent


def initialize_master_agent(project_root: Optional[Path] = None) -> MasterOrchestrator:
    """
    Initialize Master Agent orchestrator

    Args:
        project_root: Project root directory (None = current directory)

    Returns:
        Initialized MasterOrchestrator
    """
    if project_root is None:
        project_root = get_project_root()

    return MasterOrchestrator(project_root)
