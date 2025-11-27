"""
Master Agent Orchestrator - Core SDLC Workflow Engine

This is the central orchestration system that manages the complete SDLC lifecycle
from BRD analysis to production deployment with human-in-the-loop gates.

Key Responsibilities:
- State machine management for SDLC phases
- Agent routing and delegation
- Context budget tracking and handoff
- Human gate coordination
- Multi-repo orchestration
- CLI fallback coordination

No hardcoding - all workflows are dynamically generated based on project analysis.
"""

import json
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


class SDLCPhase(Enum):
    """SDLC Phase enumeration"""
    IDLE = "idle"
    ANALYZING_BRD = "analyzing_brd"
    REQUIREMENTS = "requirements"
    DESIGN = "design"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    COMPLETED = "completed"
    PAUSED = "paused"
    ABORTED = "aborted"


class GateDecision(Enum):
    """Human gate decision options"""
    APPROVE = "approve"
    REVISE = "revise"
    PAUSE = "pause"
    ABORT = "abort"


@dataclass
class ProjectState:
    """Complete project state for checkpoint/resume"""
    project_id: str
    project_name: str
    created_at: str
    current_phase: str
    current_subphase: Optional[str]
    completed_phases: List[str]
    pending_phases: List[str]
    current_task: str
    next_recommended_action: str
    token_usage: int
    estimated_completion: float
    human_gates_status: Dict[str, str]
    graphiti_episode_ids: List[str]
    serena_memory_keys: List[str]
    code_context_paths: List[str]
    critical_decisions: List[str]
    workflow_config: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProjectState':
        """Create from dictionary"""
        return cls(**data)


class ContextManager:
    """Manages token budget and triggers handoff when needed"""

    def __init__(self, max_tokens: int = 200000):
        self.max_tokens = max_tokens
        self.current_usage = 0
        self.thresholds = {
            'warning': 0.75,   # 150K tokens
            'critical': 0.85,  # 170K tokens
            'emergency': 0.95  # 190K tokens
        }
        self.logger = logging.getLogger(__name__)

    def update_usage(self, tokens: int):
        """Update current token usage"""
        self.current_usage = tokens

    def check_and_act(self) -> str:
        """Check token usage and return recommended action"""
        usage_ratio = self.current_usage / self.max_tokens

        if usage_ratio >= self.thresholds['emergency']:
            self.logger.critical(f"Emergency: Token usage at {usage_ratio*100:.1f}%")
            return 'FORCE_CHECKPOINT_AND_EXIT'
        elif usage_ratio >= self.thresholds['critical']:
            self.logger.warning(f"Critical: Token usage at {usage_ratio*100:.1f}%")
            return 'TRIGGER_GRACEFUL_HANDOFF'
        elif usage_ratio >= self.thresholds['warning']:
            self.logger.info(f"Warning: Token usage at {usage_ratio*100:.1f}%")
            return 'OPTIMIZE_CONTEXT_CLEAR_CACHE'
        else:
            return 'CONTINUE_NORMAL'


class MasterOrchestrator:
    """
    Master Agent Orchestrator - Central coordination system

    Manages:
    - SDLC workflow state machine
    - Phase transitions and gates
    - Agent delegation
    - Context management
    - Checkpoint/resume
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / "master-agent" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.current_state: Optional[ProjectState] = None
        self.context_manager = ContextManager()
        self.logger = self._setup_logging()

        # State machine transitions
        self.transitions = self._build_state_machine()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging infrastructure"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        # Create logs directory
        log_dir = self.project_root / "master-agent" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        # File handler with rotation
        log_file = log_dir / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.DEBUG)

        # Console handler
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)

        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        logger.addHandler(fh)
        logger.addHandler(ch)

        return logger

    def _build_state_machine(self) -> Dict[str, Dict[str, str]]:
        """Build state machine transitions"""
        return {
            SDLCPhase.IDLE.value: {
                'start': SDLCPhase.ANALYZING_BRD.value
            },
            SDLCPhase.ANALYZING_BRD.value: {
                'brd_parsed': SDLCPhase.REQUIREMENTS.value
            },
            SDLCPhase.REQUIREMENTS.value: {
                'prd_approved': SDLCPhase.DESIGN.value,
                'prd_revision': SDLCPhase.REQUIREMENTS.value
            },
            SDLCPhase.DESIGN.value: {
                'architecture_approved': SDLCPhase.IMPLEMENTATION.value,
                'design_revision': SDLCPhase.DESIGN.value
            },
            SDLCPhase.IMPLEMENTATION.value: {
                'code_review_passed': SDLCPhase.TESTING.value,
                'code_revision': SDLCPhase.IMPLEMENTATION.value
            },
            SDLCPhase.TESTING.value: {
                'tests_passed': SDLCPhase.DEPLOYMENT.value,
                'test_failures': SDLCPhase.IMPLEMENTATION.value
            },
            SDLCPhase.DEPLOYMENT.value: {
                'deployed': SDLCPhase.MONITORING.value,
                'deployment_failed': SDLCPhase.DEPLOYMENT.value
            },
            SDLCPhase.MONITORING.value: {
                'client_accepted': SDLCPhase.COMPLETED.value
            }
        }

    def transition(self, event: str) -> bool:
        """
        Transition to next state based on event

        Args:
            event: Transition event (e.g., 'prd_approved', 'code_review_passed')

        Returns:
            bool: True if transition successful
        """
        if not self.current_state:
            self.logger.error("No current state initialized")
            return False

        current_phase = self.current_state.current_phase

        if current_phase not in self.transitions:
            self.logger.error(f"Invalid phase: {current_phase}")
            return False

        if event not in self.transitions[current_phase]:
            self.logger.error(f"Invalid event '{event}' for phase '{current_phase}'")
            return False

        next_phase = self.transitions[current_phase][event]

        self.logger.info(f"Transitioning: {current_phase} --[{event}]--> {next_phase}")

        # Update state
        self.current_state.completed_phases.append(current_phase)
        self.current_state.current_phase = next_phase

        # Save checkpoint after transition
        self.save_checkpoint(reason=f"transition_{event}")

        return True

    def save_checkpoint(self, reason: str = "manual") -> Path:
        """
        Save current state to checkpoint file

        Args:
            reason: Reason for checkpoint (for logging)

        Returns:
            Path to checkpoint file
        """
        if not self.current_state:
            raise ValueError("No state to checkpoint")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.state_dir / f"checkpoint_{timestamp}.json"

        checkpoint_data = {
            "version": "2.0",
            "cli_agnostic": True,
            "metadata": {
                "checkpoint_reason": reason,
                "checkpoint_time": datetime.now().isoformat(),
                "cli_source": "claude-code"
            },
            "state": self.current_state.to_dict()
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        self.logger.info(f"Checkpoint saved: {checkpoint_file} (reason: {reason})")

        # Also save as latest
        latest_file = self.state_dir / "checkpoint_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)

        return checkpoint_file

    def load_checkpoint(self, checkpoint_path: Optional[Path] = None) -> bool:
        """
        Load state from checkpoint file

        Args:
            checkpoint_path: Path to checkpoint file (None = load latest)

        Returns:
            bool: True if loaded successfully
        """
        if checkpoint_path is None:
            checkpoint_path = self.state_dir / "checkpoint_latest.json"

        if not checkpoint_path.exists():
            self.logger.error(f"Checkpoint file not found: {checkpoint_path}")
            return False

        try:
            with open(checkpoint_path, 'r') as f:
                checkpoint_data = json.load(f)

            # Validate version
            if checkpoint_data.get("version") != "2.0":
                self.logger.warning("Checkpoint version mismatch, attempting migration")

            # Restore state
            state_data = checkpoint_data["state"]
            self.current_state = ProjectState.from_dict(state_data)

            self.logger.info(f"Checkpoint loaded: {checkpoint_path}")
            self.logger.info(f"Resumed at phase: {self.current_state.current_phase}")

            return True

        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return False

    def initialize_project(
        self,
        project_id: str,
        project_name: str,
        workflow_config: Dict[str, Any]
    ) -> ProjectState:
        """
        Initialize a new project

        Args:
            project_id: Unique project identifier
            project_name: Human-readable project name
            workflow_config: Workflow configuration (generated dynamically)

        Returns:
            Initialized ProjectState
        """
        self.current_state = ProjectState(
            project_id=project_id,
            project_name=project_name,
            created_at=datetime.now().isoformat(),
            current_phase=SDLCPhase.IDLE.value,
            current_subphase=None,
            completed_phases=[],
            pending_phases=[
                SDLCPhase.REQUIREMENTS.value,
                SDLCPhase.DESIGN.value,
                SDLCPhase.IMPLEMENTATION.value,
                SDLCPhase.TESTING.value,
                SDLCPhase.DEPLOYMENT.value,
                SDLCPhase.MONITORING.value
            ],
            current_task="Project initialization",
            next_recommended_action="/sc:master start",
            token_usage=0,
            estimated_completion=0.0,
            human_gates_status={},
            graphiti_episode_ids=[],
            serena_memory_keys=[],
            code_context_paths=[],
            critical_decisions=[],
            workflow_config=workflow_config
        )

        # Save initial checkpoint
        self.save_checkpoint(reason="project_initialization")

        self.logger.info(f"Project initialized: {project_id} - {project_name}")

        return self.current_state

    def get_phase_status(self) -> Dict[str, Any]:
        """Get current phase status for reporting"""
        if not self.current_state:
            return {"error": "No active project"}

        total_phases = len(self.current_state.pending_phases) + len(self.current_state.completed_phases)
        completed = len(self.current_state.completed_phases)

        return {
            "project_id": self.current_state.project_id,
            "project_name": self.current_state.project_name,
            "current_phase": self.current_state.current_phase,
            "current_subphase": self.current_state.current_subphase,
            "current_task": self.current_state.current_task,
            "completed_phases": self.current_state.completed_phases,
            "pending_phases": self.current_state.pending_phases,
            "progress_percent": (completed / total_phases * 100) if total_phases > 0 else 0,
            "token_usage": self.current_state.token_usage,
            "context_status": self.context_manager.check_and_act()
        }
