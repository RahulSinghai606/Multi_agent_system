"""
CLI Adapter Factory

Generates CLI-specific checkpoint formats for resumption across different platforms:
- Gemini CLI (Google)
- GitHub Copilot CLI (Microsoft)
- Qwen CLI (Alibaba)
- Universal (any LLM)

All adapters use the same core state format but add CLI-specific metadata.
"""

import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class CLIAdapter(ABC):
    """Base class for CLI-specific adapters"""

    def __init__(self, cli_name: str):
        self.cli_name = cli_name
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def export(self, state: Dict[str, Any], output_path: Path) -> Path:
        """Export state in CLI-specific format"""
        pass

    @abstractmethod
    def generate_resume_command(self, checkpoint_path: Path) -> str:
        """Generate CLI-specific resume command"""
        pass

    def _get_base_export(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Get base export structure (CLI-agnostic)"""
        return {
            "version": "2.0",
            "cli_agnostic": True,
            "target_cli": self.cli_name,
            "exported_at": datetime.now().isoformat(),
            "state": state,
            "instructions": self._generate_instructions(state)
        }

    def _generate_instructions(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Generate human-readable instructions for any LLM"""
        return {
            "context": f"Project: {state.get('project_name', 'Unknown')}, Phase: {state.get('current_phase', 'Unknown')}",
            "current_task": state.get("current_task", "Continue workflow"),
            "next_action": state.get("next_recommended_action", "Resume from checkpoint"),
            "completed": state.get("completed_phases", []),
            "pending": state.get("pending_phases", []),
            "important_notes": [
                "All workflows are dynamically generated - no hardcoded paths",
                "Use Graphiti for decision history and architecture evolution",
                "Serena memory contains code context and project structure"
            ]
        }


class GeminiAdapter(CLIAdapter):
    """Adapter for Gemini CLI"""

    def __init__(self):
        super().__init__("gemini")

    def export(self, state: Dict[str, Any], output_path: Path) -> Path:
        """Export for Gemini CLI"""
        export_data = self._get_base_export(state)

        # Add Gemini-specific configuration
        export_data["gemini_config"] = {
            "model": "gemini-1.5-pro",
            "tools": ["mcp_rube", "mcp_serena", "mcp_graphiti", "mcp_sequential"],
            "temperature": 0.7,
            "top_p": 0.95,
            "top_k": 40,
            "safety_settings": {
                "harassment": "BLOCK_NONE",
                "hate": "BLOCK_NONE",
                "sexual": "BLOCK_NONE",
                "dangerous": "BLOCK_NONE"
            }
        }

        # Add Gemini-specific resume instructions
        export_data["gemini_instructions"] = {
            "setup": [
                "Ensure Gemini CLI is installed and authenticated",
                "Verify MCP servers are accessible",
                "Load project context from state"
            ],
            "resume_steps": [
                "1. Load checkpoint state",
                "2. Retrieve Graphiti episodes for context",
                "3. Load Serena project memory",
                "4. Resume from current phase",
                "5. Follow workflow_config for next steps"
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Gemini export created: {output_path}")
        return output_path

    def generate_resume_command(self, checkpoint_path: Path) -> str:
        """Generate Gemini CLI resume command"""
        return f"""gemini resume \\
  --state {checkpoint_path} \\
  --project {checkpoint_path.parent.parent} \\
  --tools mcp_rube,mcp_serena,mcp_graphiti,mcp_sequential \\
  --model gemini-1.5-pro"""


class CopilotAdapter(CLIAdapter):
    """Adapter for GitHub Copilot CLI"""

    def __init__(self):
        super().__init__("copilot")

    def export(self, state: Dict[str, Any], output_path: Path) -> Path:
        """Export for GitHub Copilot CLI"""
        export_data = self._get_base_export(state)

        # Add Copilot-specific configuration
        export_data["copilot_config"] = {
            "agent_mode": "sdlc_orchestrator",
            "workspace_context": True,
            "github_integration": True,
            "pr_automation": True,
            "issue_tracking": True
        }

        # Add Copilot-specific instructions
        export_data["copilot_instructions"] = {
            "github_context": {
                "repo_urls": self._extract_repo_urls(state),
                "branch_strategy": state.get("workflow_config", {}).get("repo_structure", "single_repo")
            },
            "workflow_integration": {
                "use_github_actions": True,
                "auto_pr_creation": True,
                "code_review_automation": True
            }
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Copilot export created: {output_path}")
        return output_path

    def generate_resume_command(self, checkpoint_path: Path) -> str:
        """Generate Copilot CLI resume command"""
        return f"""gh copilot resume \\
  --checkpoint {checkpoint_path} \\
  --workspace {checkpoint_path.parent.parent} \\
  --agent-mode sdlc_orchestrator"""

    def _extract_repo_urls(self, state: Dict[str, Any]) -> List[str]:
        """Extract repository URLs from state"""
        # TODO: Extract from workflow_config or project metadata
        return []


class QwenAdapter(CLIAdapter):
    """Adapter for Qwen CLI"""

    def __init__(self):
        super().__init__("qwen")

    def export(self, state: Dict[str, Any], output_path: Path) -> Path:
        """Export for Qwen CLI"""
        export_data = self._get_base_export(state)

        # Add Qwen-specific configuration
        export_data["qwen_config"] = {
            "model": "qwen-turbo",
            "enable_tools": True,
            "enable_plugins": True,
            "max_tokens": 8000,
            "temperature": 0.7
        }

        # Add Qwen-specific instructions
        export_data["qwen_instructions"] = {
            "plugin_requirements": [
                "Document analysis plugin",
                "Code generation plugin",
                "API integration plugin"
            ],
            "tool_configuration": {
                "enable_web_search": False,
                "enable_code_interpreter": True,
                "enable_file_operations": True
            }
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Qwen export created: {output_path}")
        return output_path

    def generate_resume_command(self, checkpoint_path: Path) -> str:
        """Generate Qwen CLI resume command"""
        return f"""qwen-cli resume \\
  --checkpoint {checkpoint_path} \\
  --project-dir {checkpoint_path.parent.parent} \\
  --model qwen-turbo \\
  --enable-tools"""


class UniversalAdapter(CLIAdapter):
    """Universal adapter for any LLM CLI"""

    def __init__(self):
        super().__init__("universal")

    def export(self, state: Dict[str, Any], output_path: Path) -> Path:
        """Export in universal format"""
        export_data = self._get_base_export(state)

        # Add comprehensive instructions for any LLM
        export_data["universal_instructions"] = {
            "how_to_resume": [
                "1. Load this checkpoint file",
                "2. Read the 'state' object for current progress",
                "3. Read 'instructions' for human-readable context",
                "4. Query Graphiti using episode_ids for detailed history",
                "5. Load Serena memory using memory_keys for code context",
                "6. Follow 'next_recommended_action' to continue",
                "7. Respect 'workflow_config' for project-specific settings"
            ],
            "key_principles": [
                "NO HARDCODING - All workflows are dynamic",
                "Use Graphiti for temporal context and decisions",
                "Use Serena for code semantics and project memory",
                "Respect human gates - always ask for approval",
                "Save checkpoints frequently (every 30 min or phase completion)"
            ],
            "required_capabilities": [
                "File read/write operations",
                "MCP server integration (Rube, Serena, Graphiti, Sequential)",
                "Code generation and editing",
                "Human interaction (AskUserQuestion equivalent)"
            ]
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        self.logger.info(f"Universal export created: {output_path}")
        return output_path

    def generate_resume_command(self, checkpoint_path: Path) -> str:
        """Generate universal resume command"""
        return f"""# Universal resume command (adapt for your CLI)
# Load checkpoint: {checkpoint_path}
# Read state.current_phase for resume point
# Execute state.next_recommended_action"""


class AdapterFactory:
    """Factory for creating CLI-specific adapters"""

    _adapters = {
        "gemini": GeminiAdapter,
        "copilot": CopilotAdapter,
        "qwen": QwenAdapter,
        "universal": UniversalAdapter
    }

    @classmethod
    def create(cls, cli_type: str) -> CLIAdapter:
        """
        Create adapter for specified CLI

        Args:
            cli_type: 'gemini', 'copilot', 'qwen', or 'universal'

        Returns:
            CLIAdapter instance

        Raises:
            ValueError: If cli_type not supported
        """
        if cli_type not in cls._adapters:
            raise ValueError(
                f"Unsupported CLI type: {cli_type}. "
                f"Supported: {list(cls._adapters.keys())}"
            )

        return cls._adapters[cli_type]()

    @classmethod
    def export_for_all(
        cls,
        state: Dict[str, Any],
        output_dir: Path
    ) -> Dict[str, Path]:
        """
        Export checkpoint for all supported CLIs

        Args:
            state: Project state
            output_dir: Directory for exports

        Returns:
            Dict mapping CLI name to export file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        exports = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for cli_type in cls._adapters.keys():
            adapter = cls.create(cli_type)
            output_path = output_dir / f"export_{cli_type}_{timestamp}.json"
            export_path = adapter.export(state, output_path)
            exports[cli_type] = export_path

        return exports
