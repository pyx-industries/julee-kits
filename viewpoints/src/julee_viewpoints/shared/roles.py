"""Sphinx roles for cross-referencing domain entities.

Provides role factories for creating inline cross-references, e.g.::

    PersonaRole = make_page_role("users/personas/{slug}")
    app.add_role("persona", PersonaRole())

    StoryRole = make_anchor_role(lookup_story)
    app.add_role("story", StoryRole())

Note on what did *not* come back here
--------------------------------------
Upstream (``apps/sphinx/shared/roles.py``) also had a ``make_semantic_role``
that resolved a role by walking ``@semantic_relation`` declarations through a
``DocumentationMapping`` / semantic-relation registry (PROJECTS, PART_OF,
...). That registry is being redesigned and must not come back through this
port. Every HCD role that upstream built with ``make_semantic_role`` is
wired up directly in ``sphinx_hcd``'s ``setup()`` instead, using
``make_anchor_role`` with a small lookup function against the entity's own
repository - the same outcome, without any relation introspection.
"""

import re
from collections.abc import Callable
from typing import TYPE_CHECKING

from docutils import nodes
from sphinx.util.docutils import SphinxRole

from . import build_relative_uri

if TYPE_CHECKING:
    from sphinx.application import Sphinx


class EntityRefRole(SphinxRole):
    """Base role for entity cross-references.

    Provides:
    - Parsing of `Title <slug>` or `slug` syntax
    - Relative URI building
    - Dangling reference tolerance
    """

    def parse_target(self) -> tuple[str, str]:
        """Parse role content into (title, slug).

        Supports:
        - `slug` -> (title_from_slug, slug)
        - `Title <slug>` -> (Title, slug)
        """
        text = self.text.strip()

        match = re.match(r"^(.+?)\s*<([^>]+)>$", text)
        if match:
            title = match.group(1).strip()
            slug = match.group(2).strip()
            return title, slug

        slug = text
        title = slug.replace("-", " ").replace("_", " ").title()
        return title, slug

    def build_uri(self, target_doc: str, anchor: str | None = None) -> str:
        """Build relative URI from current document to target."""
        return build_relative_uri(self.env.docname, target_doc, anchor)

    def make_ref_node(self, title: str, uri: str) -> nodes.reference:
        """Create reference node with title and URI."""
        ref = nodes.reference("", "", refuri=uri)
        ref += nodes.Text(title)
        return ref

    def run(self) -> tuple[list[nodes.Node], list[nodes.system_message]]:
        """Execute role - subclasses should override resolve()."""
        title, slug = self.parse_target()
        uri = self.resolve(slug)
        return [self.make_ref_node(title, uri)], []

    def resolve(self, slug: str) -> str:
        """Resolve slug to URI - subclasses must implement."""
        raise NotImplementedError


def make_autoapi_role(path_pattern: str) -> type[SphinxRole]:
    """Create role that resolves to autoapi page.

    Args:
        path_pattern: Pattern with {slug} placeholder
                      e.g., "autoapi/julee/{slug}/index"

    Returns:
        Role class for registration
    """

    class AutoapiRole(EntityRefRole):
        """Role resolving to autoapi page."""

        def resolve(self, slug: str) -> str:
            target_doc = path_pattern.format(slug=slug)
            return self.build_uri(target_doc)

    return AutoapiRole


def make_page_role(page_pattern: str) -> type[SphinxRole]:
    """Create role that resolves to a dedicated page.

    Args:
        page_pattern: Pattern with {slug} placeholder
                      e.g., "users/personas/{slug}"

    Returns:
        Role class for registration

    Example:
        PersonaRole = make_page_role("users/personas/{slug}")
        app.add_role("persona", PersonaRole())
    """

    class PageRole(EntityRefRole):
        """Role resolving to dedicated page."""

        def resolve(self, slug: str) -> str:
            target_doc = page_pattern.format(slug=slug)
            return self.build_uri(target_doc)

    return PageRole


def make_anchor_role(
    lookup_func: Callable[[str, "Sphinx"], tuple[str, str] | None],
) -> type[SphinxRole]:
    """Create role that resolves to an anchor in another page.

    Args:
        lookup_func: Function(slug, app) -> (docname, anchor) or None
                     Called to resolve entity location. Pass an empty
                     string for the anchor when the target is a whole page
                     rather than an anchor within one.

    Returns:
        Role class for registration

    Example:
        def lookup_story(slug, app):
            story = get_story(app, slug)
            if story:
                return (f"users/stories/{story.app_slug}", f"story-{slug}")
            return None

        StoryRole = make_anchor_role(lookup_story)
        app.add_role("story", StoryRole())
    """

    class AnchorRole(EntityRefRole):
        """Role resolving to anchor in another page."""

        def resolve(self, slug: str) -> str:
            location = lookup_func(slug, self.env.app)
            if location:
                docname, anchor = location
                return self.build_uri(docname, anchor or None)
            # Dangling ref - just return anchor
            return f"#{slug}"

    return AnchorRole


def make_conditional_role(
    lookup_func: Callable[[str, "Sphinx"], str | tuple[str, str] | None],
) -> type[SphinxRole]:
    """Create role that conditionally resolves based on lookup result.

    The lookup function can return:
    - str: Direct target docname (no anchor)
    - tuple[str, str]: (docname, anchor)
    - None: Entity not found (dangling ref)

    This is useful for entities that can map to more than one kind of
    target depending on how they were defined.

    Args:
        lookup_func: Function(slug, app) -> docname | (docname, anchor) | None

    Returns:
        Role class for registration
    """

    class ConditionalRole(EntityRefRole):
        """Role with conditional resolution logic."""

        def resolve(self, slug: str) -> str:
            result = lookup_func(slug, self.env.app)
            if result is None:
                return f"#{slug}"
            if isinstance(result, str):
                return self.build_uri(result)
            docname, anchor = result
            return self.build_uri(docname, anchor)

    return ConditionalRole


__all__ = [
    "EntityRefRole",
    "make_autoapi_role",
    "make_page_role",
    "make_anchor_role",
    "make_conditional_role",
]
