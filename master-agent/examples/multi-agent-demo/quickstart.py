#!/usr/bin/env python3
"""
Multi-Agent Quick Start Example

Simple example to test multi-agent integration and verify API connectivity.

Usage:
    python quickstart.py

Environment Variables:
    ANTHROPIC_API_KEY - Claude API key (required)
    GOOGLE_API_KEY - Gemini API key (optional)
    GITHUB_TOKEN - GitHub Copilot token (optional)
"""

import asyncio
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import (
    MultiAgentOrchestrator,
    Task,
    TaskType,
    AgentCapability,
    get_registry
)


async def test_single_agent():
    """Test 1: Single agent execution (best agent selection)"""
    print("\n" + "="*70)
    print("TEST 1: Single Agent Execution (Best Agent Selection)")
    print("="*70)

    orchestrator = MultiAgentOrchestrator()

    task = Task(
        type=TaskType.CODE_GENERATION,
        description="Write a Python function to calculate Fibonacci numbers using memoization.",
        context={
            "system": "You are a Python expert. Write clean, efficient code.",
            "temperature": 0.7,
            "max_tokens": 500
        },
        required_capability=AgentCapability.CODE_GENERATION
    )

    result = await orchestrator.execute_task(task, strategy="best_agent")

    if result.success:
        print(f"\n✅ Success!")
        print(f"   Agent: {result.agent_name}")
        print(f"   Time: {result.execution_time_ms:.2f}ms")
        print(f"   Tokens: {result.response.tokens_used}")
        print(f"\n   Generated code:")
        print("   " + "-"*60)
        print(result.response.content[:500])
        if len(result.response.content) > 500:
            print("   ...")
    else:
        print(f"\n❌ Failed: {result.error}")


async def test_fallback_strategy():
    """Test 2: Automatic fallback on agent failure"""
    print("\n" + "="*70)
    print("TEST 2: Fallback Strategy (Automatic Agent Switching)")
    print("="*70)

    orchestrator = MultiAgentOrchestrator()

    task = Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description="Design a microservices architecture for a real-time chat application.",
        context={
            "system": "You are a system architect. Design scalable distributed systems.",
            "temperature": 0.5,
            "max_tokens": 800
        },
        required_capability=AgentCapability.ARCHITECTURE
    )

    result = await orchestrator.execute_task(task, strategy="fallback")

    if result.success:
        print(f"\n✅ Success!")
        print(f"   Agent: {result.agent_name}")
        print(f"   Time: {result.execution_time_ms:.2f}ms")
        print(f"   Tokens: {result.response.tokens_used}")
        print(f"\n   Architecture design:")
        print("   " + "-"*60)
        print(result.response.content[:400])
        if len(result.response.content) > 400:
            print("   ...")
    else:
        print(f"\n❌ Failed: {result.error}")


async def test_pipeline_execution():
    """Test 3: Sequential pipeline (output → input chaining)"""
    print("\n" + "="*70)
    print("TEST 3: Sequential Pipeline (Multi-Step Workflow)")
    print("="*70)

    orchestrator = MultiAgentOrchestrator()

    # Step 1: Requirements analysis
    task1 = Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description="List 3 key requirements for a REST API authentication system.",
        context={
            "system": "You are a requirements analyst. Be concise.",
            "temperature": 0.3,
            "max_tokens": 300
        },
        required_capability=AgentCapability.ARCHITECTURE
    )

    # Step 2: Code generation based on requirements
    task2 = Task(
        type=TaskType.CODE_GENERATION,
        description="Implement a simple JWT authentication middleware for Express.js.",
        context={
            "system": "Generate Node.js code based on requirements from previous step.",
            "temperature": 0.5,
            "max_tokens": 500
        },
        required_capability=AgentCapability.CODE_GENERATION
    )

    # Step 3: Security review
    task3 = Task(
        type=TaskType.SECURITY_AUDIT,
        description="Review the authentication code for security vulnerabilities.",
        context={
            "system": "You are a security expert. Focus on authentication flaws.",
            "temperature": 0.2,
            "max_tokens": 400
        },
        required_capability=AgentCapability.SECURITY
    )

    results = await orchestrator.execute_pipeline([task1, task2, task3])

    print(f"\n   Pipeline: {len(results)} steps completed")

    for i, result in enumerate(results, 1):
        if result.success:
            print(f"\n   ✅ Step {i}: {result.task.type.value}")
            print(f"      Agent: {result.agent_name}")
            print(f"      Time: {result.execution_time_ms:.2f}ms")
            print(f"      Preview: {result.response.content[:150]}...")
        else:
            print(f"\n   ❌ Step {i} failed: {result.error}")
            break


async def show_agent_health():
    """Display current agent health status"""
    print("\n" + "="*70)
    print("AGENT HEALTH STATUS")
    print("="*70)

    registry = get_registry()
    health = registry.get_health_report()

    print(f"\n   Timestamp: {health['timestamp']}")
    print(f"   Total agents: {health['total_agents']}")
    print(f"   Healthy agents: {health['healthy_agents']}")
    print(f"\n   Detailed status:")

    for name, info in health['agents'].items():
        status = "✅" if info['healthy'] else "❌"
        print(f"      {status} {name}")
        print(f"         Provider: {info['provider']}")
        print(f"         Success: {info['success_count']}, Failures: {info['failure_count']}")
        print(f"         Error rate: {info['error_rate']}")


async def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("MULTI-AGENT SYSTEM - QUICK START")
    print("="*70)

    # Check API keys
    api_keys = {
        "ANTHROPIC_API_KEY": bool(os.getenv("ANTHROPIC_API_KEY")),
        "GOOGLE_API_KEY": bool(os.getenv("GOOGLE_API_KEY")),
        "GITHUB_TOKEN": bool(os.getenv("GITHUB_TOKEN")),
        "OPENAI_API_KEY": bool(os.getenv("OPENAI_API_KEY"))
    }

    print("\n🔑 API Key Status:")
    for key, present in api_keys.items():
        status = "✅" if present else "❌"
        print(f"   {status} {key}")

    if not api_keys["ANTHROPIC_API_KEY"]:
        print("\n⚠️  Warning: ANTHROPIC_API_KEY not set. Some tests may fail.")
        print("   Set it in your environment: export ANTHROPIC_API_KEY='your-key'")

    # Show agent health
    await show_agent_health()

    # Run tests
    try:
        await test_single_agent()
        await test_fallback_strategy()
        await test_pipeline_execution()

        print("\n" + "="*70)
        print("✅ ALL TESTS COMPLETED")
        print("="*70)

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
