"""Software system directive for sphinx_c4.

Provides the ``define-software-system`` directive, which records a
SoftwareSystem in the C4 context and renders it inline where it is defined.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.models.software_system import SoftwareSystem, SystemType

from .base import C4Directive


class DefineSoftwareSystemDirective(C4Directive):
    """Define a software system in the C4 model.

    Usage::

        .. define-software-system:: banking-system
           :name: Internet Banking System
           :type: internal
           :owner: Digital Team
           :technology: Java, Spring Boot

           Allows customers to view balances and make payments.
    """

    required_arguments = 1
    has_content = True
    option_spec = {
        "name": directives.unchanged_required,
        "type": directives.unchanged,
        "owner": directives.unchanged,
        "technology": directives.unchanged,
        "url": directives.unchanged,
        "tags": directives.unchanged,
        "hidden": directives.flag,
    }

    def run(self) -> list[nodes.Node]:
        slug = self.arguments[0]
        name = self.options.get("name", slug.replace("-", " ").title())
        system_type = SystemType(self.options.get("type", "internal"))
        owner = self.options.get("owner", "")
        technology = self.options.get("technology", "")
        url = self.options.get("url", "")
        tags_str = self.options.get("tags", "")
        tags = tuple(t.strip() for t in tags_str.split(",") if t.strip())
        description = "\n".join(self.content).strip()
        hidden = "hidden" in self.options

        system = SoftwareSystem(
            slug=slug,
            name=name,
            description=description,
            system_type=system_type,
            owner=owner,
            technology=technology,
            url=url,
            tags=tags,
            docname=self.docname,
        )
        self.c4_context.software_system_repo.save(system)

        # If hidden, register only - no output.
        if hidden:
            return []

        result_nodes: list[nodes.Node] = []

        section = nodes.section(ids=[slug])
        section += nodes.title(text=name)

        if description:
            section += self.make_paragraph(description)

        section += self.make_field("Type", system_type.value)
        if owner:
            section += self.make_field("Owner", owner)
        if technology:
            section += self.make_field("Technology", technology)
        if tags:
            section += self.make_field("Tags", ", ".join(tags))

        result_nodes.append(section)
        return result_nodes
