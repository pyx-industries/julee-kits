"""Entity relationship graph directive.

Renders a diagram of how this kit's HCD entities relate to each other.

Upstream (``apps/sphinx/shared/directives/entity_graph.py``) built this
graph by introspecting ``@semantic_relation`` declarations through a
``RelationTraversal`` service reading a semantic-relation registry. That
registry is being redesigned and must not come back through this port, so
this directive instead renders a small, fixed table describing the
relations this kit's own directives declare - Story is part of the App
its feature file belongs to, Epic contains the Stories named by
``epic-story``, and so on. It is not introspected from decorators; it is
just what the directives in this kit actually do, written down once.
"""

from docutils import nodes
from sphinx.util.docutils import SphinxDirective

# The edges this graph draws, written down by hand.
#
# Every one of them is already in the models: Persona.app_slugs holds the
# first, Epic.story_refs the third, and so on. The table exists because
# nothing yet reads those fields and works the graph out, and it should go
# when something does. It is not the cross-kit semantics file: that says
# how this kit's terms line up with another kit's, which no field here can
# express. This is the shape of one kit's own model.
HCD_ENTITY_EDGES: tuple[tuple[str, str, str], ...] = (
    ("Story", "part_of", "App"),
    ("Story", "references", "Persona"),
    ("Epic", "contains", "Story"),
    ("Journey", "contains", "Story"),
    ("Journey", "contains", "Epic"),
    ("Journey", "references", "Persona"),
    ("App", "uses", "Accelerator"),
    ("Accelerator", "uses", "Integration"),
    ("Accelerator", "depends_on", "Accelerator"),
    ("Persona", "uses", "App"),
    ("Persona", "uses", "Accelerator"),
    ("Persona", "uses", "Contrib"),
)

_NODE_STYLES = {
    "Story": "hcd",
    "Epic": "hcd",
    "Journey": "hcd",
    "Persona": "hcd",
    "App": "viewpoint",
    "Accelerator": "viewpoint",
    "Integration": "viewpoint",
    "Contrib": "viewpoint",
}

_ARROWS = {
    "part_of": "-.->",
    "contains": "==>",
    "references": "-.->",
    "uses": "-->",
    "depends_on": "-->",
}

_RELATION_DESCRIPTIONS = {
    "part_of": "Entity is contained within another",
    "contains": "Entity aggregates others",
    "references": "Non-owning reference",
    "uses": "Entity draws on another",
    "depends_on": "Entity requires another",
}


class EntityGraphDirective(SphinxDirective):
    """Render this kit's HCD entity relationship graph.

    Usage::

        .. entity-graph::

    Options::

        :format: mermaid (default) or table
    """

    has_content = False
    option_spec = {
        "format": lambda x: x.lower() if x else "mermaid",
    }

    def run(self) -> list[nodes.Node]:
        fmt = self.options.get("format", "mermaid")
        if fmt == "table":
            return self._render_table()
        if not self._mermaid_available():
            # This kit does not depend on sphinxcontrib-mermaid, so a
            # solution that has not added it itself would otherwise get an
            # "Unknown directive" error from docutils. Degrade the same way
            # the PlantUML-based directives degrade when their extension is
            # absent, rather than failing the build.
            return self._render_table()
        return self._render_mermaid()

    @staticmethod
    def _mermaid_available() -> bool:
        try:
            import sphinxcontrib.mermaid  # noqa: F401
        except ImportError:
            return False
        return True

    def _render_mermaid(self) -> list[nodes.Node]:
        """Render the edges as a Mermaid diagram."""
        node_ids = sorted({s for s, _, _ in HCD_ENTITY_EDGES}) + sorted(
            {
                t
                for _, _, t in HCD_ENTITY_EDGES
                if t not in {s for s, _, _ in HCD_ENTITY_EDGES}
            }
        )

        lines = [
            ".. mermaid::",
            "",
            "    graph LR",
            "        %% HCD entity relationships (fixed, see module docstring)",
            "",
            "        classDef hcd fill:#f3e5f5,stroke:#7b1fa2",
            "        classDef viewpoint fill:#e8f5e9,stroke:#2e7d32",
            "",
        ]
        for node_id in node_ids:
            style = _NODE_STYLES.get(node_id, "hcd")
            lines.append(f"        {node_id}[{node_id}]:::{style}")

        lines.append("")
        for source, relation, target in HCD_ENTITY_EDGES:
            arrow = _ARROWS.get(relation, "-->")
            lines.append(f"        {source} {arrow}|{relation}| {target}")

        rst_content = "\n".join(lines)
        return list(self.parse_text_to_nodes(rst_content))

    def _render_table(self) -> list[nodes.Node]:
        """Render the relation table as an RST list-table."""
        rst_lines = [
            ".. list-table::",
            "   :header-rows: 1",
            "   :widths: 25 25 25 25",
            "",
            "   * - Source",
            "     - Relation",
            "     - Target",
            "     - Description",
        ]

        for source, relation, target in HCD_ENTITY_EDGES:
            desc = _RELATION_DESCRIPTIONS.get(relation, "")
            rst_lines.extend(
                [
                    f"   * - {source}",
                    f"     - {relation}",
                    f"     - {target}",
                    f"     - {desc}",
                ]
            )

        rst_content = "\n".join(rst_lines)
        return list(self.parse_text_to_nodes(rst_content))


def setup(app):
    """Register the directive, for use as a standalone extension."""
    app.add_directive("entity-graph", EntityGraphDirective)

    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
