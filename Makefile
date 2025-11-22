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

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

upgrade: ## Upgrade all dependencies to the latest stable versions
	@echo "=> Upgrading prek"
	@(UV_RUN_BIN) run prek autoupdate
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
	@(UV_RUN_BIN) run prek install
	@(UV_RUN_BIN) run prek install --hook-type commit-msg
	@echo "=> prek hooks installed"
	@(UV_RUN_BIN) run prek autoupdate
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
	@$(UV) venv && $(UV) pip install --quiet -U wheel setuptools cython mypy pip
	@$(UV) sync --all-extras --force-reinstall --dev
	@echo "=> Backend dependencies installed"

.PHONY: install
install: clean destroy ## Install the project, dependencies, and pre-commit for local development
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
	@$(UV) run app database upgrade --no-prompt
	@echo "rest not yet implemented"
	@echo "=> Loaded database migrations and test data"

refresh-container: clean-container up-container load-container ## Refresh the Byte database container



# =============================================================================
# Tests, Linting, Coverage
# =============================================================================

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

test:  ## Run the tests
	@$(UV) run --no-sync pytest tests

coverage:  ## Run the tests and generate coverage report
	@$(UV) run --no-sync pytest tests --cov=byte_bot
	@$(UV) run --no-sync coverage html
	@$(UV) run --no-sync coverage xml

check-all: lint test fmt-check coverage ## Run all linting, tests, and coverage checks

# =============================================================================
# Docs
# =============================================================================
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
migrations: ## Generate database migrations
	@echo "ATTENTION: This operation will create a new database migration for any defined models changes."
	@while [ -z "$$MIGRATION_MESSAGE" ]; do read -r -p "Migration message: " MIGRATION_MESSAGE; done ;
	@$(UV) run app database make-migrations --autogenerate -m "$${MIGRATION_MESSAGE}"

.PHONY: migrate
migrate: ## Apply database migrations
	@echo "ATTENTION: Will apply all database migrations."
	@$(UV) run app database upgrade --no-prompt

.PHONY: db
db: ## Run the database
	@docker compose -f "docker-compose.infra.yml" up -d --build

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
	@rm -rf .mypy_cache
	$(MAKE) docs-clean

destroy: ## Destroy the virtual environment
	@rm -rf .venv

run-dev-bot: ## Run the bot in dev mode
	@$(UV) run app run-bot

run-dev-server: up-container ## Run the app in dev mode
	@$(UV) run app run-web --http-workers 1 --reload

run-dev-frontend: ## Run the app frontend in dev mode
	@$(UV) run tailwindcss -i byte_bot/server/domain/web/resources/input.css -o byte_bot/server/domain/web/resources/style.css --watch

run-dev: up-container ## Run the bot, web, and front end in dev mode
	@$(UV) run app run-all --http-workers 1 -d -v --reload
