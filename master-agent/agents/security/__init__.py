"""
Security Agent System - SOC2 Compliance & Threat Detection

Enhanced security agents:
- AuditorEnhanced: SOC2, prompt injection, OWASP Top 10, dependency scanning
- SecretScanner: Detect exposed secrets and credentials
- ComplianceValidator: SOC2 CC6.1, CC6.6, CC6.7, CC7.2 automation

Version: 1.0.0 (Phase 2)
"""

__version__ = "1.0.0"
__author__ = "Master Agent Security Team"

from .auditor_enhanced import AuditorEnhanced, SOC2Control, SecurityIssue
from .secret_scanner import SecretScanner
from .compliance_validator import ComplianceValidator

__all__ = [
    "AuditorEnhanced",
    "SOC2Control",
    "SecurityIssue",
    "SecretScanner",
    "ComplianceValidator",
]
