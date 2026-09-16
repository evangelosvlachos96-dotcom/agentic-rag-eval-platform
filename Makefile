# Developer entry points. Every target runs inside the uv-managed environment.
# On Windows without GNU make, run the underlying `uv run ...` commands directly.

UV ?= uv

.PHONY: help install lint format typecheck test check precommit clean

help: ## Show available targets
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

install: ## Create the environment and install base + dev dependencies
	$(UV) sync

lint: ## Ruff lint and format check (no changes)
	$(UV) run ruff check .
	$(UV) run ruff format --check .

format: ## Auto-format and auto-fix lint issues
	$(UV) run ruff format .
	$(UV) run ruff check --fix .

typecheck: ## Strict mypy over src and tests
	$(UV) run mypy

test: ## Run the test suite
	$(UV) run pytest

check: lint typecheck test ## Everything CI runs

precommit: ## Install git hooks
	$(UV) run pre-commit install

clean: ## Remove caches and build artifacts
	rm -rf .ruff_cache .mypy_cache .pytest_cache .coverage htmlcov dist build
