"""Deployment node directive for sphinx_c4.

Provides the ``define-deployment-node`` directive, which records a
DeploymentNode and renders it inline where it is defined.
"""

from docutils import nodes
from docutils.parsers.rst import directives

from julee_c4.domain.models.deployment_node import DeploymentNode, NodeType

from .base import C4Directive


class DefineDeploymentNodeDirective(C4Directive):
    """Define a deployment node in the C4 model.

    Usage::

        .. define-deployment-node:: web-server-1
           :name: Web Server 1
           :environment: production
           :type: physical_server
           :technology: Ubuntu 22.04, Docker
           :parent: aws-region-east
           :containers: api-app, web-app

           Primary web server hosting the API and web application.
    """

    required_arguments = 1
    has_content = True
    option_spec = {
        "name": directives.unchanged_required,
        "environment": directives.unchanged,
        "type": directives.unchanged,
        "technology": directives.unchanged,
        "parent": directives.unchanged,
        "containers": directives.unchanged,
        "tags": directives.unchanged,
    }

    def run(self) -> list[nodes.Node]:
        slug = self.arguments[0]
        name = self.options.get("name", slug.replace("-", " ").title())
        environment = self.options.get("environment", "production")
        node_type = NodeType(self.options.get("type", "other"))
        technology = self.options.get("technology", "")
        parent_slug = self.options.get("parent", "") or None
        containers_str = self.options.get("containers", "")
        tags_str = self.options.get("tags", "")
        tags = tuple(t.strip() for t in tags_str.split(",") if t.strip())
        description = "\n".join(self.content).strip()

        node = DeploymentNode(
            slug=slug,
            name=name,
            environment=environment,
            node_type=node_type,
            description=description,
            technology=technology,
            parent_slug=parent_slug,
            tags=tags,
            docname=self.docname,
        )

        # Deploy each referenced container onto the node, one instance each.
        if containers_str:
            for container_ref in containers_str.split(","):
                container_slug = container_ref.strip()
                if container_slug:
                    node = node.with_container_instance(container_slug)

        self.c4_context.deployment_node_repo.save(node)

        result_nodes: list[nodes.Node] = []

        section = nodes.section(ids=[slug])
        section += nodes.title(text=name)

        if description:
            section += self.make_paragraph(description)

        section += self.make_field("Environment", environment)
        if node_type != NodeType.OTHER:
            section += self.make_field("Type", node_type.value)
        if technology:
            section += self.make_field("Technology", technology)
        if parent_slug:
            section += self.make_field("Parent", parent_slug)
        if node.container_instances:
            cont_names = ", ".join(ci.container_slug for ci in node.container_instances)
            section += self.make_field("Containers", cont_names)
        if tags:
            section += self.make_field("Tags", ", ".join(tags))

        result_nodes.append(section)
        return result_nodes
