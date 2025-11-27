"""
Phase 1 Integration Test

Verifies that all Phase 1 components work together correctly:
- Orchestrator initialization
- Workflow generation from BRD
- State management and checkpoints
- Gate system
- CLI export

Run with: python3 -m pytest tests/test_phase1_integration.py -v
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add master-agent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.orchestrator import MasterOrchestrator, SDLCPhase
from state.state_manager import StateManager
from workflows.workflow_generator import BRDAnalyzer, WorkflowGenerator
from gates.gate_manager import GateManager, create_standard_gates
from cli_adapters.adapter_factory import AdapterFactory


def test_orchestrator_initialization():
    """Test orchestrator can be initialized"""
    print("\n=== Test: Orchestrator Initialization ===")

    project_root = Path("/Users/rahul.singh/Downloads/ADK")
    orchestrator = MasterOrchestrator(project_root)

    assert orchestrator is not None
    assert orchestrator.current_state is None  # Not initialized yet
    assert len(orchestrator.transitions) > 0

    print("✓ Orchestrator initialized successfully")


def test_brd_analysis():
    """Test BRD analyzer can classify projects"""
    print("\n=== Test: BRD Analysis ===")

    # Sample BRD content
    brd_content = """
    Project: E-Commerce Platform

    We need to build a modern e-commerce web application using React and Node.js.
    The platform should support product catalog, shopping cart, checkout, and payment processing.

    Technical Requirements:
    - Frontend: React with TypeScript
    - Backend: Node.js with Express
    - Database: PostgreSQL
    - Payment: Stripe integration
    - Authentication: JWT-based auth

    Expected timeline: 3-4 months
    Team size: 5 developers
    Estimated LOC: 15,000
    """

    analyzer = BRDAnalyzer()
    analysis = analyzer.analyze(brd_content)

    print(f"Analysis results: {json.dumps(analysis, indent=2)}")

    assert analysis["project_type"] in ["web_application", "api_service"]
    assert analysis["complexity_level"] in ["simple", "moderate", "complex"]
    assert len(analysis["tech_stack"]) > 0

    print("✓ BRD analysis completed successfully")
    return analysis


def test_workflow_generation(analysis):
    """Test workflow can be generated from analysis"""
    print("\n=== Test: Workflow Generation ===")

    project_root = Path("/Users/rahul.singh/Downloads/ADK")
    generator = WorkflowGenerator(project_root)

    # Simulate BRD content
    brd_content = "E-commerce platform with React and Node.js"

    user_preferences = {
        "integrations": {
            "pm_tool": "jira",
            "cicd_platform": "github_actions"
        },
        "repo_structure": "multi_repo"
    }

    workflow = generator.generate_from_brd(brd_content, user_preferences)

    assert workflow is not None
    assert len(workflow.phases) >= 6  # All 6 SDLC phases
    assert workflow.integrations["pm_tool"] == "jira"
    assert workflow.repo_structure == "multi_repo"

    print(f"✓ Workflow generated with {len(workflow.phases)} phases")
    return workflow


def test_project_initialization(workflow):
    """Test project can be initialized with workflow"""
    print("\n=== Test: Project Initialization ===")

    project_root = Path("/Users/rahul.singh/Downloads/ADK")
    orchestrator = MasterOrchestrator(project_root)

    project_id = f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    project_name = "Test E-Commerce Platform"

    # Convert workflow to dict
    workflow_dict = {
        "project_type": workflow.project_type,
        "complexity_level": workflow.complexity_level,
        "tech_stack": workflow.tech_stack,
        "integrations": workflow.integrations,
        "repo_structure": workflow.repo_structure
    }

    state = orchestrator.initialize_project(
        project_id=project_id,
        project_name=project_name,
        workflow_config=workflow_dict
    )

    assert state is not None
    assert state.project_id == project_id
    assert state.current_phase == SDLCPhase.IDLE.value
    assert len(state.pending_phases) == 6

    print(f"✓ Project initialized: {project_id}")
    return orchestrator


def test_state_transitions(orchestrator):
    """Test state machine transitions"""
    print("\n=== Test: State Transitions ===")

    # IDLE -> ANALYZING_BRD
    success = orchestrator.transition('start')
    assert success
    assert orchestrator.current_state.current_phase == SDLCPhase.ANALYZING_BRD.value

    # ANALYZING_BRD -> REQUIREMENTS
    success = orchestrator.transition('brd_parsed')
    assert success
    assert orchestrator.current_state.current_phase == SDLCPhase.REQUIREMENTS.value

    print("✓ State transitions working correctly")
    return orchestrator


def test_checkpoint_save_load(orchestrator):
    """Test checkpoint can be saved and loaded"""
    print("\n=== Test: Checkpoint Save/Load ===")

    # Save checkpoint
    checkpoint_path = orchestrator.save_checkpoint(reason="test")
    assert checkpoint_path.exists()

    print(f"✓ Checkpoint saved: {checkpoint_path}")

    # Load checkpoint
    project_root = Path("/Users/rahul.singh/Downloads/ADK")
    new_orchestrator = MasterOrchestrator(project_root)

    success = new_orchestrator.load_checkpoint(checkpoint_path)
    assert success
    assert new_orchestrator.current_state is not None
    assert new_orchestrator.current_state.current_phase == orchestrator.current_state.current_phase

    print("✓ Checkpoint loaded successfully")
    return checkpoint_path


def test_gate_system():
    """Test gate manager"""
    print("\n=== Test: Gate System ===")

    project_root = Path("/Users/rahul.singh/Downloads/ADK")
    gate_manager = GateManager(project_root)

    # Create standard gates
    gates = create_standard_gates()
    assert len(gates) == 6  # 6 standard gates

    # Register a gate
    gate = gates[0]  # requirements_prd_approval
    gate_manager.register_gate(gate)

    # Check registration
    assert gate.gate_id in gate_manager.active_gates
    assert not gate_manager.is_approved(gate.gate_id)

    # Get non-blocking work
    non_blocking = gate_manager.get_non_blocking_work(gate.gate_id)
    assert isinstance(non_blocking, list)

    print(f"✓ Gate system working ({len(gates)} gates registered)")


def test_cli_export(checkpoint_path):
    """Test CLI export adapters"""
    print("\n=== Test: CLI Export ===")

    # Load checkpoint state
    with open(checkpoint_path, 'r') as f:
        checkpoint = json.load(f)

    state = checkpoint["state"]

    # Test each adapter
    output_dir = Path("/Users/rahul.singh/Downloads/ADK/master-agent/state")

    for cli_type in ["gemini", "copilot", "qwen", "universal"]:
        adapter = AdapterFactory.create(cli_type)
        export_path = output_dir / f"test_export_{cli_type}.json"

        result = adapter.export(state, export_path)
        assert result.exists()

        # Verify export content
        with open(result, 'r') as f:
            export_data = json.load(f)

        assert export_data["version"] == "2.0"
        assert export_data["cli_agnostic"] is True
        assert export_data["target_cli"] == cli_type

        # Generate resume command
        resume_cmd = adapter.generate_resume_command(result)
        assert cli_type in resume_cmd.lower() or "universal" in resume_cmd.lower()

        print(f"✓ {cli_type.upper()} export successful")

    print("✓ All CLI adapters working")


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("MASTER AGENT - PHASE 1 INTEGRATION TESTS")
    print("="*60)

    try:
        # Test 1: Orchestrator
        test_orchestrator_initialization()

        # Test 2: BRD Analysis
        analysis = test_brd_analysis()

        # Test 3: Workflow Generation
        workflow = test_workflow_generation(analysis)

        # Test 4: Project Initialization
        orchestrator = test_project_initialization(workflow)

        # Test 5: State Transitions
        orchestrator = test_state_transitions(orchestrator)

        # Test 6: Checkpoint
        checkpoint_path = test_checkpoint_save_load(orchestrator)

        # Test 7: Gates
        test_gate_system()

        # Test 8: CLI Export
        test_cli_export(checkpoint_path)

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED - PHASE 1 COMPLETE")
        print("="*60)

        return True

    except Exception as e:
        print("\n" + "="*60)
        print(f"❌ TEST FAILED: {e}")
        print("="*60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
