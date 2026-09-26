# Makefile for quality checks and testing
# Requires uv: https://docs.astral.sh/uv/getting-started/installation/
.PHONY: install check lint typecheck test test-integration test-e2e test-doctrine format clean help

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
# service of its own to talk to — a MinIO at MINIO_ENDPOINT for CEAP's
# dependency wiring — is marked e2e as well, and left out here.
# Polling's pipelines are not among them: the Temporal test server they
# use ships with temporalio and starts itself.
#
# These are in check. They once were not, back when "integration" meant
# "needs a service", and the exclusion outlived the reason: what a Sphinx
# directive does is build a page, so almost everything covering the
# directives is an integration test. A change to one could pass check
# completely and still be broken.
test-integration:
	@echo "Running integration tests..."
	uv run pytest -m "integration and not e2e" -n 2

# The tests that need a service running. One today: CEAP's dependency
# wiring, built against the MinIO at MINIO_ENDPOINT.
#
# Not in check, which must need nothing running. An empty selection is
# pytest exit code 5 and stays a failure here, so this target cannot
# report success for finding no tests — which is what happened to the
# test it runs, marked e2e and therefore excluded from every target and
# every job, until julee-kits#65.
test-e2e:
	@echo "Running e2e tests..."
	uv run pytest -m e2e

# Each kit is a julee solution, and runs julee's doctrine against itself.
# Through the command julee 0.9.0 added, which is the one a solution
# outside this workspace would use: if it does not work here it does not
# work for them, and nobody would find out from a green run of ours.
test-doctrine:
	@for kit in c4 ceap hcd polling viewpoints; do \
		echo "Running doctrine for julee-$$kit..."; \
		uv run julee doctrine verify --target $(CURDIR)/$$kit || exit $$?; \
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
	@echo "  test-integration - Tests that build something wide but need no service"
	@echo "  test-e2e      - Tests that need a service (MINIO_ENDPOINT)"
	@echo "  test-doctrine - julee's doctrine, against each kit"
	@echo "  format        - Reformat with black and ruff"
	@echo "  clean         - Remove caches"
