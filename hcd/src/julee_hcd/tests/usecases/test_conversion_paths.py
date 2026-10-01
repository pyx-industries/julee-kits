"""Generated boundaries must persist typed, usable domain values."""

import pytest
from julee.core.values.text import Slug

from julee_hcd.domain.values.journey_step import JourneyStep
from julee_hcd.dtos.crud_journey import CreateJourneyRequest, UpdateJourneyRequest
from julee_hcd.dtos.crud_persona import CreatePersonaRequest, UpdatePersonaRequest
from julee_hcd.infrastructure.repositories.memory.journey import MemoryJourneyRepository
from julee_hcd.infrastructure.repositories.memory.persona import MemoryPersonaRepository
from julee_hcd.usecases.crud_journey import CreateJourneyUseCase, UpdateJourneyUseCase
from julee_hcd.usecases.crud_persona import CreatePersonaUseCase, UpdatePersonaUseCase


@pytest.mark.asyncio
async def test_journey_dependencies_resolve_after_create_and_update():
    repo = MemoryJourneyRepository()
    create = CreateJourneyUseCase(repo)
    await create.execute(CreateJourneyRequest(slug="other-journey"))
    await create.execute(
        CreateJourneyRequest(slug="journey", depends_on=(" Other Journey ",))
    )
    assert [e.slug for e in await repo.get_dependencies("journey")] == ["other-journey"]
    await UpdateJourneyUseCase(repo).execute(
        UpdateJourneyRequest(slug="journey", depends_on=("OTHER JOURNEY",))
    )
    assert [e.slug for e in await repo.get_dependencies("journey")] == ["other-journey"]
    entity = await repo.get("journey")
    assert entity is not None
    assert isinstance(entity.depends_on[0], Slug)


@pytest.mark.asyncio
async def test_updated_steps_remain_usable_domain_values():
    repo = MemoryJourneyRepository()
    await CreateJourneyUseCase(repo).execute(CreateJourneyRequest(slug="journey"))
    await UpdateJourneyUseCase(repo).execute(
        UpdateJourneyRequest.model_validate(
            {"slug": "journey", "steps": [{"step_type": "story", "ref": " A story "}]}
        )
    )
    entity = await repo.get("journey")
    assert entity is not None
    assert isinstance(entity.steps[0], JourneyStep)
    assert entity.get_story_refs() == ["A story"]
    await UpdateJourneyUseCase(repo).execute(
        UpdateJourneyRequest(slug="journey", goal="New goal")
    )
    entity = await repo.get("journey")
    assert entity is not None
    assert entity.get_story_refs() == ["A story"]
    await UpdateJourneyUseCase(repo).execute(
        UpdateJourneyRequest(slug="journey", steps=())
    )
    entity = await repo.get("journey")
    assert entity is not None
    assert entity.steps == ()


@pytest.mark.parametrize(
    "field", ["app_slugs", "epic_slugs", "accelerator_slugs", "contrib_slugs"]
)
@pytest.mark.asyncio
async def test_persona_reference_collections_are_normalised(field):
    repo = MemoryPersonaRepository()
    await CreatePersonaUseCase(repo).execute(
        CreatePersonaRequest.model_validate(
            {"slug": "persona", "name": "Persona", field: [" Some Target "]}
        )
    )
    assert getattr(await repo.get("persona"), field) == ("some-target",)
    await UpdatePersonaUseCase(repo).execute(
        UpdatePersonaRequest.model_validate(
            {"slug": "persona", field: [" Other Target "]}
        )
    )
    assert isinstance(getattr(await repo.get("persona"), field)[0], Slug)
    assert getattr(await repo.get("persona"), field) == ("other-target",)


@pytest.mark.asyncio
async def test_invalid_dependency_is_refused_before_save():
    repo = MemoryJourneyRepository()
    await CreateJourneyUseCase(repo).execute(CreateJourneyRequest(slug="journey"))
    original = await repo.get("journey")
    with pytest.raises(ValueError):
        await UpdateJourneyUseCase(repo).execute(
            UpdateJourneyRequest(slug="journey", depends_on=("   ",))
        )
    assert await repo.get("journey") is original
