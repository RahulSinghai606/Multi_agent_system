"""
Multi-Agent Registry

Manages multiple AI agents (Claude, Gemini, Copilot, etc.) and coordinates their collaboration.

Supports:
- Agent registration and discovery
- Task routing based on agent capabilities
- Load balancing across agents
- Fallback mechanisms
- Agent health monitoring
"""

from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class AgentProvider(Enum):
    """Supported AI agent providers"""
    CLAUDE = "claude"  # Primary orchestrator
    GEMINI = "gemini"  # Google's Gemini
    COPILOT = "copilot"  # GitHub Copilot
    OPENAI = "openai"  # ChatGPT/GPT-4
    CUSTOM = "custom"  # Custom agents


class AgentCapability(Enum):
    """Agent capabilities for task routing"""
    # Master Agent personas
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE = "architecture"
    SECURITY = "security"
    FRONTEND = "frontend"
    BACKEND = "backend"
    DEVOPS = "devops"
    TESTING = "testing"
    DOCUMENTATION = "documentation"

    # Specialized capabilities
    MULTIMODAL = "multimodal"  # Images, audio, video
    LONG_CONTEXT = "long_context"  # Large codebases
    REAL_TIME = "real_time"  # Live collaboration
    CODE_COMPLETION = "code_completion"  # IDE integration


@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    provider: AgentProvider
    name: str
    api_key: str
    model: Optional[str] = None
    capabilities: List[AgentCapability] = field(default_factory=list)
    max_tokens: int = 100000
    temperature: float = 0.7
    endpoint: Optional[str] = None
    priority: int = 1  # Higher = preferred for tasks
    enabled: bool = True


@dataclass
class AgentHealth:
    """Agent health status"""
    agent_name: str
    is_healthy: bool
    last_check: datetime
    response_time_ms: float
    error_rate: float
    success_count: int
    failure_count: int


class AgentRegistry:
    """
    Multi-agent registry and coordinator

    Manages multiple AI agents and routes tasks based on:
    - Agent capabilities
    - Current load
    - Health status
    - Priority
    """

    def __init__(self):
        self.agents: Dict[str, AgentConfig] = {}
        self.health_status: Dict[str, AgentHealth] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.logger = logging.getLogger(f"{__name__}.AgentRegistry")

    def register_agent(self, config: AgentConfig):
        """Register an AI agent"""
        self.agents[config.name] = config
        self.health_status[config.name] = AgentHealth(
            agent_name=config.name,
            is_healthy=True,
            last_check=datetime.now(),
            response_time_ms=0.0,
            error_rate=0.0,
            success_count=0,
            failure_count=0
        )
        self.logger.info(f"Registered agent: {config.name} ({config.provider.value})")

    def get_agent_for_task(
        self,
        required_capability: AgentCapability,
        exclude_agents: Optional[List[str]] = None
    ) -> Optional[AgentConfig]:
        """
        Get best agent for a task based on capability and health

        Selection criteria:
        1. Has required capability
        2. Is healthy and enabled
        3. Not in exclude list
        4. Highest priority
        5. Lowest current load
        """
        exclude_agents = exclude_agents or []

        candidates = [
            (name, agent) for name, agent in self.agents.items()
            if (
                required_capability in agent.capabilities
                and agent.enabled
                and name not in exclude_agents
                and self.health_status[name].is_healthy
            )
        ]

        if not candidates:
            self.logger.warning(
                f"No healthy agents found for capability: {required_capability.value}"
            )
            return None

        # Sort by priority (descending), then error rate (ascending)
        candidates.sort(
            key=lambda x: (
                -x[1].priority,
                self.health_status[x[0]].error_rate
            )
        )

        selected_name, selected_agent = candidates[0]
        self.logger.info(
            f"Selected agent '{selected_name}' for {required_capability.value}"
        )

        return selected_agent

    def get_agents_by_capability(
        self,
        capability: AgentCapability
    ) -> List[AgentConfig]:
        """Get all agents with specific capability"""
        return [
            agent for agent in self.agents.values()
            if capability in agent.capabilities and agent.enabled
        ]

    async def execute_with_fallback(
        self,
        task: Dict[str, Any],
        required_capability: AgentCapability,
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Execute task with automatic fallback to other agents on failure

        Args:
            task: Task to execute
            required_capability: Required agent capability
            max_retries: Maximum retry attempts

        Returns:
            Task result from successful agent
        """
        excluded = []

        for attempt in range(max_retries):
            agent = self.get_agent_for_task(required_capability, exclude_agents=excluded)

            if not agent:
                raise RuntimeError(
                    f"No available agents for {required_capability.value} "
                    f"after {attempt + 1} attempts"
                )

            try:
                self.logger.info(
                    f"Attempt {attempt + 1}: Executing task with {agent.name}"
                )

                result = await self._execute_task(agent, task)

                # Update health status on success
                self._update_health_success(agent.name)

                return result

            except Exception as e:
                self.logger.error(
                    f"Agent {agent.name} failed: {e}. "
                    f"Attempting fallback (attempt {attempt + 1}/{max_retries})"
                )

                # Update health status on failure
                self._update_health_failure(agent.name)

                # Exclude failed agent from next attempt
                excluded.append(agent.name)

        raise RuntimeError(
            f"All agents failed for {required_capability.value} "
            f"after {max_retries} attempts"
        )

    async def _execute_task(
        self,
        agent: AgentConfig,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute task on specific agent (to be implemented by integrations)"""
        # This will be implemented by specific agent integrations
        # See agent_integrations.py for implementations
        raise NotImplementedError(
            "Task execution must be implemented by agent integrations"
        )

    def _update_health_success(self, agent_name: str):
        """Update agent health on successful task"""
        health = self.health_status[agent_name]
        health.success_count += 1
        health.error_rate = health.failure_count / (health.success_count + health.failure_count)
        health.last_check = datetime.now()

    def _update_health_failure(self, agent_name: str):
        """Update agent health on failed task"""
        health = self.health_status[agent_name]
        health.failure_count += 1
        health.error_rate = health.failure_count / (health.success_count + health.failure_count)
        health.last_check = datetime.now()

        # Mark as unhealthy if error rate too high
        if health.error_rate > 0.5:  # 50% error rate
            health.is_healthy = False
            self.logger.warning(
                f"Agent {agent_name} marked unhealthy. "
                f"Error rate: {health.error_rate:.2%}"
            )

    def get_health_report(self) -> Dict[str, Any]:
        """Get comprehensive health report for all agents"""
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "healthy_agents": sum(
                1 for h in self.health_status.values() if h.is_healthy
            ),
            "agents": {
                name: {
                    "provider": self.agents[name].provider.value,
                    "healthy": health.is_healthy,
                    "success_count": health.success_count,
                    "failure_count": health.failure_count,
                    "error_rate": f"{health.error_rate:.2%}",
                    "last_check": health.last_check.isoformat()
                }
                for name, health in self.health_status.items()
            }
        }


# Global registry instance
_registry = None


def get_registry() -> AgentRegistry:
    """Get global agent registry instance"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry


def initialize_default_agents():
    """
    Initialize default multi-agent configuration

    This should be called during Master Agent startup
    """
    registry = get_registry()

    # Claude (Primary - Master Agent orchestrator)
    registry.register_agent(AgentConfig(
        provider=AgentProvider.CLAUDE,
        name="claude-sonnet",
        api_key="${ANTHROPIC_API_KEY}",
        model="claude-sonnet-4-5",
        capabilities=[
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_REVIEW,
            AgentCapability.ARCHITECTURE,
            AgentCapability.SECURITY,
            AgentCapability.FRONTEND,
            AgentCapability.BACKEND,
            AgentCapability.DEVOPS,
            AgentCapability.TESTING,
            AgentCapability.DOCUMENTATION,
            AgentCapability.LONG_CONTEXT  # 200K tokens
        ],
        max_tokens=200000,
        priority=10,  # Highest priority
        enabled=True
    ))

    # Gemini (Google - Multimodal + long context)
    registry.register_agent(AgentConfig(
        provider=AgentProvider.GEMINI,
        name="gemini-pro",
        api_key="${GOOGLE_API_KEY}",
        model="gemini-2.0-flash-exp",
        capabilities=[
            AgentCapability.CODE_GENERATION,
            AgentCapability.MULTIMODAL,  # Images, audio, video
            AgentCapability.LONG_CONTEXT,  # 1M+ tokens
            AgentCapability.REAL_TIME
        ],
        max_tokens=1000000,
        endpoint="https://generativelanguage.googleapis.com/v1beta",
        priority=8,
        enabled=True
    ))

    # GitHub Copilot (Code completion specialist)
    registry.register_agent(AgentConfig(
        provider=AgentProvider.COPILOT,
        name="copilot",
        api_key="${GITHUB_TOKEN}",
        model="gpt-4",
        capabilities=[
            AgentCapability.CODE_COMPLETION,
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_REVIEW
        ],
        max_tokens=8000,
        priority=7,
        enabled=True
    ))

    # OpenAI (GPT-4 - General purpose)
    registry.register_agent(AgentConfig(
        provider=AgentProvider.OPENAI,
        name="gpt-4",
        api_key="${OPENAI_API_KEY}",
        model="gpt-4-turbo",
        capabilities=[
            AgentCapability.CODE_GENERATION,
            AgentCapability.CODE_REVIEW,
            AgentCapability.DOCUMENTATION
        ],
        max_tokens=128000,
        priority=6,
        enabled=False  # Disabled by default, enable if needed
    ))

    logger.info("Default multi-agent configuration initialized")
