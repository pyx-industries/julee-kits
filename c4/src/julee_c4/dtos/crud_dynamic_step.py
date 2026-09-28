"""Generated CRUD messages for DynamicStep.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.dynamic_step import DynamicStep, ElementType


class GetDynamicStepRequest(BaseModel):
    """Request for getting a DynamicStep by slug."""

    slug: str


class GetDynamicStepResponse(BaseModel):
    """Response for getting a DynamicStep."""

    dynamic_step: DynamicStep


class ListDynamicStepsRequest(BaseModel):
    """Request for listing all DynamicSteps."""


class ListDynamicStepsResponse(BaseModel):
    """Response for listing all DynamicSteps."""

    dynamic_steps: list[DynamicStep]
    total_count: int


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
    docname: str = ""


class CreateDynamicStepResponse(BaseModel):
    """Response for creating a DynamicStep."""

    dynamic_step: DynamicStep


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
    docname: str | None = None

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateDynamicStepResponse(BaseModel):
    """Response for updating a DynamicStep."""

    dynamic_step: DynamicStep


class DeleteDynamicStepRequest(BaseModel):
    """Request for deleting a DynamicStep by slug."""

    slug: str


class DeleteDynamicStepResponse(BaseModel):
    """Response for deleting a DynamicStep."""

    deleted: bool
