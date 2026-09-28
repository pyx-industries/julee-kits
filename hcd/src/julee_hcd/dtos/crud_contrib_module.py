"""Generated CRUD messages for ContribModule.

Do not edit — regenerate with generate-crud.sh.
"""

from typing import Any

from pydantic import BaseModel

from julee_hcd.domain.models.contrib import ContribModule


class GetContribModuleRequest(BaseModel):
    """Request for getting a ContribModule by slug."""

    slug: str


class GetContribModuleResponse(BaseModel):
    """Response for getting a ContribModule."""

    contrib_module: ContribModule


class ListContribModulesRequest(BaseModel):
    """Request for listing all ContribModules."""


class ListContribModulesResponse(BaseModel):
    """Response for listing all ContribModules."""

    contrib_modules: list[ContribModule]
    total_count: int


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
        return self.model_dump(exclude={"slug"}, exclude_unset=True)


class UpdateContribModuleResponse(BaseModel):
    """Response for updating a ContribModule."""

    contrib_module: ContribModule


class DeleteContribModuleRequest(BaseModel):
    """Request for deleting a ContribModule by slug."""

    slug: str


class DeleteContribModuleResponse(BaseModel):
    """Response for deleting a ContribModule."""

    deleted: bool
