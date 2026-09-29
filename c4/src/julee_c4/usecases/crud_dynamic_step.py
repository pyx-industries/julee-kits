"""Generated CRUD use cases for DynamicStep.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from julee.core.entities.text import Name, Slug
from julee.core.usecases.generic_crud import (
    CreateUseCase,
    DeleteUseCase,
    GetUseCase,
    ListUseCase,
    UpdateUseCase,
)

from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository

from ..dtos.crud_dynamic_step import (
    CreateDynamicStepRequest,
    CreateDynamicStepResponse,
    DeleteDynamicStepRequest,
    DeleteDynamicStepResponse,
    GetDynamicStepRequest,
    GetDynamicStepResponse,
    ListDynamicStepsRequest,
    ListDynamicStepsResponse,
    UpdateDynamicStepRequest,
    UpdateDynamicStepResponse,
)


class GetDynamicStepUseCase(GetUseCase[DynamicStep, DynamicStepRepository]):
    """Get a DynamicStep by slug."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(self, request: GetDynamicStepRequest) -> GetDynamicStepResponse:
        """Execute the get dynamic_step use case."""
        entity = await self._get_by_id(request.slug)
        return GetDynamicStepResponse.of(entity)


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
        return ListDynamicStepsResponse.of(entities)


class CreateDynamicStepUseCase(CreateUseCase[DynamicStep, DynamicStepRepository]):
    """Create a new DynamicStep."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    def _build_entity(self, entity_id: str, **kwargs: Any) -> DynamicStep:
        """Construct a DynamicStep from a generated ID and request fields.

        A request that names no slug leaves the entity to work
        one out, so the field is left out rather than passed empty.
        """
        if not entity_id:
            return DynamicStep(**kwargs)

        return DynamicStep(slug=Slug(entity_id), **kwargs)

    async def execute(
        self, request: CreateDynamicStepRequest
    ) -> CreateDynamicStepResponse:
        """Execute the create dynamic_step use case."""
        entity = await self._create(
            entity_id=request.slug,
            sequence_name=Name(request.sequence_name),
            step_number=request.step_number,
            source_type=ElementType(request.source_type),
            source_slug=Slug(request.source_slug),
            destination_type=ElementType(request.destination_type),
            destination_slug=Slug(request.destination_slug),
            description=request.description,
            technology=request.technology,
            return_value=request.return_value,
            is_async=request.is_async,
            docname=request.docname,
        )
        return CreateDynamicStepResponse.of(entity)


class UpdateDynamicStepUseCase(UpdateUseCase[DynamicStep, DynamicStepRepository]):
    """Update a DynamicStep."""

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(
        self, request: UpdateDynamicStepRequest
    ) -> UpdateDynamicStepResponse:
        """Execute the update dynamic_step use case."""
        changes = request.changes()
        if changes.get("destination_slug") is not None:
            changes["destination_slug"] = Slug(changes["destination_slug"])
        if changes.get("destination_type") is not None:
            changes["destination_type"] = ElementType(changes["destination_type"])
        if changes.get("sequence_name") is not None:
            changes["sequence_name"] = Name(changes["sequence_name"])
        if changes.get("source_slug") is not None:
            changes["source_slug"] = Slug(changes["source_slug"])
        if changes.get("source_type") is not None:
            changes["source_type"] = ElementType(changes["source_type"])
        entity = await self._update_by_id(request.slug, changes)
        return UpdateDynamicStepResponse.of(entity)


class DeleteDynamicStepUseCase(DeleteUseCase[DynamicStep, DynamicStepRepository]):
    """Delete a DynamicStep by slug.

    Reports whether anything was deleted rather than raising, since
    "it was already gone" is the outcome the caller asked for.
    """

    def __init__(self, repo: DynamicStepRepository) -> None:
        """Initialise with the dynamic_step repository."""
        super().__init__(repo)

    async def execute(
        self, request: DeleteDynamicStepRequest
    ) -> DeleteDynamicStepResponse:
        """Execute the delete dynamic_step use case."""
        deleted = await self._delete_by_id(request.slug)
        return DeleteDynamicStepResponse(deleted=deleted)
