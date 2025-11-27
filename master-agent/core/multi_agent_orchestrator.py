"""
Multi-Agent Orchestrator

Coordinates tasks across multiple AI agents (Claude, Gemini, Copilot, etc.)

Key Features:
- Intelligent task routing based on agent capabilities
- Parallel task execution across multiple agents
- Consensus-based decision making
- Automatic fallback on failures
- Performance optimization
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import asyncio
import logging

from .agent_registry import (
    get_registry,
    AgentCapability,
    AgentProvider,
    initialize_default_agents
)
from .agent_integrations import (
    get_agent_integration,
    AgentResponse
)

logger = logging.getLogger(__name__)


class TaskType(Enum):
    """Types of tasks that can be orchestrated"""
    CODE_GENERATION = "code_generation"
    CODE_REVIEW = "code_review"
    ARCHITECTURE_DESIGN = "architecture_design"
    SECURITY_AUDIT = "security_audit"
    DOCUMENTATION = "documentation"
    MULTIMODAL_ANALYSIS = "multimodal_analysis"
    REAL_TIME_COLLABORATION = "real_time_collaboration"


@dataclass
class Task:
    """Task to be executed by agents"""
    type: TaskType
    description: str
    context: Dict[str, Any]
    required_capability: AgentCapability
    priority: int = 1
    metadata: Dict[str, Any] = None


@dataclass
class TaskResult:
    """Result from task execution"""
    task: Task
    response: AgentResponse
    agent_name: str
    execution_time_ms: float
    success: bool
    error: Optional[str] = None


class MultiAgentOrchestrator:
    """
    Orchestrates tasks across multiple AI agents

    Strategies:
    1. Single Agent: Route to best agent
    2. Parallel Execution: Multiple agents for same task (consensus)
    3. Sequential Pipeline: Chain agents for complex workflows
    4. Fallback: Try alternative agents on failure
    """

    def __init__(self):
        self.registry = get_registry()
        self.logger = logging.getLogger(f"{__name__}.MultiAgentOrchestrator")

        # Initialize default agents
        initialize_default_agents()

    async def execute_task(
        self,
        task: Task,
        strategy: str = "best_agent"
    ) -> TaskResult:
        """
        Execute task using specified strategy

        Args:
            task: Task to execute
            strategy: Execution strategy
                - "best_agent": Route to single best agent
                - "parallel": Execute on multiple agents (consensus)
                - "fallback": Try fallback agents on failure

        Returns:
            Task result
        """
        if strategy == "best_agent":
            return await self._execute_single(task)
        elif strategy == "parallel":
            return await self._execute_parallel(task)
        elif strategy == "fallback":
            return await self._execute_with_fallback(task)
        else:
            raise ValueError(f"Unknown strategy: {strategy}")

    async def _execute_single(self, task: Task) -> TaskResult:
        """Execute task on single best agent"""
        import time

        start_time = time.time()

        # Get best agent for task
        agent_config = self.registry.get_agent_for_task(task.required_capability)

        if not agent_config:
            return TaskResult(
                task=task,
                response=None,
                agent_name="none",
                execution_time_ms=0,
                success=False,
                error=f"No agent available for {task.required_capability.value}"
            )

        try:
            # Get agent integration
            integration = get_agent_integration(
                provider=agent_config.provider.value,
                api_key=agent_config.api_key,
                model=agent_config.model
            )

            # Execute task
            self.logger.info(
                f"Executing task '{task.type.value}' on {agent_config.name}"
            )

            response = await integration.generate(
                prompt=task.description,
                system_instruction=task.context.get("system"),
                temperature=task.context.get("temperature", 0.7),
                max_tokens=task.context.get("max_tokens", 8192)
            )

            execution_time = (time.time() - start_time) * 1000

            self.logger.info(
                f"Task completed by {agent_config.name} in {execution_time:.2f}ms"
            )

            return TaskResult(
                task=task,
                response=response,
                agent_name=agent_config.name,
                execution_time_ms=execution_time,
                success=True
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            self.logger.error(
                f"Task failed on {agent_config.name}: {e}"
            )

            return TaskResult(
                task=task,
                response=None,
                agent_name=agent_config.name,
                execution_time_ms=execution_time,
                success=False,
                error=str(e)
            )

    async def _execute_parallel(self, task: Task) -> TaskResult:
        """
        Execute task on multiple agents in parallel and get consensus

        Useful for:
        - Code review (multiple perspectives)
        - Security audits (multiple checks)
        - Architecture decisions (multiple opinions)
        """
        # Get all capable agents
        agents = self.registry.get_agents_by_capability(task.required_capability)

        if not agents:
            return TaskResult(
                task=task,
                response=None,
                agent_name="none",
                execution_time_ms=0,
                success=False,
                error=f"No agents available for {task.required_capability.value}"
            )

        self.logger.info(
            f"Executing task in parallel on {len(agents)} agents"
        )

        # Create tasks for each agent
        async_tasks = []
        for agent_config in agents:
            async_tasks.append(self._execute_on_agent(task, agent_config))

        # Execute in parallel
        results = await asyncio.gather(*async_tasks, return_exceptions=True)

        # Filter successful results
        successful_results = [
            r for r in results
            if isinstance(r, TaskResult) and r.success
        ]

        if not successful_results:
            return TaskResult(
                task=task,
                response=None,
                agent_name="parallel_execution",
                execution_time_ms=0,
                success=False,
                error="All agents failed"
            )

        # Get consensus (for now, use first successful result)
        # In production, implement voting/consensus mechanism
        best_result = max(successful_results, key=lambda r: r.response.tokens_used)

        self.logger.info(
            f"Parallel execution: {len(successful_results)}/{len(agents)} "
            f"agents succeeded"
        )

        return best_result

    async def _execute_with_fallback(self, task: Task) -> TaskResult:
        """Execute with automatic fallback to alternative agents"""
        excluded_agents = []
        max_attempts = 3

        for attempt in range(max_attempts):
            agent_config = self.registry.get_agent_for_task(
                task.required_capability,
                exclude_agents=excluded_agents
            )

            if not agent_config:
                return TaskResult(
                    task=task,
                    response=None,
                    agent_name="fallback_execution",
                    execution_time_ms=0,
                    success=False,
                    error=f"No agents available after {attempt + 1} attempts"
                )

            result = await self._execute_on_agent(task, agent_config)

            if result.success:
                return result

            # Add to excluded list and try next agent
            excluded_agents.append(agent_config.name)
            self.logger.warning(
                f"Attempt {attempt + 1} failed on {agent_config.name}, "
                f"trying fallback..."
            )

        return TaskResult(
            task=task,
            response=None,
            agent_name="fallback_execution",
            execution_time_ms=0,
            success=False,
            error=f"All fallback attempts failed after {max_attempts} tries"
        )

    async def _execute_on_agent(self, task: Task, agent_config) -> TaskResult:
        """Helper to execute task on specific agent"""
        import time

        start_time = time.time()

        try:
            integration = get_agent_integration(
                provider=agent_config.provider.value,
                api_key=agent_config.api_key,
                model=agent_config.model
            )

            response = await integration.generate(
                prompt=task.description,
                system_instruction=task.context.get("system"),
                temperature=task.context.get("temperature", 0.7),
                max_tokens=task.context.get("max_tokens", 8192)
            )

            execution_time = (time.time() - start_time) * 1000

            return TaskResult(
                task=task,
                response=response,
                agent_name=agent_config.name,
                execution_time_ms=execution_time,
                success=True
            )

        except Exception as e:
            execution_time = (time.time() - start_time) * 1000

            return TaskResult(
                task=task,
                response=None,
                agent_name=agent_config.name,
                execution_time_ms=execution_time,
                success=False,
                error=str(e)
            )

    async def execute_pipeline(
        self,
        tasks: List[Task]
    ) -> List[TaskResult]:
        """
        Execute sequential pipeline of tasks

        Each task output becomes input to next task

        Example pipeline:
        1. Gemini: Analyze images/diagrams → Extract requirements
        2. Claude: Generate architecture → Create design
        3. Copilot: Generate code → Implement design
        4. Claude: Review code → Ensure quality
        """
        results = []
        context = {}

        for i, task in enumerate(tasks):
            self.logger.info(
                f"Pipeline step {i + 1}/{len(tasks)}: {task.type.value}"
            )

            # Add previous results to context
            task.context["pipeline_context"] = context

            # Execute task
            result = await self.execute_task(task, strategy="fallback")
            results.append(result)

            if not result.success:
                self.logger.error(
                    f"Pipeline failed at step {i + 1}: {result.error}"
                )
                break

            # Add result to context for next task
            context[f"step_{i + 1}"] = {
                "task_type": task.type.value,
                "response": result.response.content,
                "agent": result.agent_name
            }

        return results


# Example usage
async def example_multi_agent_workflow():
    """Example: Multi-agent collaboration for feature development"""
    orchestrator = MultiAgentOrchestrator()

    # Task 1: Gemini analyzes design mockups (multimodal)
    design_task = Task(
        type=TaskType.MULTIMODAL_ANALYSIS,
        description="Analyze UI mockup and extract component requirements",
        context={
            "system": "You are a UI/UX analyst. Extract detailed component specs.",
            "images": ["base64_encoded_mockup_image"]
        },
        required_capability=AgentCapability.MULTIMODAL
    )

    # Task 2: Claude generates component architecture
    architecture_task = Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description="Design React component architecture based on requirements",
        context={
            "system": "You are a frontend architect. Create scalable component design."
        },
        required_capability=AgentCapability.ARCHITECTURE
    )

    # Task 3: Generate code (parallel execution for consensus)
    code_task = Task(
        type=TaskType.CODE_GENERATION,
        description="Implement React components based on architecture",
        context={
            "system": "Generate production-ready React code with TypeScript."
        },
        required_capability=AgentCapability.CODE_GENERATION
    )

    # Task 4: Security audit
    security_task = Task(
        type=TaskType.SECURITY_AUDIT,
        description="Audit code for security vulnerabilities",
        context={
            "system": "Perform comprehensive security audit (OWASP Top 10, XSS, etc.)"
        },
        required_capability=AgentCapability.SECURITY
    )

    # Execute pipeline
    results = await orchestrator.execute_pipeline([
        design_task,
        architecture_task,
        code_task,
        security_task
    ])

    # Print results
    for i, result in enumerate(results):
        print(f"\n{'='*70}")
        print(f"Step {i + 1}: {result.task.type.value}")
        print(f"Agent: {result.agent_name}")
        print(f"Success: {result.success}")
        print(f"Execution time: {result.execution_time_ms:.2f}ms")

        if result.success:
            print(f"Response preview: {result.response.content[:200]}...")
        else:
            print(f"Error: {result.error}")
