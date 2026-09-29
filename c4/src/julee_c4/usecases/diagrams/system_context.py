"""GetSystemContextDiagramUseCase.

Use case for computing a system context diagram.

A System Context diagram shows the software system in scope and its
relationships with users (persons) and other software systems.
"""

from julee_c4.domain.models.relationship import ElementType
from julee_c4.domain.models.software_system import SoftwareSystem
from julee_c4.domain.repositories.relationship import RelationshipRepository
from julee_c4.domain.repositories.software_system import SoftwareSystemRepository
from julee_c4.domain.values.diagrams import SystemContextDiagram
from julee_c4.dtos.diagrams.system_context import (
    GetSystemContextDiagramRequest,
    GetSystemContextDiagramResponse,
)


class GetSystemContextDiagramUseCase:
    """Use case for computing a system context diagram.

    .. usecase-documentation:: julee.c4.domain.use_cases.diagrams.system_context:GetSystemContextDiagramUseCase

    The diagram shows:
    - The system in scope (center)
    - External systems that interact with it
    - Persons (users) that interact with it
    - Relationships between all these elements
    """

    def __init__(
        self,
        software_system_repo: SoftwareSystemRepository,
        relationship_repo: RelationshipRepository,
    ) -> None:
        """Initialize with repository dependencies.

        Args:
            software_system_repo: SoftwareSystem repository instance
            relationship_repo: Relationship repository instance
        """
        self.software_system_repo = software_system_repo
        self.relationship_repo = relationship_repo

    async def execute(
        self, request: GetSystemContextDiagramRequest
    ) -> GetSystemContextDiagramResponse:
        """Compute the system context diagram data.

        Args:
            request: Request containing system_slug

        Returns:
            Response containing diagram data, or diagram=None if system doesn't exist
        """
        system = await self.software_system_repo.get(request.system_slug)
        if not system:
            return GetSystemContextDiagramResponse(diagram=None)

        relationships = await self.relationship_repo.get_for_element(
            ElementType.SOFTWARE_SYSTEM, request.system_slug
        )

        external_system_slugs: set[str] = set()
        person_slugs: set[str] = set()

        for rel in relationships:
            if rel.source_type == ElementType.SOFTWARE_SYSTEM:
                if rel.source_slug != request.system_slug:
                    external_system_slugs.add(rel.source_slug)
            elif rel.source_type == ElementType.PERSON:
                person_slugs.add(rel.source_slug)

            if rel.destination_type == ElementType.SOFTWARE_SYSTEM:
                if rel.destination_slug != request.system_slug:
                    external_system_slugs.add(rel.destination_slug)
            elif rel.destination_type == ElementType.PERSON:
                person_slugs.add(rel.destination_slug)

        external_systems: list[SoftwareSystem] = []
        for slug in external_system_slugs:
            ext_system = await self.software_system_repo.get(slug)
            if ext_system:
                external_systems.append(ext_system)

        diagram = SystemContextDiagram(
            system=system,
            external_systems=tuple(external_systems),
            person_slugs=tuple(person_slugs),
            relationships=tuple(relationships),
        )
        return GetSystemContextDiagramResponse(diagram=diagram)
