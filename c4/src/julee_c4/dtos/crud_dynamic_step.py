"""Generated CRUD messages for DynamicStep.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType


class DynamicStepMessage(BaseModel):
    """What a DynamicStep is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    sequence_name: str
    step_number: int
    source_type: ElementType
    source_slug: str
    destination_type: ElementType
    destination_slug: str
    description: str
    technology: str
    return_value: str
    is_async: bool
    docname: str
    slug: str

    @classmethod
    def of(cls, entity: DynamicStep) -> "DynamicStepMessage":
        """The message for one dynamic_step."""
        return cls(
            sequence_name=str(entity.sequence_name),
            step_number=entity.step_number,
            source_type=entity.source_type,
            source_slug=str(entity.source_slug),
            destination_type=entity.destination_type,
            destination_slug=str(entity.destination_slug),
            description=entity.description,
            technology=entity.technology,
            return_value=entity.return_value,
            is_async=entity.is_async,
            docname=entity.docname,
            slug=str(entity.slug),
        )


class GetDynamicStepRequest(BaseModel):
    """Request for getting a DynamicStep by slug."""

    slug: str


class GetDynamicStepResponse(BaseModel):
    """Response for getting a DynamicStep."""

    dynamic_step: DynamicStepMessage

    @classmethod
    def of(cls, entity: DynamicStep) -> "GetDynamicStepResponse":
        """The response for the dynamic_step that was found."""
        return cls(dynamic_step=DynamicStepMessage.of(entity))


class ListDynamicStepsRequest(BaseModel):
    """Request for listing all DynamicSteps."""


class ListDynamicStepsResponse(BaseModel):
    """Response for listing all DynamicSteps.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    dynamic_steps: list[DynamicStepMessage]

    @classmethod
    def of(cls, entities: list[DynamicStep]) -> "ListDynamicStepsResponse":
        """The response for the dynamic_steps that were found."""
        return cls(dynamic_steps=[DynamicStepMessage.of(entity) for entity in entities])


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

    dynamic_step: DynamicStepMessage

    @classmethod
    def of(cls, entity: DynamicStep) -> "CreateDynamicStepResponse":
        """The response for the dynamic_step that was created."""
        return cls(dynamic_step=DynamicStepMessage.of(entity))


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

    dynamic_step: DynamicStepMessage

    @classmethod
    def of(cls, entity: DynamicStep) -> "UpdateDynamicStepResponse":
        """The response for the dynamic_step as it now is."""
        return cls(dynamic_step=DynamicStepMessage.of(entity))


class DeleteDynamicStepRequest(BaseModel):
    """Request for deleting a DynamicStep by slug."""

    slug: str


class DeleteDynamicStepResponse(BaseModel):
    """Response for deleting a DynamicStep."""

    deleted: bool
