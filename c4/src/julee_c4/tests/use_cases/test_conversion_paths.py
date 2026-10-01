"""Parent references survive the generated request/domain boundary."""

import pytest
from julee.core.values.text import Slug

from julee_c4.dtos.crud_deployment_node import (
    CreateDeploymentNodeRequest,
    UpdateDeploymentNodeRequest,
)
from julee_c4.infrastructure.repositories.memory.deployment_node import (
    MemoryDeploymentNodeRepository,
)
from julee_c4.usecases.crud_deployment_node import (
    CreateDeploymentNodeUseCase,
    UpdateDeploymentNodeUseCase,
)


@pytest.mark.asyncio
async def test_parent_reference_resolves_after_create_update_and_clear():
    repo = MemoryDeploymentNodeRepository()
    await CreateDeploymentNodeUseCase(repo).execute(
        CreateDeploymentNodeRequest(
            slug="child", name="Child", parent_slug=" Parent Node "
        )
    )
    assert len(await repo.get_children("parent-node")) == 1
    entity = await repo.get("child")
    assert entity is not None
    assert isinstance(entity.parent_slug, Slug)
    update = UpdateDeploymentNodeUseCase(repo)
    await update.execute(
        UpdateDeploymentNodeRequest(slug="child", parent_slug=" Other Parent ")
    )
    assert len(await repo.get_children("other-parent")) == 1
    await update.execute(
        UpdateDeploymentNodeRequest(slug="child", description="Changed")
    )
    entity = await repo.get("child")
    assert entity is not None
    assert entity.parent_slug == "other-parent"
    await update.execute(UpdateDeploymentNodeRequest(slug="child", parent_slug=None))
    entity = await repo.get("child")
    assert entity is not None
    assert entity.parent_slug is None


@pytest.mark.asyncio
async def test_invalid_parent_is_refused_before_save():
    repo = MemoryDeploymentNodeRepository()
    create = CreateDeploymentNodeUseCase(repo)
    with pytest.raises(ValueError):
        await create.execute(
            CreateDeploymentNodeRequest(slug="child", name="Child", parent_slug="   ")
        )
    assert await repo.get("child") is None
    await create.execute(CreateDeploymentNodeRequest(slug="child", name="Child"))
    original = await repo.get("child")
    with pytest.raises(ValueError):
        await UpdateDeploymentNodeUseCase(repo).execute(
            UpdateDeploymentNodeRequest(slug="child", parent_slug="   ")
        )
    assert await repo.get("child") is original
