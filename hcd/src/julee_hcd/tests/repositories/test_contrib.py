"""Tests for MemoryContribRepository's own query."""

import pytest

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.infrastructure.repositories.memory.contrib import (
    MemoryContribRepository,
)

pytestmark = pytest.mark.unit


async def test_modules_are_listed_per_solution() -> None:
    """One site may document several solutions, each with its own utilities."""
    repo = MemoryContribRepository()
    await repo.save(ContribModule(slug="polling", solution_slug="shop"))
    await repo.save(ContribModule(slug="auth", solution_slug="shop"))
    await repo.save(ContribModule(slug="other", solution_slug="warehouse"))

    found = await repo.list_for_solution("shop")

    assert {m.slug for m in found} == {"polling", "auth"}


async def test_a_solution_with_no_modules_lists_none() -> None:
    """Not every solution ships utilities."""
    repo = MemoryContribRepository()
    await repo.save(ContribModule(slug="polling", solution_slug="shop"))

    assert await repo.list_for_solution("warehouse") == []
