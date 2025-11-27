"""
Integration Manager

Interactive CLI for selecting and configuring PM and CI/CD integrations.
Provides:
- Interactive tool selection prompts
- Configuration generation
- Setup validation
- Documentation links
"""

from typing import Dict, Any, Optional
from pathlib import Path
import sys
import logging

from .pm_integrations import PMConfig, get_pm_integration
from .cicd_integrations import CICDConfig, get_cicd_integration

logger = logging.getLogger(__name__)


class IntegrationManager:
    """Manage PM and CI/CD integrations"""

    PM_TOOLS = {
        "1": {"name": "Jira", "key": "jira", "description": "Atlassian Jira (Cloud or Server)"},
        "2": {"name": "Linear", "key": "linear", "description": "Linear issue tracker"},
        "3": {"name": "Notion", "key": "notion", "description": "Notion databases"},
        "4": {"name": "GitHub Projects", "key": "github_projects", "description": "GitHub Projects (v2)"},
        "5": {"name": "None", "key": "none", "description": "Skip PM integration"}
    }

    CICD_PLATFORMS = {
        "1": {"name": "GitHub Actions", "key": "github_actions", "description": "GitHub native CI/CD"},
        "2": {"name": "GitLab CI", "key": "gitlab_ci", "description": "GitLab native CI/CD"},
        "3": {"name": "Jenkins", "key": "jenkins", "description": "Jenkins automation server"},
        "4": {"name": "CircleCI", "key": "circleci", "description": "CircleCI cloud platform"},
        "5": {"name": "None", "key": "none", "description": "Skip CI/CD integration"}
    }

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logging.getLogger(f"{__name__}.IntegrationManager")

    def interactive_setup(self) -> Dict[str, Any]:
        """
        Interactive setup wizard for integrations

        Returns:
            Configuration summary
        """
        print("\n" + "=" * 70)
        print("Master Agent Integration Setup")
        print("=" * 70)

        # Select PM tool
        pm_tool = self._select_pm_tool()
        pm_config = None

        if pm_tool != "none":
            pm_config = self._configure_pm_tool(pm_tool)

        # Select CI/CD platform
        cicd_platform = self._select_cicd_platform()
        cicd_config = None

        if cicd_platform != "none":
            cicd_config = self._configure_cicd_platform(cicd_platform)

        # Generate configurations
        results = {
            "pm_tool": pm_tool,
            "cicd_platform": cicd_platform,
            "files_created": []
        }

        if pm_config:
            self._generate_pm_integration(pm_tool, pm_config, results)

        if cicd_config:
            self._generate_cicd_integration(cicd_platform, cicd_config, results)

        self._print_summary(results)

        return results

    def _select_pm_tool(self) -> str:
        """Interactive PM tool selection"""
        print("\n📋 SELECT PROJECT MANAGEMENT TOOL")
        print("-" * 70)

        for key, tool in self.PM_TOOLS.items():
            print(f"  {key}. {tool['name']:<20} - {tool['description']}")

        while True:
            choice = input("\nSelect PM tool (1-5): ").strip()

            if choice in self.PM_TOOLS:
                selected = self.PM_TOOLS[choice]
                print(f"\n✓ Selected: {selected['name']}")
                return selected["key"]
            else:
                print("Invalid selection. Please choose 1-5.")

    def _select_cicd_platform(self) -> str:
        """Interactive CI/CD platform selection"""
        print("\n🚀 SELECT CI/CD PLATFORM")
        print("-" * 70)

        for key, platform in self.CICD_PLATFORMS.items():
            print(f"  {key}. {platform['name']:<20} - {platform['description']}")

        while True:
            choice = input("\nSelect CI/CD platform (1-5): ").strip()

            if choice in self.CICD_PLATFORMS:
                selected = self.CICD_PLATFORMS[choice]
                print(f"\n✓ Selected: {selected['name']}")
                return selected["key"]
            else:
                print("Invalid selection. Please choose 1-5.")

    def _configure_pm_tool(self, tool: str) -> PMConfig:
        """Configure selected PM tool"""
        print(f"\n⚙️  CONFIGURE {tool.upper()}")
        print("-" * 70)

        config = PMConfig(tool=tool)

        if tool == "jira":
            config.api_url = input("Jira URL (e.g., https://your-domain.atlassian.net): ").strip()
            config.project_key = input("Project key (e.g., PROJ): ").strip().upper()
            print("\n💡 Tip: Set JIRA_EMAIL and JIRA_API_TOKEN in your .env file")

        elif tool == "linear":
            config.workspace_id = input("Linear workspace ID: ").strip()
            print("\n💡 Tip: Set LINEAR_API_KEY and LINEAR_TEAM_ID in your .env file")

        elif tool == "notion":
            config.workspace_id = input("Notion workspace ID: ").strip()
            print("\n💡 Tip: Set NOTION_API_TOKEN and NOTION_DATABASE_ID in your .env file")

        elif tool == "github_projects":
            print("\n💡 Tip: Set GITHUB_TOKEN, GITHUB_ORG, and GITHUB_PROJECT_NUMBER in your .env file")

        return config

    def _configure_cicd_platform(self, platform: str) -> CICDConfig:
        """Configure selected CI/CD platform"""
        print(f"\n⚙️  CONFIGURE {platform.upper()}")
        print("-" * 70)

        repository = input("Repository name (e.g., org/repo): ").strip()
        default_branch = input("Default branch [main]: ").strip() or "main"

        enable_security = input("Enable security scanning? (y/n) [y]: ").strip().lower() != 'n'
        enable_deps = input("Enable dependency tracking? (y/n) [y]: ").strip().lower() != 'n'

        config = CICDConfig(
            platform=platform,
            repository=repository,
            default_branch=default_branch,
            enable_security_scanning=enable_security,
            enable_dependency_tracking=enable_deps
        )

        return config

    def _generate_pm_integration(self, tool: str, config: PMConfig, results: Dict[str, Any]):
        """Generate PM integration files"""
        print(f"\n📝 Generating {tool} integration...")

        try:
            integration = get_pm_integration(tool, config, self.project_root)

            # Save configuration
            config_path = self.project_root / ".master-agent" / f"{tool}_config.json"
            integration.save_config(config_path)
            results["files_created"].append(str(config_path))

            # Save workflow template
            workflow_path = self.project_root / ".master-agent" / f"{tool}_workflow.md"
            workflow_path.parent.mkdir(parents=True, exist_ok=True)
            workflow_path.write_text(integration.generate_workflow_template())
            results["files_created"].append(str(workflow_path))

            # Save webhook config
            webhook_path = self.project_root / ".master-agent" / f"{tool}_webhooks.json"
            import json
            webhook_path.write_text(json.dumps(integration.generate_webhook_config(), indent=2))
            results["files_created"].append(str(webhook_path))

            print(f"✓ {tool} integration files created")

        except Exception as e:
            self.logger.error(f"Error generating {tool} integration: {e}")
            print(f"✗ Error: {e}")

    def _generate_cicd_integration(self, platform: str, config: CICDConfig, results: Dict[str, Any]):
        """Generate CI/CD integration files"""
        print(f"\n📝 Generating {platform} integration...")

        try:
            integration = get_cicd_integration(platform, config, self.project_root)

            # Save pipeline config
            integration.save_config()
            config_path = integration._get_default_config_path()
            results["files_created"].append(str(config_path))

            # Save deployment script
            deploy_script_path = self.project_root / "scripts" / "deploy.sh"
            deploy_script_path.parent.mkdir(parents=True, exist_ok=True)
            deploy_script_path.write_text(integration.generate_deployment_config())
            deploy_script_path.chmod(0o755)  # Make executable
            results["files_created"].append(str(deploy_script_path))

            print(f"✓ {platform} integration files created")

        except Exception as e:
            self.logger.error(f"Error generating {platform} integration: {e}")
            print(f"✗ Error: {e}")

    def _print_summary(self, results: Dict[str, Any]):
        """Print setup summary"""
        print("\n" + "=" * 70)
        print("✅ SETUP COMPLETE")
        print("=" * 70)

        if results["pm_tool"] != "none":
            print(f"\n📋 PM Tool: {results['pm_tool']}")

        if results["cicd_platform"] != "none":
            print(f"🚀 CI/CD Platform: {results['cicd_platform']}")

        if results["files_created"]:
            print("\n📁 Files Created:")
            for file_path in results["files_created"]:
                print(f"  - {file_path}")

        print("\n📚 Next Steps:")
        print("  1. Review generated configuration files")
        print("  2. Set required environment variables (check .env.example)")
        print("  3. Review workflow templates in .master-agent/")
        print("  4. Customize deployment scripts in scripts/")
        print("  5. Test integration with your project")

        if results["pm_tool"] != "none":
            print(f"\n💡 PM Tool Documentation:")
            print(f"  - Configuration: .master-agent/{results['pm_tool']}_config.json")
            print(f"  - Workflow: .master-agent/{results['pm_tool']}_workflow.md")
            print(f"  - Webhooks: .master-agent/{results['pm_tool']}_webhooks.json")

        if results["cicd_platform"] != "none":
            config_file = {
                "github_actions": ".github/workflows/master-agent.yml",
                "gitlab_ci": ".gitlab-ci.yml",
                "jenkins": "Jenkinsfile",
                "circleci": ".circleci/config.yml"
            }.get(results["cicd_platform"])

            print(f"\n💡 CI/CD Platform Documentation:")
            print(f"  - Pipeline: {config_file}")
            print(f"  - Deployment: scripts/deploy.sh")

        print("\n" + "=" * 70 + "\n")

    @classmethod
    def quick_setup(cls, project_root: Path, pm_tool: str, cicd_platform: str) -> Dict[str, Any]:
        """
        Non-interactive setup for automation

        Args:
            project_root: Project root directory
            pm_tool: PM tool key (jira, linear, notion, github_projects, none)
            cicd_platform: CI/CD platform key (github_actions, gitlab_ci, jenkins, circleci, none)

        Returns:
            Configuration summary
        """
        manager = cls(project_root)

        results = {
            "pm_tool": pm_tool,
            "cicd_platform": cicd_platform,
            "files_created": []
        }

        if pm_tool != "none":
            config = PMConfig(tool=pm_tool)
            manager._generate_pm_integration(pm_tool, config, results)

        if cicd_platform != "none":
            config = CICDConfig(
                platform=cicd_platform,
                repository="org/repo",  # Default, should be overridden
                default_branch="main"
            )
            manager._generate_cicd_integration(cicd_platform, config, results)

        return results


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Master Agent Integration Setup")
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: current directory)"
    )
    parser.add_argument(
        "--pm-tool",
        choices=["jira", "linear", "notion", "github_projects", "none"],
        help="PM tool for non-interactive setup"
    )
    parser.add_argument(
        "--cicd-platform",
        choices=["github_actions", "gitlab_ci", "jenkins", "circleci", "none"],
        help="CI/CD platform for non-interactive setup"
    )

    args = parser.parse_args()

    manager = IntegrationManager(args.project_root)

    if args.pm_tool or args.cicd_platform:
        # Non-interactive mode
        pm_tool = args.pm_tool or "none"
        cicd_platform = args.cicd_platform or "none"

        results = IntegrationManager.quick_setup(args.project_root, pm_tool, cicd_platform)
        manager._print_summary(results)
    else:
        # Interactive mode
        manager.interactive_setup()


if __name__ == "__main__":
    main()
