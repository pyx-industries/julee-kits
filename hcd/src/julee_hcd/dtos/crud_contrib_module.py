"""Generated CRUD messages for ContribModule.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.contrib import ContribModule


class ContribModuleMessage(BaseModel):
    """What a ContribModule is, as a use case reports it.

    Built from the entity and never holding one. A checked string goes
    out as str, a value object rides inside as it is, and an enum stays
    what it was.
    """

    solution_slug: str
    docname: str
    page_title: str
    preamble_rst: str
    epilogue_rst: str
    slug: str
    name: str
    description: str
    technology: str
    code_path: str

    @classmethod
    def of(cls, entity: ContribModule) -> "ContribModuleMessage":
        """The message for one contrib_module."""
        return cls(
            solution_slug=entity.solution_slug,
            docname=entity.docname,
            page_title=entity.page_title,
            preamble_rst=entity.preamble_rst,
            epilogue_rst=entity.epilogue_rst,
            slug=str(entity.slug),
            name=entity.name,
            description=entity.description,
            technology=entity.technology,
            code_path=entity.code_path,
        )


class GetContribModuleRequest(BaseModel):
    """Request for getting a ContribModule by slug."""

    slug: str


class GetContribModuleResponse(BaseModel):
    """Response for getting a ContribModule."""

    contrib_module: ContribModuleMessage

    @classmethod
    def of(cls, entity: ContribModule) -> "GetContribModuleResponse":
        """The response for the contrib_module that was found."""
        return cls(contrib_module=ContribModuleMessage.of(entity))


class ListContribModulesRequest(BaseModel):
    """Request for listing all ContribModules."""


class ListContribModulesResponse(BaseModel):
    """Response for listing all ContribModules.

    The list and nothing else. Paging is a thing HTTP cares about, so
    a router that needs a page and a count wraps this; a caller in the
    same process does not.
    """

    contrib_modules: list[ContribModuleMessage]

    @classmethod
    def of(cls, entities: list[ContribModule]) -> "ListContribModulesResponse":
        """The response for the contrib_modules that were found."""
        return cls(
            contrib_modules=[ContribModuleMessage.of(entity) for entity in entities]
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

    contrib_module: ContribModuleMessage

    @classmethod
    def of(cls, entity: ContribModule) -> "CreateContribModuleResponse":
        """The response for the contrib_module that was created."""
        return cls(contrib_module=ContribModuleMessage.of(entity))


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

    def changes(self) -> dict[str, Any]:
        """The fields the caller named, without the slug.

        Which fields a caller named is a pydantic question — it is the
        difference between a field left out and one set to its default
        — so the message answers it. A use case asks for the changes
        and never learns how they were worked out.
        """
        return {
            name: getattr(self, name)
            for name in self.model_fields_set
            if name != "slug"
        }


class UpdateContribModuleResponse(BaseModel):
    """Response for updating a ContribModule."""

    contrib_module: ContribModuleMessage

    @classmethod
    def of(cls, entity: ContribModule) -> "UpdateContribModuleResponse":
        """The response for the contrib_module as it now is."""
        return cls(contrib_module=ContribModuleMessage.of(entity))


class DeleteContribModuleRequest(BaseModel):
    """Request for deleting a ContribModule by slug."""

    slug: str


class DeleteContribModuleResponse(BaseModel):
    """Response for deleting a ContribModule."""

    deleted: bool
