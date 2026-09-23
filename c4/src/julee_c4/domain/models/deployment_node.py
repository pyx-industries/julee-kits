"""DeploymentNode domain model.

Infrastructure where containers are deployed.
"""

from collections.abc import Mapping
from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.utils import slugify
from pydantic import Field, field_validator


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


class ContainerInstance(Entity):
    """A deployed instance of a container.

    Represents a container running within a deployment node.
    """

    container_slug: str
    instance_count: int = 1
    properties: Mapping[str, str] = Field(default_factory=dict)

    @field_validator("container_slug", mode="before")
    @classmethod
    def validate_container_slug(cls, v: str) -> str:
        """Validate container_slug is not empty."""
        if not v or not v.strip():
            raise ValueError("container_slug cannot be empty")
        return v.strip()


class DeploymentNode(Entity):
    """DeploymentNode entity.

    Represents infrastructure where containers run - physical servers,
    VMs, Docker hosts, Kubernetes clusters, execution environments, etc.

    Deployment nodes can be nested to represent infrastructure hierarchy
    (e.g., Cloud Region > Availability Zone > Kubernetes Cluster > Pod).
    """

    slug: str
    name: str
    environment: str = "production"
    node_type: NodeType = NodeType.OTHER
    description: str = ""
    technology: str = ""
    instances: int = 1
    parent_slug: str | None = None
    container_instances: tuple[ContainerInstance, ...] = Field(default_factory=tuple)
    properties: Mapping[str, str] = Field(default_factory=dict)
    tags: tuple[str, ...] = Field(default_factory=tuple)
    docname: str = ""

    @field_validator("slug", mode="before")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate and normalize slug."""
        if not v or not v.strip():
            raise ValueError("slug cannot be empty")
        return slugify(v.strip())

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name is not empty."""
        if not v or not v.strip():
            raise ValueError("name cannot be empty")
        return v.strip()

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
        """Check if a specific container is deployed here."""
        return any(
            ci.container_slug == container_slug for ci in self.container_instances
        )

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
        instances = []
        found = False
        for instance in self.container_instances:
            if instance.container_slug == container_slug:
                found = True
                instances.append(
                    instance.model_copy(
                        update={
                            "instance_count": instance.instance_count + instance_count,
                            "properties": {**instance.properties, **(properties or {})},
                        }
                    )
                )
            else:
                instances.append(instance)
        if not found:
            instances.append(
                ContainerInstance(
                    container_slug=container_slug,
                    instance_count=instance_count,
                    properties=properties or {},
                )
            )
        return self.model_copy(update={"container_instances": tuple(instances)})

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
        return self.model_copy(update={"tags": (*self.tags, tag)})
