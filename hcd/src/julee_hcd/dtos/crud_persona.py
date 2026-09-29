"""Generated CRUD messages for Persona.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.persona import Persona


class PersonaMessage(BaseModel):
    """What a Persona is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    solution_slug: str
    docname: str
    page_title: str
    preamble_rst: str
    epilogue_rst: str
    name: str
    slug: str
    goals: tuple[str, ...]
    frustrations: tuple[str, ...]
    jobs_to_be_done: tuple[str, ...]
    context: str
    app_slugs: tuple[str, ...]
    epic_slugs: tuple[str, ...]
    accelerator_slugs: tuple[str, ...]
    contrib_slugs: tuple[str, ...]

    @classmethod
    def of(cls, entity: Persona) -> "PersonaMessage":
        """The message for one persona."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            name=str(entity.name),
            slug=str(entity.slug),
            goals=entity.goals,
            frustrations=entity.frustrations,
            jobs_to_be_done=entity.jobs_to_be_done,
            context=entity.context,
            app_slugs=tuple(str(item) for item in entity.app_slugs),
            epic_slugs=tuple(str(item) for item in entity.epic_slugs),
            accelerator_slugs=tuple(str(item) for item in entity.accelerator_slugs),
            contrib_slugs=tuple(str(item) for item in entity.contrib_slugs),
        )


class GetPersonaRequest(BaseModel):
    """Request for getting a Persona by slug."""

    slug: str


class GetPersonaResponse(BaseModel):
    """Response for getting a Persona."""

    persona: PersonaMessage

    @classmethod
    def of(cls, entity: Persona) -> "GetPersonaResponse":
        """The response for the persona that was found."""
        return cls(persona=PersonaMessage.of(entity))


class ListPersonasRequest(BaseModel):
    """Request for listing all Personas."""


class ListPersonasResponse(BaseModel):
    """Response for listing all Personas.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    personas: list[PersonaMessage]

    @classmethod
    def of(cls, entities: list[Persona]) -> "ListPersonasResponse":
        """The response for the personas that were found."""
        return cls(personas=[PersonaMessage.of(entity) for entity in entities])


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

    persona: PersonaMessage

    @classmethod
    def of(cls, entity: Persona) -> "CreatePersonaResponse":
        """The response for the persona that was created."""
        return cls(persona=PersonaMessage.of(entity))


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

    persona: PersonaMessage

    @classmethod
    def of(cls, entity: Persona) -> "UpdatePersonaResponse":
        """The response for the persona as it now is."""
        return cls(persona=PersonaMessage.of(entity))


class DeletePersonaRequest(BaseModel):
    """Request for deleting a Persona by slug."""

    slug: str


class DeletePersonaResponse(BaseModel):
    """Response for deleting a Persona."""

    deleted: bool
