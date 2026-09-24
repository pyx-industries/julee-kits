# Makefile for quality checks and testing
# Requires uv: https://docs.astral.sh/uv/getting-started/installation/
.PHONY: install check lint typecheck test test-integration test-doctrine format clean help

# Install every kit in the workspace, with dev dependencies
install:
	uv sync --all-packages --extra dev

# Linting
lint:
	@echo "Linting..."
	uv run black --check c4/src/ ceap/src/ hcd/src/ polling/src/ viewpoints/src/
	uv run ruff check c4/src/ ceap/src/ hcd/src/ polling/src/ viewpoints/src/

# Type checking
typecheck:
	@echo "Type checking..."
	uv run mypy c4/src/ ceap/src/ hcd/src/ polling/src/ viewpoints/src/

# Tests that need nothing but Python. Chosen by what is left out, so a
# test with no marker runs rather than hides.
test:
	@echo "Running unit tests..."
	uv run pytest -m "not integration and not e2e"

# Integration tests that need nothing but Python. Anything wanting a
# service to talk to — a MinIO at MINIO_ENDPOINT for CEAP's dependency
# wiring, a Temporal test server for polling's pipelines — is marked e2e
# as well, and left out here.
#
# These are in check. They once were not, back when "integration" meant
# "needs a service", and the exclusion outlived the reason: what a Sphinx
# directive does is build a page, so almost everything covering the
# directives is an integration test. A change to one could pass check
# completely and still be broken.
test-integration:
	@echo "Running integration tests..."
	uv run pytest -m "integration and not e2e" -n 2

# Each kit is a julee solution, and runs julee's doctrine against itself
test-doctrine:
	@for kit in c4 ceap hcd polling viewpoints; do \
		echo "Running doctrine tests for julee-$$kit..."; \
		JULEE_TARGET=$(CURDIR)/$$kit uv run pytest --pyargs julee.core.doctrine || exit $$?; \
	done

# The checks CI runs; run before pushing
check: lint typecheck test test-integration test-doctrine

# Format
format:
	uv run black c4/src/ ceap/src/ hcd/src/ polling/src/ viewpoints/src/
	uv run ruff check --fix c4/src/ ceap/src/ hcd/src/ polling/src/ viewpoints/src/

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
