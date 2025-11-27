"""
State Management System with Graphiti Integration

Hybrid state management:
- File-based checkpoints for portability and CLI resumption
- Graphiti knowledge graph for temporal querying and decision tracking

This enables:
- Resume from any checkpoint by any CLI (Claude, Gemini, Copilot, Qwen)
- Query historical decisions and architecture evolution
- Learn from past project patterns
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class GraphitiEpisode:
    """Episode data for Graphiti storage"""
    name: str
    content: str
    entities: List[str]
    relationships: List[Dict[str, str]]
    timestamp: str
    metadata: Dict[str, Any]


class StateManager:
    """
    Hybrid State Management System

    Responsibilities:
    - File-based checkpoint persistence
    - Graphiti integration for knowledge graph
    - Cross-CLI state compatibility
    - Decision tracking and learning
    """

    def __init__(self, project_root: Path, enable_graphiti: bool = True):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / "master-agent" / "state"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        self.enable_graphiti = enable_graphiti
        self.logger = self._setup_logging()

        # Graphiti client (lazy initialization)
        self._graphiti_client = None

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        return logger

    @property
    def graphiti_client(self):
        """Lazy load Graphiti client"""
        if self._graphiti_client is None and self.enable_graphiti:
            try:
                # Import Graphiti tools dynamically
                # This will use the MCP tools when available
                self._graphiti_client = GraphitiClient()
                self.logger.info("Graphiti client initialized")
            except Exception as e:
                self.logger.warning(f"Graphiti not available: {e}")
                self.enable_graphiti = False
        return self._graphiti_client

    def save_checkpoint(
        self,
        state_data: Dict[str, Any],
        reason: str = "manual"
    ) -> Path:
        """
        Save checkpoint to file system

        Args:
            state_data: Complete state dictionary
            reason: Reason for checkpoint

        Returns:
            Path to checkpoint file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        checkpoint_file = self.state_dir / f"checkpoint_{timestamp}.json"

        checkpoint = {
            "version": "2.0",
            "cli_agnostic": True,
            "metadata": {
                "checkpoint_reason": reason,
                "checkpoint_time": datetime.now().isoformat(),
                "cli_source": "claude-code"
            },
            "state": state_data,
            "instructions_for_any_llm": self._generate_resume_instructions(state_data)
        }

        with open(checkpoint_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        # Save as latest
        latest_file = self.state_dir / "checkpoint_latest.json"
        with open(latest_file, 'w') as f:
            json.dump(checkpoint, f, indent=2)

        self.logger.info(f"Checkpoint saved: {checkpoint_file}")

        return checkpoint_file

    def load_checkpoint(self, checkpoint_path: Optional[Path] = None) -> Optional[Dict[str, Any]]:
        """
        Load checkpoint from file

        Args:
            checkpoint_path: Path to checkpoint (None = latest)

        Returns:
            State data or None if failed
        """
        if checkpoint_path is None:
            checkpoint_path = self.state_dir / "checkpoint_latest.json"

        if not checkpoint_path.exists():
            self.logger.error(f"Checkpoint not found: {checkpoint_path}")
            return None

        try:
            with open(checkpoint_path, 'r') as f:
                checkpoint = json.load(f)

            self.logger.info(f"Checkpoint loaded: {checkpoint_path}")
            return checkpoint["state"]

        except Exception as e:
            self.logger.error(f"Failed to load checkpoint: {e}")
            return None

    def store_in_graphiti(self, episode: GraphitiEpisode) -> Optional[str]:
        """
        Store episode in Graphiti knowledge graph

        Args:
            episode: GraphitiEpisode data

        Returns:
            Episode ID or None if failed
        """
        if not self.enable_graphiti:
            self.logger.debug("Graphiti disabled, skipping storage")
            return None

        try:
            # Use Graphiti MCP tool to add episode
            # This will be replaced with actual MCP call
            episode_id = self._add_episode_to_graphiti(episode)
            self.logger.info(f"Stored in Graphiti: {episode_id}")
            return episode_id

        except Exception as e:
            self.logger.error(f"Failed to store in Graphiti: {e}")
            return None

    def query_graphiti(
        self,
        query: str,
        limit: int = 10
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Query Graphiti knowledge graph

        Args:
            query: Search query
            limit: Max results

        Returns:
            List of matching nodes/episodes
        """
        if not self.enable_graphiti:
            return None

        try:
            # Use Graphiti search MCP tool
            results = self._search_graphiti(query, limit)
            return results

        except Exception as e:
            self.logger.error(f"Graphiti query failed: {e}")
            return None

    def _add_episode_to_graphiti(self, episode: GraphitiEpisode) -> str:
        """
        Add episode to Graphiti (placeholder for MCP call)

        This will be replaced with actual mcp__graphiti-memory__add_memory call
        """
        # Placeholder: In actual implementation, this calls the MCP tool
        episode_data = {
            "name": episode.name,
            "content": episode.content,
            "entities": episode.entities,
            "relationships": episode.relationships,
            "timestamp": episode.timestamp,
            "metadata": episode.metadata
        }

        # TODO: Replace with actual MCP call
        # result = mcp__graphiti_memory__add_memory(
        #     content=episode.content,
        #     entities=episode.entities,
        #     ...
        # )

        # For now, simulate episode ID
        episode_id = f"ep_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.logger.debug(f"Graphiti episode created: {episode_id}")

        return episode_id

    def _search_graphiti(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """
        Search Graphiti (placeholder for MCP call)

        This will be replaced with actual mcp__graphiti-memory__search_memory_nodes call
        """
        # TODO: Replace with actual MCP call
        # results = mcp__graphiti_memory__search_memory_nodes(
        #     query=query,
        #     limit=limit
        # )

        # For now, return empty list
        return []

    def _generate_resume_instructions(self, state_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate human-readable instructions for any LLM to resume

        This ensures any CLI (Claude, Gemini, Copilot, Qwen) can understand the state
        """
        current_phase = state_data.get("current_phase", "unknown")
        project_name = state_data.get("project_name", "Unknown Project")
        current_task = state_data.get("current_task", "Unknown task")

        return {
            "context": f"This is a {project_name} project currently in {current_phase} phase.",

            "what_was_completed": state_data.get("completed_phases", []),

            "what_needs_doing_next": [
                current_task,
                state_data.get("next_recommended_action", "Continue with current phase")
            ],

            "important_context": [
                f"• Current phase: {current_phase}",
                f"• Progress: {state_data.get('estimated_completion', 0)}%",
                f"• Token usage: {state_data.get('token_usage', 0)}",
                "• All workflows are dynamically generated - no hardcoded paths"
            ],

            "resume_command_suggestions": {
                "claude_code": "/sc:master resume --checkpoint checkpoint_latest.json",
                "gemini_cli": "gemini resume --state checkpoint_latest.json --project .",
                "copilot_cli": "gh copilot resume --checkpoint checkpoint_latest.json",
                "qwen_cli": "qwen-cli resume --checkpoint checkpoint_latest.json"
            },

            "critical_decisions": state_data.get("critical_decisions", []),

            "graphiti_context": {
                "episode_ids": state_data.get("graphiti_episode_ids", []),
                "note": "Use Graphiti to query detailed decision history and architecture evolution"
            }
        }

    def export_for_cli(self, cli_type: str, checkpoint_path: Optional[Path] = None) -> Path:
        """
        Export checkpoint in CLI-specific format

        Args:
            cli_type: 'gemini', 'copilot', 'qwen', or 'universal'
            checkpoint_path: Source checkpoint (None = latest)

        Returns:
            Path to exported file
        """
        state = self.load_checkpoint(checkpoint_path)
        if not state:
            raise ValueError("No checkpoint to export")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        export_file = self.state_dir / f"export_{cli_type}_{timestamp}.json"

        # Base export structure (CLI-agnostic)
        export_data = {
            "version": "2.0",
            "cli_agnostic": True,
            "target_cli": cli_type,
            "exported_at": datetime.now().isoformat(),
            "state": state,
            "instructions": self._generate_resume_instructions(state)
        }

        # CLI-specific adaptations
        if cli_type == "gemini":
            export_data["gemini_config"] = {
                "model": "gemini-1.5-pro",
                "tools": ["mcp_rube", "mcp_serena", "mcp_graphiti"],
                "temperature": 0.7
            }
        elif cli_type == "copilot":
            export_data["copilot_config"] = {
                "agent_mode": "sdlc_orchestrator",
                "workspace_context": True
            }
        elif cli_type == "qwen":
            export_data["qwen_config"] = {
                "model": "qwen-turbo",
                "enable_tools": True
            }

        with open(export_file, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Exported for {cli_type}: {export_file}")
        return export_file

    def get_decision_history(self) -> List[Dict[str, Any]]:
        """
        Get decision history from Graphiti

        Returns:
            List of decisions with context
        """
        if not self.enable_graphiti:
            return []

        # Query Graphiti for decision episodes
        query = "architecture decisions design choices technical decisions"
        results = self.query_graphiti(query, limit=50)

        return results or []


class GraphitiClient:
    """Wrapper for Graphiti MCP integration"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Initialize Graphiti connection
        # This will use MCP tools when available

    def add_episode(self, episode_data: Dict[str, Any]) -> str:
        """Add episode to Graphiti"""
        # Placeholder for MCP tool call
        return f"ep_{datetime.now().strftime('%Y%m%d%H%M%S')}"

    def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Graphiti"""
        # Placeholder for MCP tool call
        return []
