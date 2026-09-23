"""Generated CRUD use cases for DynamicStep.

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

from julee_c4.domain.models.dynamic_step import DynamicStep, ElementType
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository


class GetDynamicStepRequest(BaseModel):
    """Request for getting a DynamicStep by slug."""

    slug: str


class GetDynamicStepResponse(BaseModel):
    """Response for getting a DynamicStep."""

    dynamic_step: DynamicStep


class GetDynamicStepUseCase(GetUseCase[DynamicStep, DynamicStepRepository]):
    """Get a DynamicStep by slug."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(self, request: GetDynamicStepRequest) -> GetDynamicStepResponse:
        """Execute the get dynamic_step use case."""
        entity = await self._get_by_id(request.slug)
        return GetDynamicStepResponse(dynamic_step=entity)


class ListDynamicStepsRequest(BaseModel):
    """Request for listing all DynamicSteps."""


class ListDynamicStepsResponse(BaseModel):
    """Response for listing all DynamicSteps."""

    dynamic_steps: list[DynamicStep]
    total_count: int


class ListDynamicStepsUseCase(ListUseCase[DynamicStep, DynamicStepRepository]):
    """List all DynamicSteps."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(
        self, request: ListDynamicStepsRequest
    ) -> ListDynamicStepsResponse:
        """Execute the list dynamic_steps use case."""
        entities = await self._list_all()
        return ListDynamicStepsResponse(
            dynamic_steps=entities, total_count=len(entities)
        )


class CreateDynamicStepRequest(BaseModel):
    """Request for creating a DynamicStep."""

    slug: str = ""
    sequence_name: str
    step_number: int
    source_type: ElementType
    source_slug: str
    destination_type: ElementType
    destination_slug: str
    description: str = ""
    technology: str = ""
    return_value: str = ""
    is_async: bool = False
    tags: tuple[str, ...] = ()
    docname: str = ""


class CreateDynamicStepResponse(BaseModel):
    """Response for creating a DynamicStep."""

    dynamic_step: DynamicStep


class CreateDynamicStepUseCase(CreateUseCase[DynamicStep, DynamicStepRepository]):
    """Create a new DynamicStep."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> DynamicStep:
        """Construct a DynamicStep from a generated ID and request fields."""
        return DynamicStep(slug=entity_id, **kwargs)

    async def execute(
        self, request: CreateDynamicStepRequest
    ) -> CreateDynamicStepResponse:
        """Execute the create dynamic_step use case."""
        entity = await self._create(
            entity_id=request.slug,
            sequence_name=request.sequence_name,
            step_number=request.step_number,
            source_type=request.source_type,
            source_slug=request.source_slug,
            destination_type=request.destination_type,
            destination_slug=request.destination_slug,
            description=request.description,
            technology=request.technology,
            return_value=request.return_value,
            is_async=request.is_async,
            tags=request.tags,
            docname=request.docname,
        )
        return CreateDynamicStepResponse(dynamic_step=entity)


class UpdateDynamicStepRequest(BaseModel):
    """Request for updating a DynamicStep.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    sequence_name: str | None = None
    step_number: int | None = None
    source_type: ElementType | None = None
    source_slug: str | None = None
    destination_type: ElementType | None = None
    destination_slug: str | None = None
    description: str | None = None
    technology: str | None = None
    return_value: str | None = None
    is_async: bool | None = None
    tags: tuple[str, ...] | None = None
    docname: str | None = None


class UpdateDynamicStepResponse(BaseModel):
    """Response for updating a DynamicStep."""

    dynamic_step: DynamicStep


class UpdateDynamicStepUseCase(UpdateUseCase[DynamicStep, DynamicStepRepository]):
    """Update a DynamicStep."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateDynamicStepRequest
    ) -> UpdateDynamicStepResponse:
        """Execute the update dynamic_step use case."""
        entity = await self._update_by_id(
            request.slug,
            request.model_dump(exclude={"slug"}, exclude_unset=True),
        )
        return UpdateDynamicStepResponse(dynamic_step=entity)
