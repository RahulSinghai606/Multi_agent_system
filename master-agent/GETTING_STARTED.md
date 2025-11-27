# Getting Started with Master Agent v3.0.0

Welcome to Master Agent - a production-ready AI-powered SDLC orchestration platform with multi-provider intelligence.

---

## 🎯 What is Master Agent?

Master Agent is an **intelligent SDLC orchestration system** that automates software development from requirements to production deployment, using **multi-agent AI coordination** across Claude, Gemini, Copilot, and OpenAI.

### Key Capabilities

- **Multi-Agent Orchestration**: Automatically route tasks to optimal AI provider
- **4 Execution Strategies**: best_agent, parallel, fallback, pipeline
- **Dynamic Workflow Generation**: No hardcoded workflows - adapts to your project
- **Human-in-the-Loop Gates**: Control critical decisions
- **State Management**: Resume work across sessions and tools
- **Multi-Provider Support**: Claude, Gemini, Copilot, OpenAI

---

## ⚡ Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd /path/to/master-agent

# Install Python packages
pip install anthropic google-generativeai httpx pytest pytest-asyncio
```

### 2. Set API Keys

**Required**:
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

**Optional** (enable additional agents):
```bash
export GOOGLE_API_KEY="AIza..."          # Gemini
export GITHUB_TOKEN="ghp_..."            # Copilot
export OPENAI_API_KEY="sk-..."           # GPT-4
```

### 3. Test Installation

```bash
cd examples/multi-agent-demo
python quickstart.py
```

**Expected Output**:
```
🚀 Master Agent Multi-Agent System - Quick Start Tests

✅ Test 1: Single Agent Execution - Success!
   Agent: claude-sonnet
   Time: 2.3s

✅ Test 2: Fallback Strategy - Success!
   Tried: claude-sonnet
   Time: 2.1s

✅ Test 3: Sequential Pipeline - Success!
   Phase 1: claude-sonnet (2.3s)
   Phase 2: claude-sonnet (1.9s)
   Phase 3: claude-sonnet (2.1s)

✅ Test 4: Health Monitoring - Success!
   Healthy agents: 4/4

🎉 All tests passed! Master Agent is ready.
```

### 4. Your First Multi-Agent Task

Create `my_first_task.py`:

```python
import asyncio
from core import MultiAgentOrchestrator, Task, TaskType, AgentCapability

async def main():
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    # Define task
    task = Task(
        type=TaskType.CODE_GENERATION,
        description="Write a Python function to validate email addresses",
        context={"temperature": 0.7},
        required_capability=AgentCapability.CODE_GENERATION
    )

    # Execute with best agent strategy
    result = await orchestrator.execute_task(task, strategy="best_agent")

    # Display results
    print(f"✅ Completed by: {result.agent_name}")
    print(f"⏱️  Time: {result.execution_time_ms:.0f}ms")
    print(f"🎯 Tokens: {result.response.tokens_used}")
    print("\n📝 Generated Code:\n")
    print(result.response.content)

if __name__ == "__main__":
    asyncio.run(main())
```

Run it:
```bash
python my_first_task.py
```

---

## 📚 Learning Path

### Beginner (30 minutes)

1. **Read**: [README.md](README.md) - Overview and features
2. **Read**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick reference guide
3. **Run**: `examples/multi-agent-demo/quickstart.py` - See it work
4. **Explore**: [examples/multi-agent-demo/README.md](examples/multi-agent-demo/README.md) - Examples

### Intermediate (2 hours)

1. **Read**: [MULTI_AGENT_COMPLETE.md](MULTI_AGENT_COMPLETE.md) - Complete system docs
2. **Read**: [MASTER_AGENT_MULTI_AGENT_INTEGRATION.md](MASTER_AGENT_MULTI_AGENT_INTEGRATION.md) - Integration patterns
3. **Run**: `examples/multi-agent-demo/full_workflow_example.py` - Full pipeline
4. **Experiment**: Modify examples, try different strategies

### Advanced (1 day)

1. **Read**: [PHASE_2_AND_MULTI_AGENT_FINAL_SUMMARY.md](PHASE_2_AND_MULTI_AGENT_FINAL_SUMMARY.md) - Executive summary
2. **Study**: Source code in `core/` - Implementation details
3. **Review**: `tests/test_multi_agent.py` - Test patterns
4. **Build**: Create your own multi-agent workflow

---

## 🎨 Common Use Cases

### Use Case 1: Code Generation

```python
task = Task(
    type=TaskType.CODE_GENERATION,
    description="Create a REST API endpoint for user authentication",
    context={"temperature": 0.5},
    required_capability=AgentCapability.CODE_GENERATION
)

result = await orchestrator.execute_task(task, strategy="best_agent")
# Best for: Standard coding tasks
# Cost: $0.01-0.04 | Time: 2-15s
```

### Use Case 2: Security Audit

```python
task = Task(
    type=TaskType.SECURITY_AUDIT,
    description="Audit this payment processing code for vulnerabilities:\n" + code,
    context={"temperature": 0.2},
    required_capability=AgentCapability.SECURITY
)

result = await orchestrator.execute_task(task, strategy="parallel")
# Best for: Critical code review
# Cost: $0.06-0.20 | Time: 5-20s | Consensus: 3-4 agents
```

### Use Case 3: Architecture Design

```python
task = Task(
    type=TaskType.ARCHITECTURE_DESIGN,
    description="Design a microservices architecture for e-commerce platform",
    context={"temperature": 0.5},
    required_capability=AgentCapability.ARCHITECTURE
)

result = await orchestrator.execute_task(task, strategy="fallback")
# Best for: System design with reliability
# Cost: $0.01-0.15 | Time: 2-45s
```

### Use Case 4: Full Development Pipeline

```python
tasks = [
    Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description="Design authentication system",
        required_capability=AgentCapability.ARCHITECTURE
    ),
    Task(
        type=TaskType.CODE_GENERATION,
        description="Implement the design",
        required_capability=AgentCapability.CODE_GENERATION
    ),
    Task(
        type=TaskType.SECURITY_AUDIT,
        description="Audit the implementation",
        required_capability=AgentCapability.SECURITY
    )
]

results = await orchestrator.execute_pipeline(tasks)
# Best for: Multi-phase development
# Cost: $0.50-2.00 | Time: 30-180s
```

---

## 🛠️ Configuration

### Agent Priorities

Customize which agents are preferred (in `core/agent_registry.py`):

```python
# Default priorities:
# Claude (Anthropic): 10 - Primary development
# Gemini (Google): 8 - Multimodal, large context
# Copilot (GitHub): 7 - Code completion
# OpenAI (GPT-4): 6 - General purpose

# Customize by modifying priority values in initialize_default_agents()
```

### Strategy Selection

Choose the right strategy for your task:

| Strategy | When to Use | Cost | Speed | Reliability |
|----------|-------------|------|-------|-------------|
| **best_agent** | Standard tasks | 1x | Fast | Good |
| **parallel** | Critical decisions | 3x | Medium | Best |
| **fallback** | Production ops | 1-4x | Variable | Excellent |
| **pipeline** | Multi-step workflows | Varies | Slow | Good |

### Health Monitoring

Check agent health anytime:

```python
from core import get_registry

registry = get_registry()
health = registry.get_health_report()

print(f"Total agents: {health['total_agents']}")
print(f"Healthy agents: {health['healthy_agents']}")

for name, info in health['agents'].items():
    status = "✅" if info['healthy'] else "❌"
    print(f"{status} {name}: {info['error_rate']:.1%} errors")
```

---

## 🧪 Testing

### Run Test Suite

```bash
# All tests
pytest tests/test_multi_agent.py -v

# With coverage
pytest tests/test_multi_agent.py --cov=core --cov-report=term-missing

# Specific test
pytest tests/test_multi_agent.py::TestAgentRegistry::test_register_agent -v
```

### Write Your Own Tests

```python
import pytest
from core import MultiAgentOrchestrator, Task, TaskType, AgentCapability

@pytest.mark.asyncio
async def test_my_workflow():
    orchestrator = MultiAgentOrchestrator()

    task = Task(
        type=TaskType.CODE_GENERATION,
        description="Test task",
        context={},
        required_capability=AgentCapability.CODE_GENERATION
    )

    result = await orchestrator.execute_task(task)
    assert result.success
    assert result.agent_name in ["claude-sonnet", "gemini-pro", "copilot", "gpt-4"]
```

---

## 🐛 Troubleshooting

### Issue: No agents available

**Symptom**: `No agent available for code_generation`

**Solution**:
```bash
# 1. Check API keys
echo $ANTHROPIC_API_KEY

# 2. Verify agent health
python -c "from core import get_registry; print(get_registry().get_health_report())"

# 3. Check initialization
python -c "from core import initialize_default_agents, get_registry; initialize_default_agents(); print(get_registry().get_health_report())"
```

### Issue: All agents failing

**Symptom**: `All agents failed after 3 attempts`

**Solutions**:
1. Check API rate limits
2. Verify API keys are valid
3. Review task description clarity
4. Check network connectivity

### Issue: Slow execution

**Symptom**: Tasks taking 30+ seconds

**Solutions**:
```python
# Reduce max_tokens
task.context["max_tokens"] = 2000  # Instead of 10000

# Use best_agent instead of parallel
strategy = "best_agent"  # Instead of "parallel"
```

### Issue: Import errors

**Symptom**: `ModuleNotFoundError: No module named 'core'`

**Solution**:
```bash
# Ensure you're in the master-agent directory
cd /path/to/master-agent

# Verify Python path
python -c "import sys; print(sys.path)"

# Install dependencies
pip install anthropic google-generativeai httpx
```

---

## 📊 Performance Optimization

### Cost Optimization

```python
# ❌ BAD: Excessive tokens
task = Task(
    description="Simple task",
    context={"max_tokens": 100000}  # Wasteful
)

# ✅ GOOD: Appropriate tokens
task = Task(
    description="Simple task",
    context={"max_tokens": 2000}  # Sufficient
)
```

### Strategy Optimization

```python
# ❌ BAD: Parallel for simple task
result = await orchestrator.execute_task(
    simple_task,
    strategy="parallel"  # 3x cost for no benefit
)

# ✅ GOOD: Best agent for simple task
result = await orchestrator.execute_task(
    simple_task,
    strategy="best_agent"  # 1x cost
)
```

### Token Tracking

```python
result = await orchestrator.execute_task(task)

print(f"Execution time: {result.execution_time_ms:.2f}ms")
print(f"Tokens used: {result.response.tokens_used}")
print(f"Agent: {result.agent_name}")
```

---

## 🔗 Integration Examples

### Master Agent with Custom Workflow

```bash
# In Claude Code CLI
/sc:master start --brd client_requirements.pdf

# Output:
# ✓ Multi-agent system initialized (Claude, Gemini, Copilot)
# ✓ BRD analyzed: Web Application (Moderate complexity)
# ✓ Workflow generated (6 phases)
# → Starting Phase 1: Requirements Analysis...
```

### Multi-Agent with PM Tools

```python
# 1. Execute task
result = await orchestrator.execute_task(code_gen_task)

# 2. Update Jira
from integrations.pm_integrations import JiraIntegration

jira = JiraIntegration(api_key="...")
jira.update_issue(
    issue_key="PROJ-123",
    status="In Review",
    comment=f"Code generated by {result.agent_name}"
)
```

### Multi-Agent with CI/CD

```python
# 1. Generate code
code_result = await orchestrator.execute_task(code_gen_task)

# 2. Trigger CI pipeline
from integrations.cicd_integrations import GitHubActionsIntegration

github = GitHubActionsIntegration(token="ghp_...")
github.trigger_workflow(
    repo="owner/repo",
    workflow="test.yml",
    ref="main"
)
```

---

## 📚 Documentation Map

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| **README.md** | Overview and features | 5 min |
| **GETTING_STARTED.md** (this) | Quick start guide | 10 min |
| **QUICK_REFERENCE.md** | Quick reference | 15 min |
| **examples/multi-agent-demo/README.md** | Examples and tutorials | 30 min |
| **MULTI_AGENT_COMPLETE.md** | Complete system docs | 2 hours |
| **MASTER_AGENT_MULTI_AGENT_INTEGRATION.md** | Integration patterns | 1 hour |
| **PHASE_2_AND_MULTI_AGENT_FINAL_SUMMARY.md** | Executive summary | 45 min |
| **DOCUMENTATION_INDEX.md** | Navigation hub | 5 min |

---

## 🎓 Next Steps

### 1. Run Examples

```bash
# Quick start (5 minutes)
cd examples/multi-agent-demo
python quickstart.py

# Full workflow (10 minutes)
python full_workflow_example.py
```

### 2. Read Documentation

Start with [QUICK_REFERENCE.md](QUICK_REFERENCE.md), then explore others based on your needs.

### 3. Try Master Agent

```bash
# Start a new project
/sc:master start --brd your_requirements.pdf

# Or use directly
python your_workflow.py
```

### 4. Customize and Extend

- Modify agent priorities in `core/agent_registry.py`
- Add custom task types in `core/multi_agent_orchestrator.py`
- Create custom integrations in `integrations/`
- Write your own personas in `agents/`

---

## 🆘 Getting Help

### Quick Checks

```bash
# 1. Check agent health
python -c "from core import get_registry; print(get_registry().get_health_report())"

# 2. Run test suite
pytest tests/test_multi_agent.py -v

# 3. Run quick start
cd examples/multi-agent-demo && python quickstart.py
```

### Resources

- **Quick Reference**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Examples**: [examples/multi-agent-demo/](examples/multi-agent-demo/)
- **Complete Docs**: [MULTI_AGENT_COMPLETE.md](MULTI_AGENT_COMPLETE.md)
- **Index**: [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## ✨ Key Takeaways

1. **Start Simple**: Use `best_agent` strategy for most tasks
2. **Use Parallel for Critical**: Security audits, architecture reviews
3. **Check Health**: Monitor agent status with `get_health_report()`
4. **Optimize Costs**: Use appropriate `max_tokens` and strategies
5. **Test First**: Run `quickstart.py` to verify installation
6. **Read Examples**: Learn from working code in `examples/`

---

**Welcome to Master Agent v3.0.0!**

*AI-Powered SDLC Orchestration with Multi-Agent Intelligence*

**Ready to start?** Run `python examples/multi-agent-demo/quickstart.py` now!
