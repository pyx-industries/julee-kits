"""Contrib module domain model.

A contrib module is a reusable utility a solution picks up — a polling
workflow, an authentication helper — as against an accelerator, which is
a way of thinking about a problem. The difference is that a solution runs
a contrib module and reasons with an accelerator.
"""

from dataclasses import dataclass

from julee.core.entities.text import Slug

from .base import Authored


@dataclass(frozen=True, kw_only=True)
class ContribModule(Authored):
    """A reusable utility a solution uses."""

    slug: Slug
    """Identifier for the contrib module."""

    name: str = ""
    """Display name; derived from slug if blank."""

    description: str = ""
    """What the module does."""

    technology: str = "Python"
    """What the module is built with."""

    code_path: str = ""
    """Where the module's code lives in the repository."""

    @property
    def display_title(self) -> str:
        """What to call the module, falling back to a readable slug."""
        return self.name if self.name else self.slug.replace("-", " ").title()

    @property
    def c4_description(self) -> str:
        """What to write on the module's box in a diagram."""
        return self.description if self.description else f"{self.display_title} utility"
