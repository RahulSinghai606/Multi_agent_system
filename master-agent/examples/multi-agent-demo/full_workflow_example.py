#!/usr/bin/env python3
"""
Multi-Agent Workflow Example

Demonstrates complete integration of Master Agent with multiple AI providers
for a real-world feature development workflow.

Scenario: Building a "Smart Document Analyzer" feature
- Gemini: Analyzes design mockups (multimodal)
- Claude: Designs architecture and reviews code
- Copilot: Generates boilerplate code
- All agents: Parallel security audit (consensus)

Requirements:
    pip install anthropic google-generativeai httpx

Environment Variables:
    ANTHROPIC_API_KEY - Claude API key
    GOOGLE_API_KEY - Gemini API key
    GITHUB_TOKEN - GitHub Copilot access token (optional)
    OPENAI_API_KEY - OpenAI API key (optional)
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from core import (
    MultiAgentOrchestrator,
    Task,
    TaskType,
    AgentCapability,
    get_registry,
    initialize_default_agents
)


async def main():
    """
    Complete multi-agent workflow for feature development

    Pipeline:
    1. Gemini: Analyze UI mockup image → Extract component requirements
    2. Claude: Design architecture → Create system design
    3. Copilot: Generate code → Implement components
    4. All agents (parallel): Security audit → Find vulnerabilities
    5. Claude: Final review → Approve for deployment
    """

    print("\n" + "="*80)
    print("MULTI-AGENT WORKFLOW: Smart Document Analyzer Feature")
    print("="*80)

    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    # Verify agents are registered
    registry = get_registry()
    health_report = registry.get_health_report()

    print(f"\n📊 Agent Status:")
    print(f"   Total agents: {health_report['total_agents']}")
    print(f"   Healthy agents: {health_report['healthy_agents']}")
    print(f"\n   Registered agents:")
    for agent_name, agent_info in health_report['agents'].items():
        status = "✅" if agent_info['healthy'] else "❌"
        print(f"   {status} {agent_name} ({agent_info['provider']})")

    # Phase 1: Multimodal Analysis with Gemini
    # ==========================================
    print("\n" + "-"*80)
    print("PHASE 1: UI Mockup Analysis (Gemini - Multimodal)")
    print("-"*80)

    design_task = Task(
        type=TaskType.MULTIMODAL_ANALYSIS,
        description="""
        Analyze the Smart Document Analyzer UI mockup and extract:
        1. Component structure (header, sidebar, main content, preview pane)
        2. User interactions (upload, drag-drop, analysis controls)
        3. Data flow (file upload → processing → results display)
        4. Accessibility requirements (keyboard navigation, screen reader support)
        5. Performance considerations (large file handling, real-time preview)

        Provide detailed component specifications for implementation.
        """,
        context={
            "system": "You are a UI/UX analyst. Extract detailed component requirements from designs.",
            "temperature": 0.3,  # More focused analysis
            # In real scenario, include base64 image:
            # "images": [base64_encoded_mockup]
        },
        required_capability=AgentCapability.MULTIMODAL
    )

    design_result = await orchestrator.execute_task(design_task, strategy="best_agent")

    if design_result.success:
        print(f"\n✅ Analysis completed by {design_result.agent_name}")
        print(f"   Execution time: {design_result.execution_time_ms:.2f}ms")
        print(f"   Tokens used: {design_result.response.tokens_used}")
        print(f"\n   Requirements extracted:")
        # In real scenario, parse and display structured requirements
        print(f"   {design_result.response.content[:300]}...")
    else:
        print(f"\n❌ Analysis failed: {design_result.error}")
        return

    # Phase 2: Architecture Design with Claude
    # =========================================
    print("\n" + "-"*80)
    print("PHASE 2: Architecture Design (Claude - System Design)")
    print("-"*80)

    architecture_task = Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description=f"""
        Based on the UI requirements:
        {design_result.response.content[:500]}

        Design a scalable React component architecture for the Smart Document Analyzer:

        Requirements:
        - Component hierarchy and data flow
        - State management strategy (Context API vs Redux)
        - File upload and processing pipeline
        - Real-time analysis results streaming
        - Error handling and loading states
        - TypeScript type definitions
        - Testing strategy (unit + integration)

        Provide:
        1. Component tree diagram
        2. Data flow architecture
        3. API integration points
        4. Performance optimization strategy
        """,
        context={
            "system": "You are a senior frontend architect. Create production-ready component designs.",
            "temperature": 0.5,
            "pipeline_context": {
                "phase_1": {
                    "task": "UI Analysis",
                    "result": design_result.response.content[:200]
                }
            }
        },
        required_capability=AgentCapability.ARCHITECTURE
    )

    architecture_result = await orchestrator.execute_task(
        architecture_task,
        strategy="best_agent"
    )

    if architecture_result.success:
        print(f"\n✅ Architecture designed by {architecture_result.agent_name}")
        print(f"   Execution time: {architecture_result.execution_time_ms:.2f}ms")
        print(f"   Tokens used: {architecture_result.response.tokens_used}")
        print(f"\n   Architecture highlights:")
        print(f"   {architecture_result.response.content[:400]}...")
    else:
        print(f"\n❌ Architecture design failed: {architecture_result.error}")
        return

    # Phase 3: Code Generation (Parallel - Consensus)
    # ================================================
    print("\n" + "-"*80)
    print("PHASE 3: Code Generation (Parallel - Multiple Agents)")
    print("-"*80)

    code_task = Task(
        type=TaskType.CODE_GENERATION,
        description=f"""
        Implement the DocumentAnalyzer component based on this architecture:
        {architecture_result.response.content[:500]}

        Generate production-ready React TypeScript code for:
        1. DocumentAnalyzer.tsx - Main container component
        2. FileUploader.tsx - Drag-drop file upload
        3. AnalysisResults.tsx - Results display with streaming updates
        4. PreviewPane.tsx - Document preview component

        Include:
        - Full TypeScript type definitions
        - Error handling and loading states
        - Accessibility attributes (ARIA labels)
        - Unit test setup with Jest/RTL
        - CSS modules for styling

        Follow best practices:
        - React hooks (useState, useEffect, useCallback)
        - Proper prop drilling vs context
        - Memoization for performance
        - Error boundaries
        """,
        context={
            "system": "Generate production-ready React TypeScript code with full type safety.",
            "temperature": 0.4,
            "max_tokens": 4000
        },
        required_capability=AgentCapability.CODE_GENERATION
    )

    # Execute on multiple agents for consensus
    code_result = await orchestrator.execute_task(code_task, strategy="parallel")

    if code_result.success:
        print(f"\n✅ Code generated by {code_result.agent_name}")
        print(f"   Execution time: {code_result.execution_time_ms:.2f}ms")
        print(f"   Tokens used: {code_result.response.tokens_used}")
        print(f"\n   Generated components:")
        print(f"   {code_result.response.content[:500]}...")
    else:
        print(f"\n❌ Code generation failed: {code_result.error}")
        return

    # Phase 4: Security Audit (Parallel - All Agents)
    # ===============================================
    print("\n" + "-"*80)
    print("PHASE 4: Security Audit (Parallel - Consensus from Multiple Agents)")
    print("-"*80)

    security_task = Task(
        type=TaskType.SECURITY_AUDIT,
        description=f"""
        Perform comprehensive security audit of the generated code:

        {code_result.response.content[:1000]}

        Check for:
        1. XSS vulnerabilities (file upload, user input)
        2. CSRF protection (file operations)
        3. Input validation (file types, sizes, content)
        4. Authentication/authorization (if applicable)
        5. Data sanitization (before display)
        6. Secure file handling (path traversal, malicious files)
        7. Rate limiting (upload frequency)
        8. OWASP Top 10 compliance

        Provide:
        - List of vulnerabilities (severity: critical/high/medium/low)
        - Exploitation scenarios
        - Remediation recommendations with code examples
        - Security best practices checklist
        """,
        context={
            "system": "You are a security expert. Perform thorough vulnerability assessment.",
            "temperature": 0.2,  # More deterministic for security
            "max_tokens": 3000
        },
        required_capability=AgentCapability.SECURITY
    )

    # Parallel execution for consensus
    security_result = await orchestrator.execute_task(security_task, strategy="parallel")

    if security_result.success:
        print(f"\n✅ Security audit completed")
        print(f"   Lead auditor: {security_result.agent_name}")
        print(f"   Execution time: {security_result.execution_time_ms:.2f}ms")
        print(f"   Tokens used: {security_result.response.tokens_used}")
        print(f"\n   Security findings:")
        print(f"   {security_result.response.content[:600]}...")
    else:
        print(f"\n❌ Security audit failed: {security_result.error}")
        return

    # Phase 5: Final Review with Claude
    # ==================================
    print("\n" + "-"*80)
    print("PHASE 5: Final Code Review (Claude - Quality Gate)")
    print("-"*80)

    review_task = Task(
        type=TaskType.CODE_REVIEW,
        description=f"""
        Final code review before deployment approval.

        Code:
        {code_result.response.content[:800]}

        Security Audit Results:
        {security_result.response.content[:500]}

        Review checklist:
        1. Code quality and maintainability
        2. TypeScript type safety
        3. React best practices adherence
        4. Security vulnerabilities addressed
        5. Accessibility compliance (WCAG 2.1 AA)
        6. Performance optimizations applied
        7. Test coverage adequate
        8. Documentation completeness

        Provide:
        - APPROVED / NEEDS_CHANGES decision
        - Critical issues blocking deployment
        - Recommended improvements (non-blocking)
        - Deployment readiness score (0-100)
        """,
        context={
            "system": "You are a senior code reviewer. Apply strict quality standards.",
            "temperature": 0.3
        },
        required_capability=AgentCapability.CODE_REVIEW
    )

    review_result = await orchestrator.execute_task(review_task, strategy="best_agent")

    if review_result.success:
        print(f"\n✅ Review completed by {review_result.agent_name}")
        print(f"   Execution time: {review_result.execution_time_ms:.2f}ms")
        print(f"   Tokens used: {review_result.response.tokens_used}")
        print(f"\n   Review summary:")
        print(f"   {review_result.response.content[:500]}...")
    else:
        print(f"\n❌ Review failed: {review_result.error}")
        return

    # Summary
    # =======
    print("\n" + "="*80)
    print("WORKFLOW COMPLETE")
    print("="*80)

    total_time = sum([
        design_result.execution_time_ms,
        architecture_result.execution_time_ms,
        code_result.execution_time_ms,
        security_result.execution_time_ms,
        review_result.execution_time_ms
    ])

    total_tokens = sum([
        design_result.response.tokens_used,
        architecture_result.response.tokens_used,
        code_result.response.tokens_used,
        security_result.response.tokens_used,
        review_result.response.tokens_used
    ])

    print(f"\n📊 Workflow Statistics:")
    print(f"   Total execution time: {total_time:.2f}ms ({total_time/1000:.2f}s)")
    print(f"   Total tokens used: {total_tokens:,}")
    print(f"   Phases completed: 5/5")
    print(f"\n   Phase breakdown:")
    print(f"   1. UI Analysis (Gemini): {design_result.execution_time_ms:.0f}ms")
    print(f"   2. Architecture (Claude): {architecture_result.execution_time_ms:.0f}ms")
    print(f"   3. Code Generation (Parallel): {code_result.execution_time_ms:.0f}ms")
    print(f"   4. Security Audit (Parallel): {security_result.execution_time_ms:.0f}ms")
    print(f"   5. Final Review (Claude): {review_result.execution_time_ms:.0f}ms")

    print(f"\n✅ Feature development pipeline completed successfully!")
    print(f"   Ready for deployment approval based on final review.")


if __name__ == "__main__":
    asyncio.run(main())
