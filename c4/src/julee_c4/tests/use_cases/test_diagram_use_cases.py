"""Tests for diagram computation use cases."""

import pytest
from julee.core.entities.text import Name, Slug

from julee_c4.domain.models.component import Component
from julee_c4.domain.models.container import Container, ContainerType
from julee_c4.domain.models.deployment_node import (
    ContainerInstance,
    DeploymentNode,
    NodeType,
)
from julee_c4.domain.models.dynamic_step import DynamicStep
from julee_c4.domain.models.relationship import ElementType, Relationship
from julee_c4.domain.models.software_system import (
    SoftwareSystem,
    SystemType,
)
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
from julee_c4.usecases.diagrams.component_diagram import (
    GetComponentDiagramRequest,
    GetComponentDiagramUseCase,
)
from julee_c4.usecases.diagrams.container_diagram import (
    GetContainerDiagramRequest,
    GetContainerDiagramUseCase,
)
from julee_c4.usecases.diagrams.deployment_diagram import (
    GetDeploymentDiagramRequest,
    GetDeploymentDiagramUseCase,
)
from julee_c4.usecases.diagrams.dynamic_diagram import (
    GetDynamicDiagramRequest,
    GetDynamicDiagramUseCase,
)
from julee_c4.usecases.diagrams.system_context import (
    GetSystemContextDiagramRequest,
    GetSystemContextDiagramUseCase,
)
from julee_c4.usecases.diagrams.system_landscape import (
    GetSystemLandscapeDiagramRequest,
    GetSystemLandscapeDiagramUseCase,
)


class TestGetSystemContextDiagramUseCase:
    """Test system context diagram generation."""

    @pytest.fixture
    def system_repo(self) -> MemorySoftwareSystemRepository:
        return MemorySoftwareSystemRepository()

    @pytest.fixture
    def relationship_repo(self) -> MemoryRelationshipRepository:
        return MemoryRelationshipRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        system_repo: MemorySoftwareSystemRepository,
        relationship_repo: MemoryRelationshipRepository,
    ) -> tuple[MemorySoftwareSystemRepository, MemoryRelationshipRepository]:
        """Set up repos with sample data."""
        # Systems
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("banking-system"),
                name=Name("Banking System"),
                system_type=SystemType.INTERNAL,
            )
        )
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("email-system"),
                name=Name("Email System"),
                system_type=SystemType.EXTERNAL,
            )
        )
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("crm-system"),
                name=Name("CRM System"),
                system_type=SystemType.EXTERNAL,
            )
        )

        # Relationships
        await relationship_repo.save(
            Relationship(
                slug=Slug("customer-to-banking"),
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("banking-system"),
                description="Uses",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("banking-to-email"),
                source_type=ElementType.SOFTWARE_SYSTEM,
                source_slug=Slug("banking-system"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("email-system"),
                description="Sends emails using",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("banking-to-crm"),
                source_type=ElementType.SOFTWARE_SYSTEM,
                source_slug=Slug("banking-system"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("crm-system"),
                description="Gets customer data from",
            )
        )

        return system_repo, relationship_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetSystemContextDiagramUseCase:
        system_repo, relationship_repo = populated_repos
        return GetSystemContextDiagramUseCase(system_repo, relationship_repo)

    @pytest.mark.asyncio
    async def test_get_system_context_success(
        self, use_case: GetSystemContextDiagramUseCase
    ) -> None:
        """Test getting system context diagram."""
        request = GetSystemContextDiagramRequest(system_slug="banking-system")
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert response.diagram.system.slug == "banking-system"
        assert len(response.diagram.external_systems) == 2
        assert len(response.diagram.person_slugs) == 1
        assert "customer" in response.diagram.person_slugs
        assert len(response.diagram.relationships) == 3

    @pytest.mark.asyncio
    async def test_get_system_context_nonexistent(
        self, use_case: GetSystemContextDiagramUseCase
    ) -> None:
        """Test getting diagram for nonexistent system returns None."""
        request = GetSystemContextDiagramRequest(system_slug="nonexistent")
        response = await use_case.execute(request)
        assert response.diagram is None


class TestGetContainerDiagramUseCase:
    """Test container diagram generation."""

    @pytest.fixture
    def system_repo(self) -> MemorySoftwareSystemRepository:
        return MemorySoftwareSystemRepository()

    @pytest.fixture
    def container_repo(self) -> MemoryContainerRepository:
        return MemoryContainerRepository()

    @pytest.fixture
    def relationship_repo(self) -> MemoryRelationshipRepository:
        return MemoryRelationshipRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        system_repo: MemorySoftwareSystemRepository,
        container_repo: MemoryContainerRepository,
        relationship_repo: MemoryRelationshipRepository,
    ) -> tuple:
        """Set up repos with sample data."""
        # System
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("banking-system"),
                name=Name("Banking System"),
                system_type=SystemType.INTERNAL,
            )
        )
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("email-system"),
                name=Name("Email System"),
                system_type=SystemType.EXTERNAL,
            )
        )

        # Containers
        await container_repo.save(
            Container(
                slug=Slug("web-app"),
                name=Name("Web Application"),
                system_slug=Slug("banking-system"),
                container_type=ContainerType.WEB_APPLICATION,
            )
        )
        await container_repo.save(
            Container(
                slug=Slug("api-app"),
                name=Name("API Application"),
                system_slug=Slug("banking-system"),
                container_type=ContainerType.API,
            )
        )
        await container_repo.save(
            Container(
                slug=Slug("database"),
                name=Name("Database"),
                system_slug=Slug("banking-system"),
                container_type=ContainerType.DATABASE,
            )
        )

        # Relationships
        await relationship_repo.save(
            Relationship(
                slug=Slug("customer-to-web"),
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("web-app"),
                description="Uses",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("web-to-api"),
                source_type=ElementType.CONTAINER,
                source_slug=Slug("web-app"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("api-app"),
                description="Calls",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("api-to-db"),
                source_type=ElementType.CONTAINER,
                source_slug=Slug("api-app"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("database"),
                description="Reads/writes",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("api-to-email"),
                source_type=ElementType.CONTAINER,
                source_slug=Slug("api-app"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("email-system"),
                description="Sends emails via",
            )
        )

        return system_repo, container_repo, relationship_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetContainerDiagramUseCase:
        system_repo, container_repo, relationship_repo = populated_repos
        return GetContainerDiagramUseCase(
            system_repo, container_repo, relationship_repo
        )

    @pytest.mark.asyncio
    async def test_get_container_diagram_success(
        self, use_case: GetContainerDiagramUseCase
    ) -> None:
        """Test getting container diagram."""
        request = GetContainerDiagramRequest(system_slug="banking-system")
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert response.diagram.system.slug == "banking-system"
        assert len(response.diagram.containers) == 3
        assert len(response.diagram.external_systems) == 1
        assert response.diagram.external_systems[0].slug == "email-system"
        assert len(response.diagram.person_slugs) == 1
        assert "customer" in response.diagram.person_slugs

    @pytest.mark.asyncio
    async def test_get_container_diagram_nonexistent(
        self, use_case: GetContainerDiagramUseCase
    ) -> None:
        """Test getting diagram for nonexistent system returns None."""
        request = GetContainerDiagramRequest(system_slug="nonexistent")
        response = await use_case.execute(request)
        assert response.diagram is None


class TestGetComponentDiagramUseCase:
    """Test component diagram generation."""

    @pytest.fixture
    def system_repo(self) -> MemorySoftwareSystemRepository:
        return MemorySoftwareSystemRepository()

    @pytest.fixture
    def container_repo(self) -> MemoryContainerRepository:
        return MemoryContainerRepository()

    @pytest.fixture
    def component_repo(self) -> MemoryComponentRepository:
        return MemoryComponentRepository()

    @pytest.fixture
    def relationship_repo(self) -> MemoryRelationshipRepository:
        return MemoryRelationshipRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        system_repo: MemorySoftwareSystemRepository,
        container_repo: MemoryContainerRepository,
        component_repo: MemoryComponentRepository,
        relationship_repo: MemoryRelationshipRepository,
    ) -> tuple:
        """Set up repos with sample data."""
        # System
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("banking-system"),
                name=Name("Banking System"),
                system_type=SystemType.INTERNAL,
            )
        )

        # Container
        await container_repo.save(
            Container(
                slug=Slug("api-app"),
                name=Name("API Application"),
                system_slug=Slug("banking-system"),
                container_type=ContainerType.API,
            )
        )

        # Components
        await component_repo.save(
            Component(
                slug=Slug("auth-controller"),
                name=Name("Auth Controller"),
                container_slug=Slug("api-app"),
                system_slug=Slug("banking-system"),
            )
        )
        await component_repo.save(
            Component(
                slug=Slug("user-service"),
                name=Name("User Service"),
                container_slug=Slug("api-app"),
                system_slug=Slug("banking-system"),
            )
        )
        await component_repo.save(
            Component(
                slug=Slug("account-service"),
                name=Name("Account Service"),
                container_slug=Slug("api-app"),
                system_slug=Slug("banking-system"),
            )
        )

        # Relationships
        await relationship_repo.save(
            Relationship(
                slug=Slug("auth-to-user"),
                source_type=ElementType.COMPONENT,
                source_slug=Slug("auth-controller"),
                destination_type=ElementType.COMPONENT,
                destination_slug=Slug("user-service"),
                description="Validates users via",
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("auth-to-account"),
                source_type=ElementType.COMPONENT,
                source_slug=Slug("auth-controller"),
                destination_type=ElementType.COMPONENT,
                destination_slug=Slug("account-service"),
                description="Gets accounts via",
            )
        )

        return system_repo, container_repo, component_repo, relationship_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetComponentDiagramUseCase:
        system_repo, container_repo, component_repo, relationship_repo = populated_repos
        return GetComponentDiagramUseCase(
            system_repo, container_repo, component_repo, relationship_repo
        )

    @pytest.mark.asyncio
    async def test_get_component_diagram_success(
        self, use_case: GetComponentDiagramUseCase
    ) -> None:
        """Test getting component diagram."""
        request = GetComponentDiagramRequest(container_slug="api-app")
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert response.diagram.container.slug == "api-app"
        assert len(response.diagram.components) == 3
        assert len(response.diagram.relationships) == 2

    @pytest.mark.asyncio
    async def test_get_component_diagram_nonexistent(
        self, use_case: GetComponentDiagramUseCase
    ) -> None:
        """Test getting diagram for nonexistent container returns None."""
        request = GetComponentDiagramRequest(container_slug="nonexistent")
        response = await use_case.execute(request)
        assert response.diagram is None


class TestGetSystemLandscapeDiagramUseCase:
    """Test system landscape diagram generation."""

    @pytest.fixture
    def system_repo(self) -> MemorySoftwareSystemRepository:
        return MemorySoftwareSystemRepository()

    @pytest.fixture
    def relationship_repo(self) -> MemoryRelationshipRepository:
        return MemoryRelationshipRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        system_repo: MemorySoftwareSystemRepository,
        relationship_repo: MemoryRelationshipRepository,
    ) -> tuple:
        """Set up repos with sample data."""
        # Systems
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("banking-system"),
                name=Name("Banking System"),
                system_type=SystemType.INTERNAL,
            )
        )
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("insurance-system"),
                name=Name("Insurance System"),
                system_type=SystemType.INTERNAL,
            )
        )
        await system_repo.save(
            SoftwareSystem(
                slug=Slug("email-system"),
                name=Name("Email System"),
                system_type=SystemType.EXTERNAL,
            )
        )

        # Relationships
        await relationship_repo.save(
            Relationship(
                slug=Slug("customer-to-banking"),
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("banking-system"),
            )
        )
        await relationship_repo.save(
            Relationship(
                slug=Slug("banking-to-insurance"),
                source_type=ElementType.SOFTWARE_SYSTEM,
                source_slug=Slug("banking-system"),
                destination_type=ElementType.SOFTWARE_SYSTEM,
                destination_slug=Slug("insurance-system"),
            )
        )

        return system_repo, relationship_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetSystemLandscapeDiagramUseCase:
        system_repo, relationship_repo = populated_repos
        return GetSystemLandscapeDiagramUseCase(system_repo, relationship_repo)

    @pytest.mark.asyncio
    async def test_get_system_landscape_success(
        self, use_case: GetSystemLandscapeDiagramUseCase
    ) -> None:
        """Test getting system landscape diagram."""
        request = GetSystemLandscapeDiagramRequest()
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert len(response.diagram.systems) == 3
        assert len(response.diagram.person_slugs) == 1
        assert "customer" in response.diagram.person_slugs
        assert len(response.diagram.relationships) == 2


class TestGetDeploymentDiagramUseCase:
    """Test deployment diagram generation."""

    @pytest.fixture
    def deployment_node_repo(self) -> MemoryDeploymentNodeRepository:
        return MemoryDeploymentNodeRepository()

    @pytest.fixture
    def container_repo(self) -> MemoryContainerRepository:
        return MemoryContainerRepository()

    @pytest.fixture
    def relationship_repo(self) -> MemoryRelationshipRepository:
        return MemoryRelationshipRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        deployment_node_repo: MemoryDeploymentNodeRepository,
        container_repo: MemoryContainerRepository,
        relationship_repo: MemoryRelationshipRepository,
    ) -> tuple:
        """Set up repos with sample data."""
        # Containers
        await container_repo.save(
            Container(
                slug=Slug("api-app"),
                name=Name("API Application"),
                system_slug=Slug("banking-system"),
            )
        )
        await container_repo.save(
            Container(
                slug=Slug("web-app"),
                name=Name("Web Application"),
                system_slug=Slug("banking-system"),
            )
        )

        # Deployment nodes
        await deployment_node_repo.save(
            DeploymentNode(
                slug=Slug("aws-region"),
                name=Name("AWS Region"),
                environment="production",
                node_type=NodeType.CLOUD_REGION,
            )
        )
        await deployment_node_repo.save(
            DeploymentNode(
                slug=Slug("k8s-cluster"),
                name=Name("Kubernetes Cluster"),
                environment="production",
                node_type=NodeType.KUBERNETES_CLUSTER,
                parent_slug=Slug("aws-region"),
                container_instances=(
                    ContainerInstance(container_slug=Slug("api-app"), instance_count=3),
                    ContainerInstance(container_slug=Slug("web-app"), instance_count=2),
                ),
            )
        )
        await deployment_node_repo.save(
            DeploymentNode(
                slug=Slug("staging-server"),
                name=Name("Staging Server"),
                environment="staging",
                node_type=NodeType.VIRTUAL_MACHINE,
            )
        )

        # Container relationships
        await relationship_repo.save(
            Relationship(
                slug=Slug("web-to-api"),
                source_type=ElementType.CONTAINER,
                source_slug=Slug("web-app"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("api-app"),
                description="Makes API calls",
            )
        )

        return deployment_node_repo, container_repo, relationship_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetDeploymentDiagramUseCase:
        deployment_node_repo, container_repo, relationship_repo = populated_repos
        return GetDeploymentDiagramUseCase(
            deployment_node_repo, container_repo, relationship_repo
        )

    @pytest.mark.asyncio
    async def test_get_deployment_diagram_success(
        self, use_case: GetDeploymentDiagramUseCase
    ) -> None:
        """Test getting deployment diagram."""
        request = GetDeploymentDiagramRequest(environment="production")
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert response.diagram.environment == "production"
        assert len(response.diagram.nodes) == 2
        assert len(response.diagram.containers) == 2

    @pytest.mark.asyncio
    async def test_get_deployment_diagram_empty_env(
        self, use_case: GetDeploymentDiagramUseCase
    ) -> None:
        """Test getting diagram for environment with no nodes."""
        request = GetDeploymentDiagramRequest(environment="development")
        response = await use_case.execute(request)

        # Returns data but with empty nodes
        assert response.diagram is not None
        assert len(response.diagram.nodes) == 0


class TestGetDynamicDiagramUseCase:
    """Test dynamic diagram generation."""

    @pytest.fixture
    def dynamic_step_repo(self) -> MemoryDynamicStepRepository:
        return MemoryDynamicStepRepository()

    @pytest.fixture
    def system_repo(self) -> MemorySoftwareSystemRepository:
        return MemorySoftwareSystemRepository()

    @pytest.fixture
    def container_repo(self) -> MemoryContainerRepository:
        return MemoryContainerRepository()

    @pytest.fixture
    def component_repo(self) -> MemoryComponentRepository:
        return MemoryComponentRepository()

    @pytest.fixture
    async def populated_repos(
        self,
        dynamic_step_repo: MemoryDynamicStepRepository,
        system_repo: MemorySoftwareSystemRepository,
        container_repo: MemoryContainerRepository,
        component_repo: MemoryComponentRepository,
    ) -> tuple:
        """Set up repos with sample data."""
        # Containers
        await container_repo.save(
            Container(
                slug=Slug("web-app"),
                name=Name("Web Application"),
                system_slug=Slug("banking-system"),
            )
        )
        await container_repo.save(
            Container(
                slug=Slug("api-app"),
                name=Name("API Application"),
                system_slug=Slug("banking-system"),
            )
        )
        await container_repo.save(
            Container(
                slug=Slug("database"),
                name=Name("Database"),
                system_slug=Slug("banking-system"),
            )
        )

        # Dynamic steps for login sequence
        await dynamic_step_repo.save(
            DynamicStep(
                slug=Slug("login-1"),
                sequence_name=Name("user-login"),
                step_number=1,
                source_type=ElementType.PERSON,
                source_slug=Slug("customer"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("web-app"),
                description="Enters credentials",
            )
        )
        await dynamic_step_repo.save(
            DynamicStep(
                slug=Slug("login-2"),
                sequence_name=Name("user-login"),
                step_number=2,
                source_type=ElementType.CONTAINER,
                source_slug=Slug("web-app"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("api-app"),
                description="Validates credentials",
            )
        )
        await dynamic_step_repo.save(
            DynamicStep(
                slug=Slug("login-3"),
                sequence_name=Name("user-login"),
                step_number=3,
                source_type=ElementType.CONTAINER,
                source_slug=Slug("api-app"),
                destination_type=ElementType.CONTAINER,
                destination_slug=Slug("database"),
                description="Queries user",
            )
        )

        return dynamic_step_repo, system_repo, container_repo, component_repo

    @pytest.fixture
    def use_case(self, populated_repos: tuple) -> GetDynamicDiagramUseCase:
        dynamic_step_repo, system_repo, container_repo, component_repo = populated_repos
        return GetDynamicDiagramUseCase(
            dynamic_step_repo, system_repo, container_repo, component_repo
        )

    @pytest.mark.asyncio
    async def test_get_dynamic_diagram_success(
        self, use_case: GetDynamicDiagramUseCase
    ) -> None:
        """Test getting dynamic diagram."""
        request = GetDynamicDiagramRequest(sequence_name="user-login")
        response = await use_case.execute(request)

        assert response.diagram is not None
        assert response.diagram.sequence_name == "user-login"
        assert len(response.diagram.steps) == 3
        # Steps should be in order
        assert [s.step_number for s in response.diagram.steps] == [1, 2, 3]
        assert len(response.diagram.containers) == 3
        assert len(response.diagram.person_slugs) == 1
        assert "customer" in response.diagram.person_slugs

    @pytest.mark.asyncio
    async def test_get_dynamic_diagram_nonexistent(
        self, use_case: GetDynamicDiagramUseCase
    ) -> None:
        """Test getting diagram for nonexistent sequence returns None."""
        request = GetDynamicDiagramRequest(sequence_name="nonexistent-sequence")
        response = await use_case.execute(request)
        assert response.diagram is None
