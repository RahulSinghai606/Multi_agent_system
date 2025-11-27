#!/usr/bin/env python3
"""
Multi-Agent System Test Suite

Tests for multi-agent orchestration, agent registry, and integrations.

Usage:
    pytest tests/test_multi_agent.py -v
    python -m pytest tests/test_multi_agent.py --cov=core
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core import (
    MultiAgentOrchestrator,
    Task,
    TaskType,
    TaskResult,
    AgentCapability,
    AgentProvider,
    AgentConfig,
    AgentRegistry,
    AgentResponse,
    get_registry,
    initialize_default_agents
)


class TestAgentRegistry:
    """Test AgentRegistry functionality"""

    def test_register_agent(self):
        """Test agent registration"""
        registry = AgentRegistry()

        config = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="test-claude",
            api_key="test-key",
            model="claude-3-5-sonnet-20241022",
            capabilities=[AgentCapability.CODE_GENERATION],
            priority=10
        )

        registry.register_agent(config)

        assert "test-claude" in registry.agents
        assert registry.agents["test-claude"] == config
        assert "test-claude" in registry.health_status

    def test_get_agent_for_task(self):
        """Test agent selection based on capability"""
        registry = AgentRegistry()

        # Register multiple agents
        claude = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="claude",
            api_key="key1",
            capabilities=[AgentCapability.CODE_GENERATION, AgentCapability.ARCHITECTURE],
            priority=10
        )

        gemini = AgentConfig(
            provider=AgentProvider.GEMINI,
            name="gemini",
            api_key="key2",
            capabilities=[AgentCapability.MULTIMODAL],
            priority=8
        )

        registry.register_agent(claude)
        registry.register_agent(gemini)

        # Test capability matching
        agent = registry.get_agent_for_task(AgentCapability.CODE_GENERATION)
        assert agent.name == "claude"

        agent = registry.get_agent_for_task(AgentCapability.MULTIMODAL)
        assert agent.name == "gemini"

        # Test no match
        agent = registry.get_agent_for_task(AgentCapability.REAL_TIME)
        assert agent is None

    def test_get_agent_priority(self):
        """Test that highest priority agent is selected"""
        registry = AgentRegistry()

        low_priority = AgentConfig(
            provider=AgentProvider.OPENAI,
            name="low",
            api_key="key1",
            capabilities=[AgentCapability.CODE_GENERATION],
            priority=5
        )

        high_priority = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="high",
            api_key="key2",
            capabilities=[AgentCapability.CODE_GENERATION],
            priority=10
        )

        registry.register_agent(low_priority)
        registry.register_agent(high_priority)

        agent = registry.get_agent_for_task(AgentCapability.CODE_GENERATION)
        assert agent.name == "high"

    def test_exclude_agents(self):
        """Test agent exclusion from selection"""
        registry = AgentRegistry()

        agent1 = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="agent1",
            api_key="key1",
            capabilities=[AgentCapability.CODE_GENERATION],
            priority=10
        )

        agent2 = AgentConfig(
            provider=AgentProvider.GEMINI,
            name="agent2",
            api_key="key2",
            capabilities=[AgentCapability.CODE_GENERATION],
            priority=8
        )

        registry.register_agent(agent1)
        registry.register_agent(agent2)

        # Without exclusion
        agent = registry.get_agent_for_task(AgentCapability.CODE_GENERATION)
        assert agent.name == "agent1"

        # With exclusion
        agent = registry.get_agent_for_task(
            AgentCapability.CODE_GENERATION,
            exclude_agents=["agent1"]
        )
        assert agent.name == "agent2"

    def test_health_monitoring(self):
        """Test agent health tracking"""
        registry = AgentRegistry()

        config = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="test-agent",
            api_key="key",
            capabilities=[AgentCapability.CODE_GENERATION]
        )

        registry.register_agent(config)

        # Initial health
        health = registry.health_status["test-agent"]
        assert health.is_healthy is True
        assert health.success_count == 0
        assert health.failure_count == 0

        # Success updates
        registry._update_health_success("test-agent")
        health = registry.health_status["test-agent"]
        assert health.success_count == 1
        assert health.error_rate == 0.0

        # Failure updates
        registry._update_health_failure("test-agent")
        health = registry.health_status["test-agent"]
        assert health.failure_count == 1
        assert health.error_rate == 0.5  # 1 failure / 2 total

    def test_health_degradation(self):
        """Test agent marked unhealthy at high error rate"""
        registry = AgentRegistry()

        config = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="failing-agent",
            api_key="key",
            capabilities=[AgentCapability.CODE_GENERATION]
        )

        registry.register_agent(config)

        # Simulate failures
        for _ in range(10):
            registry._update_health_failure("failing-agent")

        health = registry.health_status["failing-agent"]
        assert health.is_healthy is False  # Should be marked unhealthy
        assert health.error_rate == 1.0

    def test_get_health_report(self):
        """Test health report generation"""
        registry = AgentRegistry()

        agent1 = AgentConfig(
            provider=AgentProvider.CLAUDE,
            name="healthy",
            api_key="key1",
            capabilities=[AgentCapability.CODE_GENERATION]
        )

        agent2 = AgentConfig(
            provider=AgentProvider.GEMINI,
            name="unhealthy",
            api_key="key2",
            capabilities=[AgentCapability.MULTIMODAL]
        )

        registry.register_agent(agent1)
        registry.register_agent(agent2)

        # Make one unhealthy
        for _ in range(10):
            registry._update_health_failure("unhealthy")

        report = registry.get_health_report()

        assert report["total_agents"] == 2
        assert report["healthy_agents"] == 1
        assert "healthy" in report["agents"]
        assert "unhealthy" in report["agents"]
        assert report["agents"]["healthy"]["healthy"] is True
        assert report["agents"]["unhealthy"]["healthy"] is False


class TestMultiAgentOrchestrator:
    """Test MultiAgentOrchestrator functionality"""

    @pytest.mark.asyncio
    async def test_execute_single_task_success(self):
        """Test successful single agent execution"""
        orchestrator = MultiAgentOrchestrator()

        # Mock agent integration
        mock_response = AgentResponse(
            content="Generated code",
            model="claude-3-5-sonnet-20241022",
            tokens_used=100,
            finish_reason="stop",
            metadata={}
        )

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.return_value = mock_response
            mock_get_integration.return_value = mock_integration

            task = Task(
                type=TaskType.CODE_GENERATION,
                description="Write a function",
                context={},
                required_capability=AgentCapability.CODE_GENERATION
            )

            result = await orchestrator._execute_single(task)

            assert result.success is True
            assert result.response.content == "Generated code"
            assert result.response.tokens_used == 100

    @pytest.mark.asyncio
    async def test_execute_single_task_failure(self):
        """Test failed single agent execution"""
        orchestrator = MultiAgentOrchestrator()

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.side_effect = Exception("API Error")
            mock_get_integration.return_value = mock_integration

            task = Task(
                type=TaskType.CODE_GENERATION,
                description="Write a function",
                context={},
                required_capability=AgentCapability.CODE_GENERATION
            )

            result = await orchestrator._execute_single(task)

            assert result.success is False
            assert "API Error" in result.error

    @pytest.mark.asyncio
    async def test_execute_parallel(self):
        """Test parallel execution across multiple agents"""
        orchestrator = MultiAgentOrchestrator()

        mock_response = AgentResponse(
            content="Code review results",
            model="claude-3-5-sonnet-20241022",
            tokens_used=200,
            finish_reason="stop",
            metadata={}
        )

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.return_value = mock_response
            mock_get_integration.return_value = mock_integration

            task = Task(
                type=TaskType.CODE_REVIEW,
                description="Review this code",
                context={},
                required_capability=AgentCapability.CODE_REVIEW
            )

            result = await orchestrator._execute_parallel(task)

            assert result.success is True
            assert result.agent_name == "parallel_execution" or "claude" in result.agent_name

    @pytest.mark.asyncio
    async def test_execute_with_fallback_success_first_try(self):
        """Test fallback strategy succeeds on first attempt"""
        orchestrator = MultiAgentOrchestrator()

        mock_response = AgentResponse(
            content="Architecture design",
            model="claude-3-5-sonnet-20241022",
            tokens_used=300,
            finish_reason="stop",
            metadata={}
        )

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.return_value = mock_response
            mock_get_integration.return_value = mock_integration

            task = Task(
                type=TaskType.ARCHITECTURE_DESIGN,
                description="Design a system",
                context={},
                required_capability=AgentCapability.ARCHITECTURE
            )

            result = await orchestrator._execute_with_fallback(task)

            assert result.success is True
            assert result.response.content == "Architecture design"

    @pytest.mark.asyncio
    async def test_execute_pipeline(self):
        """Test sequential pipeline execution"""
        orchestrator = MultiAgentOrchestrator()

        # Mock responses for each step
        responses = [
            AgentResponse("Step 1 output", "model", 100, "stop", {}),
            AgentResponse("Step 2 output", "model", 150, "stop", {}),
            AgentResponse("Step 3 output", "model", 200, "stop", {})
        ]

        response_iter = iter(responses)

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.side_effect = lambda **kwargs: next(response_iter)
            mock_get_integration.return_value = mock_integration

            tasks = [
                Task(
                    type=TaskType.ARCHITECTURE_DESIGN,
                    description="Step 1",
                    context={},
                    required_capability=AgentCapability.ARCHITECTURE
                ),
                Task(
                    type=TaskType.CODE_GENERATION,
                    description="Step 2",
                    context={},
                    required_capability=AgentCapability.CODE_GENERATION
                ),
                Task(
                    type=TaskType.CODE_REVIEW,
                    description="Step 3",
                    context={},
                    required_capability=AgentCapability.CODE_REVIEW
                )
            ]

            results = await orchestrator.execute_pipeline(tasks)

            assert len(results) == 3
            assert all(r.success for r in results)
            assert results[0].response.content == "Step 1 output"
            assert results[1].response.content == "Step 2 output"
            assert results[2].response.content == "Step 3 output"


class TestTaskTypes:
    """Test Task and TaskType functionality"""

    def test_task_creation(self):
        """Test task object creation"""
        task = Task(
            type=TaskType.CODE_GENERATION,
            description="Generate auth middleware",
            context={"temperature": 0.7},
            required_capability=AgentCapability.CODE_GENERATION,
            priority=5
        )

        assert task.type == TaskType.CODE_GENERATION
        assert task.description == "Generate auth middleware"
        assert task.context["temperature"] == 0.7
        assert task.required_capability == AgentCapability.CODE_GENERATION
        assert task.priority == 5

    def test_task_types_enum(self):
        """Test all TaskType values"""
        expected_types = [
            "code_generation",
            "code_review",
            "architecture_design",
            "security_audit",
            "documentation",
            "multimodal_analysis",
            "real_time_collaboration"
        ]

        actual_types = [t.value for t in TaskType]

        for expected in expected_types:
            assert expected in actual_types


class TestAgentCapabilities:
    """Test AgentCapability functionality"""

    def test_all_capabilities_defined(self):
        """Test all capability types are defined"""
        expected_capabilities = [
            "code_generation",
            "code_review",
            "architecture",
            "security",
            "frontend",
            "backend",
            "devops",
            "testing",
            "documentation",
            "multimodal",
            "long_context",
            "real_time",
            "code_completion"
        ]

        actual_capabilities = [c.value for c in AgentCapability]

        for expected in expected_capabilities:
            assert expected in actual_capabilities


class TestIntegration:
    """Integration tests for complete workflows"""

    @pytest.mark.asyncio
    async def test_full_workflow_mock(self):
        """Test complete multi-step workflow with mocks"""
        orchestrator = MultiAgentOrchestrator()

        # Mock all agent responses
        mock_responses = {
            "design": AgentResponse("Design output", "claude", 500, "stop", {}),
            "code": AgentResponse("Code output", "claude", 800, "stop", {}),
            "security": AgentResponse("Security report", "claude", 600, "stop", {}),
            "review": AgentResponse("APPROVED", "claude", 400, "stop", {})
        }

        async def mock_generate(**kwargs):
            prompt = kwargs.get("prompt", "")
            if "Design" in prompt:
                return mock_responses["design"]
            elif "Implement" in prompt:
                return mock_responses["code"]
            elif "Security" in prompt:
                return mock_responses["security"]
            else:
                return mock_responses["review"]

        with patch("core.agent_integrations.get_agent_integration") as mock_get_integration:
            mock_integration = AsyncMock()
            mock_integration.generate.side_effect = mock_generate
            mock_get_integration.return_value = mock_integration

            # Create workflow tasks
            tasks = [
                Task(
                    type=TaskType.ARCHITECTURE_DESIGN,
                    description="Design system",
                    context={},
                    required_capability=AgentCapability.ARCHITECTURE
                ),
                Task(
                    type=TaskType.CODE_GENERATION,
                    description="Implement design",
                    context={},
                    required_capability=AgentCapability.CODE_GENERATION
                ),
                Task(
                    type=TaskType.SECURITY_AUDIT,
                    description="Security audit",
                    context={},
                    required_capability=AgentCapability.SECURITY
                ),
                Task(
                    type=TaskType.CODE_REVIEW,
                    description="Final review",
                    context={},
                    required_capability=AgentCapability.CODE_REVIEW
                )
            ]

            results = await orchestrator.execute_pipeline(tasks)

            assert len(results) == 4
            assert all(r.success for r in results)
            assert results[0].response.content == "Design output"
            assert results[1].response.content == "Code output"
            assert results[2].response.content == "Security report"
            assert results[3].response.content == "APPROVED"


def test_initialize_default_agents():
    """Test default agent initialization"""
    # Clear registry
    from core.agent_registry import _registry
    import core.agent_registry
    core.agent_registry._registry = None

    # Initialize
    initialize_default_agents()
    registry = get_registry()

    # Verify agents registered
    assert len(registry.agents) >= 3  # At least Claude, Gemini, Copilot

    # Verify Claude registered
    assert "claude-sonnet" in registry.agents
    claude = registry.agents["claude-sonnet"]
    assert claude.provider == AgentProvider.CLAUDE
    assert AgentCapability.CODE_GENERATION in claude.capabilities

    # Verify Gemini registered
    assert "gemini-pro" in registry.agents
    gemini = registry.agents["gemini-pro"]
    assert gemini.provider == AgentProvider.GEMINI
    assert AgentCapability.MULTIMODAL in gemini.capabilities


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=core", "--cov-report=term-missing"])
