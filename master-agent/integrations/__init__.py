"""
Master Agent Integration System

Provides dynamic integration with project management tools and CI/CD platforms:
- Project Management: Jira, Linear, Notion, GitHub Projects
- CI/CD: GitHub Actions, GitLab CI, Jenkins, CircleCI
- Interactive selection during project initialization
- Auto-generation of configuration files
"""

from .pm_integrations import (
    PMIntegration,
    JiraIntegration,
    LinearIntegration,
    NotionIntegration,
    GitHubProjectsIntegration,
    get_pm_integration
)

from .cicd_integrations import (
    CICDIntegration,
    GitHubActionsIntegration,
    GitLabCIIntegration,
    JenkinsIntegration,
    CircleCIIntegration,
    get_cicd_integration
)

from .integration_manager import IntegrationManager

__all__ = [
    # PM Integrations
    "PMIntegration",
    "JiraIntegration",
    "LinearIntegration",
    "NotionIntegration",
    "GitHubProjectsIntegration",
    "get_pm_integration",

    # CI/CD Integrations
    "CICDIntegration",
    "GitHubActionsIntegration",
    "GitLabCIIntegration",
    "JenkinsIntegration",
    "CircleCIIntegration",
    "get_cicd_integration",

    # Manager
    "IntegrationManager"
]
