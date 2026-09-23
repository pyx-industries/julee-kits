"""Contrib module domain model.

A contrib module is a reusable utility a solution picks up — a polling
workflow, an authentication helper — as against an accelerator, which is
a way of thinking about a problem. The difference is that a solution runs
a contrib module and reasons with an accelerator.
"""

from pydantic import Field, field_validator

from .base import Authored


class ContribModule(Authored):
    """A reusable utility a solution uses."""

    slug: str = Field(description="Identifier for the contrib module")
    name: str = Field(
        default="", description="Display name; derived from slug if blank"
    )
    description: str = Field(default="", description="What the module does")
    technology: str = Field(
        default="Python", description="What the module is built with"
    )
    code_path: str = Field(
        default="", description="Where the module's code lives in the repository"
    )

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """A contrib module without a slug cannot be referred to."""
        if not v or not v.strip():
            raise ValueError("slug cannot be empty")
        return v.strip()

    @property
    def display_title(self) -> str:
        """What to call the module, falling back to a readable slug."""
        return self.name if self.name else self.slug.replace("-", " ").title()

    @property
    def c4_description(self) -> str:
        """What to write on the module's box in a diagram."""
        return self.description if self.description else f"{self.display_title} utility"
