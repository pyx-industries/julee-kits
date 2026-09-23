"""Tests for deriving personas from the two places they come from.

A persona is either written up, or inferred from the "As a ..." of a
story. This use case has to produce one list from both, and the archived
version could not: it called a merge_with_derived method that was never
defined anywhere, so the authored path would have raised AttributeError.
"""

import pytest

from julee_hcd.domain.models.epic import Epic
from julee_hcd.domain.models.persona import Persona
from julee_hcd.domain.models.story import Story
from julee_hcd.infrastructure.repositories.memory.epic import MemoryEpicRepository
from julee_hcd.infrastructure.repositories.memory.persona import (
    MemoryPersonaRepository,
)
from julee_hcd.infrastructure.repositories.memory.story import MemoryStoryRepository
from julee_hcd.usecases.derive_personas import (
    DerivePersonasRequest,
    DerivePersonasUseCase,
)

pytestmark = pytest.mark.unit


def _story(persona: str, app: str, title: str) -> Story:
    """A story told by a persona about an app."""
    return Story(
        slug=f"{app}--{title.lower().replace(' ', '-')}",
        feature_title=title,
        persona=persona,
        i_want="to do a thing",
        so_that="something follows",
        app_slug=app,
        file_path=f"features/{title}.feature",
    )


@pytest.fixture
async def repos() -> tuple[MemoryStoryRepository, MemoryEpicRepository]:
    """Two stories by two personas, one of them in an epic."""
    stories = MemoryStoryRepository()
    await stories.save(_story("Knowledge Curator", "library", "Search"))
    await stories.save(_story("Casual Reader", "library", "Browse"))
    epics = MemoryEpicRepository()
    await epics.save(Epic(slug="finding", story_refs=("Search",)))
    return stories, epics


async def test_a_persona_only_a_story_mentions_is_still_produced(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """Most personas are never written up; they should still appear."""
    stories, epics = repos

    response = await DerivePersonasUseCase(stories, epics).execute(
        DerivePersonasRequest()
    )

    assert {p.name for p in response.personas} == {
        "Knowledge Curator",
        "Casual Reader",
    }


async def test_a_derived_persona_knows_the_app_its_story_was_about(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """That link is the only thing a story tells us beyond the name."""
    stories, epics = repos

    response = await DerivePersonasUseCase(stories, epics).execute(
        DerivePersonasRequest()
    )
    curator = next(p for p in response.personas if p.name == "Knowledge Curator")

    assert curator.app_slugs == ("library",)


async def test_an_authored_persona_keeps_what_was_written_about_it(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """The regression this file exists for: the merge used to be a dead call."""
    stories, epics = repos
    personas = MemoryPersonaRepository()
    await personas.save(
        Persona.from_definition(
            slug="curator",
            name="Knowledge Curator",
            goals=("Find things",),
            context="Works in a reading room",
        )
    )

    response = await DerivePersonasUseCase(stories, epics, personas).execute(
        DerivePersonasRequest()
    )
    curator = next(p for p in response.personas if p.name == "Knowledge Curator")

    assert curator.goals == ("Find things",)
    assert curator.context == "Works in a reading room"
    assert curator.is_defined is True


async def test_an_authored_persona_gains_the_apps_its_stories_name(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """Authored wins on what it says, and learns what it does not say."""
    stories, epics = repos
    personas = MemoryPersonaRepository()
    await personas.save(
        Persona.from_definition(slug="curator", name="Knowledge Curator")
    )

    response = await DerivePersonasUseCase(stories, epics, personas).execute(
        DerivePersonasRequest()
    )
    curator = next(p for p in response.personas if p.name == "Knowledge Curator")

    assert curator.app_slugs == ("library",)
    assert curator.epic_slugs == ("finding",)


async def test_an_authored_persona_is_not_duplicated_by_its_own_stories(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """One person, however many ways the documentation mentions them."""
    stories, epics = repos
    personas = MemoryPersonaRepository()
    await personas.save(
        Persona.from_definition(slug="curator", name="Knowledge Curator")
    )

    response = await DerivePersonasUseCase(stories, epics, personas).execute(
        DerivePersonasRequest()
    )

    names = [p.name for p in response.personas]
    assert names.count("Knowledge Curator") == 1


async def test_an_authored_persona_nobody_tells_stories_about_survives(
    repos: tuple[MemoryStoryRepository, MemoryEpicRepository],
) -> None:
    """Writing someone up should be enough to have them documented."""
    stories, epics = repos
    personas = MemoryPersonaRepository()
    await personas.save(
        Persona.from_definition(slug="archivist", name="Archivist", goals=("Keep",))
    )

    response = await DerivePersonasUseCase(stories, epics, personas).execute(
        DerivePersonasRequest()
    )

    assert "Archivist" in {p.name for p in response.personas}
