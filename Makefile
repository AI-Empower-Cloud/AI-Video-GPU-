# =============================================================================
# AI Video GPU - Makefile
# Complete automation and management commands
# =============================================================================

.PHONY: help setup build start stop restart logs status health shell clean test deploy

# Default environment
ENVIRONMENT ?= development
COMPOSE_FILE ?= docker-compose.prebuilt.yml

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

help: ## Show this help message
	@echo "$(BLUE)AI Video GPU - Management Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup & Installation:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "setup|install|build" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Service Management:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "start|stop|restart|logs|status|health" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "test|lint|format|shell|clean" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Deployment:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | grep -E "deploy|backup|restore|scale" | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make setup                    # Complete setup"
	@echo "  make start                    # Start all services"
	@echo "  make logs SERVICE=ai-video-gpu # Show specific service logs"
	@echo "  make test                     # Run test suite"
	@echo "  make deploy ENV=production    # Deploy to production"

# =============================================================================
# Setup & Installation
# =============================================================================

setup: ## Complete setup (dependencies, build, start)
	@echo "$(BLUE)Running complete AI Video GPU setup...$(NC)"
	./setup-prebuilt.sh -e $(ENVIRONMENT)

setup-dev: ## Setup for development (with test dependencies)
	@echo "$(BLUE)Setting up development environment...$(NC)"
	./setup-prebuilt.sh -e development -v

setup-prod: ## Setup for production
	@echo "$(BLUE)Setting up production environment...$(NC)"
	./setup-prebuilt.sh -e production

install-deps: ## Install system dependencies only
	@echo "$(BLUE)Installing system dependencies...$(NC)"
	./setup-prebuilt.sh --skip-gpu-check --no-start

build: ## Build all containers
	@echo "$(BLUE)Building containers...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

build-no-cache: ## Build containers without cache
	@echo "$(BLUE)Building containers (no cache)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

pull: ## Pull latest base images
	@echo "$(BLUE)Pulling latest images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) pull

# =============================================================================
# Service Management
# =============================================================================

start: ## Start all services
	@echo "$(BLUE)Starting AI Video GPU services...$(NC)"
	./scripts/orchestrate.sh start

stop: ## Stop all services
	@echo "$(BLUE)Stopping services...$(NC)"
	./scripts/orchestrate.sh stop

restart: ## Restart all services
	@echo "$(BLUE)Restarting services...$(NC)"
	./scripts/orchestrate.sh restart

up: start ## Alias for start

down: stop ## Alias for stop

logs: ## Show logs for all services (or specific SERVICE=name)
ifdef SERVICE
	@echo "$(BLUE)Showing logs for $(SERVICE)...$(NC)"
	./scripts/orchestrate.sh logs -s $(SERVICE)
else
	@echo "$(BLUE)Showing logs for all services...$(NC)"
	./scripts/orchestrate.sh logs
endif

status: ## Show status of all services
	@echo "$(BLUE)Service status:$(NC)"
	./scripts/orchestrate.sh status

health: ## Check health of all services
	@echo "$(BLUE)Checking service health...$(NC)"
	./scripts/orchestrate.sh health

ps: status ## Alias for status

# =============================================================================
# Development
# =============================================================================

shell: ## Open shell in main container
	@echo "$(BLUE)Opening shell in AI Video GPU container...$(NC)"
	./scripts/orchestrate.sh shell

exec: ## Execute command in container (CMD=command)
ifdef CMD
	@echo "$(BLUE)Executing: $(CMD)$(NC)"
	./scripts/orchestrate.sh exec "$(CMD)"
else
	@echo "$(YELLOW)Usage: make exec CMD=\"your command\"$(NC)"
endif

test: ## Run test suite
	@echo "$(BLUE)Running test suite...$(NC)"
	python -m pytest tests/ -v

test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	python -m pytest tests/unit/ -v

test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	python -m pytest tests/integration/ -v

test-api: ## Run API tests only
	@echo "$(BLUE)Running API tests...$(NC)"
	python -m pytest tests/api/ -v

test-gpu: ## Run GPU tests (requires GPU)
	@echo "$(BLUE)Running GPU tests...$(NC)"
	python -m pytest tests/gpu/ -v --gpu-required

lint: ## Run code linting
	@echo "$(BLUE)Running linters...$(NC)"
	flake8 src/
	mypy src/ --ignore-missing-imports
	bandit -r src/

format: ## Format code
	@echo "$(BLUE)Formatting code...$(NC)"
	black src/
	isort src/

format-check: ## Check code formatting
	@echo "$(BLUE)Checking code format...$(NC)"
	black --check src/
	isort --check-only src/

security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	bandit -r src/ -f json -o security-report.json
	safety check

clean: ## Clean up containers, volumes, and images
	@echo "$(BLUE)Cleaning up...$(NC)"
	./scripts/orchestrate.sh clean

clean-all: clean ## Alias for clean

# =============================================================================
# Deployment
# =============================================================================

deploy: ## Deploy to environment (ENV=development|staging|production)
ifdef ENV
	@echo "$(BLUE)Deploying to $(ENV)...$(NC)"
	./scripts/deploy.sh -e $(ENV)
else
	@echo "$(BLUE)Deploying to $(ENVIRONMENT)...$(NC)"
	./scripts/deploy.sh -e $(ENVIRONMENT)
endif

deploy-staging: ## Deploy to staging
	@echo "$(BLUE)Deploying to staging...$(NC)"
	./scripts/deploy.sh -e staging

deploy-prod: ## Deploy to production
	@echo "$(BLUE)Deploying to production...$(NC)"
	./scripts/deploy.sh -e production

scale: ## Scale services (SERVICE=name COUNT=number)
ifdef SERVICE
ifdef COUNT
	@echo "$(BLUE)Scaling $(SERVICE) to $(COUNT) replicas...$(NC)"
	./scripts/orchestrate.sh scale -s $(SERVICE)=$(COUNT)
else
	@echo "$(YELLOW)Usage: make scale SERVICE=ai-video-gpu COUNT=3$(NC)"
endif
else
	@echo "$(YELLOW)Usage: make scale SERVICE=ai-video-gpu COUNT=3$(NC)"
endif

backup: ## Create backup of all data
	@echo "$(BLUE)Creating backup...$(NC)"
	./scripts/orchestrate.sh backup

restore: ## Restore from backup (BACKUP_DIR=path)
ifdef BACKUP_DIR
	@echo "$(BLUE)Restoring from $(BACKUP_DIR)...$(NC)"
	./scripts/orchestrate.sh restore -s $(BACKUP_DIR)
else
	@echo "$(YELLOW)Usage: make restore BACKUP_DIR=backups/20240101_120000$(NC)"
endif

update: ## Update services to latest version
	@echo "$(BLUE)Updating services...$(NC)"
	./scripts/orchestrate.sh update

monitor: ## Open monitoring dashboard
	@echo "$(BLUE)Opening monitoring dashboard...$(NC)"
	./scripts/orchestrate.sh monitor

# =============================================================================
# Utilities
# =============================================================================

config: ## Validate configuration
	@echo "$(BLUE)Validating configuration...$(NC)"
	docker-compose -f $(COMPOSE_FILE) config

env: ## Show environment information
	@echo "$(BLUE)Environment Information:$(NC)"
	@echo "Environment: $(ENVIRONMENT)"
	@echo "Compose File: $(COMPOSE_FILE)"
	@echo "Docker Version: $$(docker --version)"
	@echo "Docker Compose Version: $$(docker-compose --version)"
	@echo "System: $$(uname -a)"
	@if command -v nvidia-smi >/dev/null 2>&1; then echo "GPU: $$(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"; fi

version: ## Show version information
	@echo "$(BLUE)AI Video GPU Version Information:$(NC)"
	@echo "Version: 1.0.0"
	@echo "Build: $$(git rev-parse --short HEAD 2>/dev/null || echo 'unknown')"
	@echo "Date: $$(date)"

reset: ## Reset everything (stop, clean, rebuild)
	@echo "$(YELLOW)This will remove all containers, volumes, and data. Continue? [y/N]$(NC)"
	@read -r REPLY; if [ "$$REPLY" = "y" ] || [ "$$REPLY" = "Y" ]; then \
		echo "$(BLUE)Resetting system...$(NC)"; \
		$(MAKE) stop; \
		$(MAKE) clean; \
		$(MAKE) build; \
		echo "$(GREEN)Reset complete. Run 'make start' to restart.$(NC)"; \
	else \
		echo "$(YELLOW)Reset cancelled.$(NC)"; \
	fi

demo: ## Start demo environment with sample data
	@echo "$(BLUE)Starting demo environment...$(NC)"
	$(MAKE) start
	@echo "$(GREEN)Demo ready! Visit http://localhost:8501$(NC)"

# =============================================================================
# CI/CD Helpers
# =============================================================================

ci-test: ## Run CI test suite
	@echo "$(BLUE)Running CI tests...$(NC)"
	python -m pytest tests/ -v --cov=src --cov-report=xml

ci-build: ## Build for CI
	@echo "$(BLUE)Building for CI...$(NC)"
	docker build -f docker/Dockerfile.prebuilt -t ai-video-gpu:ci .

ci-scan: ## Run security scans for CI
	@echo "$(BLUE)Running CI security scans...$(NC)"
	trivy image ai-video-gpu:ci

# =============================================================================
# Documentation
# =============================================================================

docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@if command -v sphinx-build >/dev/null 2>&1; then \
		sphinx-build -b html docs/ docs/_build/; \
	else \
		echo "$(YELLOW)Sphinx not installed. Install with: pip install sphinx$(NC)"; \
	fi

docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation at http://localhost:8000$(NC)"
	python -m http.server 8000 --directory docs/_build/

# =============================================================================
# Development Shortcuts
# =============================================================================

dev: ## Start development environment
	$(MAKE) setup-dev

quick: ## Quick start (build and run)
	$(MAKE) build && $(MAKE) start

restart-app: ## Restart only the main application
	./scripts/orchestrate.sh restart -s ai-video-gpu

tail: ## Follow logs for main application
	./scripts/orchestrate.sh logs -s ai-video-gpu

api-test: ## Test API endpoints
	@echo "$(BLUE)Testing API endpoints...$(NC)"
	curl -s http://localhost:8000/health | jq .
	curl -s http://localhost:8000/api/v1/info | jq .

gpu-check: ## Check GPU availability
	@echo "$(BLUE)GPU Status:$(NC)"
	@if command -v nvidia-smi >/dev/null 2>&1; then \
		nvidia-smi; \
	else \
		echo "$(YELLOW)NVIDIA GPU not detected$(NC)"; \
	fi
	@docker run --rm --gpus all nvidia/cuda:12.2-base-ubuntu22.04 nvidia-smi 2>/dev/null || echo "$(YELLOW)NVIDIA Docker runtime not available$(NC)"

# =============================================================================
# Wasabi Cloud Storage
# =============================================================================

wasabi-setup: ## Setup Wasabi cloud storage
	@echo "$(BLUE)Setting up Wasabi cloud storage...$(NC)"
	./scripts/setup-wasabi.sh

wasabi-test: ## Test Wasabi connection
	@echo "$(BLUE)Testing Wasabi connection...$(NC)"
	python -m src.cli.wasabi_commands test

wasabi-status: ## Show Wasabi storage status
	@echo "$(BLUE)Checking Wasabi storage status...$(NC)"
	python -m src.cli.wasabi_commands status

wasabi-init: ## Initialize Wasabi buckets
	@echo "$(BLUE)Initializing Wasabi buckets...$(NC)"
	python -m src.cli.wasabi_commands init

wasabi-upload: ## Upload file to Wasabi (FILE=path BUCKET=type)
ifdef FILE
ifdef BUCKET
	@echo "$(BLUE)Uploading $(FILE) to $(BUCKET) bucket...$(NC)"
	python -m src.cli.wasabi_commands upload $(FILE) --bucket-type $(BUCKET)
else
	@echo "$(YELLOW)Usage: make wasabi-upload FILE=video.mp4 BUCKET=outputs$(NC)"
endif
else
	@echo "$(YELLOW)Usage: make wasabi-upload FILE=video.mp4 BUCKET=outputs$(NC)"
endif

wasabi-list: ## List files in Wasabi bucket (BUCKET=type)
ifdef BUCKET
	@echo "$(BLUE)Listing files in $(BUCKET) bucket...$(NC)"
	python -m src.cli.wasabi_commands list --bucket-type $(BUCKET)
else
	@echo "$(BLUE)Listing files in outputs bucket...$(NC)"
	python -m src.cli.wasabi_commands list --bucket-type outputs
endif

wasabi-sync: ## Sync directory to Wasabi (DIR=path BUCKET=type)
ifdef DIR
ifdef BUCKET
	@echo "$(BLUE)Syncing $(DIR) to $(BUCKET) bucket...$(NC)"
	python -m src.cli.wasabi_commands sync $(DIR) --bucket-type $(BUCKET)
else
	@echo "$(YELLOW)Usage: make wasabi-sync DIR=./outputs BUCKET=outputs$(NC)"
endif
else
	@echo "$(YELLOW)Usage: make wasabi-sync DIR=./outputs BUCKET=outputs$(NC)"
endif
