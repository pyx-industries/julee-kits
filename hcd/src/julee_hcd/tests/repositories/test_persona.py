"""Tests for MemoryPersonaRepository.

There was no persona repository before this kit: viewpoints derived
personas and never stored them. These cover the lookups a story needs,
which go by name rather than by slug.
"""

import pytest

from julee_hcd.domain.models.persona import Persona
from julee_hcd.infrastructure.repositories.memory.persona import (
    MemoryPersonaRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
async def repo() -> MemoryPersonaRepository:
    """A repository holding one authored and one derived persona."""
    repo = MemoryPersonaRepository()
    await repo.save(
        Persona.from_definition(
            slug="curator",
            name="Knowledge Curator",
            goals=("Find things",),
            docname="personas/curator",
        )
    )
    await repo.save(Persona.from_story_reference("Casual Reader"))
    return repo


async def test_a_persona_is_found_by_its_display_name(
    repo: MemoryPersonaRepository,
) -> None:
    """A story says "As a Knowledge Curator", not "As a curator"."""
    found = await repo.get_by_name("Knowledge Curator")

    assert found is not None
    assert found.slug == "curator"


async def test_an_unknown_name_is_none(repo: MemoryPersonaRepository) -> None:
    """A story may name a persona nobody has written up."""
    assert await repo.get_by_name("Nobody") is None


async def test_names_match_across_case_and_separators(
    repo: MemoryPersonaRepository,
) -> None:
    """What a story calls a persona and what a definition calls it differ."""
    found = await repo.get_by_normalized_name("knowledge-curator")

    assert found is not None
    assert found.slug == "curator"


async def test_the_exact_name_lookup_does_not_match_across_case(
    repo: MemoryPersonaRepository,
) -> None:
    """Two lookups exist because they answer differently; this is why."""
    assert await repo.get_by_name("knowledge curator") is None


async def test_only_the_written_up_personas_are_listed_as_defined(
    repo: MemoryPersonaRepository,
) -> None:
    """A persona index should show people somebody described."""
    defined = await repo.list_defined()

    assert [p.slug for p in defined] == ["curator"]


async def test_a_derived_persona_is_still_stored_and_retrievable(
    repo: MemoryPersonaRepository,
) -> None:
    """Being underdescribed is not being absent."""
    found = await repo.get("casual-reader")

    assert found is not None
    assert found.is_defined is False
