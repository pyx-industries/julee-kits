"""Tests for the generated CRUD use cases.

The code is generated, so these do not re-test the generator — julee does
that. They cover what is particular to this kit: that the field lists in
generate-crud.sh say what the entities say, that a slug the caller chose
is kept, and that the derived fields were left out of the requests on
purpose.
"""

import pytest

from julee_hcd.infrastructure.repositories.memory.persona import (
    MemoryPersonaRepository,
)
from julee_hcd.infrastructure.repositories.memory.story import MemoryStoryRepository
from julee_hcd.usecases.crud_persona import (
    CreatePersonaRequest,
    CreatePersonaUseCase,
    DeletePersonaRequest,
    DeletePersonaUseCase,
    GetPersonaRequest,
    GetPersonaUseCase,
    ListPersonasRequest,
    ListPersonasUseCase,
    UpdatePersonaRequest,
    UpdatePersonaUseCase,
)
from julee_hcd.usecases.crud_story import CreateStoryRequest

pytestmark = pytest.mark.unit


@pytest.fixture
def repo() -> MemoryPersonaRepository:
    """An empty persona repository."""
    return MemoryPersonaRepository()


async def test_creating_a_persona_keeps_the_slug_it_was_given(
    repo: MemoryPersonaRepository,
) -> None:
    """An HCD entity is keyed by its own slug, not one the repository mints."""
    response = await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest(slug="curator", name="Knowledge Curator")
    )

    assert response.persona.slug == "curator"


async def test_creating_a_persona_without_a_slug_derives_one(
    repo: MemoryPersonaRepository,
) -> None:
    """The repository mints nothing; the entity derives it from the name."""
    response = await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest(name="Knowledge Curator")
    )

    assert response.persona.slug == "knowledge-curator"


async def test_creating_a_persona_needs_only_a_name(
    repo: MemoryPersonaRepository,
) -> None:
    """Everything the entity defaults, the request defaults too."""
    response = await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest(name="Knowledge Curator")
    )

    assert response.persona.goals == ()
    assert response.persona.context == ""
    assert response.persona.solution_slug == ""


async def test_an_update_changes_only_what_it_names(
    repo: MemoryPersonaRepository,
) -> None:
    """The defect julee 0.5.1 fixed; this kit depends on it being fixed."""
    await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest(
            slug="curator", name="Knowledge Curator", context="Reading room"
        )
    )

    response = await UpdatePersonaUseCase(repo).execute(
        UpdatePersonaRequest(slug="curator", goals=("Find things",))
    )

    assert response.persona.goals == ("Find things",)
    assert response.persona.context == "Reading room"
    assert response.persona.name == "Knowledge Curator"


async def test_getting_a_persona_that_is_not_there_raises(
    repo: MemoryPersonaRepository,
) -> None:
    """Absence is an error here, as it is everywhere else in julee."""
    from julee.core.usecases.generic_crud import EntityNotFoundError

    with pytest.raises(EntityNotFoundError):
        await GetPersonaUseCase(repo).execute(GetPersonaRequest(slug="nobody"))


async def test_listing_reports_how_many_there_are(
    repo: MemoryPersonaRepository,
) -> None:
    """The index pages need the count as well as the personas."""
    await CreatePersonaUseCase(repo).execute(CreatePersonaRequest(name="One"))
    await CreatePersonaUseCase(repo).execute(CreatePersonaRequest(name="Two"))

    response = await ListPersonasUseCase(repo).execute(ListPersonasRequest())

    assert response.total_count == 2
    assert len(response.personas) == 2


async def test_deleting_reports_whether_there_was_anything_to_delete(
    repo: MemoryPersonaRepository,
) -> None:
    """Deleting what is already gone is the outcome the caller wanted."""
    await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest(slug="curator", name="Knowledge Curator")
    )
    use_case = DeletePersonaUseCase(repo)

    assert (await use_case.execute(DeletePersonaRequest(slug="curator"))).deleted
    assert not (await use_case.execute(DeletePersonaRequest(slug="curator"))).deleted


def test_derived_fields_are_not_accepted_on_the_way_in() -> None:
    """A caller must not be able to contradict what the entity computes."""
    assert "persona_normalized" not in CreateStoryRequest.model_fields
    assert "app_normalized" not in CreateStoryRequest.model_fields


def test_a_story_must_say_what_it_wants_and_why() -> None:
    """The entity defaults these for a feature file that said nothing.

    A caller creating a story deliberately has no such excuse, so
    generate-crud.sh makes them required.
    """
    # mypy objects to this call for the same reason the test exists: the
    # two fields are required, and leaving them out is the point.
    with pytest.raises(ValueError):
        CreateStoryRequest(  # type: ignore[call-arg]
            slug="s",
            feature_title="Search",
            persona="Reader",
            app_slug="library",
            file_path="features/search.feature",
        )


async def test_the_story_repository_and_its_use_cases_agree_on_the_key() -> None:
    """A smoke test that the generated wiring matches the repository."""
    from julee_hcd.usecases.crud_story import (
        CreateStoryUseCase,
        GetStoryRequest,
        GetStoryUseCase,
    )

    repo = MemoryStoryRepository()
    await CreateStoryUseCase(repo).execute(
        CreateStoryRequest(
            slug="library--search",
            feature_title="Search",
            persona="Reader",
            i_want="to search",
            so_that="I find things",
            app_slug="library",
            file_path="features/search.feature",
        )
    )

    found = await GetStoryUseCase(repo).execute(GetStoryRequest(slug="library--search"))

    assert found.story.feature_title == "Search"
