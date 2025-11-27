"""
Secret Scanner Agent

Expert in detecting exposed secrets and credentials:
- API keys, tokens, passwords in code
- Hardcoded credentials
- Private keys and certificates
- Database connection strings
- Cloud provider credentials (AWS, GCP, Azure)
- OAuth tokens and JWT secrets
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime
import json
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class SecretMatch:
    """Detected secret match"""

    secret_type: str  # "api_key", "password", "private_key", "token"
    file_path: str
    line_number: int
    line_content: str
    matched_pattern: str
    confidence: str  # "high", "medium", "low"
    severity: str  # "critical", "high", "medium"
    provider: Optional[str] = None  # "aws", "gcp", "github", "stripe", etc.
    remediation: str = ""


class SecretScanner:
    """
    Secret detection and credential scanning

    Detects:
    - API keys (AWS, GCP, Azure, Stripe, SendGrid, etc.)
    - Hardcoded passwords and tokens
    - Private keys (RSA, SSH, PGP)
    - Database credentials
    - OAuth secrets and JWT keys
    - Generic high-entropy strings
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "security-reports"
        self.logger = logging.getLogger(f"{__name__}.SecretScanner")

        # Initialize secret patterns
        self.secret_patterns = self._initialize_secret_patterns()

        # File extensions to scan
        self.scan_extensions = {
            ".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go",
            ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".sh",
            ".yaml", ".yml", ".json", ".xml", ".env", ".config",
            ".properties", ".conf", ".ini", ".toml"
        }

        # Paths to exclude
        self.exclude_paths = {
            "node_modules", ".git", "venv", "env", ".venv",
            "__pycache__", "build", "dist", ".next", ".cache"
        }

    def scan_for_secrets(self) -> List[SecretMatch]:
        """
        Scan project for exposed secrets

        Returns:
            List of detected secret matches
        """
        self.logger.info("Starting secret scan")

        matches = []
        scanned_files = 0

        # Find all files to scan
        for file_path in self._get_scannable_files():
            try:
                file_matches = self._scan_file(file_path)
                matches.extend(file_matches)
                scanned_files += 1

                if scanned_files % 100 == 0:
                    self.logger.info(f"Scanned {scanned_files} files, {len(matches)} secrets found")

            except Exception as e:
                self.logger.warning(f"Error scanning {file_path}: {e}")

        self.logger.info(f"Secret scan complete: {len(matches)} secrets in {scanned_files} files")

        return matches

    def scan_file(self, file_path: Path) -> List[SecretMatch]:
        """Scan single file for secrets"""
        return self._scan_file(file_path)

    def generate_report(self, matches: List[SecretMatch]) -> Dict[str, Any]:
        """Generate secret scanning report"""

        # Group by severity
        by_severity = {"critical": 0, "high": 0, "medium": 0}
        for match in matches:
            by_severity[match.severity] = by_severity.get(match.severity, 0) + 1

        # Group by secret type
        by_type = {}
        for match in matches:
            by_type[match.secret_type] = by_type.get(match.secret_type, 0) + 1

        # Group by provider
        by_provider = {}
        for match in matches:
            if match.provider:
                by_provider[match.provider] = by_provider.get(match.provider, 0) + 1

        # Group by file
        by_file = {}
        for match in matches:
            by_file[match.file_path] = by_file.get(match.file_path, 0) + 1

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_secrets": len(matches),
                "critical": by_severity.get("critical", 0),
                "high": by_severity.get("high", 0),
                "medium": by_severity.get("medium", 0),
                "affected_files": len(by_file)
            },
            "by_type": by_type,
            "by_provider": by_provider,
            "by_file": by_file,
            "matches": [
                {
                    "type": m.secret_type,
                    "file": m.file_path,
                    "line": m.line_number,
                    "severity": m.severity,
                    "confidence": m.confidence,
                    "provider": m.provider,
                    "pattern": m.matched_pattern,
                    "remediation": m.remediation
                }
                for m in matches
            ]
        }

        return report

    def save_report(self, report: Dict[str, Any], filename: str = "secret_scan.json") -> Path:
        """Save secret scan report"""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        report_path = self.output_dir / filename

        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Secret scan report saved to {report_path}")

        # Also save markdown
        md_path = self.output_dir / filename.replace('.json', '.md')
        self._save_markdown_report(report, md_path)

        return report_path

    def _initialize_secret_patterns(self) -> List[Dict[str, Any]]:
        """Initialize secret detection patterns"""

        patterns = [
            # AWS
            {
                "name": "AWS Access Key ID",
                "regex": r"AKIA[0-9A-Z]{16}",
                "type": "api_key",
                "provider": "aws",
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "AWS Secret Access Key",
                "regex": r"aws_secret_access_key\s*=\s*['\"]([A-Za-z0-9/+=]{40})['\"]",
                "type": "api_key",
                "provider": "aws",
                "severity": "critical",
                "confidence": "high"
            },

            # GitHub
            {
                "name": "GitHub Personal Access Token",
                "regex": r"ghp_[a-zA-Z0-9]{36}",
                "type": "token",
                "provider": "github",
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "GitHub OAuth Token",
                "regex": r"gho_[a-zA-Z0-9]{36}",
                "type": "token",
                "provider": "github",
                "severity": "critical",
                "confidence": "high"
            },

            # Google Cloud
            {
                "name": "Google API Key",
                "regex": r"AIza[0-9A-Za-z\\-_]{35}",
                "type": "api_key",
                "provider": "gcp",
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "Google OAuth",
                "regex": r"[0-9]+-[0-9A-Za-z_]{32}\\.apps\\.googleusercontent\\.com",
                "type": "oauth",
                "provider": "gcp",
                "severity": "high",
                "confidence": "high"
            },

            # Stripe
            {
                "name": "Stripe API Key",
                "regex": r"sk_live_[0-9a-zA-Z]{24}",
                "type": "api_key",
                "provider": "stripe",
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "Stripe Restricted API Key",
                "regex": r"rk_live_[0-9a-zA-Z]{24}",
                "type": "api_key",
                "provider": "stripe",
                "severity": "critical",
                "confidence": "high"
            },

            # Private Keys
            {
                "name": "RSA Private Key",
                "regex": r"-----BEGIN RSA PRIVATE KEY-----",
                "type": "private_key",
                "provider": None,
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "SSH Private Key",
                "regex": r"-----BEGIN OPENSSH PRIVATE KEY-----",
                "type": "private_key",
                "provider": None,
                "severity": "critical",
                "confidence": "high"
            },
            {
                "name": "PGP Private Key",
                "regex": r"-----BEGIN PGP PRIVATE KEY BLOCK-----",
                "type": "private_key",
                "provider": None,
                "severity": "critical",
                "confidence": "high"
            },

            # Generic Secrets
            {
                "name": "Generic API Key",
                "regex": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]([a-zA-Z0-9_\\-]{20,})['\"]",
                "type": "api_key",
                "provider": None,
                "severity": "high",
                "confidence": "medium"
            },
            {
                "name": "Generic Secret",
                "regex": r"(?i)(secret|token|password)\s*[:=]\s*['\"]([a-zA-Z0-9_\\-]{20,})['\"]",
                "type": "token",
                "provider": None,
                "severity": "high",
                "confidence": "medium"
            },
            {
                "name": "Database Connection String",
                "regex": r"(?i)(mongodb|mysql|postgres|postgresql)://[^\\s]+:[^\\s]+@[^\\s]+",
                "type": "password",
                "provider": None,
                "severity": "critical",
                "confidence": "high"
            },

            # JWT
            {
                "name": "JWT Token",
                "regex": r"eyJ[a-zA-Z0-9_-]+\\.eyJ[a-zA-Z0-9_-]+\\.[a-zA-Z0-9_-]+",
                "type": "token",
                "provider": None,
                "severity": "high",
                "confidence": "medium"
            },

            # SendGrid
            {
                "name": "SendGrid API Key",
                "regex": r"SG\\.[a-zA-Z0-9_-]{22}\\.[a-zA-Z0-9_-]{43}",
                "type": "api_key",
                "provider": "sendgrid",
                "severity": "critical",
                "confidence": "high"
            },

            # Slack
            {
                "name": "Slack Token",
                "regex": r"xox[baprs]-[0-9a-zA-Z]{10,48}",
                "type": "token",
                "provider": "slack",
                "severity": "critical",
                "confidence": "high"
            },

            # Azure
            {
                "name": "Azure Storage Account Key",
                "regex": r"(?i)DefaultEndpointsProtocol=https;AccountName=[^;]+;AccountKey=([a-zA-Z0-9+/=]{88})",
                "type": "api_key",
                "provider": "azure",
                "severity": "critical",
                "confidence": "high"
            },

            # Mailgun
            {
                "name": "Mailgun API Key",
                "regex": r"key-[0-9a-zA-Z]{32}",
                "type": "api_key",
                "provider": "mailgun",
                "severity": "high",
                "confidence": "medium"
            },

            # Twilio
            {
                "name": "Twilio API Key",
                "regex": r"SK[0-9a-fA-F]{32}",
                "type": "api_key",
                "provider": "twilio",
                "severity": "critical",
                "confidence": "high"
            }
        ]

        return patterns

    def _get_scannable_files(self) -> List[Path]:
        """Get list of files to scan"""
        files = []

        for file_path in self.project_root.rglob("*"):
            # Skip directories
            if file_path.is_dir():
                continue

            # Skip excluded paths
            if any(excluded in str(file_path) for excluded in self.exclude_paths):
                continue

            # Check file extension
            if file_path.suffix in self.scan_extensions:
                files.append(file_path)

        return files

    def _scan_file(self, file_path: Path) -> List[SecretMatch]:
        """Scan single file for secrets"""
        matches = []

        try:
            content = file_path.read_text(errors='ignore')
            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                for pattern in self.secret_patterns:
                    regex_matches = re.finditer(pattern["regex"], line)

                    for regex_match in regex_matches:
                        # Skip if in comment (basic heuristic)
                        if self._is_likely_comment(line):
                            continue

                        # Skip common false positives
                        if self._is_false_positive(line, pattern):
                            continue

                        matches.append(SecretMatch(
                            secret_type=pattern["type"],
                            file_path=str(file_path.relative_to(self.project_root)),
                            line_number=line_num,
                            line_content=line.strip(),
                            matched_pattern=pattern["name"],
                            confidence=pattern["confidence"],
                            severity=pattern["severity"],
                            provider=pattern.get("provider"),
                            remediation=self._get_remediation(pattern["type"])
                        ))

        except Exception as e:
            self.logger.warning(f"Error reading {file_path}: {e}")

        return matches

    def _is_likely_comment(self, line: str) -> bool:
        """Check if line is likely a comment"""
        stripped = line.strip()
        return (
            stripped.startswith("#") or
            stripped.startswith("//") or
            stripped.startswith("/*") or
            stripped.startswith("*")
        )

    def _is_false_positive(self, line: str, pattern: Dict[str, Any]) -> bool:
        """Check for common false positives"""

        # Example/placeholder patterns
        false_positive_indicators = [
            "example", "placeholder", "your_api_key", "xxx",
            "<your", "REPLACE", "TODO", "FIXME"
        ]

        line_lower = line.lower()
        return any(indicator in line_lower for indicator in false_positive_indicators)

    def _get_remediation(self, secret_type: str) -> str:
        """Get remediation advice for secret type"""

        remediations = {
            "api_key": "Remove hardcoded API key. Use environment variables or secret management system.",
            "token": "Remove hardcoded token. Store in environment variables or secure vault.",
            "password": "Remove hardcoded password. Use environment variables and rotate credentials.",
            "private_key": "Remove private key from code. Store in secure key management system.",
            "oauth": "Remove OAuth credentials. Use environment variables and secure storage."
        }

        return remediations.get(secret_type, "Remove hardcoded secret and use secure storage.")

    def _save_markdown_report(self, report: Dict[str, Any], path: Path):
        """Save human-readable markdown report"""

        md_content = f"""# Secret Scan Report

**Date**: {report['timestamp']}

## Executive Summary

- **Total Secrets Found**: {report['summary']['total_secrets']}
- **Critical**: {report['summary']['critical']}
- **High**: {report['summary']['high']}
- **Medium**: {report['summary']['medium']}
- **Affected Files**: {report['summary']['affected_files']}

## Secrets by Type

"""

        for secret_type, count in report['by_type'].items():
            md_content += f"- **{secret_type}**: {count}\n"

        if report['by_provider']:
            md_content += "\n## Secrets by Provider\n\n"
            for provider, count in report['by_provider'].items():
                md_content += f"- **{provider}**: {count}\n"

        md_content += "\n## Detailed Findings\n\n"

        for match in report['matches']:
            severity_emoji = {
                "critical": "🔴",
                "high": "🟠",
                "medium": "🟡"
            }.get(match['severity'], "⚪")

            md_content += f"### {severity_emoji} {match['pattern']}\n\n"
            md_content += f"**File**: `{match['file']}:{match['line']}`\n"
            md_content += f"**Severity**: {match['severity'].upper()}\n"
            md_content += f"**Type**: {match['type']}\n"

            if match.get('provider'):
                md_content += f"**Provider**: {match['provider']}\n"

            md_content += f"**Confidence**: {match['confidence']}\n\n"
            md_content += f"**Remediation**: {match['remediation']}\n\n"
            md_content += "---\n\n"

        with open(path, 'w') as f:
            f.write(md_content)

        self.logger.info(f"Markdown report saved to {path}")
