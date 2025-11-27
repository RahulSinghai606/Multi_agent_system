"""
CI/CD Platform Integrations

Supports:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI

Each integration provides:
- Pipeline configuration generation
- Multi-stage workflow templates
- Security scanning integration
- Deployment automation
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


@dataclass
class CICDConfig:
    """CI/CD platform configuration"""
    platform: str  # github_actions, gitlab_ci, jenkins, circleci
    repository: str
    default_branch: str = "main"
    environments: List[str] = field(default_factory=lambda: ["development", "staging", "production"])
    enable_security_scanning: bool = True
    enable_dependency_tracking: bool = True
    custom_steps: Dict[str, Any] = field(default_factory=dict)


class CICDIntegration(ABC):
    """Base class for CI/CD integrations"""

    def __init__(self, config: CICDConfig, project_root: Path):
        self.config = config
        self.project_root = project_root
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    @abstractmethod
    def generate_pipeline_config(self) -> str:
        """Generate CI/CD pipeline configuration"""
        pass

    @abstractmethod
    def generate_deployment_config(self) -> str:
        """Generate deployment configuration"""
        pass

    def save_config(self, output_path: Optional[Path] = None):
        """Save pipeline configuration to appropriate location"""
        config_content = self.generate_pipeline_config()

        if output_path is None:
            output_path = self._get_default_config_path()

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(config_content)

        self.logger.info(f"CI/CD configuration saved to {output_path}")

    @abstractmethod
    def _get_default_config_path(self) -> Path:
        """Get default config path for this platform"""
        pass


class GitHubActionsIntegration(CICDIntegration):
    """GitHub Actions integration"""

    def _get_default_config_path(self) -> Path:
        return self.project_root / ".github" / "workflows" / "master-agent.yml"

    def generate_pipeline_config(self) -> str:
        """Generate GitHub Actions workflow"""
        security_scan = ""
        if self.config.enable_security_scanning:
            security_scan = """
      - name: Security Scan
        run: |
          python -m master_agent.agents.security.secret_scanner
          python -m master_agent.agents.security.compliance_validator
"""

        dependency_check = ""
        if self.config.enable_dependency_tracking:
            dependency_check = """
      - name: Dependency Tracking
        run: |
          python -m master_agent.orchestration.dependency_tracker
"""

        return f'''name: Master Agent CI/CD

on:
  push:
    branches: [{self.config.default_branch}]
  pull_request:
    branches: [{self.config.default_branch}]
  workflow_dispatch:

env:
  PYTHON_VERSION: "3.11"
  NODE_VERSION: "18"

jobs:
  # Quality Gates
  quality:
    name: Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for better analysis

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: ${{{{ env.PYTHON_VERSION }}}}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .

      - name: Run linters
        run: |
          flake8 .
          black --check .
          mypy .

      - name: Run tests
        run: |
          pytest --cov=master_agent --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml
{security_scan}{dependency_check}

  # Build and Package
  build:
    name: Build
    needs: quality
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{{{ matrix.python-version }}}}
        uses: actions/setup-python@v4
        with:
          python-version: ${{{{ matrix.python-version }}}}

      - name: Build package
        run: |
          python -m pip install --upgrade pip build
          python -m build

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: dist-${{{{ matrix.python-version }}}}
          path: dist/

  # Deploy to Development
  deploy_dev:
    name: Deploy to Development
    needs: build
    if: github.event_name == 'push' && github.ref == 'refs/heads/{self.config.default_branch}'
    runs-on: ubuntu-latest
    environment:
      name: development
      url: ${{{{ steps.deploy.outputs.url }}}}
    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist-${{{{ env.PYTHON_VERSION }}}}
          path: dist/

      - name: Deploy to Development
        id: deploy
        run: |
          echo "Deploying to development environment..."
          # Add your deployment script here
          echo "url=https://dev.example.com" >> $GITHUB_OUTPUT

  # Deploy to Staging (on manual trigger or tag)
  deploy_staging:
    name: Deploy to Staging
    needs: build
    if: github.event_name == 'workflow_dispatch' || startsWith(github.ref, 'refs/tags/')
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: ${{{{ steps.deploy.outputs.url }}}}
    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist-${{{{ env.PYTHON_VERSION }}}}
          path: dist/

      - name: Deploy to Staging
        id: deploy
        run: |
          echo "Deploying to staging environment..."
          # Add your deployment script here
          echo "url=https://staging.example.com" >> $GITHUB_OUTPUT

  # Deploy to Production (manual approval required)
  deploy_production:
    name: Deploy to Production
    needs: deploy_staging
    if: github.event_name == 'workflow_dispatch'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: ${{{{ steps.deploy.outputs.url }}}}
    steps:
      - uses: actions/checkout@v4

      - name: Download artifacts
        uses: actions/download-artifact@v3
        with:
          name: dist-${{{{ env.PYTHON_VERSION }}}}
          path: dist/

      - name: Deploy to Production
        id: deploy
        run: |
          echo "Deploying to production environment..."
          # Add your deployment script here
          echo "url=https://app.example.com" >> $GITHUB_OUTPUT

      - name: Create release
        uses: actions/create-release@v1
        env:
          GITHUB_TOKEN: ${{{{ secrets.GITHUB_TOKEN }}}}
        with:
          tag_name: ${{{{ github.ref }}}}
          release_name: Release ${{{{ github.ref }}}}
          draft: false
          prerelease: false
'''

    def generate_deployment_config(self) -> str:
        """Generate deployment script template"""
        return '''#!/bin/bash
# Master Agent Deployment Script

set -e

ENVIRONMENT=$1
VERSION=${2:-latest}

if [ -z "$ENVIRONMENT" ]; then
    echo "Usage: $0 <environment> [version]"
    exit 1
fi

echo "Deploying Master Agent to $ENVIRONMENT (version: $VERSION)"

case $ENVIRONMENT in
    development)
        echo "Deploying to development..."
        # Add development deployment commands
        ;;
    staging)
        echo "Deploying to staging..."
        # Add staging deployment commands
        ;;
    production)
        echo "Deploying to production..."
        # Add production deployment commands
        ;;
    *)
        echo "Unknown environment: $ENVIRONMENT"
        exit 1
        ;;
esac

echo "Deployment complete!"
'''


class GitLabCIIntegration(CICDIntegration):
    """GitLab CI/CD integration"""

    def _get_default_config_path(self) -> Path:
        return self.project_root / ".gitlab-ci.yml"

    def generate_pipeline_config(self) -> str:
        """Generate GitLab CI configuration"""
        security_scan = ""
        if self.config.enable_security_scanning:
            security_scan = """
  script:
    - python -m master_agent.agents.security.secret_scanner
    - python -m master_agent.agents.security.compliance_validator
  only:
    - merge_requests
    - main
"""

        return f'''# Master Agent GitLab CI/CD Pipeline

stages:
  - quality
  - build
  - test
  - security
  - deploy

variables:
  PYTHON_VERSION: "3.11"
  PIP_CACHE_DIR: "$CI_PROJECT_DIR/.cache/pip"

cache:
  paths:
    - .cache/pip
    - venv/

# Quality Checks
lint:
  stage: quality
  image: python:$PYTHON_VERSION
  before_script:
    - pip install flake8 black mypy
  script:
    - flake8 .
    - black --check .
    - mypy .
  only:
    - merge_requests
    - {self.config.default_branch}

# Build
build:
  stage: build
  image: python:$PYTHON_VERSION
  before_script:
    - pip install --upgrade pip build
  script:
    - python -m build
  artifacts:
    paths:
      - dist/
    expire_in: 1 week
  only:
    - merge_requests
    - {self.config.default_branch}
    - tags

# Tests
test:
  stage: test
  image: python:$PYTHON_VERSION
  parallel:
    matrix:
      - PYTHON_VERSION: ["3.10", "3.11", "3.12"]
  before_script:
    - pip install -r requirements.txt
    - pip install pytest pytest-cov
  script:
    - pytest --cov=master_agent --cov-report=xml --cov-report=term
  coverage: '/(?i)total.*? (100(?:\\.0+)?\\%|[1-9]?\\d(?:\\.\\d+)?\\%)$/'
  artifacts:
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
  only:
    - merge_requests
    - {self.config.default_branch}

# Security Scanning
security:
  stage: security
  image: python:$PYTHON_VERSION
  before_script:
    - pip install -r requirements.txt
    - pip install -e .{security_scan}

# Dependency Scanning
dependency_scanning:
  stage: security
  image: python:$PYTHON_VERSION
  before_script:
    - pip install -r requirements.txt
    - pip install -e .
  script:
    - python -m master_agent.orchestration.dependency_tracker
  artifacts:
    reports:
      dependency_scanning: dependency-report.json
  only:
    - merge_requests
    - {self.config.default_branch}

# Deploy to Development
deploy_dev:
  stage: deploy
  image: python:$PYTHON_VERSION
  script:
    - echo "Deploying to development environment..."
    - ./scripts/deploy.sh development
  environment:
    name: development
    url: https://dev.example.com
  only:
    - {self.config.default_branch}

# Deploy to Staging
deploy_staging:
  stage: deploy
  image: python:$PYTHON_VERSION
  script:
    - echo "Deploying to staging environment..."
    - ./scripts/deploy.sh staging
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - tags
  when: manual

# Deploy to Production
deploy_production:
  stage: deploy
  image: python:$PYTHON_VERSION
  script:
    - echo "Deploying to production environment..."
    - ./scripts/deploy.sh production
  environment:
    name: production
    url: https://app.example.com
  only:
    - tags
  when: manual
  needs:
    - deploy_staging
'''

    def generate_deployment_config(self) -> str:
        """Generate deployment script for GitLab"""
        return '''#!/bin/bash
# GitLab CI Deployment Script

set -e

ENVIRONMENT=$1

echo "Deploying Master Agent to $ENVIRONMENT via GitLab CI"

# GitLab CI provides many variables:
# - $CI_COMMIT_SHA
# - $CI_COMMIT_REF_NAME
# - $CI_PIPELINE_ID
# - $CI_ENVIRONMENT_NAME

case $ENVIRONMENT in
    development)
        echo "Development deployment"
        # Add development commands
        ;;
    staging)
        echo "Staging deployment"
        # Add staging commands
        ;;
    production)
        echo "Production deployment"
        # Add production commands
        ;;
esac

echo "Deployed successfully!"
'''


class JenkinsIntegration(CICDIntegration):
    """Jenkins integration"""

    def _get_default_config_path(self) -> Path:
        return self.project_root / "Jenkinsfile"

    def generate_pipeline_config(self) -> str:
        """Generate Jenkins pipeline"""
        security_scan = ""
        if self.config.enable_security_scanning:
            security_scan = """
        stage('Security Scan') {
            steps {
                sh 'python -m master_agent.agents.security.secret_scanner'
                sh 'python -m master_agent.agents.security.compliance_validator'
            }
        }
"""

        return f'''// Master Agent Jenkins Pipeline

pipeline {{
    agent any

    environment {{
        PYTHON_VERSION = '3.11'
    }}

    stages {{
        stage('Setup') {{
            steps {{
                sh 'python3 -m venv venv'
                sh '. venv/bin/activate && pip install --upgrade pip'
                sh '. venv/bin/activate && pip install -r requirements.txt'
            }}
        }}

        stage('Quality Checks') {{
            parallel {{
                stage('Lint') {{
                    steps {{
                        sh '. venv/bin/activate && flake8 .'
                        sh '. venv/bin/activate && black --check .'
                    }}
                }}

                stage('Type Check') {{
                    steps {{
                        sh '. venv/bin/activate && mypy .'
                    }}
                }}
            }}
        }}

        stage('Test') {{
            steps {{
                sh '. venv/bin/activate && pytest --cov=master_agent --cov-report=xml'
            }}
            post {{
                always {{
                    junit 'test-results/**/*.xml'
                    publishCoverage adapters: [coberturaAdapter('coverage.xml')]
                }}
            }}
        }}

        stage('Build') {{
            steps {{
                sh '. venv/bin/activate && python -m build'
            }}
            post {{
                success {{
                    archiveArtifacts artifacts: 'dist/*', fingerprint: true
                }}
            }}
        }}
{security_scan}
        stage('Deploy') {{
            when {{
                branch '{self.config.default_branch}'
            }}
            stages {{
                stage('Deploy to Dev') {{
                    steps {{
                        sh './scripts/deploy.sh development'
                    }}
                }}

                stage('Deploy to Staging') {{
                    when {{
                        tag pattern: "v\\\\d+\\\\.\\\\d+\\\\.\\\\d+", comparator: "REGEXP"
                    }}
                    steps {{
                        input message: 'Deploy to staging?', ok: 'Deploy'
                        sh './scripts/deploy.sh staging'
                    }}
                }}

                stage('Deploy to Production') {{
                    when {{
                        tag pattern: "v\\\\d+\\\\.\\\\d+\\\\.\\\\d+", comparator: "REGEXP"
                    }}
                    steps {{
                        input message: 'Deploy to production?', ok: 'Deploy'
                        sh './scripts/deploy.sh production'
                    }}
                    post {{
                        success {{
                            emailext (
                                subject: "Master Agent deployed to production: ${{env.TAG_NAME}}",
                                body: "Successfully deployed version ${{env.TAG_NAME}} to production",
                                to: "${{env.DEPLOYMENT_NOTIFICATION_EMAIL}}"
                            )
                        }}
                    }}
                }}
            }}
        }}
    }}

    post {{
        always {{
            cleanWs()
        }}
        failure {{
            emailext (
                subject: "Build failed: ${{env.JOB_NAME}} - ${{env.BUILD_NUMBER}}",
                body: "Build failed. Check console output at ${{env.BUILD_URL}}",
                to: "${{env.BUILD_NOTIFICATION_EMAIL}}"
            )
        }}
    }}
}}
'''

    def generate_deployment_config(self) -> str:
        """Generate deployment script for Jenkins"""
        return '''#!/bin/bash
# Jenkins Deployment Script

set -e

ENVIRONMENT=$1

echo "Deploying Master Agent to $ENVIRONMENT via Jenkins"

# Jenkins provides many variables:
# - $BUILD_NUMBER
# - $BUILD_ID
# - $JOB_NAME
# - $WORKSPACE

case $ENVIRONMENT in
    development)
        echo "Development deployment from Jenkins"
        # Add development commands
        ;;
    staging)
        echo "Staging deployment from Jenkins"
        # Add staging commands
        ;;
    production)
        echo "Production deployment from Jenkins"
        # Add production commands
        ;;
esac

echo "Jenkins deployment complete!"
'''


class CircleCIIntegration(CICDIntegration):
    """CircleCI integration"""

    def _get_default_config_path(self) -> Path:
        return self.project_root / ".circleci" / "config.yml"

    def generate_pipeline_config(self) -> str:
        """Generate CircleCI configuration"""
        return f'''# Master Agent CircleCI Configuration

version: 2.1

orbs:
  python: circleci/python@2.1.1

executors:
  python-executor:
    docker:
      - image: cimg/python:3.11
    working_directory: ~/project

jobs:
  quality-checks:
    executor: python-executor
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          args: flake8 black mypy
      - run:
          name: Lint with flake8
          command: flake8 .
      - run:
          name: Check formatting with black
          command: black --check .
      - run:
          name: Type check with mypy
          command: mypy .

  test:
    executor: python-executor
    parallelism: 3
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run:
          name: Run tests
          command: |
            pytest --cov=master_agent \\
                   --cov-report=xml \\
                   --junitxml=test-results/junit.xml \\
                   --splits 3 \\
                   --group $CIRCLE_NODE_INDEX
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: coverage.xml

  security-scan:
    executor: python-executor
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
      - run:
          name: Secret Scanner
          command: python -m master_agent.agents.security.secret_scanner
      - run:
          name: Compliance Validator
          command: python -m master_agent.agents.security.compliance_validator

  build:
    executor: python-executor
    steps:
      - checkout
      - python/install-packages:
          pkg-manager: pip
          args: build
      - run:
          name: Build package
          command: python -m build
      - persist_to_workspace:
          root: .
          paths:
            - dist

  deploy-dev:
    executor: python-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - run:
          name: Deploy to Development
          command: ./scripts/deploy.sh development

  deploy-staging:
    executor: python-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - run:
          name: Deploy to Staging
          command: ./scripts/deploy.sh staging

  deploy-production:
    executor: python-executor
    steps:
      - checkout
      - attach_workspace:
          at: .
      - run:
          name: Deploy to Production
          command: ./scripts/deploy.sh production

workflows:
  build-test-deploy:
    jobs:
      - quality-checks
      - test:
          requires:
            - quality-checks
      - security-scan:
          requires:
            - quality-checks
      - build:
          requires:
            - test
            - security-scan

      # Development deployment
      - deploy-dev:
          requires:
            - build
          filters:
            branches:
              only: {self.config.default_branch}

      # Staging deployment (tags only)
      - deploy-staging:
          requires:
            - build
          filters:
            tags:
              only: /^v.*/
            branches:
              ignore: /.*/

      # Production deployment (manual approval)
      - hold-production:
          type: approval
          requires:
            - deploy-staging
          filters:
            tags:
              only: /^v.*/
            branches:
              ignore: /.*/

      - deploy-production:
          requires:
            - hold-production
          filters:
            tags:
              only: /^v.*/
            branches:
              ignore: /.*/
'''

    def generate_deployment_config(self) -> str:
        """Generate deployment script for CircleCI"""
        return '''#!/bin/bash
# CircleCI Deployment Script

set -e

ENVIRONMENT=$1

echo "Deploying Master Agent to $ENVIRONMENT via CircleCI"

# CircleCI provides many variables:
# - $CIRCLE_BUILD_NUM
# - $CIRCLE_SHA1
# - $CIRCLE_BRANCH
# - $CIRCLE_TAG

case $ENVIRONMENT in
    development)
        echo "Development deployment from CircleCI"
        # Add development commands
        ;;
    staging)
        echo "Staging deployment from CircleCI"
        # Add staging commands
        ;;
    production)
        echo "Production deployment from CircleCI"
        # Add production commands
        ;;
esac

echo "CircleCI deployment complete!"
'''


def get_cicd_integration(platform: str, config: CICDConfig, project_root: Path) -> CICDIntegration:
    """Factory function to get appropriate CI/CD integration"""
    integrations = {
        "github_actions": GitHubActionsIntegration,
        "gitlab_ci": GitLabCIIntegration,
        "jenkins": JenkinsIntegration,
        "circleci": CircleCIIntegration
    }

    integration_class = integrations.get(platform.lower())

    if not integration_class:
        raise ValueError(f"Unsupported CI/CD platform: {platform}. Supported: {', '.join(integrations.keys())}")

    return integration_class(config, project_root)
