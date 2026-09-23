"""Base directive for C4 Sphinx directives.

Provides common functionality for accessing the C4 context and building
docutils nodes shared by the define-*, diagram, and index directives.
"""

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

from julee_c4.domain.models.relationship import ElementType

from ..context import C4Context, get_c4_context

_ELEMENT_TYPE_PREFIXES = {
    "person": ElementType.PERSON,
    "system": ElementType.SOFTWARE_SYSTEM,
    "container": ElementType.CONTAINER,
    "component": ElementType.COMPONENT,
}


def parse_element_ref(ref: str) -> tuple[ElementType, str]:
    """Split an element reference like ``container:api-app`` into its parts.

    Args:
        ref: Element reference, e.g. ``person:customer`` or ``system:banking``

    Returns:
        The element's type and slug. A reference with no ``type:`` prefix
        is treated as a software system, matching a bare ``banking-system``.
    """
    if ":" in ref:
        type_str, slug = ref.split(":", 1)
        return (
            _ELEMENT_TYPE_PREFIXES.get(type_str.lower(), ElementType.SOFTWARE_SYSTEM),
            slug,
        )
    return ElementType.SOFTWARE_SYSTEM, ref


class C4Directive(SphinxDirective):
    """Base directive for C4 elements.

    Provides common utilities for building docutils nodes and accessing
    the repositories on ``C4Context``.
    """

    @property
    def docname(self) -> str:
        """Get the current document name."""
        docname: str = self.env.docname
        return docname

    @property
    def c4_context(self) -> C4Context:
        """Get the C4Context for this build.

        Raises:
            RuntimeError: If the context has not been created yet, which
                means ``julee_viewpoints.sphinx_c4`` was not registered as
                a Sphinx extension.
        """
        context = get_c4_context(self.env.app)
        if context is None:
            raise RuntimeError(
                "C4 context is not initialized; is "
                "'julee_viewpoints.sphinx_c4' registered as a Sphinx "
                "extension?"
            )
        return context

    def empty_result(self, message: str) -> list[nodes.Node]:
        """Create an emphasized message for empty results."""
        para = nodes.paragraph()
        para += nodes.emphasis(text=message)
        return [para]

    def warning_node(self, message: str) -> nodes.paragraph:
        """Create a warning paragraph."""
        para = nodes.paragraph()
        para += nodes.problematic(text=f"[{message}]")
        return para

    def make_title(self, text: str, level: int = 2) -> nodes.title:
        """Create a title node.

        Args:
            text: Title text
            level: Heading level (1-6)

        Returns:
            Title node
        """
        return nodes.title(text=text)

    def make_paragraph(self, text: str) -> nodes.paragraph:
        """Create a paragraph node.

        Args:
            text: Paragraph text

        Returns:
            Paragraph node
        """
        para = nodes.paragraph()
        para += nodes.Text(text)
        return para

    def make_field(self, name: str, value: str) -> nodes.paragraph:
        """Create a field paragraph with bold name.

        Args:
            name: Field name
            value: Field value

        Returns:
            Paragraph node with bold name
        """
        para = nodes.paragraph()
        para += nodes.strong(text=f"{name}: ")
        para += nodes.Text(value)
        return para
