SHELL := /bin/bash
# =============================================================================
# Variables
# =============================================================================

.DEFAULT_GOAL:=help
.ONESHELL:
USING_PDM	=	$(shell grep "tool.pdm" pyproject.toml && echo "yes")
ENV_PREFIX		=	$(shell python3 -c "if __import__('pathlib').Path('.venv/3.11/lib').exists(): print('.venv/3.11/lib/')")
VENV_EXISTS		=	$(shell python3 -c "if __import__('pathlib').Path('.venv/bin/activate').exists(): print('yes')")
REPO_INFO 		?= 	$(shell git config --get remote.origin.url)
COMMIT_SHA 		?= 	git-$(shell git rev-parse --short HEAD)
PDM_OPTS 		?=
PDM 			?= 	pdm $(PDM_OPTS)
PDM_RUN_BIN 	= 	$(PDM) run
SPHINXBUILD 	=	sphinx-build
SPHINXAUTOBUILD = 	sphinx-autobuild

.EXPORT_ALL_VARIABLES:

.PHONY: help upgrade install-pre-commit install
.PHONY: fmt-fix test coverage check-all lint fmt-check
.PHONY: docs-install docs-clean docs-serve docs-build
.PHONY: clean run-dev-frontend run-dev-server production develop destroy

help: ## Display this help text for Makefile
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

upgrade:       ## Upgrade all dependencies to the latest stable versions
	@if [ "$(USING_PDM)" ]; then $(PDM) update; fi
	@echo "Dependencies Updated"

# =============================================================================
# Developer Utils
# =============================================================================

install-pdm: 										## Install latest version of PDM
	@curl -sSLO https://pdm.fming.dev/install-pdm.py && \
	curl -sSL https://pdm.fming.dev/install-pdm.py.sha256 | shasum -a 256 -c - && \
	python3 install-pdm.py

install-pre-commit: ## Install pre-commit and install hooks
	@echo "Installing pre-commit"
	@$(PDM) add pre-commit
	@pre-commit install --install-hooks --all
	@pre-commit install --hook-type commit-msg
	@echo "pre-commit installed"

install: ## Install all dependencies
	@echo "Installing..."
	@command -v $(PDM) > /dev/null || (echo "PDM not found. Installing..." && $(MAKE) install-pdm)
	$(MAKE) install-pre-commit

up-container: ## Start the Byte database container
	@echo "=> Starting Byte database container"
	@docker compose -f docker-compose.infra.yml up -d
	@echo "=> Started Byte database container"

clean-container: ## Stop, remove, and wipe the Byte database container and volume
	@echo "=> Stopping and removing Byte database container"
	@docker stop byte-db-1
	@docker rm byte-db-1
	@docker volume rm byte_db-data
	@echo "=> Stopped and removed Byte database container"

load-container: migrate ## Perform database migrations and load test data into the Byte database container
	@echo "=> Loading database migrations and test data"
	# load data, we already run migrate

	@echo "=> Loaded database migrations and test data"

.PHONY: refresh-lockfiles
refresh-lockfiles:                                 ## Sync lockfiles with requirements files.
	$(PDM) update --update-reuse -G:all

.PHONY: lock
lock:                                             ## Rebuild lockfiles from scratch, updating all dependencies
	$(PDM) update --update-eager -G:all

# =============================================================================
# Tests, Linting, Coverage
# =============================================================================

lint: ## Runs pre-commit hooks; includes ruff linting, codespell, black
	$(PDM_RUN_BIN) pre-commit run --all-files

fmt-check: ## Runs Ruff format in check mode (no changes)
	$(PDM_RUN_BIN) ruff format --check .

fmt: ## Runs Ruff format, makes changes where necessary
	$(PDM_RUN_BIN) ruff format .

ruff: ## Runs Ruff
	$(PDM_RUN_BIN) ruff check . --unsafe-fixes --fix

test:  ## Run the tests
	$(PDM_RUN_BIN) pytest tests

coverage:  ## Run the tests and generate coverage report
	$(PDM_RUN_BIN) pytest tests --cov=src
	$(PDM_RUN_BIN) coverage html
	$(PDM_RUN_BIN) coverage xml

check-all: lint test fmt-check coverage ## Run all linting, tests, and coverage checks

# =============================================================================
# Docs
# =============================================================================
.PHONY: docs-install
docs-install: 										## Install docs dependencies
	@echo "=> Installing documentation dependencies"
	@$(PDM) install -G:docs
	@echo "=> Installed documentation dependencies"

docs-clean: 										## Dump the existing built docs
	@echo "=> Cleaning documentation build assets"
	@rm -rf docs/_build
	@echo "=> Removed existing documentation build assets"

docs-serve: docs-clean 								## Serve the docs locally
	@echo "=> Serving documentation"
	$(PDM_RUN_BIN) sphinx-autobuild docs docs/_build/ -j auto --watch src --watch docs --watch tests --watch CONTRIBUTING.rst --port 8002

docs: docs-clean 									## Dump the existing built docs and rebuild them
	@echo "=> Building documentation"
	@$(PDM_RUN_BIN) sphinx-build -M html docs docs/_build/ -E -a -j auto --keep-going

# =============================================================================
# Database
# =============================================================================
migrations:       ## Generate database migrations
	@echo "ATTENTION: This operation will create a new database migration for any defined models changes."
	@while [ -z "$$MIGRATION_MESSAGE" ]; do read -r -p "Migration message: " MIGRATION_MESSAGE; done ;
	@$(ENV_PREFIX)app database make-migrations --autogenerate -m "$${MIGRATION_MESSAGE}"

.PHONY: migrate
migrate:          ## Apply database migrations
	@echo "ATTENTION: Will apply all database migrations."
	@$(ENV_PREFIX)app database upgrade --no-prompt

# =============================================================================
# Main
# =============================================================================

clean: ## Autogenerated File Cleanup
	rm -rf .scannerwork/
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .hypothesis
	rm -rf build/
	rm -rf dist/
	rm -rf .eggs/
	find . -name '*.egg-info' -exec rm -rf {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +
	find . -name '.ipynb_checkpoints' -exec rm -rf {} +
	rm -rf .coverage
	rm -rf coverage.xml
	rm -rf coverage.json
	rm -rf htmlcov/
	rm -rf .pytest_cache
	rm -rf tests/.pytest_cache
	rm -rf tests/**/.pytest_cache
	rm -rf .mypy_cache
	find tools/downloads -type f -delete
	$(MAKE) docs-clean

destroy: ## Destroy the virtual environment
	rm -rf .venv

develop: install ## Install the project in dev mode.
	@if ! $(PDM) --version > /dev/null; then echo 'PDM is required, installing...'; $(MAKE) install-pdm; fi
	@if [ "$(VENV_EXISTS)" ]; then echo "Removing existing virtual environment"; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) destroy; fi
	if [ "$(VENV_EXISTS)" ]; then $(MAKE) clean; fi
	if [ "$(USING_PDM)" ]; then $(PDM) config venv.in_project true && python3 -m venv --copies .venv && source .venv/bin/activate && .venv/bin/pip install -U wheel setuptools cython pip; fi
	if [ "$(USING_PDM)" ]; then $(PDM) install -G:all; fi
	if [ "$(VENV_EXISTS)" && ! -f .env ]; then cp .env.example .env; fi
	@echo "=> Install complete! Note: If you want to re-install re-run 'make develop'"

run-dev-bot: ## Run the bot in dev mode
	$(PDM_RUN_BIN) app run-bot

run-dev-server: ## Run the app in dev mode
	$(PDM_RUN_BIN) app run-web --http-workers 1 --reload

run-dev-frontend: ## Run the app frontend in dev mode
	$(PDM_RUN_BIN) tailwindcss -i src/server/domain/web/resources/input.css -o src/server/domain/web/resources/style.css --watch

run-dev: ## Run the bot, web, and front end in dev mode
	$(PDM_RUN_BIN) app run-all --http-workers 1 -d -v --reload
