SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
USING_UV		=	$(shell grep "tool.uv" pyproject.toml && echo "yes")
VENV_EXISTS		=	$(shell python3 -c "if __import__('pathlib').Path('.venv/bin/activate').exists(): print('yes')")
UV_OPTS 		?=
UV 			    ?= 	uv $(UV_OPTS)

.EXPORT_ALL_VARIABLES:

.PHONY: help upgrade install-prek install
.PHONY: fmt-fix test coverage check-all lint fmt-check
.PHONY: docs-install docs-clean docs-serve docs-build
.PHONY: clean run-dev-frontend run-dev-server production develop destroy
.PHONY: docker-up docker-down docker-logs docker-shell-api docker-shell-bot docker-ps
.PHONY: docker-restart docker-rebuild infra-up infra-down
.PHONY: worktree worktree-prune

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

upgrade: ## Upgrade all dependencies to the latest stable versions
	@echo "=> Upgrading prek"
	@$(UV) run prek autoupdate
	@if [ "$(USING_UV)" ]; then $(UV) lock --upgrade
	@echo "Dependencies Updated"

# =============================================================================
# Developer Utils
# =============================================================================

install-uv: ## Install latest version of UV
	@echo "=> Installing uv"
	@curl -LsSf https://astral.sh/uv/install.sh | sh
	@echo "=> uv installed"

install-prek: ## Install prek and install hooks
	@echo "Installing prek hooks"
	@$(UV) run prek install
	@$(UV) run prek install --hook-type commit-msg
	@$(UV) run prek install --hook-type pre-push
	@echo "=> prek hooks installed"
	@$(UV) run prek autoupdate
	@echo "prek installed"

.PHONY: install-frontend
install-frontend: ## Install the frontend dependencies
	@echo "=> Installing frontend dependencies"
	@nodeenv --python-virtualenv
	@npm install
	@echo "=> Frontend dependencies installed"

.PHONY: install-backend
install-backend: ## Install the backend dependencies
	@echo "=> Installing backend dependencies"
	@$(UV) venv && $(UV) pip install --quiet -U wheel setuptools cython pip
	@$(UV) sync --all-extras --force-reinstall --dev
	@echo "=> Backend dependencies installed"

.PHONY: install
install: clean destroy ## Install the project, dependencies, and prek for local development
	@if ! $(UV) --version > /dev/null; then $(MAKE) install-uv; fi
	@$(MAKE) install-backend
	@$(MAKE) install-frontend
	@echo "=> Install complete! Note: If you want to re-install re-run 'make install'"

up-container: ## Start the Byte database container
	@echo "=> Starting Byte database container"
	@docker compose -f docker-compose.infra.yml up -d
	@echo "=> Started Byte database container"

clean-container: ## Stop, remove, and wipe the Byte database container, volume, network, and orphans
	@echo "=> Stopping and removing Byte database container, volumes, networks, and orphans"
	@docker compose -f docker-compose.infra.yml down -v --remove-orphans
	@echo "=> Stopped and removed Byte database container, volumes, networks, and orphans"

load-container: up-container migrate ## Perform database migrations and load test data into the Byte database container
	@echo "=> Loading database migrations and test data"
	@cd services/api && $(UV) run python -m byte_api.scripts.migrate
	@echo "rest not yet implemented"
	@echo "=> Loaded database migrations and test data"

refresh-container: clean-container up-container load-container ## Refresh the Byte database container



# =============================================================================
# Tests, Linting, Coverage
# =============================================================================

##@ Code Quality

lint: ## Runs prek hooks; includes ruff linting, codespell, black
	@$(UV) run --no-sync prek run --all-files

fmt-check: ## Runs Ruff format in check mode (no changes)
	@$(UV) run --no-sync ruff format --check .

fmt: ## Runs Ruff format, makes changes where necessary
	@$(UV) run --no-sync ruff format .

ruff: ## Runs Ruff
	@$(UV) run --no-sync ruff check . --unsafe-fixes --fix

ruff-check: ## Runs Ruff without changing files
	@$(UV) run --no-sync ruff check .

ruff-noqa: ## Runs Ruff, adding noqa comments to disable warnings
	@$(UV) run --no-sync ruff check . --add-noqa

type-check: ## Run ty type checker
	@$(UV) run --no-sync ty check

test:  ## Run the tests
	@$(UV) run --no-sync pytest tests

coverage:  ## Run the tests and generate coverage report
	@$(UV) run --no-sync pytest tests --cov=byte_bot
	@$(UV) run --no-sync coverage html
	@$(UV) run --no-sync coverage xml

check-all: lint type-check fmt test  ## Run all linting, formatting, and tests

ci: check-all  ## Run all checks for CI

# =============================================================================
# Docs
# =============================================================================

##@ Documentation

docs-clean: ## Dump the existing built docs
	@echo "=> Cleaning documentation build assets"
	@rm -rf docs/_build
	@echo "=> Removed existing documentation build assets"

docs-serve: docs-clean ## Serve the docs locally
	@echo "=> Serving documentation"
	$(UV) run sphinx-autobuild docs docs/_build/ -j auto --watch byte_bot --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002

docs: docs-clean ## Dump the existing built docs and rebuild them
	@echo "=> Building documentation"
	@$(UV) run sphinx-build -M html docs docs/_build/ -E -a -j auto --keep-going

# =============================================================================
# Database
# =============================================================================

##@ Database Operations

migrations: ## Generate database migrations
	@echo "ATTENTION: This operation will create a new database migration for any defined models changes."
	@while [ -z "$$MIGRATION_MESSAGE" ]; do read -r -p "Migration message: " MIGRATION_MESSAGE; done ;
	@cd services/api && $(UV) run alembic revision --autogenerate -m "$${MIGRATION_MESSAGE}"

.PHONY: migrate
migrate: ## Apply database migrations
	@echo "ATTENTION: Will apply all database migrations."
	@cd services/api && $(UV) run python -m byte_api.scripts.migrate

.PHONY: db
db: ## Run the database
	@docker compose -f "docker-compose.infra.yml" up -d --build

# =============================================================================
# Docker Compose Commands
# =============================================================================

##@ Docker Development

.PHONY: docker-up
docker-up: ## Start all services (PostgreSQL, API, Bot) with Docker Compose
	@echo "=> Starting all services with Docker Compose"
	@docker compose up -d --build
	@echo "=> All services started. API: http://localhost:8000"

.PHONY: docker-down
docker-down: ## Stop all Docker Compose services
	@echo "=> Stopping all Docker Compose services"
	@docker compose down
	@echo "=> All services stopped"

.PHONY: docker-down-volumes
docker-down-volumes: ## Stop all services and remove volumes
	@echo "=> Stopping all services and removing volumes"
	@docker compose down -v
	@echo "=> All services stopped and volumes removed"

.PHONY: docker-logs
docker-logs: ## Follow logs from all Docker Compose services
	@docker compose logs -f

.PHONY: docker-logs-api
docker-logs-api: ## Follow logs from API service
	@docker compose logs -f api

.PHONY: docker-logs-bot
docker-logs-bot: ## Follow logs from bot service
	@docker compose logs -f bot

.PHONY: docker-logs-postgres
docker-logs-postgres: ## Follow logs from PostgreSQL service
	@docker compose logs -f postgres

.PHONY: docker-shell-api
docker-shell-api: ## Open shell in API container
	@docker compose exec api /bin/bash

.PHONY: docker-shell-bot
docker-shell-bot: ## Open shell in bot container
	@docker compose exec bot /bin/bash

.PHONY: docker-shell-postgres
docker-shell-postgres: ## Open PostgreSQL shell
	@docker compose exec postgres psql -U byte -d byte

.PHONY: docker-restart
docker-restart: ## Restart all Docker Compose services
	@echo "=> Restarting all services"
	@docker compose restart
	@echo "=> All services restarted"

.PHONY: docker-restart-api
docker-restart-api: ## Restart API service
	@docker compose restart api

.PHONY: docker-restart-bot
docker-restart-bot: ## Restart bot service
	@docker compose restart bot

.PHONY: docker-ps
docker-ps: ## Show status of Docker Compose services
	@docker compose ps

.PHONY: docker-rebuild
docker-rebuild: ## Rebuild and restart all services
	@echo "=> Rebuilding all services"
	@docker compose up -d --build --force-recreate
	@echo "=> All services rebuilt and restarted"

.PHONY: infra-up
infra-up: ## Start only PostgreSQL infrastructure
	@echo "=> Starting PostgreSQL infrastructure"
	@docker compose -f docker-compose.infra.yml up -d
	@echo "=> PostgreSQL started on localhost:5432"

.PHONY: infra-down
infra-down: ## Stop PostgreSQL infrastructure
	@echo "=> Stopping PostgreSQL infrastructure"
	@docker compose -f docker-compose.infra.yml down
	@echo "=> PostgreSQL stopped"

# =============================================================================
# Git Worktree Management
# =============================================================================

##@ Git Worktrees

worktree: ## Create a new git worktree for feature branch
	@echo "=> Creating git worktree"
	@read -p "Feature name: " name; \
	git checkout main && git pull && \
	git worktree add worktrees/$$name -b feature/$$name && \
	echo "=> Worktree created at worktrees/$$name on branch feature/$$name"

worktree-prune: ## Clean up stale git worktrees
	@echo "=> Pruning stale git worktrees"
	@git worktree prune -v
	@echo "=> Stale worktrees pruned"

# =============================================================================
# Main
# =============================================================================

clean: ## Autogenerated File Cleanup
	@echo "=> Cleaning up autogenerated files"
	@rm -rf .scannerwork/
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf .hypothesis
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@find . -name '*.egg-info' -exec rm -rf {} +
	@find . -name '*.egg' -exec rm -rf {} +
	@find . -name '*.pyc' -exec rm -rf {} +
	@find . -name '*.pyo' -exec rm -rf {} +
	@find . -name '*~' -exec rm -rf {} +
	@find . -name '__pycache__' -exec rm -rf {} +
	@find . -name '.ipynb_checkpoints' -exec rm -rf {} +
	@rm -rf .coverage
	@rm -rf coverage.xml
	@rm -rf coverage.json
	@rm -rf htmlcov/
	@rm -rf .pytest_cache
	@rm -rf tests/.pytest_cache
	@rm -rf tests/**/.pytest_cache
	$(MAKE) docs-clean

destroy: ## Destroy the virtual environment
	@rm -rf .venv

run-dev-bot: ## Run the bot in dev mode
	@cd services/bot && $(UV) run python -m byte_bot

run-dev-server: up-container ## Run the app in dev mode
	@cd services/api && $(UV) run litestar run --app byte_api.app:create_app --reload --debug

run-dev-frontend: ## Run the app frontend in dev mode
	@cd services/api && $(UV) run tailwindcss -i src/byte_api/domain/web/resources/input.css -o src/byte_api/domain/web/resources/style.css --watch

run-dev: up-container ## Run the bot, web, and front end in dev mode
	@echo "NOTE: Run each service separately in different terminals:"
	@echo "  Terminal 1: make run-dev-bot"
	@echo "  Terminal 2: make run-dev-server"
	@echo "  Terminal 3: make run-dev-frontend"
