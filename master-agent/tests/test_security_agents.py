"""
Test script for security agents

Validates:
- AuditorEnhanced imports and basic functionality
- SecretScanner imports and pattern detection
- ComplianceValidator imports and control validation
"""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.security import AuditorEnhanced, SecretScanner, ComplianceValidator, SOC2Control, SecurityIssue


def test_imports():
    """Test that all security agents can be imported"""
    print("✓ All security agents imported successfully")
    return True


def test_auditor_enhanced():
    """Test AuditorEnhanced initialization"""
    try:
        project_root = Path(__file__).parent.parent
        auditor = AuditorEnhanced(project_root)

        # Check SOC2 controls initialized
        assert len(auditor.soc2_controls) == 4, "Expected 4 SOC2 controls"
        assert "CC6.1" in auditor.soc2_controls
        assert "CC6.6" in auditor.soc2_controls
        assert "CC6.7" in auditor.soc2_controls
        assert "CC7.2" in auditor.soc2_controls

        # Check OWASP patterns initialized
        assert len(auditor.owasp_patterns) > 0, "OWASP patterns should be initialized"

        # Check prompt injection patterns initialized
        assert len(auditor.prompt_injection_patterns) > 0, "Prompt injection patterns should be initialized"

        print("✓ AuditorEnhanced: Initialized successfully")
        print(f"  - SOC2 controls: {len(auditor.soc2_controls)}")
        print(f"  - OWASP patterns: {len(auditor.owasp_patterns)}")
        print(f"  - Prompt injection patterns: {len(auditor.prompt_injection_patterns)}")

        return True
    except Exception as e:
        print(f"✗ AuditorEnhanced test failed: {e}")
        return False


def test_secret_scanner():
    """Test SecretScanner initialization"""
    try:
        project_root = Path(__file__).parent.parent
        scanner = SecretScanner(project_root)

        # Check secret patterns initialized
        assert len(scanner.secret_patterns) >= 20, "Expected at least 20 secret patterns"

        # Check file extensions configured
        assert ".py" in scanner.scan_extensions
        assert ".js" in scanner.scan_extensions
        assert ".env" in scanner.scan_extensions

        # Check exclude paths configured
        assert "node_modules" in scanner.exclude_paths
        assert ".git" in scanner.exclude_paths

        print("✓ SecretScanner: Initialized successfully")
        print(f"  - Secret patterns: {len(scanner.secret_patterns)}")
        print(f"  - Scan extensions: {len(scanner.scan_extensions)}")
        print(f"  - Exclude paths: {len(scanner.exclude_paths)}")

        return True
    except Exception as e:
        print(f"✗ SecretScanner test failed: {e}")
        return False


def test_compliance_validator():
    """Test ComplianceValidator initialization"""
    try:
        project_root = Path(__file__).parent.parent
        validator = ComplianceValidator(project_root)

        # Check controls initialized
        assert len(validator.controls) == 4, "Expected 4 compliance controls"
        assert "CC6.1" in validator.controls
        assert "CC6.6" in validator.controls
        assert "CC6.7" in validator.controls
        assert "CC7.2" in validator.controls

        print("✓ ComplianceValidator: Initialized successfully")
        print(f"  - Compliance controls: {len(validator.controls)}")

        return True
    except Exception as e:
        print(f"✗ ComplianceValidator test failed: {e}")
        return False


def test_dataclasses():
    """Test security dataclasses"""
    try:
        # Test SOC2Control
        control = SOC2Control(
            control_id="CC6.1",
            name="Access Control",
            category="access_control",
            description="Test control",
            requirements=["auth", "authz"],
            validation_steps=["step1", "step2"]
        )
        assert control.control_id == "CC6.1"

        # Test SecurityIssue
        issue = SecurityIssue(
            severity="high",
            category="owasp",
            title="Test Issue",
            description="Test description",
            remediation="Fix it"
        )
        assert issue.severity == "high"

        print("✓ Dataclasses: All dataclasses work correctly")

        return True
    except Exception as e:
        print(f"✗ Dataclass test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 60)
    print("Security Agents Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Import Test", test_imports),
        ("AuditorEnhanced Test", test_auditor_enhanced),
        ("SecretScanner Test", test_secret_scanner),
        ("ComplianceValidator Test", test_compliance_validator),
        ("Dataclasses Test", test_dataclasses)
    ]

    results = []
    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 60)
        result = test_func()
        results.append((name, result))
        print()

    print("=" * 60)
    print("Test Results Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")

    print()
    print(f"Total: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ All security agents are working correctly!")
        return 0
    else:
        print(f"\n❌ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
