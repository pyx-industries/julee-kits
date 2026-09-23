"""Generated CRUD use cases for ContribModule.

Do not edit — regenerate with make generate-crud.
"""

from typing import Any

from julee.core.usecases.generic_crud import (
    CreateUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)
from pydantic import BaseModel

from julee_hcd.domain.models.contrib import ContribModule
from julee_hcd.domain.repositories.contrib import ContribRepository

ContribModuleRepository = ContribRepository


class GetContribModuleRequest(BaseModel):
    """Request for getting a ContribModule by slug."""

    slug: str


class GetContribModuleResponse(BaseModel):
    """Response for getting a ContribModule."""

    contrib_module: ContribModule


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
        return GetContribModuleResponse(contrib_module=entity)


class ListContribModulesRequest(BaseModel):
    """Request for listing all ContribModules."""


class ListContribModulesResponse(BaseModel):
    """Response for listing all ContribModules."""

    contrib_modules: list[ContribModule]
    total_count: int


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
        return ListContribModulesResponse(
            contrib_modules=entities, total_count=len(entities)
        )


class CreateContribModuleRequest(BaseModel):
    """Request for creating a ContribModule."""

    slug: str
    name: str = ""
    description: str = ""
    technology: str = "Python"
    code_path: str = ""
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreateContribModuleResponse(BaseModel):
    """Response for creating a ContribModule."""

    contrib_module: ContribModule


class CreateContribModuleUseCase(CreateUseCase[ContribModule, ContribModuleRepository]):
    """Create a new ContribModule."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> ContribModule:
        """Construct a ContribModule from a generated ID and request fields."""
        return ContribModule(slug=entity_id, **kwargs)

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
        return CreateContribModuleResponse(contrib_module=entity)


class UpdateContribModuleRequest(BaseModel):
    """Request for updating a ContribModule.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    description: str | None = None
    technology: str | None = None
    code_path: str | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None


class UpdateContribModuleResponse(BaseModel):
    """Response for updating a ContribModule."""

    contrib_module: ContribModule


class UpdateContribModuleUseCase(UpdateUseCase[ContribModule, ContribModuleRepository]):
    """Update a ContribModule."""

    def __init__(self, repo: ContribModuleRepository) -> None:
        """Initialise with the contrib_module repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateContribModuleRequest
    ) -> UpdateContribModuleResponse:
        """Execute the update contrib_module use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateContribModuleResponse(contrib_module=entity)
