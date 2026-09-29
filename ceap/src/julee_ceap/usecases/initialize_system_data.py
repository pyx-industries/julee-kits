"""Put the data a system starts with in place, if it is not there already.

Idempotent: a second run creates nothing and says so.

This was 911 lines. Most of it was reading YAML and JSON off disk,
turning what it found into entities, and logging every step — work that
belongs to an adapter and now sits behind SystemDataService (ADR 016)
and in its fixture implementation.

What is left is the decision this use case exists to make: for each
thing the system should have, does it have one, and if not, put it
there. The counts it used to log are in its response, because a use case
reports and an adapter logs (ADR 017).
"""

from julee.core.witnesses.clock import ClockWitness, SystemClockWitness

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.models.seed import DocumentSeed
from julee_ceap.domain.repositories import (
    AssemblySpecificationRepository,
    DocumentRepository,
    KnowledgeServiceConfigRepository,
    KnowledgeServiceQueryRepository,
)
from julee_ceap.domain.services.system_data import SystemDataService

from ..dtos.initialize_system_data import (
    InitializeSystemDataRequest,
    InitializeSystemDataResponse,
    Seeded,
)


class InitializeSystemDataUseCase:
    """Ensure a system has what it needs before anyone uses it."""

    def __init__(
        self,
        knowledge_service_config_repository: KnowledgeServiceConfigRepository,
        document_repository: DocumentRepository,
        knowledge_service_query_repository: KnowledgeServiceQueryRepository,
        assembly_specification_repository: AssemblySpecificationRepository,
        system_data: SystemDataService,
        clock_witness: ClockWitness | None = None,
    ) -> None:
        """Initialise with the repositories and the data to seed from.

        Args:
            knowledge_service_config_repository: Where configurations are kept
            document_repository: Where documents are kept
            knowledge_service_query_repository: Where queries are kept
            assembly_specification_repository: Where specifications are kept
            system_data: What the system should start with
            clock_witness: For stamping a document as it is created.
                Defaults to SystemClockWitness.
        """
        self.config_repo = knowledge_service_config_repository
        self.document_repo = document_repository
        self.query_repo = knowledge_service_query_repository
        self.assembly_spec_repo = assembly_specification_repository
        self.system_data = system_data
        self._clock_witness: ClockWitness = clock_witness or SystemClockWitness()

    async def execute(
        self, request: InitializeSystemDataRequest
    ) -> InitializeSystemDataResponse:
        """Put every kind of system data in place.

        Args:
            request: Carries nothing; what to seed is the service's to say

        Returns:
            How many of each kind were created, and how many were
            already there
        """
        return InitializeSystemDataResponse(
            knowledge_service_configs=await self._ensure_configs(),
            knowledge_service_queries=await self._ensure_queries(),
            example_documents=await self._ensure_documents(),
            assembly_specifications=await self._ensure_specifications(),
        )

    async def _ensure_configs(self) -> Seeded:
        """Save every configuration the system does not already have.

        Returns:
            What was created and what was already there
        """
        offered = await self.system_data.knowledge_service_configs()
        created = 0
        for config in offered:
            if await self.config_repo.get(config.knowledge_service_id):
                continue
            await self.config_repo.save(config)
            created += 1
        return Seeded(created=created, already_there=len(offered) - created)

    async def _ensure_queries(self) -> Seeded:
        """Save every query the system does not already have.

        Returns:
            What was created and what was already there
        """
        offered = await self.system_data.knowledge_service_queries()
        created = 0
        for query in offered:
            if await self.query_repo.get(query.query_id):
                continue
            await self.query_repo.save(query)
            created += 1
        return Seeded(created=created, already_there=len(offered) - created)

    async def _ensure_specifications(self) -> Seeded:
        """Save every specification the system does not already have.

        Returns:
            What was created and what was already there
        """
        offered = await self.system_data.assembly_specifications()
        created = 0
        for specification in offered:
            if await self.assembly_spec_repo.get(
                specification.assembly_specification_id
            ):
                continue
            await self.assembly_spec_repo.save(specification)
            created += 1
        return Seeded(created=created, already_there=len(offered) - created)

    async def _ensure_documents(self) -> Seeded:
        """Store and save every example document the system does not have.

        Returns:
            What was created and what was already there
        """
        offered = await self.system_data.example_documents()
        created = 0
        for seed in offered:
            if await self.document_repo.get(seed.document_id):
                continue
            await self.document_repo.save(await self._a_document(seed))
            created += 1
        return Seeded(created=created, already_there=len(offered) - created)

    async def _a_document(self, seed: DocumentSeed) -> Document:
        """The document for one seed, its content stored first.

        Content is addressed by what it is, so it has to be stored before
        anything can name it. That ordering is the reason this is here and
        not in the adapter that read the bytes.

        Args:
            seed: What the document should be, and the bytes it is of

        Returns:
            A document naming content that is now in the store
        """
        stored = await self.document_repo.store_content(seed.content)
        now = self._clock_witness.now()
        return Document(
            document_id=seed.document_id,
            original_filename=seed.original_filename,
            content_type=seed.content_type,
            size_bytes=len(seed.content),
            content_multihash=stored,
            status=DocumentStatus.CAPTURED,
            created_at=now,
            updated_at=now,
        )


__all__ = [
    "InitializeSystemDataRequest",
    "InitializeSystemDataResponse",
    "InitializeSystemDataUseCase",
    "Seeded",
]
