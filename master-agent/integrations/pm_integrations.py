"""
Project Management Tool Integrations

Supports:
- Jira (Cloud and Server)
- Linear
- Notion
- GitHub Projects

Each integration provides:
- Configuration generation
- Webhook setup templates
- API client initialization
- Workflow automation templates
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class PMConfig:
    """Project management tool configuration"""
    tool: str  # jira, linear, notion, github_projects
    project_key: Optional[str] = None
    api_url: Optional[str] = None
    api_token: Optional[str] = None
    workspace_id: Optional[str] = None
    custom_fields: Dict[str, Any] = field(default_factory=dict)


class PMIntegration(ABC):
    """Base class for project management integrations"""

    def __init__(self, config: PMConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def generate_config(self) -> Dict[str, Any]:
        """Generate tool-specific configuration"""
        pass

    @abstractmethod
    def generate_workflow_template(self) -> str:
        """Generate workflow automation template"""
        pass

    @abstractmethod
    def generate_webhook_config(self) -> Dict[str, Any]:
        """Generate webhook configuration"""
        pass

    def save_config(self, output_path: Optional[Path] = None):
        """Save configuration to file"""
        config_data = self.generate_config()

        if output_path is None:
            output_path = self.project_root / ".master-agent" / f"{self.config.tool}_config.json"

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(config_data, f, indent=2)

        self.logger.info(f"Configuration saved to {output_path}")


class JiraIntegration(PMIntegration):
    """Jira integration (Cloud and Server)"""

    def generate_config(self) -> Dict[str, Any]:
        """Generate Jira configuration"""
        return {
            "tool": "jira",
            "connection": {
                "url": self.config.api_url or "https://your-domain.atlassian.net",
                "email": "${JIRA_EMAIL}",
                "api_token": "${JIRA_API_TOKEN}",
                "project_key": self.config.project_key or "PROJ"
            },
            "issue_types": {
                "epic": "Epic",
                "story": "Story",
                "task": "Task",
                "bug": "Bug",
                "subtask": "Sub-task"
            },
            "custom_fields": self.config.custom_fields,
            "workflow": {
                "statuses": ["To Do", "In Progress", "In Review", "Done"],
                "transitions": {
                    "start": "In Progress",
                    "review": "In Review",
                    "complete": "Done"
                }
            },
            "automation": {
                "auto_link_commits": True,
                "auto_transition_on_pr": True,
                "auto_create_from_prd": True
            }
        }

    def generate_workflow_template(self) -> str:
        """Generate Jira workflow automation template"""
        return '''# Jira Workflow Automation

## Auto-create Issues from PRD

```python
from master_agent.integrations import JiraIntegration

# Initialize Jira client
jira = JiraIntegration.from_config()

# Parse PRD and create epic
epic = jira.create_issue(
    issue_type="Epic",
    summary="Feature: User Authentication",
    description=prd_content,
    labels=["security", "authentication"]
)

# Create user stories
for requirement in prd.requirements:
    story = jira.create_issue(
        issue_type="Story",
        summary=requirement.title,
        description=requirement.description,
        parent=epic.key,
        labels=requirement.tags
    )

    # Create technical tasks
    for task in requirement.technical_tasks:
        jira.create_issue(
            issue_type="Task",
            summary=task.title,
            description=task.description,
            parent=story.key,
            assignee=task.owner
        )
```

## Auto-transition on Git Events

```python
# In CI/CD pipeline
def on_commit(commit_message: str):
    # Extract Jira issue key from commit
    issue_key = extract_jira_key(commit_message)  # e.g., "PROJ-123"

    if issue_key:
        jira.add_comment(
            issue_key,
            f"Commit: {commit_message}\\nAuthor: {commit.author}"
        )
        jira.transition_issue(issue_key, "In Progress")

def on_pull_request_opened(pr: PullRequest):
    issue_key = extract_jira_key(pr.title)

    if issue_key:
        jira.add_comment(
            issue_key,
            f"PR created: {pr.url}\\nReviewers: {', '.join(pr.reviewers)}"
        )
        jira.transition_issue(issue_key, "In Review")

def on_pull_request_merged(pr: PullRequest):
    issue_key = extract_jira_key(pr.title)

    if issue_key:
        jira.add_comment(issue_key, f"PR merged: {pr.url}")
        jira.transition_issue(issue_key, "Done")
```

## Environment Variables

```bash
# .env
JIRA_EMAIL=your-email@example.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJ
JIRA_URL=https://your-domain.atlassian.net
```
'''

    def generate_webhook_config(self) -> Dict[str, Any]:
        """Generate Jira webhook configuration"""
        return {
            "webhooks": [
                {
                    "name": "Master Agent - Issue Created",
                    "url": "${WEBHOOK_BASE_URL}/jira/issue-created",
                    "events": ["jira:issue_created"],
                    "filters": {
                        "issue-related-events-section": f"project = {self.config.project_key}"
                    }
                },
                {
                    "name": "Master Agent - Issue Updated",
                    "url": "${WEBHOOK_BASE_URL}/jira/issue-updated",
                    "events": ["jira:issue_updated"],
                    "filters": {
                        "issue-related-events-section": f"project = {self.config.project_key}"
                    }
                },
                {
                    "name": "Master Agent - Issue Transitioned",
                    "url": "${WEBHOOK_BASE_URL}/jira/issue-transitioned",
                    "events": ["jira:issue_updated"],
                    "filters": {
                        "issue-related-events-section": f"project = {self.config.project_key} AND status CHANGED"
                    }
                }
            ],
            "setup_instructions": [
                "1. Go to Jira Settings → System → Webhooks",
                "2. Click 'Create a webhook'",
                "3. Use the configurations above",
                "4. Set WEBHOOK_BASE_URL in your environment",
                "5. Implement webhook handlers in your CI/CD pipeline"
            ]
        }


class LinearIntegration(PMIntegration):
    """Linear integration"""

    def generate_config(self) -> Dict[str, Any]:
        """Generate Linear configuration"""
        return {
            "tool": "linear",
            "connection": {
                "api_key": "${LINEAR_API_KEY}",
                "workspace_id": self.config.workspace_id or "your-workspace",
                "team_id": "${LINEAR_TEAM_ID}"
            },
            "labels": {
                "feature": "Feature",
                "bug": "Bug",
                "improvement": "Improvement",
                "security": "Security"
            },
            "workflow": {
                "states": ["Backlog", "Todo", "In Progress", "In Review", "Done", "Canceled"],
                "default_state": "Backlog"
            },
            "automation": {
                "auto_link_branches": True,
                "auto_close_on_merge": True,
                "auto_assign_from_commit": True
            }
        }

    def generate_workflow_template(self) -> str:
        """Generate Linear workflow automation template"""
        return '''# Linear Workflow Automation

## Auto-create Issues from PRD

```python
from master_agent.integrations import LinearIntegration

# Initialize Linear client
linear = LinearIntegration.from_config()

# Create parent issue for feature
feature = linear.create_issue(
    title="Feature: User Authentication",
    description=prd_content,
    labels=["feature", "security"],
    priority=1  # High priority
)

# Create sub-issues for requirements
for requirement in prd.requirements:
    linear.create_issue(
        title=requirement.title,
        description=requirement.description,
        parent=feature.id,
        labels=requirement.tags,
        assignee=requirement.owner
    )
```

## Git Integration

```python
# Branch naming convention: {team-key}-{issue-number}-{description}
# Example: ENG-123-user-authentication

def on_branch_created(branch_name: str):
    issue_id = extract_linear_id(branch_name)  # e.g., "ENG-123"

    if issue_id:
        linear.add_comment(
            issue_id,
            f"Branch created: {branch_name}"
        )
        linear.update_state(issue_id, "In Progress")

def on_pr_merged(pr: PullRequest):
    issue_id = extract_linear_id(pr.branch)

    if issue_id:
        linear.update_state(issue_id, "Done")
        linear.add_comment(issue_id, f"Completed via PR: {pr.url}")
```

## Environment Variables

```bash
# .env
LINEAR_API_KEY=lin_api_your-key-here
LINEAR_TEAM_ID=team-id-here
LINEAR_WORKSPACE_ID=workspace-id-here
```
'''

    def generate_webhook_config(self) -> Dict[str, Any]:
        """Generate Linear webhook configuration"""
        return {
            "webhooks": [
                {
                    "label": "Master Agent - Issue Events",
                    "url": "${WEBHOOK_BASE_URL}/linear/issue-event",
                    "resource_types": ["Issue"],
                    "event_types": ["create", "update", "remove"]
                },
                {
                    "label": "Master Agent - Comment Events",
                    "url": "${WEBHOOK_BASE_URL}/linear/comment-event",
                    "resource_types": ["Comment"],
                    "event_types": ["create"]
                }
            ],
            "setup_instructions": [
                "1. Go to Linear Settings → Workspace → Webhooks",
                "2. Click 'New webhook'",
                "3. Use the configurations above",
                "4. Set WEBHOOK_BASE_URL in your environment",
                "5. Linear will sign requests with a secret - verify signatures"
            ]
        }


class NotionIntegration(PMIntegration):
    """Notion integration"""

    def generate_config(self) -> Dict[str, Any]:
        """Generate Notion configuration"""
        return {
            "tool": "notion",
            "connection": {
                "api_token": "${NOTION_API_TOKEN}",
                "workspace_id": self.config.workspace_id or "your-workspace",
                "database_id": "${NOTION_DATABASE_ID}"
            },
            "database_schema": {
                "properties": {
                    "Name": {"type": "title"},
                    "Status": {
                        "type": "select",
                        "options": ["Backlog", "In Progress", "Review", "Complete"]
                    },
                    "Type": {
                        "type": "select",
                        "options": ["Epic", "Story", "Task", "Bug"]
                    },
                    "Priority": {
                        "type": "select",
                        "options": ["High", "Medium", "Low"]
                    },
                    "Assignee": {"type": "people"},
                    "Due Date": {"type": "date"},
                    "Tags": {"type": "multi_select"}
                }
            },
            "automation": {
                "auto_update_from_git": True,
                "sync_to_calendar": True,
                "generate_reports": True
            }
        }

    def generate_workflow_template(self) -> str:
        """Generate Notion workflow automation template"""
        return '''# Notion Workflow Automation

## Auto-create Database Entries from PRD

```python
from master_agent.integrations import NotionIntegration

# Initialize Notion client
notion = NotionIntegration.from_config()

# Create epic page
epic_page = notion.create_database_entry(
    database_id=notion.database_id,
    properties={
        "Name": {"title": [{"text": {"content": "Feature: User Authentication"}}]},
        "Type": {"select": {"name": "Epic"}},
        "Status": {"select": {"name": "Backlog"}},
        "Priority": {"select": {"name": "High"}},
        "Tags": {"multi_select": [{"name": "security"}, {"name": "authentication"}]}
    },
    children=[
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"text": {"content": "Overview"}}]}
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": prd_content}}]}
        }
    ]
)

# Create linked story pages
for requirement in prd.requirements:
    notion.create_database_entry(
        database_id=notion.database_id,
        properties={
            "Name": {"title": [{"text": {"content": requirement.title}}]},
            "Type": {"select": {"name": "Story"}},
            "Status": {"select": {"name": "Backlog"}},
            "Parent": {"relation": [{"id": epic_page.id}]}
        }
    )
```

## Git Integration

```python
def on_commit(commit: Commit):
    # Find Notion pages linked to this commit
    pages = notion.search_pages(query=commit.branch)

    for page in pages:
        # Update status
        notion.update_page_property(
            page.id,
            "Status",
            {"select": {"name": "In Progress"}}
        )

        # Add commit to page
        notion.append_block(
            page.id,
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "icon": {"emoji": "💾"},
                    "rich_text": [{
                        "text": {"content": f"Commit: {commit.message}\\nBy: {commit.author}"}
                    }]
                }
            }
        )
```

## Environment Variables

```bash
# .env
NOTION_API_TOKEN=secret_your-token-here
NOTION_DATABASE_ID=database-id-here
NOTION_WORKSPACE_ID=workspace-id-here
```
'''

    def generate_webhook_config(self) -> Dict[str, Any]:
        """Generate Notion webhook configuration"""
        return {
            "note": "Notion does not support webhooks directly. Use polling or Notion API events.",
            "polling_setup": {
                "method": "API polling",
                "interval": "5 minutes",
                "endpoints": [
                    {
                        "name": "Check database updates",
                        "endpoint": "POST https://api.notion.com/v1/databases/{database_id}/query",
                        "filter": {
                            "property": "Last edited time",
                            "date": {"after": "${LAST_CHECK_TIME}"}
                        }
                    }
                ]
            },
            "alternative": "Use Zapier or Make.com for webhook-like functionality"
        }


class GitHubProjectsIntegration(PMIntegration):
    """GitHub Projects (v2) integration"""

    def generate_config(self) -> Dict[str, Any]:
        """Generate GitHub Projects configuration"""
        return {
            "tool": "github_projects",
            "connection": {
                "token": "${GITHUB_TOKEN}",
                "org": "${GITHUB_ORG}",
                "project_number": "${GITHUB_PROJECT_NUMBER}"
            },
            "fields": {
                "status": {
                    "options": ["Backlog", "Todo", "In Progress", "In Review", "Done"]
                },
                "priority": {
                    "options": ["High", "Medium", "Low"]
                },
                "size": {
                    "options": ["XS", "S", "M", "L", "XL"]
                }
            },
            "automation": {
                "auto_add_issues": True,
                "auto_add_prs": True,
                "auto_move_on_pr_merge": True
            }
        }

    def generate_workflow_template(self) -> str:
        """Generate GitHub Projects workflow automation template"""
        return '''# GitHub Projects Workflow Automation

## Auto-create Issues from PRD

```python
from master_agent.integrations import GitHubProjectsIntegration

# Initialize GitHub client
gh = GitHubProjectsIntegration.from_config()

# Create epic issue
epic = gh.create_issue(
    title="Feature: User Authentication",
    body=prd_content,
    labels=["epic", "security", "authentication"]
)

# Add to project
gh.add_issue_to_project(epic.number)
gh.set_field_value(epic.number, "Status", "Backlog")
gh.set_field_value(epic.number, "Priority", "High")

# Create story issues
for requirement in prd.requirements:
    story = gh.create_issue(
        title=requirement.title,
        body=f"Epic: #{epic.number}\\n\\n{requirement.description}",
        labels=["story"] + requirement.tags
    )

    gh.add_issue_to_project(story.number)
    gh.set_field_value(story.number, "Status", "Backlog")
```

## GitHub Actions Integration

```yaml
# .github/workflows/project-automation.yml
name: Project Automation

on:
  issues:
    types: [opened, closed]
  pull_request:
    types: [opened, closed]

jobs:
  update_project:
    runs-on: ubuntu-latest
    steps:
      - name: Add issue to project
        if: github.event_name == 'issues' && github.event.action == 'opened'
        uses: actions/add-to-project@v0.4.0
        with:
          project-url: https://github.com/orgs/${{ github.repository_owner }}/projects/${PROJECT_NUMBER}
          github-token: ${{ secrets.GITHUB_TOKEN }}

      - name: Move to In Progress
        if: github.event_name == 'pull_request' && github.event.action == 'opened'
        uses: leonsteinhaeuser/project-beta-automations@v2.1.0
        with:
          gh_token: ${{ secrets.GITHUB_TOKEN }}
          organization: ${{ github.repository_owner }}
          project_id: ${PROJECT_NUMBER}
          resource_node_id: ${{ github.event.pull_request.node_id }}
          status_value: "In Progress"

      - name: Move to Done
        if: github.event_name == 'pull_request' && github.event.action == 'closed' && github.event.pull_request.merged
        uses: leonsteinhaeuser/project-beta-automations@v2.1.0
        with:
          gh_token: ${{ secrets.GITHUB_TOKEN }}
          organization: ${{ github.repository_owner }}
          project_id: ${PROJECT_NUMBER}
          resource_node_id: ${{ github.event.pull_request.node_id }}
          status_value: "Done"
```

## Environment Variables

```bash
# .env
GITHUB_TOKEN=ghp_your-token-here
GITHUB_ORG=your-org
GITHUB_PROJECT_NUMBER=1
```
'''

    def generate_webhook_config(self) -> Dict[str, Any]:
        """Generate GitHub Projects webhook configuration"""
        return {
            "note": "GitHub Projects uses repository webhooks. Configure at repository level.",
            "webhook_events": [
                "issues",
                "pull_request",
                "project_card",
                "project_column"
            ],
            "github_actions_recommended": True,
            "setup_instructions": [
                "1. Use GitHub Actions for automation (see workflow template)",
                "2. Or set up repository webhook at Settings → Webhooks",
                "3. Subscribe to: issues, pull_request, project events",
                "4. Point to your webhook handler URL",
                "5. Verify webhook signature for security"
            ]
        }


def get_pm_integration(tool: str, config: PMConfig, project_root: Path) -> PMIntegration:
    """Factory function to get appropriate PM integration"""
    integrations = {
        "jira": JiraIntegration,
        "linear": LinearIntegration,
        "notion": NotionIntegration,
        "github_projects": GitHubProjectsIntegration
    }

    integration_class = integrations.get(tool.lower())

    if not integration_class:
        raise ValueError(f"Unsupported PM tool: {tool}. Supported: {', '.join(integrations.keys())}")

    return integration_class(config, project_root)
