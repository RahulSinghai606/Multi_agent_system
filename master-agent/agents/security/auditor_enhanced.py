"""
Enhanced Auditor Agent

Expert in:
- SOC2 compliance automation (CC6.1, CC6.6, CC6.7, CC7.2)
- Prompt injection detection and prevention
- OWASP Top 10 automated scanning
- Real-time dependency vulnerability scanning
- Security best practices enforcement

Capabilities:
- SOC2 Type II control validation
- LLM prompt injection detection
- XSS, SQL injection, CSRF prevention
- Dependency CVE scanning
- Security code review
- Compliance reporting
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
class SOC2Control:
    """SOC2 Trust Services Criteria control"""

    control_id: str  # CC6.1, CC6.6, CC6.7, CC7.2
    name: str
    category: str  # "access_control", "encryption", "monitoring", "change_management"
    description: str
    requirements: List[str]
    validation_steps: List[str]
    compliance_status: str = "not_checked"  # "compliant", "non_compliant", "partial", "not_checked"
    findings: List[str] = field(default_factory=list)
    evidence: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class SecurityIssue:
    """Security vulnerability or compliance issue"""

    severity: str  # "critical", "high", "medium", "low", "info"
    category: str  # "soc2", "owasp", "prompt_injection", "dependency", "secret"
    title: str
    description: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    cwe_id: Optional[str] = None
    cve_id: Optional[str] = None
    remediation: str = ""
    code_example: Optional[str] = None
    affected_component: Optional[str] = None


@dataclass
class DependencyVulnerability:
    """Dependency vulnerability from CVE database"""

    package_name: str
    current_version: str
    vulnerable_versions: str
    fixed_version: Optional[str]
    cve_id: str
    severity: str
    description: str
    cvss_score: float


class AuditorEnhanced:
    """
    Enhanced security auditor with SOC2, OWASP, prompt injection

    Automated security validation:
    - SOC2 Type II compliance (CC6.1, CC6.6, CC6.7, CC7.2)
    - OWASP Top 10 vulnerability scanning
    - Prompt injection attack detection
    - Dependency vulnerability scanning
    - Secret detection
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "security-reports"
        self.logger = logging.getLogger(f"{__name__}.AuditorEnhanced")

        # Initialize SOC2 controls
        self.soc2_controls = self._initialize_soc2_controls()

        # OWASP patterns
        self.owasp_patterns = self._initialize_owasp_patterns()

        # Prompt injection patterns
        self.prompt_injection_patterns = self._initialize_prompt_injection_patterns()

    def comprehensive_audit(
        self,
        include_soc2: bool = True,
        include_owasp: bool = True,
        include_prompt_injection: bool = True,
        include_dependencies: bool = True,
        include_secrets: bool = True
    ) -> Dict[str, Any]:
        """
        Run comprehensive security audit

        Returns:
            Complete audit report with all findings
        """
        self.logger.info("Starting comprehensive security audit")

        issues: List[SecurityIssue] = []

        # SOC2 compliance check
        if include_soc2:
            self.logger.info("Running SOC2 compliance audit")
            soc2_results = self.audit_soc2_compliance()
            issues.extend(soc2_results["issues"])

        # OWASP Top 10 scan
        if include_owasp:
            self.logger.info("Running OWASP Top 10 scan")
            owasp_results = self.scan_owasp_top10()
            issues.extend(owasp_results)

        # Prompt injection detection
        if include_prompt_injection:
            self.logger.info("Running prompt injection detection")
            prompt_issues = self.detect_prompt_injection()
            issues.extend(prompt_issues)

        # Dependency vulnerabilities
        if include_dependencies:
            self.logger.info("Scanning dependencies for vulnerabilities")
            dep_issues = self.scan_dependencies()
            issues.extend(dep_issues)

        # Secret detection
        if include_secrets:
            self.logger.info("Scanning for exposed secrets")
            secret_issues = self.scan_secrets()
            issues.extend(secret_issues)

        # Generate report
        report = self._generate_audit_report(issues)

        self.logger.info(f"Audit complete: {len(issues)} issues found")

        return report

    def audit_soc2_compliance(self) -> Dict[str, Any]:
        """
        Audit SOC2 Type II compliance

        Focus on:
        - CC6.1: Logical and physical access controls
        - CC6.6: Encryption in transit and at rest
        - CC6.7: Transmission of data
        - CC7.2: Detection and monitoring
        """
        self.logger.info("Auditing SOC2 compliance controls")

        issues = []

        for control_id, control in self.soc2_controls.items():
            self.logger.info(f"Validating {control_id}: {control.name}")

            if control_id == "CC6.1":
                control_issues = self._audit_cc61_access_control()
            elif control_id == "CC6.6":
                control_issues = self._audit_cc66_encryption()
            elif control_id == "CC6.7":
                control_issues = self._audit_cc67_transmission()
            elif control_id == "CC7.2":
                control_issues = self._audit_cc72_monitoring()
            else:
                continue

            control.findings = [issue.description for issue in control_issues]
            control.compliance_status = "non_compliant" if control_issues else "compliant"

            issues.extend(control_issues)

        return {
            "controls": self.soc2_controls,
            "issues": issues,
            "compliant_count": sum(1 for c in self.soc2_controls.values() if c.compliance_status == "compliant"),
            "total_controls": len(self.soc2_controls)
        }

    def scan_owasp_top10(self) -> List[SecurityIssue]:
        """Scan for OWASP Top 10 vulnerabilities"""
        issues = []

        # Find all code files
        code_files = list(self.project_root.rglob("*.py")) + \
                    list(self.project_root.rglob("*.js")) + \
                    list(self.project_root.rglob("*.ts")) + \
                    list(self.project_root.rglob("*.tsx"))

        for file_path in code_files:
            if "node_modules" in str(file_path) or ".git" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                # A01: Broken Access Control
                issues.extend(self._check_broken_access_control(content, file_path))

                # A02: Cryptographic Failures
                issues.extend(self._check_crypto_failures(content, file_path))

                # A03: Injection
                issues.extend(self._check_injection(content, file_path))

                # A05: Security Misconfiguration
                issues.extend(self._check_security_misconfig(content, file_path))

                # A07: XSS
                issues.extend(self._check_xss(content, file_path))

                # A08: Insecure Deserialization
                issues.extend(self._check_insecure_deserialization(content, file_path))

            except Exception as e:
                self.logger.warning(f"Error scanning {file_path}: {e}")

        return issues

    def detect_prompt_injection(self) -> List[SecurityIssue]:
        """Detect prompt injection vulnerabilities in LLM integrations"""
        issues = []

        # Find files with LLM API calls
        code_files = list(self.project_root.rglob("*.py")) + \
                    list(self.project_root.rglob("*.js")) + \
                    list(self.project_root.rglob("*.ts"))

        for file_path in code_files:
            if "node_modules" in str(file_path) or ".git" in str(file_path):
                continue

            try:
                content = file_path.read_text()

                # Check for LLM API usage
                if not self._has_llm_api_call(content):
                    continue

                # Check for input sanitization
                if not self._has_input_sanitization(content):
                    issues.append(SecurityIssue(
                        severity="high",
                        category="prompt_injection",
                        title="Missing input sanitization before LLM call",
                        description="User input passed to LLM without sanitization/validation",
                        file_path=str(file_path),
                        remediation="Implement input validation and sanitization before LLM API calls",
                        code_example="# Sanitize user input\nuser_input = sanitize_input(user_input)\nprompt = f'Task: {user_input}'"
                    ))

                # Check for prompt injection indicators
                for pattern in self.prompt_injection_patterns:
                    if re.search(pattern["regex"], content, re.IGNORECASE):
                        issues.append(SecurityIssue(
                            severity="high",
                            category="prompt_injection",
                            title=f"Potential prompt injection: {pattern['name']}",
                            description=pattern["description"],
                            file_path=str(file_path),
                            remediation=pattern["remediation"]
                        ))

                # Check for output validation
                if not self._has_output_validation(content):
                    issues.append(SecurityIssue(
                        severity="medium",
                        category="prompt_injection",
                        title="Missing output validation from LLM",
                        description="LLM output not validated before use",
                        file_path=str(file_path),
                        remediation="Validate and sanitize LLM outputs before execution/display"
                    ))

            except Exception as e:
                self.logger.warning(f"Error checking {file_path}: {e}")

        return issues

    def scan_dependencies(self) -> List[SecurityIssue]:
        """Scan dependencies for known vulnerabilities"""
        issues = []

        # Check Python dependencies (requirements.txt, pyproject.toml)
        requirements_files = list(self.project_root.rglob("requirements*.txt")) + \
                           list(self.project_root.rglob("pyproject.toml"))

        for req_file in requirements_files:
            vulnerabilities = self._check_python_dependencies(req_file)

            for vuln in vulnerabilities:
                issues.append(SecurityIssue(
                    severity=vuln.severity,
                    category="dependency",
                    title=f"Vulnerable dependency: {vuln.package_name}",
                    description=f"{vuln.description} (CVE: {vuln.cve_id})",
                    file_path=str(req_file),
                    cve_id=vuln.cve_id,
                    remediation=f"Update {vuln.package_name} to version {vuln.fixed_version or 'latest'}"
                ))

        # Check JavaScript dependencies (package.json)
        package_jsons = list(self.project_root.rglob("package.json"))

        for pkg_file in package_jsons:
            if "node_modules" in str(pkg_file):
                continue

            vulnerabilities = self._check_npm_dependencies(pkg_file)

            for vuln in vulnerabilities:
                issues.append(SecurityIssue(
                    severity=vuln.severity,
                    category="dependency",
                    title=f"Vulnerable npm package: {vuln.package_name}",
                    description=f"{vuln.description} (CVE: {vuln.cve_id})",
                    file_path=str(pkg_file),
                    cve_id=vuln.cve_id,
                    remediation=f"Update {vuln.package_name} to version {vuln.fixed_version or 'latest'}"
                ))

        return issues

    def scan_secrets(self) -> List[SecurityIssue]:
        """Scan for exposed secrets and credentials"""
        issues = []

        secret_patterns = [
            (r'(?i)(api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "API Key"),
            (r'(?i)(password|passwd|pwd)["\']?\s*[:=]\s*["\']([^"\']{8,})["\']', "Password"),
            (r'(?i)(secret|token)["\']?\s*[:=]\s*["\']([a-zA-Z0-9_\-]{20,})["\']', "Secret/Token"),
            (r'-----BEGIN (RSA |EC )?PRIVATE KEY-----', "Private Key"),
            (r'(?i)aws[_-]?access[_-]?key[_-]?id["\']?\s*[:=]\s*["\']([A-Z0-9]{20})["\']', "AWS Access Key"),
            (r'(?i)sk_live_[a-zA-Z0-9]{24,}', "Stripe Live Key"),
        ]

        # Scan all text files
        text_files = list(self.project_root.rglob("*.py")) + \
                    list(self.project_root.rglob("*.js")) + \
                    list(self.project_root.rglob("*.ts")) + \
                    list(self.project_root.rglob("*.env*")) + \
                    list(self.project_root.rglob("*.json")) + \
                    list(self.project_root.rglob("*.yaml")) + \
                    list(self.project_root.rglob("*.yml"))

        for file_path in text_files:
            if "node_modules" in str(file_path) or ".git" in str(file_path):
                continue

            # Skip if in .gitignore
            if file_path.name == ".env" or file_path.name.startswith(".env."):
                continue  # .env files are expected to have secrets (should be in .gitignore)

            try:
                content = file_path.read_text()

                for pattern, secret_type in secret_patterns:
                    matches = re.finditer(pattern, content)

                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1

                        issues.append(SecurityIssue(
                            severity="critical",
                            category="secret",
                            title=f"Exposed {secret_type}",
                            description=f"Hardcoded {secret_type.lower()} found in source code",
                            file_path=str(file_path),
                            line_number=line_num,
                            remediation=f"Remove hardcoded {secret_type.lower()} and use environment variables"
                        ))

            except Exception as e:
                self.logger.warning(f"Error scanning {file_path}: {e}")

        return issues

    # Private helper methods

    def _initialize_soc2_controls(self) -> Dict[str, SOC2Control]:
        """Initialize SOC2 Type II controls"""
        return {
            "CC6.1": SOC2Control(
                control_id="CC6.1",
                name="Logical and Physical Access Controls",
                category="access_control",
                description="Implements controls to prevent unauthorized access",
                requirements=[
                    "Authentication mechanisms",
                    "Authorization controls",
                    "Role-based access control (RBAC)",
                    "Multi-factor authentication (MFA)",
                    "Session management"
                ],
                validation_steps=[
                    "Check for authentication middleware",
                    "Verify RBAC implementation",
                    "Validate MFA support",
                    "Review session timeout configuration"
                ]
            ),
            "CC6.6": SOC2Control(
                control_id="CC6.6",
                name="Encryption of Data",
                category="encryption",
                description="Encrypts data in transit and at rest",
                requirements=[
                    "TLS/SSL for data in transit",
                    "Encryption at rest for sensitive data",
                    "Strong encryption algorithms (AES-256)",
                    "Secure key management"
                ],
                validation_steps=[
                    "Check HTTPS enforcement",
                    "Verify database encryption",
                    "Validate encryption algorithm strength",
                    "Review key storage mechanisms"
                ]
            ),
            "CC6.7": SOC2Control(
                control_id="CC6.7",
                name="Transmission of Data",
                category="encryption",
                description="Protects data during transmission",
                requirements=[
                    "HTTPS/TLS for all external communication",
                    "Certificate validation",
                    "Secure protocols (TLS 1.2+)",
                    "HSTS headers"
                ],
                validation_steps=[
                    "Check for HTTPS-only communication",
                    "Verify TLS version >= 1.2",
                    "Validate HSTS implementation",
                    "Check for mixed content"
                ]
            ),
            "CC7.2": SOC2Control(
                control_id="CC7.2",
                name="Detection and Monitoring",
                category="monitoring",
                description="Detects and responds to security events",
                requirements=[
                    "Logging of security events",
                    "Monitoring and alerting",
                    "Incident response procedures",
                    "Anomaly detection"
                ],
                validation_steps=[
                    "Check logging implementation",
                    "Verify monitoring tools",
                    "Review alert configurations",
                    "Validate incident response plan"
                ]
            )
        }

    def _initialize_owasp_patterns(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize OWASP Top 10 detection patterns"""
        return {
            "sql_injection": [
                {"regex": r"execute\(.*\+.*\)", "desc": "String concatenation in SQL query"},
                {"regex": r"query\(.*f['\"].*{.*}.*['\"]", "desc": "F-string in SQL query"},
            ],
            "xss": [
                {"regex": r"innerHTML\s*=\s*.*", "desc": "Direct innerHTML assignment"},
                {"regex": r"dangerouslySetInnerHTML", "desc": "Dangerous HTML insertion"},
            ],
            "broken_auth": [
                {"regex": r"password.*==.*['\"]", "desc": "Hardcoded password comparison"},
                {"regex": r"jwt.*verify.*verify:\s*false", "desc": "JWT verification disabled"},
            ]
        }

    def _initialize_prompt_injection_patterns(self) -> List[Dict[str, Any]]:
        """Initialize prompt injection detection patterns"""
        return [
            {
                "name": "Direct user input in prompt",
                "regex": r"(prompt|messages)\s*=\s*.*\+\s*(user_input|request\.|input\()",
                "description": "User input directly concatenated into LLM prompt",
                "remediation": "Use parameterized prompts or input validation"
            },
            {
                "name": "Ignore previous instructions pattern",
                "regex": r"ignore (previous|all|above) instructions",
                "description": "Prompt contains instruction override attempt",
                "remediation": "Filter out instruction override attempts"
            },
            {
                "name": "System prompt override",
                "regex": r"(you are now|forget (everything|all)|new instructions|disregard)",
                "description": "Attempt to override system prompt",
                "remediation": "Implement prompt validation and filtering"
            }
        ]

    def _audit_cc61_access_control(self) -> List[SecurityIssue]:
        """Audit CC6.1: Access Control"""
        issues = []

        # Check for authentication
        auth_files = list(self.project_root.rglob("*auth*.py")) + \
                     list(self.project_root.rglob("*auth*.js")) + \
                     list(self.project_root.rglob("*auth*.ts"))

        if not auth_files:
            issues.append(SecurityIssue(
                severity="high",
                category="soc2",
                title="CC6.1: No authentication implementation found",
                description="No authentication module detected",
                remediation="Implement authentication (JWT, OAuth, etc.)"
            ))

        # Check for RBAC
        rbac_keywords = ["role", "permission", "authorize", "can_access"]
        has_rbac = False

        for auth_file in auth_files[:5]:  # Check first 5 auth files
            try:
                content = auth_file.read_text()
                if any(keyword in content.lower() for keyword in rbac_keywords):
                    has_rbac = True
                    break
            except:
                pass

        if not has_rbac:
            issues.append(SecurityIssue(
                severity="medium",
                category="soc2",
                title="CC6.1: No RBAC implementation detected",
                description="Role-based access control not found",
                remediation="Implement RBAC for authorization"
            ))

        return issues

    def _audit_cc66_encryption(self) -> List[SecurityIssue]:
        """Audit CC6.6: Encryption"""
        issues = []

        # Check for HTTPS enforcement
        config_files = list(self.project_root.rglob("*.config.js")) + \
                      list(self.project_root.rglob("settings.py")) + \
                      list(self.project_root.rglob(".env*"))

        has_https = False
        for config_file in config_files:
            try:
                content = config_file.read_text()
                if "https" in content.lower() or "ssl" in content.lower():
                    has_https = True
                    break
            except:
                pass

        if not has_https:
            issues.append(SecurityIssue(
                severity="high",
                category="soc2",
                title="CC6.6: HTTPS not enforced",
                description="No HTTPS/SSL configuration found",
                remediation="Enforce HTTPS for all communications"
            ))

        return issues

    def _audit_cc67_transmission(self) -> List[SecurityIssue]:
        """Audit CC6.7: Data Transmission"""
        issues = []

        # Check for HTTP URLs in code
        code_files = list(self.project_root.rglob("*.py"))[:20] + \
                     list(self.project_root.rglob("*.js"))[:20]

        for code_file in code_files:
            if "node_modules" in str(code_file):
                continue

            try:
                content = code_file.read_text()
                if re.search(r'http://(?!localhost|127\.0\.0\.1)', content):
                    issues.append(SecurityIssue(
                        severity="medium",
                        category="soc2",
                        title="CC6.7: HTTP URL in code",
                        description=f"Insecure HTTP URL found in {code_file.name}",
                        file_path=str(code_file),
                        remediation="Use HTTPS for external URLs"
                    ))
                    break  # One example is enough
            except:
                pass

        return issues

    def _audit_cc72_monitoring(self) -> List[SecurityIssue]:
        """Audit CC7.2: Monitoring"""
        issues = []

        # Check for logging
        log_files = list(self.project_root.rglob("*log*.py")) + \
                   list(self.project_root.rglob("*logger*.js"))

        if not log_files:
            issues.append(SecurityIssue(
                severity="medium",
                category="soc2",
                title="CC7.2: No logging implementation",
                description="No logging module detected",
                remediation="Implement structured logging for security events"
            ))

        return issues

    def _check_broken_access_control(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for broken access control (OWASP A01)"""
        issues = []

        # Check for missing authorization
        if re.search(r'@app\.(get|post|put|delete)', content) and \
           not re.search(r'@(require_auth|login_required|authorize)', content):
            issues.append(SecurityIssue(
                severity="high",
                category="owasp",
                title="A01: Missing authorization on endpoint",
                description="API endpoint without authorization check",
                file_path=str(file_path),
                cwe_id="CWE-862",
                remediation="Add authorization decorator/middleware"
            ))

        return issues

    def _check_crypto_failures(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for cryptographic failures (OWASP A02)"""
        issues = []

        # Weak hashing algorithms
        if re.search(r'hashlib\.(md5|sha1)', content):
            issues.append(SecurityIssue(
                severity="high",
                category="owasp",
                title="A02: Weak cryptographic hash",
                description="MD5/SHA1 used (consider SHA-256+)",
                file_path=str(file_path),
                cwe_id="CWE-327",
                remediation="Use SHA-256 or bcrypt for passwords"
            ))

        return issues

    def _check_injection(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for injection vulnerabilities (OWASP A03)"""
        issues = []

        # SQL injection
        if re.search(r'execute\(.*\+|cursor\.execute\(f["\']', content):
            issues.append(SecurityIssue(
                severity="critical",
                category="owasp",
                title="A03: SQL Injection risk",
                description="SQL query with string concatenation",
                file_path=str(file_path),
                cwe_id="CWE-89",
                remediation="Use parameterized queries"
            ))

        # Command injection
        if re.search(r'os\.(system|popen|exec)', content) and '+' in content:
            issues.append(SecurityIssue(
                severity="critical",
                category="owasp",
                title="A03: Command Injection risk",
                description="OS command with user input",
                file_path=str(file_path),
                cwe_id="CWE-78",
                remediation="Avoid shell commands or use subprocess with shell=False"
            ))

        return issues

    def _check_security_misconfig(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for security misconfiguration (OWASP A05)"""
        issues = []

        # Debug mode in production
        if re.search(r'DEBUG\s*=\s*True|debug:\s*true', content):
            issues.append(SecurityIssue(
                severity="medium",
                category="owasp",
                title="A05: Debug mode enabled",
                description="Debug mode should be disabled in production",
                file_path=str(file_path),
                remediation="Set DEBUG=False in production"
            ))

        return issues

    def _check_xss(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for XSS vulnerabilities (OWASP A07)"""
        issues = []

        if re.search(r'innerHTML\s*=|dangerouslySetInnerHTML', content):
            issues.append(SecurityIssue(
                severity="high",
                category="owasp",
                title="A07: XSS risk",
                description="Direct HTML injection possible",
                file_path=str(file_path),
                cwe_id="CWE-79",
                remediation="Use textContent or sanitize HTML"
            ))

        return issues

    def _check_insecure_deserialization(self, content: str, file_path: Path) -> List[SecurityIssue]:
        """Check for insecure deserialization (OWASP A08)"""
        issues = []

        if re.search(r'pickle\.loads|yaml\.load\(', content):
            issues.append(SecurityIssue(
                severity="high",
                category="owasp",
                title="A08: Insecure deserialization",
                description="Unsafe deserialization method",
                file_path=str(file_path),
                cwe_id="CWE-502",
                remediation="Use safe_load for YAML, avoid pickle"
            ))

        return issues

    def _has_llm_api_call(self, content: str) -> bool:
        """Check if file contains LLM API calls"""
        llm_patterns = [
            r'openai\.',
            r'anthropic\.',
            r'ChatCompletion',
            r'messages\.create',
            r'llm\(',
            r'chat\('
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in llm_patterns)

    def _has_input_sanitization(self, content: str) -> bool:
        """Check for input sanitization"""
        sanitize_patterns = [
            r'sanitize',
            r'validate_input',
            r'clean_input',
            r'escape',
            r'strip_tags'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in sanitize_patterns)

    def _has_output_validation(self, content: str) -> bool:
        """Check for output validation"""
        validate_patterns = [
            r'validate_output',
            r'sanitize_output',
            r'check_response'
        ]
        return any(re.search(pattern, content, re.IGNORECASE) for pattern in validate_patterns)

    def _check_python_dependencies(self, req_file: Path) -> List[DependencyVulnerability]:
        """Check Python dependencies (simplified - would use CVE database in production)"""
        vulnerabilities = []

        # Known vulnerable packages (example - would query CVE database)
        known_vulns = {
            "django": {"versions": "<3.2.0", "cve": "CVE-2021-35042", "severity": "high", "fixed": "3.2.0"},
            "flask": {"versions": "<2.0.0", "cve": "CVE-2023-30861", "severity": "medium", "fixed": "2.3.0"},
            "requests": {"versions": "<2.31.0", "cve": "CVE-2023-32681", "severity": "medium", "fixed": "2.31.0"},
        }

        try:
            content = req_file.read_text()

            for pkg_name, vuln_info in known_vulns.items():
                if pkg_name in content.lower():
                    vulnerabilities.append(DependencyVulnerability(
                        package_name=pkg_name,
                        current_version="unknown",
                        vulnerable_versions=vuln_info["versions"],
                        fixed_version=vuln_info["fixed"],
                        cve_id=vuln_info["cve"],
                        severity=vuln_info["severity"],
                        description=f"Known vulnerability in {pkg_name}",
                        cvss_score=7.5 if vuln_info["severity"] == "high" else 5.0
                    ))
        except:
            pass

        return vulnerabilities

    def _check_npm_dependencies(self, pkg_file: Path) -> List[DependencyVulnerability]:
        """Check npm dependencies (simplified)"""
        vulnerabilities = []

        # Known vulnerable npm packages (example)
        known_vulns = {
            "axios": {"versions": "<1.6.0", "cve": "CVE-2023-45857", "severity": "medium", "fixed": "1.6.0"},
            "express": {"versions": "<4.18.0", "cve": "CVE-2022-24999", "severity": "high", "fixed": "4.18.0"},
        }

        try:
            content = pkg_file.read_text()
            pkg_json = json.loads(content)

            dependencies = {**pkg_json.get("dependencies", {}), **pkg_json.get("devDependencies", {})}

            for pkg_name, vuln_info in known_vulns.items():
                if pkg_name in dependencies:
                    vulnerabilities.append(DependencyVulnerability(
                        package_name=pkg_name,
                        current_version=dependencies[pkg_name],
                        vulnerable_versions=vuln_info["versions"],
                        fixed_version=vuln_info["fixed"],
                        cve_id=vuln_info["cve"],
                        severity=vuln_info["severity"],
                        description=f"Known vulnerability in {pkg_name}",
                        cvss_score=7.5 if vuln_info["severity"] == "high" else 5.0
                    ))
        except:
            pass

        return vulnerabilities

    def _generate_audit_report(self, issues: List[SecurityIssue]) -> Dict[str, Any]:
        """Generate comprehensive audit report"""

        # Categorize by severity
        by_severity = {
            "critical": [i for i in issues if i.severity == "critical"],
            "high": [i for i in issues if i.severity == "high"],
            "medium": [i for i in issues if i.severity == "medium"],
            "low": [i for i in issues if i.severity == "low"],
            "info": [i for i in issues if i.severity == "info"]
        }

        # Categorize by type
        by_category = {}
        for issue in issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_issues": len(issues),
                "critical": len(by_severity["critical"]),
                "high": len(by_severity["high"]),
                "medium": len(by_severity["medium"]),
                "low": len(by_severity["low"]),
                "info": len(by_severity["info"])
            },
            "by_category": {
                cat: len(issues_list) for cat, issues_list in by_category.items()
            },
            "soc2_compliance": {
                control_id: {
                    "status": control.compliance_status,
                    "findings": control.findings
                }
                for control_id, control in self.soc2_controls.items()
            },
            "issues": [
                {
                    "severity": issue.severity,
                    "category": issue.category,
                    "title": issue.title,
                    "description": issue.description,
                    "file": issue.file_path,
                    "line": issue.line_number,
                    "remediation": issue.remediation,
                    "cwe_id": issue.cwe_id,
                    "cve_id": issue.cve_id
                }
                for issue in issues
            ]
        }

        return report

    def save_report(self, report: Dict[str, Any], filename: str = "security_audit.json") -> Path:
        """Save audit report to file"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        report_path = self.output_dir / filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Security audit report saved to {report_path}")

        # Also save human-readable markdown
        md_path = self.output_dir / filename.replace('.json', '.md')
        self._save_markdown_report(report, md_path)

        return report_path

    def _save_markdown_report(self, report: Dict[str, Any], path: Path):
        """Save human-readable markdown report"""

        md_content = f"""# Security Audit Report

**Date**: {report['timestamp']}

## Executive Summary

- **Total Issues**: {report['summary']['total_issues']}
- **Critical**: {report['summary']['critical']}
- **High**: {report['summary']['high']}
- **Medium**: {report['summary']['medium']}
- **Low**: {report['summary']['low']}

## Issues by Category

"""

        for category, count in report['by_category'].items():
            md_content += f"- **{category.upper()}**: {count} issues\n"

        md_content += "\n## SOC2 Compliance Status\n\n"

        for control_id, control_data in report['soc2_compliance'].items():
            status_emoji = "✅" if control_data['status'] == "compliant" else "❌"
            md_content += f"### {status_emoji} {control_id}: {control_data['status'].upper()}\n\n"

            if control_data['findings']:
                md_content += "**Findings**:\n"
                for finding in control_data['findings']:
                    md_content += f"- {finding}\n"
                md_content += "\n"

        md_content += "\n## Detailed Issues\n\n"

        for issue in report['issues']:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡",
                "low": "🔵",
                "info": "⚪"
            }.get(issue['severity'], "⚪")

            md_content += f"### {severity_emoji} {issue['title']}\n\n"
            md_content += f"**Severity**: {issue['severity'].upper()}\n"
            md_content += f"**Category**: {issue['category']}\n"

            if issue.get('file'):
                md_content += f"**File**: `{issue['file']}`"
                if issue.get('line'):
                    md_content += f" (line {issue['line']})"
                md_content += "\n"

            md_content += f"\n**Description**: {issue['description']}\n\n"
            md_content += f"**Remediation**: {issue['remediation']}\n\n"

            if issue.get('cwe_id'):
                md_content += f"**CWE**: {issue['cwe_id']}\n"
            if issue.get('cve_id'):
                md_content += f"**CVE**: {issue['cve_id']}\n"

            md_content += "\n---\n\n"

        with open(path, 'w') as f:
            f.write(md_content)

        self.logger.info(f"Markdown report saved to {path}")
