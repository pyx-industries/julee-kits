"""Relationship directive for sphinx_c4.

Provides the ``define-relationship`` directive, which records a
Relationship between two C4 elements and renders it inline as a one-line
summary where it is defined.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.models.relationship import Relationship

from .base import C4Directive, parse_element_ref


class DefineRelationshipDirective(C4Directive):
    """Define a relationship between C4 elements.

    Usage::

        .. define-relationship::
           :from: person:customer
           :to: system:banking-system
           :description: Views balances, makes payments
           :technology: HTTPS

        .. define-relationship::
           :from: container:api-app
           :to: container:database
           :description: Reads/writes data
           :technology: SQL/TCP
    """

    has_content = False
    option_spec = {
        "from": directives.unchanged_required,
        "to": directives.unchanged_required,
        "description": directives.unchanged,
        "technology": directives.unchanged,
        "bidirectional": directives.flag,
        "tags": directives.unchanged,
        "hidden": directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        from_ref = self.options.get("from", "")
        to_ref = self.options.get("to", "")
        description = self.options.get("description", "Uses")
        technology = self.options.get("technology", "")
        bidirectional = "bidirectional" in self.options
        tags_str = self.options.get("tags", "")
        tags = tuple(t.strip() for t in tags_str.split(",") if t.strip())
        hidden = "hidden" in self.options

        source_type, source_slug = parse_element_ref(from_ref)
        dest_type, dest_slug = parse_element_ref(to_ref)

        # Slug is left blank - Relationship derives it from source/destination.
        relationship = Relationship(
            source_type=source_type,
            source_slug=source_slug,
            destination_type=dest_type,
            destination_slug=dest_slug,
            description=description,
            technology=technology,
            bidirectional=bidirectional,
            tags=tags,
            docname=self.docname,
        )
        self.c4_context.relationship_repo.save(relationship)

        if hidden:
            return []

        result_nodes: list[nodes.Node] = []

        para = nodes.paragraph()
        para += nodes.strong(text=source_slug)
        para += nodes.Text(" <-> " if bidirectional else " -> ")
        para += nodes.strong(text=dest_slug)
        para += nodes.Text(f": {description}")
        if technology:
            para += nodes.Text(f" [{technology}]")

        result_nodes.append(para)
        return result_nodes
