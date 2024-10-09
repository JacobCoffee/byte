SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
USING_UV		=	$(shell grep "tool.uv" pyproject.toml && echo "yes")
ENV_PREFIX		=  .venv/bin/
VENV_EXISTS		=	$(shell python3 -c "if __import__('pathlib').Path('.venv/bin/activate').exists(): print('yes')")
uv_OPTS 		?=
uv 			    ?= 	uv $(uv_OPTS)

.EXPORT_ALL_VARIABLES:

.PHONY: help upgrade install-pre-commit install
.PHONY: fmt-fix test coverage check-all lint fmt-check
.PHONY: docs-install docs-clean docs-serve docs-build
.PHONY: clean run-dev-frontend run-dev-server production develop destroy

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

upgrade:       ## Upgrade all dependencies to the latest stable versions
	@if [ "$(USING_UV)" ]; then $(UV) lock --upgrade
	@echo "Dependencies Updated"

# =============================================================================
# Developer Utils
# =============================================================================

install-uv: 										## Install latest version of UV
	@curl -LsSf https://astral.sh/uv/install.sh | sh

install-pre-commit: ## Install pre-commit and install hooks
	@echo "Installing pre-commit hooks"
	@pre-commit install --install-hooks --all
	@pre-commit install --hook-type commit-msg
	@echo "pre-commit installed"

.PHONY: install
install: clean										## Install the project, dependencies, and pre-commit for local development
	@if ! $(uv) --version > /dev/null; then echo '=> Installing uv'; $(MAKE) install-uv; fi
	@if [ "$(VENV_EXISTS)" ]; then echo "=> Removing existing virtual environment"; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) destroy; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) clean; fi
	@if [ "$(USING_UV)" ]; then uv venv && uv pip install --quiet -U wheel setuptools cython mypy pip; fi
	@if [ "$(USING_UV)" ]; then $(uv) sync --all-extras --dev; fi
	@echo "=> Install complete! Note: If you want to re-install re-run 'make install'"

# =============================================================================
# Tests, Linting, Coverage
# =============================================================================

lint: ## Runs pre-commit hooks; includes ruff linting, codespell, black
	$(UV_RUN_BIN) pre-commit run --all-files

fmt-check: ## Runs Ruff format in check mode (no changes)
	$(UV_RUN_BIN) ruff format --check .

fmt: ## Runs Ruff format, makes changes where necessary
	$(UV_RUN_BIN) ruff format .

ruff: ## Runs Ruff
	$(UV_RUN_BIN) ruff check . --unsafe-fixes --fix

test:  ## Run the tests
	$(UV_RUN_BIN) pytest tests

coverage:  ## Run the tests and generate coverage report
	$(UV_RUN_BIN) pytest tests --cov=src
	$(UV_RUN_BIN) coverage html
	$(UV_RUN_BIN) coverage xml

check-all: lint test fmt-check coverage ## Run all linting, tests, and coverage checks

# =============================================================================
# Docs
# =============================================================================
docs-clean: 										## Dump the existing built docs
	@echo "=> Cleaning documentation build assets"
	@rm -rf docs/_build
	@echo "=> Removed existing documentation build assets"

docs-serve: docs-clean 								## Serve the docs locally
	@echo "=> Serving documentation"
	$(UV_RUN_BIN) sphinx-autobuild docs docs/_build/ -j auto --watch src --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002

docs: docs-clean 									## Dump the existing built docs and rebuild them
	@echo "=> Building documentation"
	@$(UV_RUN_BIN) sphinx-build -M html docs docs/_build/ -E -a -j auto --keep-going

# =============================================================================
# Database
# =============================================================================
migrations:       ## Generate database migrations
	@echo "ATTENTION: This operation will create a new database migration for any defined models changes."
	@while [ -z "$$MIGRATION_MESSAGE" ]; do read -r -p "Migration message: " MIGRATION_MESSAGE; done ;
	@$(UV_RUN_BIN) app database make-migrations --autogenerate -m "$${MIGRATION_MESSAGE}"

.PHONY: migrate
migrate:          ## Apply database migrations
	@echo "ATTENTION: Will apply all database migrations."
	@$(UV_RUN_BIN) app database upgrade --no-prompt

# =============================================================================
# Main
# =============================================================================

clean: ## Autogenerated File Cleanup
	@rm -rf .scannerwork/
	@rm -rf .pytest_cache
	@rm -rf .ruff_cache
	@rm -rf .hypothesis
	@rm -rf build/
	@rm -rf dist/
	@rm -rf .eggs/
	@find . -name '*.egg-info' -exec rm -rf {} +
	@find . -name '*.egg' -exec rm -f {} +
	@find . -name '*.pyc' -exec rm -f {} +
	@find . -name '*.pyo' -exec rm -f {} +
	@find . -name '*~' -exec rm -f {} +
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
	rm -rf .venv

develop: install ## Install the project in dev mode.
	@if ! $(UV) --version > /dev/null; then echo 'UV is required, installing...'; $(MAKE) install-uv; fi
	@if [ "$(VENV_EXISTS)" ]; then echo "Removing existing virtual environment"; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) destroy; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) clean; fi
	if [ "$(USING_UV)" ]; then $(UV) config venv.in_project true && python3 -m venv --copies .venv && source .venv/bin/activate && .venv/bin/pip install -U wheel setuptools cython pip; fi
	if [ "$(USING_UV)" ]; then $(UV) install -G:all; fi
	if [ "$(VENV_EXISTS)" && ! -f .env ]; then cp .env.example .env; fi
	@echo "=> Install complete! Note: If you want to re-install re-run 'make develop'"

run-dev-bot: ## Run the bot in dev mode
	$(UV_RUN_BIN) app run-bot

run-dev-server: ## Run the app in dev mode
	$(UV_RUN_BIN) app run-web --http-workers 1 --reload

run-dev-frontend: ## Run the app frontend in dev mode
	$(UV_RUN_BIN) tailwindcss -i src/server/domain/web/resources/input.css -o src/server/domain/web/resources/style.css --watch

run-dev: ## Run the bot, web, and front end in dev mode
	$(UV_RUN_BIN) app run-all --http-workers 1 -d -v --reload
