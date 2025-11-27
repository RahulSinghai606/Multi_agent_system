# Master Agent - Quick Reference Guide

**Version:** 3.0.0 | **Last Updated:** 2025-01-26

---

## 🚀 Quick Start (5 Minutes)

### Installation

```bash
# 1. Install dependencies
pip install anthropic google-generativeai httpx pytest pytest-asyncio

# 2. Set API keys (minimum: ANTHROPIC_API_KEY)
export ANTHROPIC_API_KEY="sk-ant-..."
export GOOGLE_API_KEY="AIza..."          # Optional
export GITHUB_TOKEN="ghp_..."            # Optional
export OPENAI_API_KEY="sk-..."           # Optional

# 3. Test installation
cd examples/multi-agent-demo
python quickstart.py
```

### First Multi-Agent Task

```python
import asyncio
from core import MultiAgentOrchestrator, Task, TaskType, AgentCapability

async def main():
    orchestrator = MultiAgentOrchestrator()

    task = Task(
        type=TaskType.CODE_GENERATION,
        description="Write a Python function for binary search",
        context={"temperature": 0.7},
        required_capability=AgentCapability.CODE_GENERATION
    )

    result = await orchestrator.execute_task(task, strategy="best_agent")
    print(result.response.content)

asyncio.run(main())
```

---

## 📚 Common Tasks

### Task 1: Code Generation

```python
task = Task(
    type=TaskType.CODE_GENERATION,
    description="Create a REST API endpoint for user authentication",
    context={"temperature": 0.5, "max_tokens": 2000},
    required_capability=AgentCapability.CODE_GENERATION
)

result = await orchestrator.execute_task(task, strategy="best_agent")
```

### Task 2: Security Audit

```python
security_task = Task(
    type=TaskType.SECURITY_AUDIT,
    description="Audit this code for OWASP Top 10 vulnerabilities:\n\n" + code,
    context={"temperature": 0.2},
    required_capability=AgentCapability.SECURITY
)

# For critical code, use parallel for consensus
result = await orchestrator.execute_task(security_task, strategy="parallel")
```

### Task 3: Architecture Design

```python
arch_task = Task(
    type=TaskType.ARCHITECTURE_DESIGN,
    description="Design a microservices architecture for e-commerce platform",
    context={"temperature": 0.5},
    required_capability=AgentCapability.ARCHITECTURE
)

result = await orchestrator.execute_task(arch_task, strategy="fallback")
```

### Task 4: Multimodal Analysis (Gemini)

```python
import base64

# Load image
with open("ui_mockup.png", "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

multimodal_task = Task(
    type=TaskType.MULTIMODAL_ANALYSIS,
    description="Analyze this UI mockup and extract component requirements",
    context={"images": [image_data]},
    required_capability=AgentCapability.MULTIMODAL
)

result = await orchestrator.execute_task(multimodal_task)
```

### Task 5: Sequential Pipeline

```python
tasks = [
    Task(
        type=TaskType.ARCHITECTURE_DESIGN,
        description="Design authentication system",
        required_capability=AgentCapability.ARCHITECTURE
    ),
    Task(
        type=TaskType.CODE_GENERATION,
        description="Implement design from Phase 1",
        required_capability=AgentCapability.CODE_GENERATION
    ),
    Task(
        type=TaskType.SECURITY_AUDIT,
        description="Audit code from Phase 2",
        required_capability=AgentCapability.SECURITY
    )
]

results = await orchestrator.execute_pipeline(tasks)
```

---

## 🎯 Strategy Selection Guide

| Scenario | Strategy | Why |
|----------|----------|-----|
| Standard task | `best_agent` | Fast, cost-effective |
| Critical decision | `parallel` | Multiple perspectives, consensus |
| Production deployment | `fallback` | Reliable, auto-retry |
| Multi-step workflow | `pipeline` | Context passing, sequential |

### Strategy Examples

```python
# Fast and cheap
result = await orchestrator.execute_task(task, strategy="best_agent")

# Thorough and reliable
result = await orchestrator.execute_task(task, strategy="parallel")

# Auto-retry on failure
result = await orchestrator.execute_task(task, strategy="fallback")

# Multi-step with context
results = await orchestrator.execute_pipeline([task1, task2, task3])
```

---

## 🔧 Configuration

### Check Agent Health

```python
from core import get_registry

registry = get_registry()
health = registry.get_health_report()

print(f"Healthy agents: {health['healthy_agents']}/{health['total_agents']}")

for name, info in health['agents'].items():
    status = "✅" if info['healthy'] else "❌"
    print(f"{status} {name}: {info['error_rate']}")
```

### Customize Agent Priorities

```python
# In core/agent_registry.py:initialize_default_agents()

registry.register_agent(AgentConfig(
    provider=AgentProvider.CLAUDE,
    name="claude-sonnet",
    api_key=os.getenv("ANTHROPIC_API_KEY"),
    model="claude-sonnet-4-5",
    capabilities=[AgentCapability.CODE_GENERATION, ...],
    priority=10,  # Adjust priority (higher = preferred)
    enabled=True
))
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

### Write Custom Tests

```python
import pytest
from core import MultiAgentOrchestrator, Task, TaskType, AgentCapability

@pytest.mark.asyncio
async def test_custom_workflow():
    orchestrator = MultiAgentOrchestrator()

    task = Task(
        type=TaskType.CODE_GENERATION,
        description="Test task",
        context={},
        required_capability=AgentCapability.CODE_GENERATION
    )

    result = await orchestrator.execute_task(task)
    assert result.success
```

---

## 📊 Monitoring & Debugging

### Enable Logging

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("core")
```

### Track Execution Time

```python
result = await orchestrator.execute_task(task)
print(f"Execution time: {result.execution_time_ms:.2f}ms")
print(f"Tokens used: {result.response.tokens_used}")
```

### Error Handling

```python
result = await orchestrator.execute_task(task, strategy="fallback")

if not result.success:
    print(f"❌ Error: {result.error}")
    # Fallback to manual process
else:
    print(f"✅ Completed by {result.agent_name}")
    # Process result
```

---

## 💰 Cost Optimization

### Token Limits

```python
# ❌ BAD: Excessive
task = Task(
    description="Simple task",
    context={"max_tokens": 100000}  # Wasteful
)

# ✅ GOOD: Appropriate
task = Task(
    description="Simple task",
    context={"max_tokens": 2000}  # Sufficient
)
```

### Strategy Selection

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

---

## 🚨 Common Issues

### Issue: No agents available

```
❌ No agent available for code_generation
```

**Fix:**
```bash
# 1. Check API keys
echo $ANTHROPIC_API_KEY

# 2. Verify initialization
python -c "
from core import initialize_default_agents, get_registry
initialize_default_agents()
print(get_registry().get_health_report())
"

# 3. Check health
python -c "
from core import get_registry
health = get_registry().get_health_report()
print(f\"Healthy: {health['healthy_agents']}/{health['total_agents']}\")
"
```

### Issue: All agents failing

```
❌ All agents failed after 3 attempts
```

**Fix:**
1. Check API rate limits
2. Verify API keys are valid
3. Review task description clarity
4. Check network connectivity

### Issue: Slow execution

```
Execution time: 45000ms (45 seconds)
```

**Fix:**
```python
# Reduce max_tokens
task.context["max_tokens"] = 2000  # Instead of 10000

# Use best_agent instead of parallel
strategy = "best_agent"
```

---

## 📁 File Structure

```
master-agent/
├── core/
│   ├── __init__.py              # Package exports
│   ├── agent_registry.py        # Agent management (400 lines)
│   ├── agent_integrations.py   # API integrations (350 lines)
│   └── multi_agent_orchestrator.py  # Orchestration (450 lines)
├── agents/
│   ├── security/                # Security agents
│   ├── design/                  # Design persona
│   └── ...                      # Other personas
├── workflows/
│   └── monorepo/                # Multi-repo coordination
├── integrations/
│   ├── pm_integrations.py       # PM tools (950 lines)
│   ├── cicd_integrations.py    # CI/CD platforms (1,100 lines)
│   └── integration_manager.py  # Setup wizard (350 lines)
├── examples/
│   ├── multi-agent-demo/
│   │   ├── quickstart.py        # Quick start test
│   │   ├── full_workflow_example.py  # Complete pipeline
│   │   └── README.md            # Documentation
│   └── ecommerce-platform/
│       └── README.md            # Real-world example
├── tests/
│   ├── test_multi_agent.py      # Multi-agent tests (800 lines)
│   ├── test_security.py         # Security tests (700 lines)
│   └── ...                      # Other tests
└── docs/
    ├── MULTI_AGENT_SETUP_GUIDE.md
    ├── MASTER_AGENT_MULTI_AGENT_INTEGRATION.md
    ├── MULTI_AGENT_COMPLETE.md
    └── PHASE_2_AND_MULTI_AGENT_FINAL_SUMMARY.md
```

---

## 🔗 Useful Commands

```bash
# Check agent health
python -c "from core import get_registry; print(get_registry().get_health_report())"

# Run quick start
cd examples/multi-agent-demo && python quickstart.py

# Run full workflow
cd examples/multi-agent-demo && python full_workflow_example.py

# Run tests
pytest tests/test_multi_agent.py -v

# Run with coverage
pytest --cov=core --cov-report=term-missing

# Check API keys
env | grep -E "ANTHROPIC|GOOGLE|GITHUB|OPENAI"
```

---

## 📖 Documentation Links

| Document | Purpose | Lines |
|----------|---------|-------|
| **MULTI_AGENT_SETUP_GUIDE.md** | Installation & setup | 500+ |
| **MASTER_AGENT_MULTI_AGENT_INTEGRATION.md** | Integration patterns | 2,500+ |
| **MULTI_AGENT_COMPLETE.md** | Complete system docs | 3,500+ |
| **examples/multi-agent-demo/README.md** | Examples & tutorials | 2,000+ |
| **PHASE_2_AND_MULTI_AGENT_FINAL_SUMMARY.md** | Final summary | 3,000+ |

---

## 🎯 Key Concepts

### Task Types

```python
TaskType.CODE_GENERATION       # Generate code
TaskType.CODE_REVIEW           # Review code
TaskType.ARCHITECTURE_DESIGN   # Design systems
TaskType.SECURITY_AUDIT        # Security analysis
TaskType.DOCUMENTATION         # Write docs
TaskType.MULTIMODAL_ANALYSIS   # Analyze images/diagrams
TaskType.REAL_TIME_COLLABORATION  # Live collaboration
```

### Agent Capabilities

```python
AgentCapability.CODE_GENERATION    # Code gen
AgentCapability.ARCHITECTURE       # System design
AgentCapability.SECURITY           # Security
AgentCapability.MULTIMODAL         # Images/audio/video
AgentCapability.LONG_CONTEXT       # 1M+ tokens
AgentCapability.CODE_COMPLETION    # IDE completion
```

### Agent Providers

```python
AgentProvider.CLAUDE    # Anthropic Claude
AgentProvider.GEMINI    # Google Gemini
AgentProvider.COPILOT   # GitHub Copilot
AgentProvider.OPENAI    # OpenAI GPT-4
AgentProvider.CUSTOM    # Custom agents
```

---

## 💡 Pro Tips

### Tip 1: Context Awareness

```python
# Let system choose best agent for large context
context_size = estimate_tokens(code)

if context_size > 100000:
    # Gemini handles 1M+ tokens
    task.required_capability = AgentCapability.LONG_CONTEXT
else:
    # Standard capability
    task.required_capability = AgentCapability.CODE_GENERATION
```

### Tip 2: Parallel for Critical Only

```python
# Critical code (payment, auth) → parallel
if is_critical(code):
    strategy = "parallel"  # Multiple perspectives
else:
    strategy = "best_agent"  # Cost-effective
```

### Tip 3: Pipeline Context

```python
# Each task has access to previous results
# Use task.context["pipeline_context"] to access

tasks = [task1, task2, task3]
results = await orchestrator.execute_pipeline(tasks)

# task2 receives task1 output in context
# task3 receives task1 + task2 outputs
```

### Tip 4: Health Checks

```python
# Check health before critical operations
health = get_registry().get_health_report()

if health['healthy_agents'] < 2:
    # Wait or notify admin
    await wait_for_agents()
```

---

## 📊 Performance Benchmarks

| Operation | Time | Tokens | Cost |
|-----------|------|--------|------|
| Simple code gen | 2-5s | 100-300 | $0.01 |
| Medium code gen | 5-15s | 500-1500 | $0.04 |
| Large code gen | 15-45s | 2000-5000 | $0.15 |
| Security audit | 5-10s | 300-800 | $0.02 |
| Architecture design | 10-20s | 800-2000 | $0.06 |
| Full pipeline (5 steps) | 30-90s | 3000-8000 | $0.50 |

---

## ✅ Checklist

### Before Production

- [ ] Set all API keys
- [ ] Test with `quickstart.py`
- [ ] Check agent health
- [ ] Run test suite
- [ ] Review cost estimates
- [ ] Configure logging
- [ ] Set up monitoring

### For Each Task

- [ ] Choose appropriate TaskType
- [ ] Set required_capability
- [ ] Select optimal strategy
- [ ] Set reasonable token limits
- [ ] Handle errors gracefully
- [ ] Log execution metrics

---

**Quick Reference Version:** 3.0.0
**Last Updated:** 2025-01-26
**For Full Docs:** See `MULTI_AGENT_COMPLETE.md`
