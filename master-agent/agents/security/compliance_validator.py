"""
Compliance Validator Agent

Expert in SOC2 Trust Services Criteria compliance validation:
- CC6.1: Logical and Physical Access Controls
- CC6.6: Encryption of Confidential Information
- CC6.7: Transmission of Confidential Information
- CC7.2: System Monitoring and Detection

Automated compliance checks with evidence collection
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import json
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class ComplianceEvidence:
    """Evidence for compliance validation"""

    control_id: str
    evidence_type: str  # "code", "config", "documentation", "test"
    file_path: Optional[str]
    line_number: Optional[int]
    description: str
    meets_requirement: bool
    details: str


@dataclass
class ComplianceResult:
    """Compliance validation result"""

    control_id: str
    control_name: str
    status: str  # "compliant", "non_compliant", "partial", "not_applicable"
    score: float  # 0.0 to 1.0
    evidence: List[ComplianceEvidence]
    gaps: List[str]
    recommendations: List[str]
    validation_timestamp: str


class ComplianceValidator:
    """
    SOC2 compliance automation and validation

    Validates:
    - CC6.1: Access controls (authentication, authorization, MFA)
    - CC6.6: Encryption at rest and in transit
    - CC6.7: Secure data transmission protocols
    - CC7.2: Logging, monitoring, and alerting

    Generates:
    - Compliance reports with evidence
    - Gap analysis
    - Remediation recommendations
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "compliance-reports"
        self.logger = logging.getLogger(f"{__name__}.ComplianceValidator")

        # Initialize compliance controls
        self.controls = self._initialize_controls()

    def validate_all_controls(self) -> Dict[str, ComplianceResult]:
        """
        Validate all SOC2 controls

        Returns:
            Dictionary of control_id -> ComplianceResult
        """
        self.logger.info("Starting SOC2 compliance validation")

        results = {}

        for control_id in ["CC6.1", "CC6.6", "CC6.7", "CC7.2"]:
            self.logger.info(f"Validating {control_id}")

            if control_id == "CC6.1":
                result = self.validate_cc61_access_control()
            elif control_id == "CC6.6":
                result = self.validate_cc66_encryption()
            elif control_id == "CC6.7":
                result = self.validate_cc67_transmission()
            elif control_id == "CC7.2":
                result = self.validate_cc72_monitoring()
            else:
                continue

            results[control_id] = result

        self.logger.info("SOC2 validation complete")

        return results

    def validate_cc61_access_control(self) -> ComplianceResult:
        """
        Validate CC6.1: Logical and Physical Access Controls

        Requirements:
        - Authentication mechanisms
        - Authorization controls
        - Multi-factor authentication (MFA)
        - Password policies
        - Session management
        - Role-based access control (RBAC)
        """
        evidence = []
        gaps = []

        # Check for authentication implementation
        auth_evidence = self._check_authentication()
        evidence.extend(auth_evidence)

        if not any(e.meets_requirement for e in auth_evidence):
            gaps.append("No authentication mechanism detected")

        # Check for authorization
        authz_evidence = self._check_authorization()
        evidence.extend(authz_evidence)

        if not any(e.meets_requirement for e in authz_evidence):
            gaps.append("No authorization controls detected")

        # Check for MFA
        mfa_evidence = self._check_mfa()
        evidence.extend(mfa_evidence)

        if not any(e.meets_requirement for e in mfa_evidence):
            gaps.append("Multi-factor authentication not implemented")

        # Check password policies
        password_evidence = self._check_password_policies()
        evidence.extend(password_evidence)

        # Calculate compliance score
        total_requirements = 4  # auth, authz, MFA, password policies
        met_requirements = sum(1 for e in evidence if e.meets_requirement)
        score = met_requirements / total_requirements if total_requirements > 0 else 0.0

        # Determine status
        if score >= 1.0:
            status = "compliant"
        elif score >= 0.5:
            status = "partial"
        else:
            status = "non_compliant"

        # Generate recommendations
        recommendations = self._generate_cc61_recommendations(gaps)

        return ComplianceResult(
            control_id="CC6.1",
            control_name="Logical and Physical Access Controls",
            status=status,
            score=score,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )

    def validate_cc66_encryption(self) -> ComplianceResult:
        """
        Validate CC6.6: Encryption of Confidential Information

        Requirements:
        - Encryption at rest
        - Encryption key management
        - Strong encryption algorithms (AES-256, RSA-2048+)
        - Database encryption
        - File system encryption
        """
        evidence = []
        gaps = []

        # Check for encryption at rest
        encryption_evidence = self._check_encryption_at_rest()
        evidence.extend(encryption_evidence)

        if not any(e.meets_requirement for e in encryption_evidence):
            gaps.append("Encryption at rest not detected")

        # Check key management
        key_mgmt_evidence = self._check_key_management()
        evidence.extend(key_mgmt_evidence)

        if not any(e.meets_requirement for e in key_mgmt_evidence):
            gaps.append("Encryption key management not implemented")

        # Check encryption algorithms
        algo_evidence = self._check_encryption_algorithms()
        evidence.extend(algo_evidence)

        # Calculate score
        total_requirements = 3
        met_requirements = sum(1 for e in evidence if e.meets_requirement)
        score = met_requirements / total_requirements if total_requirements > 0 else 0.0

        # Determine status
        if score >= 1.0:
            status = "compliant"
        elif score >= 0.5:
            status = "partial"
        else:
            status = "non_compliant"

        recommendations = self._generate_cc66_recommendations(gaps)

        return ComplianceResult(
            control_id="CC6.6",
            control_name="Encryption of Confidential Information",
            status=status,
            score=score,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )

    def validate_cc67_transmission(self) -> ComplianceResult:
        """
        Validate CC6.7: Transmission of Confidential Information

        Requirements:
        - HTTPS/TLS for web traffic
        - Secure WebSocket connections (WSS)
        - Certificate validation
        - Strong TLS protocols (TLS 1.2+)
        - Certificate pinning (optional but recommended)
        """
        evidence = []
        gaps = []

        # Check for HTTPS/TLS
        tls_evidence = self._check_tls_usage()
        evidence.extend(tls_evidence)

        if not any(e.meets_requirement for e in tls_evidence):
            gaps.append("HTTPS/TLS not properly configured")

        # Check TLS versions
        tls_version_evidence = self._check_tls_versions()
        evidence.extend(tls_version_evidence)

        # Check certificate validation
        cert_evidence = self._check_certificate_validation()
        evidence.extend(cert_evidence)

        # Calculate score
        total_requirements = 3
        met_requirements = sum(1 for e in evidence if e.meets_requirement)
        score = met_requirements / total_requirements if total_requirements > 0 else 0.0

        # Determine status
        if score >= 1.0:
            status = "compliant"
        elif score >= 0.5:
            status = "partial"
        else:
            status = "non_compliant"

        recommendations = self._generate_cc67_recommendations(gaps)

        return ComplianceResult(
            control_id="CC6.7",
            control_name="Transmission of Confidential Information",
            status=status,
            score=score,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )

    def validate_cc72_monitoring(self) -> ComplianceResult:
        """
        Validate CC7.2: System Monitoring and Detection

        Requirements:
        - Logging implementation
        - Security event monitoring
        - Anomaly detection
        - Audit trails
        - Log retention policies
        - Alerting mechanisms
        """
        evidence = []
        gaps = []

        # Check logging implementation
        logging_evidence = self._check_logging()
        evidence.extend(logging_evidence)

        if not any(e.meets_requirement for e in logging_evidence):
            gaps.append("Logging not properly implemented")

        # Check security monitoring
        monitoring_evidence = self._check_security_monitoring()
        evidence.extend(monitoring_evidence)

        if not any(e.meets_requirement for e in monitoring_evidence):
            gaps.append("Security monitoring not detected")

        # Check audit trails
        audit_evidence = self._check_audit_trails()
        evidence.extend(audit_evidence)

        # Check alerting
        alerting_evidence = self._check_alerting()
        evidence.extend(alerting_evidence)

        # Calculate score
        total_requirements = 4
        met_requirements = sum(1 for e in evidence if e.meets_requirement)
        score = met_requirements / total_requirements if total_requirements > 0 else 0.0

        # Determine status
        if score >= 1.0:
            status = "compliant"
        elif score >= 0.5:
            status = "partial"
        else:
            status = "non_compliant"

        recommendations = self._generate_cc72_recommendations(gaps)

        return ComplianceResult(
            control_id="CC7.2",
            control_name="System Monitoring and Detection",
            status=status,
            score=score,
            evidence=evidence,
            gaps=gaps,
            recommendations=recommendations,
            validation_timestamp=datetime.now().isoformat()
        )

    def generate_compliance_report(self, results: Dict[str, ComplianceResult]) -> Dict[str, Any]:
        """Generate comprehensive compliance report"""

        # Calculate overall compliance
        total_score = sum(r.score for r in results.values()) / len(results) if results else 0.0

        # Determine overall status
        if total_score >= 0.9:
            overall_status = "compliant"
        elif total_score >= 0.6:
            overall_status = "partial"
        else:
            overall_status = "non_compliant"

        # Count controls by status
        status_counts = {"compliant": 0, "partial": 0, "non_compliant": 0, "not_applicable": 0}
        for result in results.values():
            status_counts[result.status] = status_counts.get(result.status, 0) + 1

        # Collect all gaps
        all_gaps = []
        for result in results.values():
            all_gaps.extend(result.gaps)

        # Collect all recommendations
        all_recommendations = []
        for result in results.values():
            all_recommendations.extend(result.recommendations)

        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": overall_status,
            "overall_score": round(total_score, 2),
            "summary": {
                "total_controls": len(results),
                "compliant": status_counts["compliant"],
                "partial": status_counts["partial"],
                "non_compliant": status_counts["non_compliant"]
            },
            "controls": {
                control_id: {
                    "name": result.control_name,
                    "status": result.status,
                    "score": round(result.score, 2),
                    "evidence_count": len(result.evidence),
                    "gaps": result.gaps,
                    "recommendations": result.recommendations
                }
                for control_id, result in results.items()
            },
            "critical_gaps": all_gaps,
            "priority_recommendations": all_recommendations[:10]  # Top 10
        }

        return report

    def save_compliance_report(self, report: Dict[str, Any], filename: str = "soc2_compliance.json") -> Path:
        """Save compliance report to file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        report_path = self.output_dir / filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Compliance report saved to {report_path}")

        # Also save markdown
        md_path = self.output_dir / filename.replace('.json', '.md')
        self._save_markdown_report(report, md_path)

        return report_path

    # Helper methods for CC6.1 validation
    def _check_authentication(self) -> List[ComplianceEvidence]:
        """Check for authentication mechanisms"""
        evidence = []

        # Common authentication patterns
        auth_patterns = [
            r"(?i)(authenticate|auth|login|signin)",
            r"(?i)passport\.(authenticate|use)",
            r"(?i)jwt\.(sign|verify)",
            r"@RequiresAuth",
            r"@authenticated"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js")) + list(self.project_root.rglob("*.ts"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in auth_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.1",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Authentication mechanism detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence  # Found authentication

            except Exception:
                pass

        if not evidence:
            evidence.append(ComplianceEvidence(
                control_id="CC6.1",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="No authentication mechanism detected",
                meets_requirement=False,
                details="No authentication patterns found in codebase"
            ))

        return evidence

    def _check_authorization(self) -> List[ComplianceEvidence]:
        """Check for authorization controls"""
        evidence = []

        authz_patterns = [
            r"(?i)(authorize|permission|role|rbac|acl)",
            r"@RequiresRole",
            r"@RequiresPermission",
            r"canAccess|hasPermission|checkRole"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in authz_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.1",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Authorization controls detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        if not evidence:
            evidence.append(ComplianceEvidence(
                control_id="CC6.1",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="No authorization controls detected",
                meets_requirement=False,
                details="No authorization patterns found"
            ))

        return evidence

    def _check_mfa(self) -> List[ComplianceEvidence]:
        """Check for multi-factor authentication"""
        evidence = []

        mfa_patterns = [
            r"(?i)(mfa|2fa|two.factor|multi.factor|totp|otp)",
            r"(?i)authenticator|yubikey",
            r"speakeasy|otplib"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in mfa_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.1",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Multi-factor authentication detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        if not evidence:
            evidence.append(ComplianceEvidence(
                control_id="CC6.1",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="MFA not implemented",
                meets_requirement=False,
                details="No MFA patterns found"
            ))

        return evidence

    def _check_password_policies(self) -> List[ComplianceEvidence]:
        """Check for password policy enforcement"""
        evidence = []

        password_patterns = [
            r"(?i)password.?policy",
            r"(?i)password.?strength|password.?complexity",
            r"bcrypt|argon2|scrypt",
            r"(?i)min.?length|password.?length"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in password_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.1",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Password policies detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        return evidence

    # Helper methods for CC6.6 validation
    def _check_encryption_at_rest(self) -> List[ComplianceEvidence]:
        """Check for encryption at rest"""
        evidence = []

        encryption_patterns = [
            r"(?i)encrypt|cipher|aes|rsa",
            r"Fernet|cryptography",
            r"(?i)database.?encrypt"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in encryption_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.6",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Encryption at rest detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        if not evidence:
            evidence.append(ComplianceEvidence(
                control_id="CC6.6",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="Encryption at rest not detected",
                meets_requirement=False,
                details="No encryption patterns found"
            ))

        return evidence

    def _check_key_management(self) -> List[ComplianceEvidence]:
        """Check for encryption key management"""
        evidence = []

        key_mgmt_patterns = [
            r"(?i)key.?management|kms",
            r"(?i)vault|secrets.?manager",
            r"AWS.?KMS|Google.?KMS|Azure.?KeyVault"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in key_mgmt_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.6",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Key management system detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        return evidence

    def _check_encryption_algorithms(self) -> List[ComplianceEvidence]:
        """Check for strong encryption algorithms"""
        evidence = []

        strong_algos = [r"AES-?256", r"RSA-?2048", r"RSA-?4096", r"argon2", r"scrypt"]
        weak_algos = [r"DES", r"MD5", r"SHA-?1[^0-9]", r"RC4"]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                # Check for weak algorithms
                for pattern in weak_algos:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.6",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description=f"Weak encryption algorithm detected: {pattern}",
                            meets_requirement=False,
                            details="Weak algorithms should be replaced"
                        ))

                # Check for strong algorithms
                for pattern in strong_algos:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.6",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description=f"Strong encryption algorithm detected: {pattern}",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))

            except Exception:
                pass

        return evidence

    # Helper methods for CC6.7 validation
    def _check_tls_usage(self) -> List[ComplianceEvidence]:
        """Check for TLS/HTTPS usage"""
        evidence = []

        tls_patterns = [
            r"https://",
            r"(?i)tls|ssl",
            r"wss://",
            r"CERT_REQUIRED"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in tls_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.7",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="TLS/HTTPS usage detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        if not evidence:
            evidence.append(ComplianceEvidence(
                control_id="CC6.7",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="TLS/HTTPS not detected",
                meets_requirement=False,
                details="No TLS patterns found"
            ))

        return evidence

    def _check_tls_versions(self) -> List[ComplianceEvidence]:
        """Check TLS protocol versions"""
        evidence = []

        strong_tls = [r"TLS.?1\.[23]", r"TLSv1_[23]"]
        weak_tls = [r"TLS.?1\.0", r"TLSv1_0", r"SSLv[23]"]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                # Check for weak TLS
                for pattern in weak_tls:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.7",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description=f"Weak TLS version detected: {pattern}",
                            meets_requirement=False,
                            details="Upgrade to TLS 1.2 or higher"
                        ))

                # Check for strong TLS
                for pattern in strong_tls:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.7",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description=f"Strong TLS version detected: {pattern}",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))

            except Exception:
                pass

        return evidence

    def _check_certificate_validation(self) -> List[ComplianceEvidence]:
        """Check for certificate validation"""
        evidence = []

        cert_patterns = [
            r"(?i)verify.?cert|cert.?verify",
            r"CERT_REQUIRED",
            r"ssl_verify|verify_ssl"
        ]

        insecure_patterns = [
            r"verify.?=.?False",
            r"ssl_verify.?=.?False",
            r"CERT_NONE"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                # Check for insecure patterns
                for pattern in insecure_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.7",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Certificate validation disabled",
                            meets_requirement=False,
                            details="Enable certificate validation"
                        ))

                # Check for secure patterns
                for pattern in cert_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC6.7",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Certificate validation enabled",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))

            except Exception:
                pass

        return evidence

    # Helper methods for CC7.2 validation
    def _check_logging(self) -> List[ComplianceEvidence]:
        """Check for logging implementation"""
        evidence = []

        logging_patterns = [
            r"import logging",
            r"logger\.|log\.",
            r"winston|pino|bunyan",
            r"console\.(log|info|warn|error)"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        found_logging = False
        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in logging_patterns:
                    if re.search(pattern, content):
                        found_logging = True
                        break

                if found_logging:
                    break

            except Exception:
                pass

        if found_logging:
            evidence.append(ComplianceEvidence(
                control_id="CC7.2",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="Logging implementation detected",
                meets_requirement=True,
                details="Logging patterns found in codebase"
            ))
        else:
            evidence.append(ComplianceEvidence(
                control_id="CC7.2",
                evidence_type="code",
                file_path=None,
                line_number=None,
                description="Logging not detected",
                meets_requirement=False,
                details="No logging patterns found"
            ))

        return evidence

    def _check_security_monitoring(self) -> List[ComplianceEvidence]:
        """Check for security event monitoring"""
        evidence = []

        monitoring_patterns = [
            r"(?i)monitor|alert|sentry|datadog",
            r"(?i)security.?event|audit.?log",
            r"prometheus|grafana"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in monitoring_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC7.2",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Security monitoring detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        return evidence

    def _check_audit_trails(self) -> List[ComplianceEvidence]:
        """Check for audit trail implementation"""
        evidence = []

        audit_patterns = [
            r"(?i)audit.?log|audit.?trail",
            r"(?i)access.?log",
            r"(?i)user.?activity"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in audit_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC7.2",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Audit trails detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        return evidence

    def _check_alerting(self) -> List[ComplianceEvidence]:
        """Check for alerting mechanisms"""
        evidence = []

        alert_patterns = [
            r"(?i)alert|notify|notification",
            r"(?i)email.?alert|sms.?alert",
            r"pagerduty|opsgenie|victorops"
        ]

        files = list(self.project_root.rglob("*.py")) + list(self.project_root.rglob("*.js"))

        for file_path in files:
            if "node_modules" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                for pattern in alert_patterns:
                    if re.search(pattern, content, re.IGNORECASE):
                        evidence.append(ComplianceEvidence(
                            control_id="CC7.2",
                            evidence_type="code",
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=None,
                            description="Alerting mechanism detected",
                            meets_requirement=True,
                            details=f"Pattern: {pattern}"
                        ))
                        return evidence

            except Exception:
                pass

        return evidence

    # Recommendation generators
    def _generate_cc61_recommendations(self, gaps: List[str]) -> List[str]:
        """Generate recommendations for CC6.1"""
        recommendations = []

        if "No authentication mechanism detected" in str(gaps):
            recommendations.append("Implement authentication using JWT, OAuth 2.0, or similar")

        if "No authorization controls detected" in str(gaps):
            recommendations.append("Implement RBAC (Role-Based Access Control) or ABAC")

        if "Multi-factor authentication not implemented" in str(gaps):
            recommendations.append("Add MFA using TOTP (Google Authenticator) or SMS-based OTP")

        recommendations.append("Enforce strong password policies (min 12 chars, complexity requirements)")
        recommendations.append("Implement session timeout and idle logout mechanisms")

        return recommendations

    def _generate_cc66_recommendations(self, gaps: List[str]) -> List[str]:
        """Generate recommendations for CC6.6"""
        recommendations = []

        if "Encryption at rest not detected" in str(gaps):
            recommendations.append("Implement AES-256 encryption for sensitive data at rest")

        if "Encryption key management not implemented" in str(gaps):
            recommendations.append("Use AWS KMS, Google Cloud KMS, or HashiCorp Vault for key management")

        recommendations.append("Encrypt database fields containing PII/sensitive data")
        recommendations.append("Use strong encryption algorithms (AES-256, RSA-2048+)")
        recommendations.append("Implement key rotation policies")

        return recommendations

    def _generate_cc67_recommendations(self, gaps: List[str]) -> List[str]:
        """Generate recommendations for CC6.7"""
        recommendations = []

        if "HTTPS/TLS not properly configured" in str(gaps):
            recommendations.append("Enforce HTTPS for all external communications")

        recommendations.append("Use TLS 1.2 or higher, disable TLS 1.0/1.1")
        recommendations.append("Enable certificate validation for all external connections")
        recommendations.append("Implement HSTS (HTTP Strict Transport Security) headers")
        recommendations.append("Use strong cipher suites, disable weak ciphers")

        return recommendations

    def _generate_cc72_recommendations(self, gaps: List[str]) -> List[str]:
        """Generate recommendations for CC7.2"""
        recommendations = []

        if "Logging not properly implemented" in str(gaps):
            recommendations.append("Implement structured logging with appropriate log levels")

        if "Security monitoring not detected" in str(gaps):
            recommendations.append("Integrate with SIEM or monitoring tools (Datadog, Sentry, etc.)")

        recommendations.append("Log all authentication attempts and authorization decisions")
        recommendations.append("Implement automated alerting for security events")
        recommendations.append("Set up log retention policies (min 90 days for compliance)")
        recommendations.append("Monitor for anomalous patterns and potential threats")

        return recommendations

    def _initialize_controls(self) -> Dict[str, Any]:
        """Initialize SOC2 control definitions"""

        return {
            "CC6.1": {
                "name": "Logical and Physical Access Controls",
                "category": "access_control",
                "requirements": [
                    "Authentication mechanisms",
                    "Authorization controls",
                    "Multi-factor authentication",
                    "Password policies"
                ]
            },
            "CC6.6": {
                "name": "Encryption of Confidential Information",
                "category": "encryption",
                "requirements": [
                    "Encryption at rest",
                    "Key management",
                    "Strong encryption algorithms"
                ]
            },
            "CC6.7": {
                "name": "Transmission of Confidential Information",
                "category": "transmission",
                "requirements": [
                    "HTTPS/TLS usage",
                    "TLS 1.2+ protocols",
                    "Certificate validation"
                ]
            },
            "CC7.2": {
                "name": "System Monitoring and Detection",
                "category": "monitoring",
                "requirements": [
                    "Logging implementation",
                    "Security monitoring",
                    "Audit trails",
                    "Alerting mechanisms"
                ]
            }
        }

    def _save_markdown_report(self, report: Dict[str, Any], path: Path):
        """Save human-readable markdown report"""

        status_emoji = {
            "compliant": "✅",
            "partial": "🟡",
            "non_compliant": "❌"
        }

        md_content = f"""# SOC2 Compliance Report

**Date**: {report['timestamp']}

## Overall Status

**Status**: {status_emoji.get(report['overall_status'], '⚪')} {report['overall_status'].upper()}
**Score**: {report['overall_score']}/1.0

## Summary

- **Total Controls**: {report['summary']['total_controls']}
- **Compliant**: {report['summary']['compliant']}
- **Partial Compliance**: {report['summary']['partial']}
- **Non-Compliant**: {report['summary']['non_compliant']}

## Control Details

"""

        for control_id, control_data in report['controls'].items():
            emoji = status_emoji.get(control_data['status'], '⚪')
            md_content += f"### {emoji} {control_id}: {control_data['name']}\n\n"
            md_content += f"**Status**: {control_data['status'].upper()}\n"
            md_content += f"**Score**: {control_data['score']}/1.0\n"
            md_content += f"**Evidence Count**: {control_data['evidence_count']}\n\n"

            if control_data['gaps']:
                md_content += "**Gaps**:\n"
                for gap in control_data['gaps']:
                    md_content += f"- {gap}\n"
                md_content += "\n"

            if control_data['recommendations']:
                md_content += "**Recommendations**:\n"
                for rec in control_data['recommendations']:
                    md_content += f"- {rec}\n"
                md_content += "\n"

            md_content += "---\n\n"

        md_content += "## Priority Recommendations\n\n"
        for i, rec in enumerate(report['priority_recommendations'], 1):
            md_content += f"{i}. {rec}\n"

        with open(path, 'w') as f:
            f.write(md_content)

        self.logger.info(f"Markdown compliance report saved to {path}")
