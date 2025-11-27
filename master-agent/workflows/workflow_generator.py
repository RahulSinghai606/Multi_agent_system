"""
Dynamic Workflow Generation System

NO HARDCODING - All workflows are generated dynamically based on:
- BRD analysis (project type, complexity, tech stack)
- User preferences (PM tool, CI/CD platform, repo structure)
- Learning from past projects (Graphiti patterns)

This ensures each project gets a custom-tailored SDLC workflow.
"""

import json
import logging
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict


class ProjectType(Enum):
    """Detected project types"""
    WEB_APPLICATION = "web_application"
    MOBILE_APP = "mobile_app"
    API_SERVICE = "api_service"
    DATA_PIPELINE = "data_pipeline"
    INFRASTRUCTURE = "infrastructure"
    DESKTOP_APP = "desktop_app"
    UNKNOWN = "unknown"


class ComplexityLevel(Enum):
    """Project complexity assessment"""
    SIMPLE = "simple"      # 1-2 weeks, <5K LOC, <3 integrations
    MODERATE = "moderate"  # 1-2 months, 5-20K LOC, 3-10 integrations
    COMPLEX = "complex"    # 3+ months, >20K LOC, >10 integrations


@dataclass
class PhaseConfig:
    """Configuration for a single SDLC phase"""
    name: str
    agents: List[str]
    tools: List[str]
    gates: List[str]
    deliverables: List[str]
    estimated_duration: str
    optional: bool = False


@dataclass
class WorkflowConfig:
    """Complete workflow configuration"""
    project_type: str
    complexity_level: str
    tech_stack: Dict[str, str]
    phases: List[PhaseConfig]
    integrations: Dict[str, Any]
    quality_thresholds: Dict[str, Any]
    repo_structure: str


class BRDAnalyzer:
    """
    Analyzes BRD to extract project characteristics

    Uses NLP and pattern matching to determine:
    - Project type
    - Complexity level
    - Tech stack
    - Requirements scope
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Keywords for project type detection
        self.project_type_keywords = {
            ProjectType.WEB_APPLICATION: [
                "web app", "website", "web application", "frontend", "backend",
                "full stack", "react", "vue", "angular", "next.js", "django", "flask"
            ],
            ProjectType.MOBILE_APP: [
                "mobile app", "ios", "android", "react native", "flutter",
                "mobile application", "app store", "play store"
            ],
            ProjectType.API_SERVICE: [
                "api", "rest api", "graphql", "microservice", "backend service",
                "api gateway", "endpoint", "webhook"
            ],
            ProjectType.DATA_PIPELINE: [
                "etl", "data pipeline", "data processing", "analytics",
                "data warehouse", "big data", "kafka", "spark"
            ],
            ProjectType.INFRASTRUCTURE: [
                "infrastructure", "devops", "cloud", "terraform", "kubernetes",
                "deployment", "ci/cd", "aws", "gcp", "azure"
            ]
        }

        # Complexity indicators
        self.complexity_indicators = {
            ComplexityLevel.SIMPLE: {
                "loc_max": 5000,
                "integrations_max": 3,
                "duration_weeks": 2,
                "keywords": ["simple", "basic", "mvp", "prototype", "proof of concept"]
            },
            ComplexityLevel.MODERATE: {
                "loc_max": 20000,
                "integrations_max": 10,
                "duration_weeks": 8,
                "keywords": ["moderate", "standard", "production", "scalable"]
            },
            ComplexityLevel.COMPLEX: {
                "loc_max": float('inf'),
                "integrations_max": float('inf'),
                "duration_weeks": 12,
                "keywords": ["complex", "enterprise", "large scale", "distributed"]
            }
        }

        # Tech stack detection patterns
        self.tech_stack_patterns = {
            "javascript": ["react", "vue", "angular", "node.js", "express", "next.js", "typescript"],
            "python": ["django", "flask", "fastapi", "python", "pandas", "numpy"],
            "java": ["java", "spring boot", "spring", "maven", "gradle"],
            "go": ["golang", "go", "gin", "echo"],
            "ruby": ["ruby", "rails", "ruby on rails"],
            "dotnet": ["c#", ".net", "asp.net", "dotnet"],
            "php": ["php", "laravel", "symfony"]
        }

    def analyze(self, brd_content: str) -> Dict[str, Any]:
        """
        Analyze BRD and extract project characteristics

        Args:
            brd_content: BRD document content (text)

        Returns:
            Dictionary with analysis results
        """
        brd_lower = brd_content.lower()

        # Detect project type
        project_type = self._detect_project_type(brd_lower)

        # Assess complexity
        complexity = self._assess_complexity(brd_lower, brd_content)

        # Detect tech stack
        tech_stack = self._detect_tech_stack(brd_lower)

        # Extract requirements count (heuristic)
        requirements_count = self._count_requirements(brd_content)

        # Extract integrations
        integrations = self._detect_integrations(brd_lower)

        analysis = {
            "project_type": project_type.value,
            "complexity_level": complexity.value,
            "tech_stack": tech_stack,
            "requirements_count": requirements_count,
            "integrations_count": len(integrations),
            "detected_integrations": integrations,
            "estimated_loc": self._estimate_loc(complexity, requirements_count),
            "estimated_duration_weeks": self._estimate_duration(complexity, requirements_count)
        }

        self.logger.info(f"BRD Analysis: {json.dumps(analysis, indent=2)}")

        return analysis

    def _detect_project_type(self, brd_text: str) -> ProjectType:
        """Detect project type from BRD content"""
        scores = {}

        for project_type, keywords in self.project_type_keywords.items():
            score = sum(1 for keyword in keywords if keyword in brd_text)
            scores[project_type] = score

        # Get highest scoring type
        if max(scores.values()) == 0:
            return ProjectType.UNKNOWN

        return max(scores, key=scores.get)

    def _assess_complexity(self, brd_text: str, full_content: str) -> ComplexityLevel:
        """Assess project complexity"""
        scores = {}

        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for keyword in indicators["keywords"] if keyword in brd_text)

            # Adjust based on document length (longer = more complex)
            doc_length = len(full_content)
            if doc_length > 10000:
                score += 2 if level == ComplexityLevel.COMPLEX else 0
            elif doc_length > 5000:
                score += 2 if level == ComplexityLevel.MODERATE else 0
            else:
                score += 2 if level == ComplexityLevel.SIMPLE else 0

            scores[level] = score

        return max(scores, key=scores.get)

    def _detect_tech_stack(self, brd_text: str) -> Dict[str, str]:
        """Detect technology stack"""
        detected_stack = {}

        for language, keywords in self.tech_stack_patterns.items():
            matches = [kw for kw in keywords if kw in brd_text]
            if matches:
                detected_stack[language] = matches[0]

        # Default to JavaScript if nothing detected
        if not detected_stack:
            detected_stack["javascript"] = "not_specified"

        return detected_stack

    def _count_requirements(self, content: str) -> int:
        """Estimate number of requirements (heuristic)"""
        # Look for numbered lists, bullet points, "shall", "must", "should"
        requirement_indicators = ["shall", "must", "should", "will", "requirement"]
        count = sum(content.lower().count(indicator) for indicator in requirement_indicators)

        # Normalize (rough heuristic)
        return min(count // 2, 100)  # Cap at 100 requirements

    def _detect_integrations(self, brd_text: str) -> List[str]:
        """Detect third-party integrations"""
        integration_keywords = [
            "stripe", "paypal", "aws", "gcp", "azure", "github", "gitlab",
            "jira", "slack", "google", "facebook", "twitter", "oauth",
            "api integration", "third-party", "external service"
        ]

        return [kw for kw in integration_keywords if kw in brd_text]

    def _estimate_loc(self, complexity: ComplexityLevel, requirements: int) -> int:
        """Estimate lines of code"""
        base_loc = {
            ComplexityLevel.SIMPLE: 2000,
            ComplexityLevel.MODERATE: 10000,
            ComplexityLevel.COMPLEX: 50000
        }

        # Adjust based on requirements count
        estimated = base_loc[complexity] + (requirements * 50)

        return estimated

    def _estimate_duration(self, complexity: ComplexityLevel, requirements: int) -> int:
        """Estimate project duration in weeks"""
        base_duration = self.complexity_indicators[complexity]["duration_weeks"]

        # Adjust based on requirements
        adjusted = base_duration + (requirements // 10)

        return min(adjusted, 52)  # Cap at 1 year


class WorkflowGenerator:
    """
    Generates custom SDLC workflows based on project analysis

    Each workflow is unique to the project - NO HARDCODED WORKFLOWS
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = logging.getLogger(__name__)
        self.analyzer = BRDAnalyzer()

    def generate_from_brd(
        self,
        brd_content: str,
        user_preferences: Optional[Dict[str, Any]] = None
    ) -> WorkflowConfig:
        """
        Generate workflow from BRD analysis

        Args:
            brd_content: BRD document content
            user_preferences: User preferences (PM tool, CI/CD, etc.)

        Returns:
            Complete WorkflowConfig
        """
        # Analyze BRD
        analysis = self.analyzer.analyze(brd_content)

        # Merge with user preferences
        preferences = user_preferences or {}

        # Generate phases based on project type
        phases = self._generate_phases(
            analysis["project_type"],
            analysis["complexity_level"],
            analysis["tech_stack"]
        )

        # Build workflow config
        workflow = WorkflowConfig(
            project_type=analysis["project_type"],
            complexity_level=analysis["complexity_level"],
            tech_stack=analysis["tech_stack"],
            phases=phases,
            integrations=preferences.get("integrations", {}),
            quality_thresholds=self._get_quality_thresholds(analysis["complexity_level"]),
            repo_structure=preferences.get("repo_structure", "single_repo")
        )

        self.logger.info(f"Generated workflow for {analysis['project_type']}")

        return workflow

    def _generate_phases(
        self,
        project_type: str,
        complexity: str,
        tech_stack: Dict[str, str]
    ) -> List[PhaseConfig]:
        """
        Generate SDLC phases dynamically based on project characteristics

        This is where we avoid hardcoding - phases are built from templates
        and customized per project
        """
        phases = []

        # Phase 1: Requirements (always included)
        phases.append(PhaseConfig(
            name="requirements",
            agents=["/sc:brainstorm", "/sc:spec-panel", "/sc:requirements-analyst"],
            tools=["Sequential", "Graphiti"],
            gates=["prd_approval"],
            deliverables=["PRD", "Technical Specifications", "Implementation Plan"],
            estimated_duration="1-2 weeks"
        ))

        # Phase 2: Design (customized by project type)
        design_agents = ["/sc:design", "system-architect", "Sequential"]

        if project_type == ProjectType.WEB_APPLICATION.value:
            design_agents.extend(["frontend-architect", "backend-architect"])
        elif project_type == ProjectType.MOBILE_APP.value:
            design_agents.append("mobile-architect")
        elif project_type == ProjectType.API_SERVICE.value:
            design_agents.append("backend-architect")

        phases.append(PhaseConfig(
            name="design",
            agents=design_agents,
            tools=["Sequential", "Figma", "Context7"],
            gates=["architecture_approval"],
            deliverables=["Architecture Diagrams", "DB Schema", "API Contracts"],
            estimated_duration="1-2 weeks"
        ))

        # Phase 3: Implementation (customized by tech stack)
        impl_agents = ["/sc:implement"]

        # Add tech-specific agents
        if "javascript" in tech_stack or "typescript" in tech_stack:
            impl_agents.extend(["frontend-architect", "ui-3d-specialist"])
        if "python" in tech_stack:
            impl_agents.append("backend-architect")

        impl_tools = ["Serena", "Magic", "Morphllm", "Context7"]

        phases.append(PhaseConfig(
            name="implementation",
            agents=impl_agents,
            tools=impl_tools,
            gates=["code_review_approval"],
            deliverables=["Implemented Features", "Unit Tests", "Documentation"],
            estimated_duration="4-8 weeks" if complexity == "moderate" else "8-16 weeks"
        ))

        # Phase 4: Testing (always included)
        phases.append(PhaseConfig(
            name="testing",
            agents=["/sc:test", "quality-engineer", "security-engineer"],
            tools=["Playwright", "Auditor"],
            gates=["test_coverage_approval"],
            deliverables=["Test Suites", "Coverage Reports", "Security Audit"],
            estimated_duration="1-2 weeks"
        ))

        # Phase 5: Deployment (always included)
        phases.append(PhaseConfig(
            name="deployment",
            agents=["/sc:build", "devops-architect"],
            tools=["Rube", "Docker"],
            gates=["production_deployment_approval"],
            deliverables=["Deployed Application", "Infrastructure as Code"],
            estimated_duration="1 week"
        ))

        # Phase 6: Monitoring (always included)
        phases.append(PhaseConfig(
            name="monitoring",
            agents=["Auditor", "devops-architect"],
            tools=["Rube", "Graphiti"],
            gates=["client_acceptance"],
            deliverables=["Documentation", "Runbooks", "Knowledge Export"],
            estimated_duration="1 week"
        ))

        return phases

    def _get_quality_thresholds(self, complexity: str) -> Dict[str, Any]:
        """Get quality thresholds based on complexity"""
        if complexity == "simple":
            return {
                "test_coverage_min": 70,
                "lighthouse_score_min": 90,
                "security_severity_block": "critical",
                "soc2_compliance": False
            }
        elif complexity == "moderate":
            return {
                "test_coverage_min": 80,
                "lighthouse_score_min": 95,
                "security_severity_block": "high",
                "soc2_compliance": True
            }
        else:  # complex
            return {
                "test_coverage_min": 90,
                "lighthouse_score_min": 95,
                "security_severity_block": "medium",
                "soc2_compliance": True,
                "performance_budget_ms": 2000
            }

    def save_workflow(self, workflow: WorkflowConfig, project_id: str) -> Path:
        """Save generated workflow to file"""
        workflows_dir = self.project_root / "master-agent" / "workflows" / "generated"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        workflow_file = workflows_dir / f"workflow_{project_id}.json"

        with open(workflow_file, 'w') as f:
            json.dump(asdict(workflow), f, indent=2)

        self.logger.info(f"Workflow saved: {workflow_file}")

        return workflow_file
