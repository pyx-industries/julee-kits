"""Render what kits claim, and what this solution holds true.

A kit publishes semantics.toml saying how it sees its neighbours. A
solution accepts some of that and adds its own. Both are documentation
as much as configuration — the note on a claim is written for a reader —
so this projects them into the documentation like any other viewpoint.

A separate extension because it belongs to neither viewpoint: claims are
about kits in general, and c4 and hcd are two of them.

Use it in a solution's conf.py::

    extensions = [..., "julee_viewpoints.semantics"]
"""

from pathlib import Path
from typing import Any

from docutils import nodes
from julee.core.entities.claim import Claim
from julee.core.kits import adopted_kits
from julee.core.semantics import kit_claims, load_semantics
from sphinx.util.docutils import SphinxDirective

__all__ = ["SemanticsIndexDirective", "KitClaimsDirective", "setup"]


def solution_root(confdir: str) -> Path | None:
    """The solution a Sphinx project documents.

    Documentation usually lives in a directory of the project rather than
    at its root, so this walks up looking for what makes a directory a
    project.

    Args:
        confdir: Where conf.py is

    Returns:
        The project root, or None if there is no pyproject.toml above
    """
    here = Path(confdir).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "pyproject.toml").exists():
            return candidate
    return None


def _claim_table(claims: list[tuple[str, Claim]], empty: str) -> list[nodes.Node]:
    """Render claims as a table of who says what, and why.

    Args:
        claims: Claims paired with where each came from
        empty: What to say when there are none

    Returns:
        Docutils nodes
    """
    if not claims:
        para = nodes.paragraph()
        para += nodes.emphasis(text=empty)
        return [para]

    table = nodes.table()
    group = nodes.tgroup(cols=4)
    table += group
    for width in (15, 25, 10, 50):
        group += nodes.colspec(colwidth=width)

    head = nodes.thead()
    group += head
    row = nodes.row()
    head += row
    for heading in ("From", "This", "Is", "Of that"):
        entry = nodes.entry()
        entry += nodes.paragraph(text=heading)
        row += entry

    body = nodes.tbody()
    group += body
    for origin, claim in claims:
        row = nodes.row()
        body += row
        for text in (
            origin,
            claim.source.rsplit(".", 1)[-1],
            str(claim.kind).replace("_", " "),
            claim.target.rsplit(".", 1)[-1],
        ):
            entry = nodes.entry()
            entry += nodes.paragraph(text=text)
            row += entry
        if claim.note.strip():
            note_row = nodes.row()
            body += note_row
            entry = nodes.entry(morecols=3)
            entry += nodes.paragraph(text=claim.note.strip())
            note_row += entry

    return [table]


class SemanticsIndexDirective(SphinxDirective):
    """What this solution holds true about how its terms line up.

    Usage::

        .. semantics-index::
    """

    def run(self) -> list[nodes.Node]:
        """Render the solution's resolved claims."""
        root = solution_root(self.env.app.confdir)
        if root is None:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No project found above conf.py")
            return [para]

        try:
            claims = load_semantics(root, adopted_kits(root))
        except ValueError as problem:
            para = nodes.paragraph()
            para += nodes.emphasis(text=f"Semantics could not be read: {problem}")
            return [para]

        return _claim_table(
            [("this solution", claim) for claim in claims],
            "This solution holds nothing about how its terms line up.",
        )


class KitClaimsDirective(SphinxDirective):
    """What the adopted kits claim, whether or not the solution agrees.

    Usage::

        .. kit-claims::
    """

    def run(self) -> list[nodes.Node]:
        """Render every adopted kit's published claims."""
        root = solution_root(self.env.app.confdir)
        if root is None:
            para = nodes.paragraph()
            para += nodes.emphasis(text="No project found above conf.py")
            return [para]

        claims = [
            (kit.slug, claim) for kit in adopted_kits(root) for claim in kit_claims(kit)
        ]
        return _claim_table(claims, "No adopted kit claims anything.")


def setup(app: Any) -> dict[str, Any]:
    """Register the semantics directives."""
    app.add_directive("semantics-index", SemanticsIndexDirective)
    app.add_directive("kit-claims", KitClaimsDirective)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
