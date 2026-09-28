"""Generated CRUD messages for Persona.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.persona import Persona


class GetPersonaRequest(BaseModel):
    """Request for getting a Persona by slug."""

    slug: str


class GetPersonaResponse(BaseModel):
    """Response for getting a Persona."""

    persona: Persona


class ListPersonasRequest(BaseModel):
    """Request for listing all Personas."""


class ListPersonasResponse(BaseModel):
    """Response for listing all Personas."""

    personas: list[Persona]
    total_count: int


class CreatePersonaRequest(BaseModel):
    """Request for creating a Persona."""

    slug: str = ""
    name: str
    goals: tuple[str, ...] = ()
    frustrations: tuple[str, ...] = ()
    jobs_to_be_done: tuple[str, ...] = ()
    context: str = ""
    app_slugs: tuple[str, ...] = ()
    epic_slugs: tuple[str, ...] = ()
    accelerator_slugs: tuple[str, ...] = ()
    contrib_slugs: tuple[str, ...] = ()
    solution_slug: str = ""
    docname: str = ""
    page_title: str = ""
    preamble_rst: str = ""
    epilogue_rst: str = ""


class CreatePersonaResponse(BaseModel):
    """Response for creating a Persona."""

    persona: Persona


class UpdatePersonaRequest(BaseModel):
    """Request for updating a Persona.

    Every field but slug is optional: name the ones to change and the
    rest are left as they are.
    """

    slug: str
    name: str | None = None
    goals: tuple[str, ...] | None = None
    frustrations: tuple[str, ...] | None = None
    jobs_to_be_done: tuple[str, ...] | None = None
    context: str | None = None
    app_slugs: tuple[str, ...] | None = None
    epic_slugs: tuple[str, ...] | None = None
    accelerator_slugs: tuple[str, ...] | None = None
    contrib_slugs: tuple[str, ...] | None = None
    solution_slug: str | None = None
    docname: str | None = None
    page_title: str | None = None
    preamble_rst: str | None = None
    epilogue_rst: str | None = None

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdatePersonaResponse(BaseModel):
    """Response for updating a Persona."""

    persona: Persona


class DeletePersonaRequest(BaseModel):
    """Request for deleting a Persona by slug."""

    slug: str


class DeletePersonaResponse(BaseModel):
    """Response for deleting a Persona."""

    deleted: bool
