"""A container running somewhere.

A value, not an entity (ADR 018). It names a container by slug and says
how many of it are running on a node; it has no id of its own and no
repository keeps one. It lived in deployment_node.py, beside the
DeploymentNode that holds it, and was read as a second aggregate there.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field

from julee.core.entities.text import Slug


@dataclass(frozen=True)
class ContainerInstance:
    """A deployed instance of a container.

    Represents a container running within a deployment node.
    """

    container_slug: Slug
    instance_count: int = 1
    properties: Mapping[str, str] = field(default_factory=dict)
