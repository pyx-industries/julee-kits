"""Container directive for sphinx_c4.

Provides the ``define-container`` directive, which records a Container
within a software system and renders it inline where it is defined.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.models.container import Container, ContainerType

from .base import C4Directive


class DefineContainerDirective(C4Directive):
    """Define a container within a software system.

    Usage::

        .. define-container:: api-app
           :name: API Application
           :system: banking-system
           :type: web_application
           :technology: FastAPI, Python 3.11

           Provides banking functionality via REST API.
    """

    required_arguments = 1
    has_content = True
    option_spec = {
        "name": directives.unchanged_required,
        "system": directives.unchanged_required,
        "type": directives.unchanged,
        "technology": directives.unchanged,
        "url": directives.unchanged,
        "tags": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        slug = self.arguments[0]
        name = self.options.get("name", slug.replace("-", " ").title())
        system_slug = self.options.get("system", "")
        container_type = ContainerType(self.options.get("type", "other"))
        technology = self.options.get("technology", "")
        url = self.options.get("url", "")
        tags_str = self.options.get("tags", "")
        tags = tuple(t.strip() for t in tags_str.split(",") if t.strip())
        description = "\n".join(self.content).strip()

        container = Container(
            slug=slug,
            name=name,
            system_slug=system_slug,
            description=description,
            container_type=container_type,
            technology=technology,
            url=url,
            tags=tags,
            docname=self.docname,
        )
        self.c4_context.container_repo.save(container)

        result_nodes: list[nodes.Node] = []

        section = nodes.section(ids=[slug])
        section += nodes.title(text=name)

        if description:
            section += self.make_paragraph(description)

        section += self.make_field("System", system_slug)
        if container_type != ContainerType.OTHER:
            section += self.make_field("Type", container_type.value)
        if technology:
            section += self.make_field("Technology", technology)
        if tags:
            section += self.make_field("Tags", ", ".join(tags))

        result_nodes.append(section)
        return result_nodes
