"""DeploymentNode domain model.

Infrastructure where containers are deployed.
"""

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from enum import StrEnum

from julee.core.values.text import Name, Slug

from ..values.container_instance import ContainerInstance


class NodeType(StrEnum):
    """Classification of deployment nodes."""

    PHYSICAL_SERVER = "physical_server"
    VIRTUAL_MACHINE = "virtual_machine"
    CONTAINER_RUNTIME = "container_runtime"  # Docker, containerd, etc.
    KUBERNETES_CLUSTER = "kubernetes_cluster"
    KUBERNETES_POD = "kubernetes_pod"
    CLOUD_REGION = "cloud_region"
    AVAILABILITY_ZONE = "availability_zone"
    BROWSER = "browser"
    MOBILE_DEVICE = "mobile_device"
    DNS = "dns"
    LOAD_BALANCER = "load_balancer"
    FIREWALL = "firewall"
    CDN = "cdn"
    OTHER = "other"


@dataclass(frozen=True)
class DeploymentNode:
    """DeploymentNode entity.

    Represents infrastructure where containers run - physical servers,
    VMs, Docker hosts, Kubernetes clusters, execution environments, etc.

    Deployment nodes can be nested to represent infrastructure hierarchy
    (e.g., Cloud Region > Availability Zone > Kubernetes Cluster > Pod).
    """

    slug: Slug
    name: Name
    environment: str = "production"
    node_type: NodeType = NodeType.OTHER
    description: str = ""
    technology: str = ""
    instances: int = 1
    parent_slug: Slug | None = None
    container_instances: tuple[ContainerInstance, ...] = field(default_factory=tuple)
    properties: Mapping[str, str] = field(default_factory=dict)
    tags: tuple[str, ...] = field(default_factory=tuple)
    docname: str = ""

    @property
    def has_parent(self) -> bool:
        """Check if this node has a parent node."""
        return self.parent_slug is not None

    @property
    def has_containers(self) -> bool:
        """Check if this node has deployed containers."""
        return len(self.container_instances) > 0

    @property
    def total_container_instances(self) -> int:
        """Get total count of container instances."""
        return sum(ci.instance_count for ci in self.container_instances)

    def deploys_container(self, container_slug: str) -> bool:
        """Check if a specific container is deployed here.

        The argument is made a :class:`Slug` before it is compared, so
        asking with the container's display name answers the same as
        asking with its slug. Comparing the argument as given is how
        this kind of lookup silently returned nothing (#70).
        """
        wanted = Slug(container_slug)
        return any(ci.container_slug == wanted for ci in self.container_instances)

    def with_container_instance(
        self,
        container_slug: str,
        instance_count: int = 1,
        properties: Mapping[str, str] | None = None,
    ) -> "DeploymentNode":
        """The node with a container deployed on it.

        Deploying a container that is already here adds to its count and
        merges its properties, rather than listing it twice. An entity is
        immutable, so this returns a new node.

        Args:
            container_slug: Container being deployed
            instance_count: How many of it
            properties: Deployment properties, merged with any already set

        Returns:
            A new DeploymentNode
        """
        wanted = Slug(container_slug)
        instances = []
        found = False
        for instance in self.container_instances:
            if instance.container_slug == wanted:
                found = True
                instances.append(
                    replace(
                        instance,
                        instance_count=instance.instance_count + instance_count,
                        properties={**instance.properties, **(properties or {})},
                    )
                )
            else:
                instances.append(instance)
        if not found:
            instances.append(
                ContainerInstance(
                    container_slug=wanted,
                    instance_count=instance_count,
                    properties=properties or {},
                )
            )
        return replace(self, container_instances=tuple(instances))

    def has_tag(self, tag: str) -> bool:
        """Check if node has a specific tag (case-insensitive)."""
        return tag.lower() in [t.lower() for t in self.tags]

    def with_tag(self, tag: str) -> "DeploymentNode":
        """The entity with a tag added.

        An entity is immutable, so this returns a new one rather than
        changing this one. A tag already present is not added twice.

        Args:
            tag: Tag to add

        Returns:
            A new DeploymentNode, or this one if it already had the tag
        """
        if self.has_tag(tag):
            return self
        return replace(self, tags=(*self.tags, tag))
