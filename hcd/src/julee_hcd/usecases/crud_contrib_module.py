"""Generated CRUD use cases for ContribModule.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.domain.repositories.contrib import ContribRepository

from ..dtos.crud_contrib_module import (
    CreateContribModuleRequest,
    CreateContribModuleResponse,
    DeleteContribModuleRequest,
    DeleteContribModuleResponse,
    GetContribModuleRequest,
    GetContribModuleResponse,
    ListContribModulesRequest,
    ListContribModulesResponse,
    UpdateContribModuleRequest,
    UpdateContribModuleResponse,
)

ContribModuleRepository = ContribRepository


class GetContribModuleUseCase(GetUseCase[ContribModule, ContribModuleRepository]):
    """Get a ContribModule by slug."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    async def execute(
        self, request: GetContribModuleRequest
    ) -> GetContribModuleResponse:
        """Execute the get contrib_module use case."""
        entity = await self._get_by_id(request.slug)
        return GetContribModuleResponse.of(entity)


class ListContribModulesUseCase(ListUseCase[ContribModule, ContribModuleRepository]):
    """List all ContribModules."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListContribModulesRequest
    ) -> ListContribModulesResponse:
        """Execute the list contrib_modules use case."""
        entities = await self._list_all()
        return ListContribModulesResponse.of(entities)


class CreateContribModuleUseCase(CreateUseCase[ContribModule, ContribModuleRepository]):
    """Create a new ContribModule."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> ContribModule:
        """Construct a ContribModule from a generated ID and request fields."""
        return ContribModule(slug=Slug(entity_id), **kwargs)

    async def execute(
        self, request: CreateContribModuleRequest
    ) -> CreateContribModuleResponse:
        """Execute the create contrib_module use case."""
        entity = await self._create(
            entity_id=request.slug,
            name=request.name,
            description=request.description,
            technology=request.technology,
            code_path=request.code_path,
            solution_slug=request.solution_slug,
            docname=request.docname,
            page_title=request.page_title,
            preamble_rst=request.preamble_rst,
            epilogue_rst=request.epilogue_rst,
        )
        return CreateContribModuleResponse.of(entity)


class UpdateContribModuleUseCase(UpdateUseCase[ContribModule, ContribModuleRepository]):
    """Update a ContribModule."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateContribModuleRequest
    ) -> UpdateContribModuleResponse:
        """Execute the update contrib_module use case."""
        entity = await self._update_by_id(request.slug, request.changes())
        return UpdateContribModuleResponse.of(entity)


class DeleteContribModuleUseCase(DeleteUseCase[ContribModule, ContribModuleRepository]):
    """Delete a ContribModule by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteContribModuleRequest
    ) -> DeleteContribModuleResponse:
        """Execute the delete contrib_module use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteContribModuleResponse(deleted=deleted)
