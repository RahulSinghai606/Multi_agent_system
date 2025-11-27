"""
Master Agent Core Module

Provides:
- Agent orchestration and coordination
- Multi-agent registry and management
- Agent integrations (Claude, Gemini, Copilot, OpenAI)
- SDLC workflow orchestration
"""

from .orchestrator import AgentOrchestrator
from .agent_registry import (
    AgentRegistry,
    AgentProvider,
    AgentCapability,
    AgentConfig,
    AgentHealth,
    get_registry,
    initialize_default_agents
)
from .agent_integrations import (
    GeminiIntegration,
    CopilotIntegration,
    OpenAIIntegration,
    AgentResponse,
    get_agent_integration
)
from .multi_agent_orchestrator import (
    MultiAgentOrchestrator,
    Task,
    TaskType,
    TaskResult
)

__all__ = [
    # Core orchestrator
    'AgentOrchestrator',

    # Multi-agent registry
    'AgentRegistry',
    'AgentProvider',
    'AgentCapability',
    'AgentConfig',
    'AgentHealth',
    'get_registry',
    'initialize_default_agents',

    # Agent integrations
    'GeminiIntegration',
    'CopilotIntegration',
    'OpenAIIntegration',
    'AgentResponse',
    'get_agent_integration',

    # Multi-agent orchestration
    'MultiAgentOrchestrator',
    'Task',
    'TaskType',
    'TaskResult',
]
