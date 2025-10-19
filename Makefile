.PHONY: help install install-dev install-prod clean test test-coverage test-unit test-integration lint format type-check security quality-all build publish dev docs serve-docs clean-build clean-pyc clean-test validate-setup

# Default target
.DEFAULT_GOAL := help

# Project variables
PYTHON := python3
PIP := $(PYTHON) -m pip
PYTEST := $(PYTHON) -m pytest
RUFF := $(PYTHON) -m ruff
MYPY := $(PYTHON) -m mypy
PROJECT_NAME := kellerai-coderabbit-integration
SRC_DIRS := quality_checks mcp_servers
TEST_DIR := quality-checks/tests

# Color output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)KellerAI CodeRabbit Integration - Makefile$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "Usage:\n  make $(YELLOW)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(GREEN)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

validate-setup: ## Validate development environment setup
	@echo "$(BLUE)Validating development environment...$(NC)"
	@command -v $(PYTHON) >/dev/null 2>&1 || { echo "$(RED)Python 3.13+ not found!$(NC)"; exit 1; }
	@$(PYTHON) --version | grep -qE "3\.(13|14|15)" || { echo "$(RED)Python 3.13+ required!$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Python version OK$(NC)"
	@command -v git >/dev/null 2>&1 || { echo "$(RED)Git not found!$(NC)"; exit 1; }
	@echo "$(GREEN)✓ Git OK$(NC)"
	@test -f .env || { echo "$(YELLOW)⚠ .env file missing - copy from .env.example$(NC)"; }
	@echo "$(GREEN)✓ Environment setup validated$(NC)"

##@ Installation

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install -e .
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install -e .
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

install-prod: ## Install for production (optimized)
	@echo "$(BLUE)Installing for production...$(NC)"
	$(PIP) install --upgrade pip setuptools wheel
	$(PIP) install --no-cache-dir .
	@echo "$(GREEN)✓ Production installation complete$(NC)"

##@ Testing

test: ## Run all tests
	@echo "$(BLUE)Running all tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --tb=short --cov=quality_checks --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo "$(GREEN)✓ Tests complete - see htmlcov/index.html for coverage report$(NC)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "unit" --tb=short
	@echo "$(GREEN)✓ Unit tests complete$(NC)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	$(PYTEST) $(TEST_DIR) -v -m "integration" --tb=short
	@echo "$(GREEN)✓ Integration tests complete$(NC)"

test-coverage: ## Run tests with detailed coverage report
	@echo "$(BLUE)Running tests with coverage analysis...$(NC)"
	$(PYTEST) $(TEST_DIR) -v --cov=quality_checks --cov-report=term-missing --cov-report=html --cov-report=xml --cov-fail-under=90
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/$(NC)"

test-fast: ## Run tests in parallel (faster)
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	$(PYTEST) $(TEST_DIR) -n auto --tb=short
	@echo "$(GREEN)✓ Parallel tests complete$(NC)"

##@ Code Quality

lint: ## Run linter (Ruff)
	@echo "$(BLUE)Running Ruff linter...$(NC)"
	$(RUFF) check $(SRC_DIRS) --fix
	@echo "$(GREEN)✓ Linting complete$(NC)"

format: ## Format code with Ruff
	@echo "$(BLUE)Formatting code...$(NC)"
	$(RUFF) format $(SRC_DIRS)
	$(RUFF) check $(SRC_DIRS) --fix --select I
	@echo "$(GREEN)✓ Code formatted$(NC)"

type-check: ## Run type checker (mypy)
	@echo "$(BLUE)Running mypy type checker...$(NC)"
	$(MYPY) $(SRC_DIRS)
	@echo "$(GREEN)✓ Type checking complete$(NC)"

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@echo "$(YELLOW)Checking for hardcoded credentials...$(NC)"
	@grep -r -n -E '(password|secret|api[_-]?key|token)\s*=\s*["\x27][^"\x27]{8,}' quality_checks/ mcp_servers/ || echo "$(GREEN)✓ No hardcoded credentials found$(NC)"
	@echo "$(GREEN)✓ Security checks complete$(NC)"

quality-all: format lint type-check security test ## Run all quality checks
	@echo "$(GREEN)✓ All quality checks passed!$(NC)"

##@ Build & Distribution

build: clean-build ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	$(PYTHON) -m build
	@echo "$(GREEN)✓ Distribution packages built in dist/$(NC)"

publish-test: build ## Publish to Test PyPI
	@echo "$(BLUE)Publishing to Test PyPI...$(NC)"
	$(PYTHON) -m twine upload --repository testpypi dist/*
	@echo "$(GREEN)✓ Published to Test PyPI$(NC)"

publish: build ## Publish to PyPI (PRODUCTION)
	@echo "$(RED)⚠ Publishing to production PyPI...$(NC)"
	@read -p "Are you sure? [y/N] " -n 1 -r; \
	echo; \
	if [[ $$REPLY =~ ^[Yy]$$ ]]; then \
		$(PYTHON) -m twine upload dist/*; \
		echo "$(GREEN)✓ Published to PyPI$(NC)"; \
	else \
		echo "$(YELLOW)Cancelled$(NC)"; \
	fi

##@ Development

dev: install-dev ## Set up development environment
	@echo "$(BLUE)Setting up development environment...$(NC)"
	@test -f .env || cp .env.example .env
	@echo "$(GREEN)✓ Development environment ready$(NC)"
	@echo "$(YELLOW)Note: Edit .env with your credentials$(NC)"

watch-tests: ## Run tests in watch mode
	@echo "$(BLUE)Running tests in watch mode...$(NC)"
	$(PYTEST) $(TEST_DIR) -f

mcp-test: ## Test MCP server
	@echo "$(BLUE)Testing KellerAI Standards MCP server...$(NC)"
	cd mcp-servers/kellerai-standards && $(PYTHON) src/server.py
	@echo "$(GREEN)✓ MCP server test complete$(NC)"

coderabbit-test: ## Run CodeRabbit CLI on current changes
	@echo "$(BLUE)Running CodeRabbit review...$(NC)"
	coderabbit review --prompt-only --type committed --config .coderabbit.yaml &
	@echo "$(YELLOW)CodeRabbit running in background...$(NC)"

##@ Documentation

docs: ## Build documentation
	@echo "$(BLUE)Building documentation...$(NC)"
	@echo "$(YELLOW)Note: MkDocs not yet configured$(NC)"
	@echo "$(YELLOW)See docs/ directory for markdown documentation$(NC)"

serve-docs: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Note: MkDocs not yet configured$(NC)"

##@ Cleanup

clean: clean-build clean-pyc clean-test ## Remove all build, test, and Python artifacts
	@echo "$(GREEN)✓ Cleanup complete$(NC)"

clean-build: ## Remove build artifacts
	@echo "$(BLUE)Removing build artifacts...$(NC)"
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## Remove Python file artifacts
	@echo "$(BLUE)Removing Python artifacts...$(NC)"
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## Remove test and coverage artifacts
	@echo "$(BLUE)Removing test artifacts...$(NC)"
	rm -fr .pytest_cache/
	rm -fr .mypy_cache/
	rm -fr .ruff_cache/
	rm -fr htmlcov/
	rm -f .coverage
	rm -f coverage.xml

clean-all: clean ## Remove all artifacts including .env
	@echo "$(RED)⚠ Removing ALL artifacts including .env...$(NC)"
	rm -f .env
	rm -fr .tmp/

##@ Git Workflows

git-setup: ## Set up git hooks
	@echo "$(BLUE)Setting up git hooks...$(NC)"
	@echo "#!/bin/bash\nmake lint format test-fast" > .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "$(GREEN)✓ Git pre-commit hook installed$(NC)"

feature-branch: ## Create feature branch (use: make feature-branch NAME=my-feature)
	@test -n "$(NAME)" || { echo "$(RED)Error: NAME required. Usage: make feature-branch NAME=my-feature$(NC)"; exit 1; }
	@test -f scripts/create-feature-branch.sh && ./scripts/create-feature-branch.sh feat $(NAME) || git checkout -b feat/$(NAME)
	@echo "$(GREEN)✓ Feature branch feat/$(NAME) created$(NC)"

##@ Quick Workflows

check: lint type-check test-fast ## Quick quality check (lint + types + fast tests)
	@echo "$(GREEN)✓ Quick quality check passed!$(NC)"

ci: quality-all ## Run full CI pipeline locally
	@echo "$(GREEN)✓ CI pipeline complete!$(NC)"

pre-commit: format lint test-fast ## Run before committing
	@echo "$(GREEN)✓ Ready to commit!$(NC)"

pre-push: quality-all ## Run before pushing
	@echo "$(GREEN)✓ Ready to push!$(NC)"
