"""C4 context for a Sphinx build.

Holds one repository per C4 element, each wrapped so that Sphinx's
synchronous directives can call an async repository. It mirrors
HCDContext: the two viewpoints project the same solution through
different lenses, and there is no reason for them to be held differently.
"""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from julee_c4.domain.repositories.component import ComponentRepository
from julee_c4.domain.repositories.container import ContainerRepository
from julee_c4.domain.repositories.deployment_node import DeploymentNodeRepository
from julee_c4.domain.repositories.dynamic_step import DynamicStepRepository
from julee_c4.domain.repositories.relationship import RelationshipRepository
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository
from julee_c4.infrastructure.repositories.memory.component import (
    MemoryComponentRepository,
)
from julee_c4.infrastructure.repositories.memory.container import (
    MemoryContainerRepository,
)
from julee_c4.infrastructure.repositories.memory.deployment_node import (
    MemoryDeploymentNodeRepository,
)
from julee_c4.infrastructure.repositories.memory.dynamic_step import (
    MemoryDynamicStepRepository,
)
from julee_c4.infrastructure.repositories.memory.relationship import (
    MemoryRelationshipRepository,
)
from julee_c4.infrastructure.repositories.memory.software_system import (
    MemorySoftwareSystemRepository,
)

from ...sphinx_hcd.sphinx.adapters import SyncRepositoryAdapter

if TYPE_CHECKING:
    from julee_c4.domain.models.component import Component
    from julee_c4.domain.models.container import Container
    from julee_c4.domain.models.deployment_node import DeploymentNode
    from julee_c4.domain.models.dynamic_step import DynamicStep
    from julee_c4.domain.models.relationship import Relationship
    from julee_c4.domain.models.software_system import SoftwareSystem

_CONTEXT_ATTR = "_julee_c4_context"


@dataclass
class C4Context:
    """Every C4 element a build has read, ready for the directives.

    Created at builder-inited and attached to the Sphinx application.
    """

    software_system_repo: SyncRepositoryAdapter["SoftwareSystem"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemorySoftwareSystemRepository())
    )
    container_repo: SyncRepositoryAdapter["Container"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemoryContainerRepository())
    )
    component_repo: SyncRepositoryAdapter["Component"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemoryComponentRepository())
    )
    relationship_repo: SyncRepositoryAdapter["Relationship"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemoryRelationshipRepository())
    )
    deployment_node_repo: SyncRepositoryAdapter["DeploymentNode"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemoryDeploymentNodeRepository())
    )
    dynamic_step_repo: SyncRepositoryAdapter["DynamicStep"] = field(
        default_factory=lambda: SyncRepositoryAdapter(MemoryDynamicStepRepository())
    )

    def _repos(self) -> list[SyncRepositoryAdapter[Any]]:
        """Every repository, for the operations that touch all of them."""
        return [
            self.software_system_repo,
            self.container_repo,
            self.component_repo,
            self.relationship_repo,
            self.deployment_node_repo,
            self.dynamic_step_repo,
        ]

    def clear_all(self) -> None:
        """Forget every element, for a build starting from scratch."""
        for repo in self._repos():
            repo.clear()

    def clear_by_docname(self, docname: str) -> dict[str, int]:
        """Forget what one document defined, for an incremental build.

        Args:
            docname: RST document being re-read

        Returns:
            How many of each kind of element were forgotten
        """
        # SyncRepositoryAdapter.async_repo is typed as the narrow structural
        # protocol it depends on for its own methods, which does not include
        # clear_by_docname. The concrete Memory* repositories all satisfy
        # their fuller domain protocol, which does - assert it to use it.
        software_system_async = self.software_system_repo.async_repo
        assert isinstance(software_system_async, SoftwareSystemRepository)
        container_async = self.container_repo.async_repo
        assert isinstance(container_async, ContainerRepository)
        component_async = self.component_repo.async_repo
        assert isinstance(component_async, ComponentRepository)
        relationship_async = self.relationship_repo.async_repo
        assert isinstance(relationship_async, RelationshipRepository)
        deployment_node_async = self.deployment_node_repo.async_repo
        assert isinstance(deployment_node_async, DeploymentNodeRepository)
        dynamic_step_async = self.dynamic_step_repo.async_repo
        assert isinstance(dynamic_step_async, DynamicStepRepository)

        return {
            "software_systems": self.software_system_repo.run_async(
                software_system_async.clear_by_docname(docname)
            ),
            "containers": self.container_repo.run_async(
                container_async.clear_by_docname(docname)
            ),
            "components": self.component_repo.run_async(
                component_async.clear_by_docname(docname)
            ),
            "relationships": self.relationship_repo.run_async(
                relationship_async.clear_by_docname(docname)
            ),
            "deployment_nodes": self.deployment_node_repo.run_async(
                deployment_node_async.clear_by_docname(docname)
            ),
            "dynamic_steps": self.dynamic_step_repo.run_async(
                dynamic_step_async.clear_by_docname(docname)
            ),
        }


def set_c4_context(app: Any, context: C4Context) -> None:
    """Attach a context to the Sphinx application."""
    setattr(app, _CONTEXT_ATTR, context)


def get_c4_context(app: Any) -> C4Context | None:
    """The context attached to this application, if there is one."""
    result: C4Context | None = getattr(app, _CONTEXT_ATTR, None)
    return result


def ensure_c4_context(app: Any) -> C4Context:
    """The context attached to this application, creating one if needed."""
    context = get_c4_context(app)
    if context is None:
        context = C4Context()
        set_c4_context(app, context)
    return context
