"""Code-outward documentation for julee solutions.

This kit projects a solution into documentation: its personas, journeys,
epics and stories, its applications and integrations, and the bounded
contexts its code already describes (ADR 006).

It is a viewpoint kit. Its bounded contexts describe a solution rather
than implement part of one, which is why the manifest sets
``viewpoint=True``.

Use it in a solution's ``conf.py``::

    from pathlib import Path

    from julee.core.kits import sphinx_extensions

    extensions = sphinx_extensions(Path(__file__).parent.parent)

which asks the kits the solution has adopted what they provide, rather
than naming this kit's modules. Naming them still works, and is what to
do if a solution wants only some of them::

    extensions = ["julee_viewpoints.sphinx_hcd"]
"""

from julee.core.entities.kit import Kit

kit = Kit(
    slug="viewpoints",
    name="Code-outward documentation",
    package="julee_viewpoints",
    viewpoint=True,
    contributes={
        # One point, three extensions. The order is the order Sphinx
        # loads them in: sphinx_c4 borrows a persona through c4_bridge,
        # which wants the HCD side registered first.
        "sphinx.extension": (
            "julee_viewpoints.sphinx_hcd",
            "julee_viewpoints.sphinx_c4",
            "julee_viewpoints.semantics",
        ),
    },
)

__all__ = ["kit"]
