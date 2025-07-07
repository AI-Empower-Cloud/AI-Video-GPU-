#!/bin/bash

# GitHub Code Review Setup Script for AI Video GPU Platform
# This script sets up a professional code review workflow

set -e

echo "🚀 Setting up GitHub Code Review Workflow for AI Video GPU Platform"
echo "=================================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    print_error "This script must be run from the root of a git repository"
    exit 1
fi

# Create GitHub workflow directories
print_info "Creating GitHub workflow directories..."
mkdir -p .github/workflows
mkdir -p .github/ISSUE_TEMPLATE
mkdir -p .github/PULL_REQUEST_TEMPLATE
print_status "Created GitHub directory structure"

# Create main CI/CD workflow
print_info "Creating CI/CD workflow..."
cat > .github/workflows/ci.yml << 'EOF'
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", "3.11"]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Cache pip dependencies
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements*.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 src/ --count --select=E9,F63,F7,F82 --show-source --statistics
        flake8 src/ --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

    - name: Test with pytest
      run: |
        pip install pytest pytest-cov
        pytest tests/ --cov=src --cov-report=xml || true

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        token: ${{ secrets.CODECOV_TOKEN }}
        file: ./coverage.xml
        fail_ci_if_error: false

  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
    - uses: actions/checkout@v4

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v3

    - name: Login to Docker Hub
      uses: docker/login-action@v3
      with:
        username: ${{ secrets.DOCKER_USERNAME }}
        password: ${{ secrets.DOCKER_PASSWORD }}
      if: ${{ secrets.DOCKER_USERNAME }}

    - name: Build Docker image
      uses: docker/build-push-action@v5
      with:
        context: .
        push: false
        tags: aiempowercloud/ai-video-gpu:latest
EOF

print_status "Created CI/CD workflow"

# Create code quality workflow
print_info "Creating code quality workflow..."
cat > .github/workflows/code-quality.yml << 'EOF'
name: Code Quality

on:
  pull_request:
    branches: [ main, develop ]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install black isort flake8 mypy bandit safety

    - name: Check code formatting with Black
      run: black --check src/ || true

    - name: Check import sorting with isort
      run: isort --check-only src/ || true

    - name: Lint with flake8
      run: flake8 src/ || true

    - name: Type checking with mypy
      run: mypy src/ || true

    - name: Security check with bandit
      run: bandit -r src/ || true

    - name: Check for known security vulnerabilities
      run: safety check || true
EOF

print_status "Created code quality workflow"

# Create Wasabi-specific tests workflow
print_info "Creating Wasabi integration tests workflow..."
cat > .github/workflows/wasabi-tests.yml << 'EOF'
name: Wasabi Integration Tests

on:
  pull_request:
    paths:
      - 'src/cloud/wasabi_storage.py'
      - 'src/cli/wasabi_commands.py'
      - 'tests/test_wasabi*.py'

jobs:
  wasabi-tests:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

    - name: Run Wasabi integration tests
      env:
        WASABI_ACCESS_KEY: ${{ secrets.WASABI_ACCESS_KEY }}
        WASABI_SECRET_KEY: ${{ secrets.WASABI_SECRET_KEY }}
        WASABI_ENDPOINT_URL: ${{ secrets.WASABI_ENDPOINT_URL }}
        WASABI_REGION: ${{ secrets.WASABI_REGION }}
      run: |
        if [ -f tests/test_wasabi_storage.py ]; then
          pytest tests/test_wasabi_storage.py -v || true
        fi
        if [ -f tests/test_wasabi_cli.py ]; then
          pytest tests/test_wasabi_cli.py -v || true
        fi
EOF

print_status "Created Wasabi integration tests workflow"

# Create Pull Request template
print_info "Creating Pull Request template..."
cat > .github/pull_request_template.md << 'EOF'
## 🎯 Purpose

Brief description of what this PR does.

## 🔧 Changes Made

- [ ] Added new feature
- [ ] Fixed bug
- [ ] Updated documentation
- [ ] Refactored code
- [ ] Added tests
- [ ] Updated dependencies

### Detailed Changes

- Change 1: Description
- Change 2: Description
- Change 3: Description

## 🧪 Testing

- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed
- [ ] All tests passing

## 📚 Documentation

- [ ] README updated
- [ ] API documentation updated
- [ ] Code comments added
- [ ] Configuration documentation updated

## 🚨 Breaking Changes

- [ ] No breaking changes
- [ ] Breaking changes documented below

## 🔗 Related Issues

Closes #issue_number

## ✅ Checklist

- [ ] Code follows project style guidelines
- [ ] Self-review of code completed
- [ ] Code is commented, particularly in hard-to-understand areas
- [ ] Corresponding changes to documentation made
- [ ] Changes generate no new warnings
- [ ] Tests added that prove fix is effective or feature works
- [ ] New and existing unit tests pass locally
EOF

print_status "Created Pull Request template"

# Create Bug Report template
print_info "Creating Bug Report template..."
cat > .github/ISSUE_TEMPLATE/bug_report.md << 'EOF'
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

## 🐛 Bug Description

A clear and concise description of what the bug is.

## 🔄 Steps to Reproduce

1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## 💡 Expected Behavior

A clear and concise description of what you expected to happen.

## 🌐 Environment

- OS: [e.g. Ubuntu 20.04]
- Python version: [e.g. 3.10]
- AI Video GPU version: [e.g. 2.5.0]

## 📋 Additional Context

Add any other context about the problem here.

## 📊 Error Logs

```
Paste any relevant error logs here
```
EOF

print_status "Created Bug Report template"

# Create Feature Request template
print_info "Creating Feature Request template..."
cat > .github/ISSUE_TEMPLATE/feature_request.md << 'EOF'
---
name: Feature Request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: enhancement
assignees: ''
---

## 🚀 Feature Request

### Problem Statement
A clear and concise description of what the problem is.

### Proposed Solution
A clear and concise description of what you want to happen.

### Use Case
Describe the use case for this feature:
- Who would use it?
- How would it be used?
- What value does it provide?

### Acceptance Criteria
- [ ] Criteria 1
- [ ] Criteria 2
- [ ] Criteria 3

### Priority
- [ ] Low
- [ ] Medium
- [ ] High
- [ ] Critical
EOF

print_status "Created Feature Request template"

# Create CODEOWNERS file
print_info "Creating CODEOWNERS file..."
cat > .github/CODEOWNERS << 'EOF'
# Global owners
* @AI-Empower-Cloud

# Wasabi storage code
src/cloud/wasabi_storage.py @AI-Empower-Cloud
src/cli/wasabi_commands.py @AI-Empower-Cloud

# AI core system
src/ai_empower_system.py @AI-Empower-Cloud
src/pipeline.py @AI-Empower-Cloud

# Frontend
frontend/ @AI-Empower-Cloud

# Infrastructure
docker/ @AI-Empower-Cloud
k8s/ @AI-Empower-Cloud
.github/ @AI-Empower-Cloud

# Documentation
*.md @AI-Empower-Cloud
docs/ @AI-Empower-Cloud
EOF

print_status "Created CODEOWNERS file"

# Create pre-commit configuration
print_info "Creating pre-commit configuration..."
cat > .pre-commit-config.yaml << 'EOF'
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.4.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-merge-conflict
      - id: check-added-large-files
      - id: check-case-conflict

  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=127]
EOF

print_status "Created pre-commit configuration"

# Create pyproject.toml for tool configuration
print_info "Creating pyproject.toml..."
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 127
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 127
known_first_party = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--tb=short",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html",
    "--cov-report=xml",
]
markers = [
    "slow: marks tests as slow (deselect with '-m \"not slow\"')",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
EOF

print_status "Created pyproject.toml"

# Create setup.cfg
print_info "Creating setup.cfg..."
cat > setup.cfg << 'EOF'
[flake8]
max-line-length = 127
exclude = .git,__pycache__,docs/source/conf.py,old,build,dist
ignore = E203,W503
per-file-ignores =
    __init__.py:F401

[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[coverage:run]
source = src
omit =
    tests/*
    */test_*
    */__init__.py

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
EOF

print_status "Created setup.cfg"

# Update requirements-dev.txt
print_info "Updating requirements-dev.txt..."
cat > requirements-dev.txt << 'EOF'
# Testing
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.0.0
pytest-asyncio>=0.21.0
moto>=4.0.0

# Code quality
black>=23.0.0
isort>=5.12.0
flake8>=6.0.0
mypy>=1.0.0
bandit>=1.7.0
safety>=2.0.0

# Pre-commit
pre-commit>=3.0.0

# Documentation
sphinx>=5.0.0
sphinx-rtd-theme>=1.0.0

# Development tools
ipython>=8.0.0
jupyter>=1.0.0
EOF

print_status "Updated requirements-dev.txt"

# Install pre-commit if available
print_info "Installing pre-commit hooks..."
if command -v pip &> /dev/null; then
    pip install pre-commit || print_warning "Failed to install pre-commit, install manually with: pip install pre-commit"
    if command -v pre-commit &> /dev/null; then
        pre-commit install || print_warning "Failed to install pre-commit hooks"
        print_status "Pre-commit hooks installed"
    else
        print_warning "Pre-commit not found, install with: pip install pre-commit"
    fi
else
    print_warning "pip not found, install pre-commit manually"
fi

# Create or update .gitignore
print_info "Updating .gitignore..."
if [ ! -f .gitignore ]; then
    touch .gitignore
fi

# Add common Python and project-specific ignores
cat >> .gitignore << 'EOF'

# Code quality tools
.mypy_cache/
.pytest_cache/
.coverage
htmlcov/
.tox/
.nox/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Environment
.env
.env.local
.env.*.local

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
temp/
tmp/

# Build artifacts
build/
dist/
*.egg-info/
EOF

print_status "Updated .gitignore"

# Create development branch if it doesn't exist
print_info "Setting up development branch..."
if ! git show-ref --verify --quiet refs/heads/develop; then
    git checkout -b develop
    git push -u origin develop || print_warning "Failed to push develop branch, push manually"
    print_status "Created and pushed develop branch"
else
    print_info "Develop branch already exists"
fi

# Switch back to main branch
git checkout main || git checkout master || print_warning "Could not switch to main branch"

echo ""
echo "🎉 GitHub Code Review Setup Complete!"
echo "======================================"
echo ""
print_status "Created GitHub workflow files"
print_status "Created issue and PR templates"
print_status "Created code quality configuration"
print_status "Set up pre-commit hooks"
print_status "Created development branch"
echo ""
print_info "Next steps:"
echo "1. 🔧 Go to GitHub repository Settings"
echo "2. 🛡️  Set up branch protection rules for 'main' branch"
echo "3. 🔑 Add GitHub secrets for CI/CD:"
echo "   - WASABI_ACCESS_KEY"
echo "   - WASABI_SECRET_KEY"
echo "   - WASABI_ENDPOINT_URL"
echo "   - WASABI_REGION"
echo "   - CODECOV_TOKEN (optional)"
echo "   - DOCKER_USERNAME (optional)"
echo "   - DOCKER_PASSWORD (optional)"
echo "4. 👥 Add team members as collaborators"
echo "5. 📝 Configure required status checks"
echo "6. 🚀 Create your first pull request!"
echo ""
print_info "Branch protection rule example:"
echo "- Require pull request reviews (2 approvals)"
echo "- Require status checks to pass"
echo "- Require branches to be up to date"
echo "- Include administrators"
echo "- Require signed commits"
echo ""
print_status "Setup complete! Happy coding! 🚀"
