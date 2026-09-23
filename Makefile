# Makefile for quality checks and testing
# Requires uv: https://docs.astral.sh/uv/getting-started/installation/
.PHONY: install check lint typecheck test test-integration test-doctrine format clean help

# Install every kit in the workspace, with dev dependencies
install:
	uv sync --all-packages --extra dev

# Linting
lint:
	@echo "Linting..."
	uv run black --check ceap/src/ polling/src/
	uv run ruff check ceap/src/ polling/src/

# Type checking
typecheck:
	@echo "Type checking..."
	uv run mypy ceap/src/ polling/src/

# Tests that need nothing but Python. Chosen by what is left out, so a
# test with no marker runs rather than hides.
test:
	@echo "Running unit tests..."
	uv run pytest -m "not integration and not e2e"

# Tests that need something running: a MinIO at MINIO_ENDPOINT for CEAP's
# dependency wiring, a Temporal test server for polling's pipelines. Not
# part of check, because CI provides neither.
test-integration:
	@echo "Running integration tests..."
	uv run pytest -m integration -n 2

# Each kit is a julee solution, and runs julee's doctrine against itself
test-doctrine:
	@for kit in ceap polling; do \
		echo "Running doctrine tests for julee-$$kit..."; \
		JULEE_TARGET=$(CURDIR)/$$kit uv run pytest --pyargs julee.core.doctrine || exit $$?; \
	done

# The checks CI runs; run before pushing
check: lint typecheck test test-doctrine

# Format
format:
	uv run black ceap/src/ polling/src/
	uv run ruff check --fix ceap/src/ polling/src/

clean:
	rm -rf .pytest_cache .mypy_cache **/__pycache__ htmlcov .coverage

help:
	@echo "Available targets:"
	@echo "  check         - The checks CI runs (lint, types, unit, doctrine)"
	@echo "  install       - Install every kit with dev dependencies"
	@echo "  lint          - black and ruff"
	@echo "  typecheck     - mypy"
	@echo "  test          - Tests that need nothing but Python"
	@echo "  test-integration - Tests that need MinIO or a Temporal server"
	@echo "  test-doctrine - julee's doctrine, against each kit"
	@echo "  format        - Reformat with black and ruff"
	@echo "  clean         - Remove caches"
