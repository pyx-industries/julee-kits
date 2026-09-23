"""Tests for the behaviour every in-memory HCD repository shares.

Exercised through the contrib repository, the smallest entity that has
it, because the base is not a repository anyone instantiates alone.
"""

import pytest

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.infrastructure.repositories.memory.contrib import (
    MemoryContribRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> MemoryContribRepository:
    """An empty repository."""
    return MemoryContribRepository()


async def test_a_saved_entity_comes_back_by_slug(
    repo: MemoryContribRepository,
) -> None:
    """The plainest thing a repository does."""
    await repo.save(ContribModule(slug="polling"))

    found = await repo.get("polling")

    assert found is not None
    assert found.slug == "polling"


async def test_an_absent_entity_is_none_rather_than_an_error(
    repo: MemoryContribRepository,
) -> None:
    """Asking is not asserting; the use cases decide what absence means."""
    assert await repo.get("missing") is None


async def test_saving_the_same_slug_twice_replaces_rather_than_duplicates(
    repo: MemoryContribRepository,
) -> None:
    """A document re-read should not leave two of everything."""
    await repo.save(ContribModule(slug="polling", name="Old"))
    await repo.save(ContribModule(slug="polling", name="New"))

    everything = await repo.list_all()

    assert len(everything) == 1
    assert everything[0].name == "New"


async def test_get_many_reports_the_ones_it_could_not_find(
    repo: MemoryContribRepository,
) -> None:
    """A caller asking for several wants to know which are missing."""
    await repo.save(ContribModule(slug="polling"))

    found = await repo.get_many(["polling", "missing"])

    assert found["polling"] is not None
    assert found["missing"] is None


async def test_deleting_says_whether_there_was_anything_to_delete(
    repo: MemoryContribRepository,
) -> None:
    """Deleting twice is not an error, but it is not the same answer."""
    await repo.save(ContribModule(slug="polling"))

    assert await repo.delete("polling") is True
    assert await repo.delete("polling") is False


async def test_clearing_empties_the_repository(
    repo: MemoryContribRepository,
) -> None:
    """A full build starts from nothing, not from the last build."""
    await repo.save(ContribModule(slug="polling"))
    await repo.save(ContribModule(slug="auth"))

    await repo.clear()

    assert await repo.list_all() == []


async def test_entities_are_found_by_the_document_they_came_from(
    repo: MemoryContribRepository,
) -> None:
    """An incremental build works a document at a time."""
    await repo.save(ContribModule(slug="polling", docname="contrib/index"))
    await repo.save(ContribModule(slug="auth", docname="contrib/index"))
    await repo.save(ContribModule(slug="other", docname="elsewhere"))

    found = await repo.get_by_docname("contrib/index")

    assert {m.slug for m in found} == {"polling", "auth"}


async def test_clearing_a_document_leaves_the_other_documents_alone(
    repo: MemoryContribRepository,
) -> None:
    """Re-reading one file must not forget what the others said."""
    await repo.save(ContribModule(slug="polling", docname="contrib/index"))
    await repo.save(ContribModule(slug="other", docname="elsewhere"))

    removed = await repo.clear_by_docname("contrib/index")

    assert removed == 1
    assert [m.slug for m in await repo.list_all()] == ["other"]


async def test_clearing_a_document_that_defined_nothing_removes_nothing(
    repo: MemoryContribRepository,
) -> None:
    """Sphinx re-reads documents that have no HCD content in them."""
    await repo.save(ContribModule(slug="polling", docname="contrib/index"))

    assert await repo.clear_by_docname("untouched") == 0
    assert len(await repo.list_all()) == 1
