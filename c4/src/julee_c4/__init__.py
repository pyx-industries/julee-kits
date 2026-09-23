"""C4 architecture models.

A julee kit. It holds the C4 model — software systems, containers,
components, the relationships between them, deployment nodes and dynamic
steps — and the queries that assemble those into the six C4 diagrams.

It describes how a system is built rather than what business it is in, so
it carries no domain of its own. julee-viewpoints renders what a solution
declares here into its documentation.

Install it, then adopt it::

    [tool.julee]
    kits = ["c4"]
"""

from julee.core.entities.kit import Kit

kit = Kit(
    slug="c4",
    name="C4 architecture models",
    package="julee_c4",
    viewpoint=True,
)

__all__ = ["kit"]
