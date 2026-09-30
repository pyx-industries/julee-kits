"""Where the data a system starts with comes from.

A service rather than a repository (ADR 016): it is bound to four of
this context's entities rather than one, so calling it a repository
would claim an aggregate it does not have.

It does I/O — the descriptions live somewhere, and somewhere is a
filesystem today — so it is reached from workflow code through an
activity.

It hands over entities rather than parsed files. Reading YAML, reading
JSON and turning either into a Document is the adapter's work, and it
was done inside a use case: four ``_load_fixture_*`` methods and four
``_create_*_from_fixture_data`` methods, which is why a use case
imported yaml, json and pathlib. Those methods also handed plain strs to
fields declared NonEmptyText and a list to a field declared tuple, which
pydantic used to paper over.
"""

from typing import Protocol, runtime_checkable

from julee_ceap.domain.models.assembly_specification.assembly_specification import (
    AssemblySpecification,
)
from julee_ceap.domain.models.assembly_specification.knowledge_service_query import (
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.knowledge_service_config import KnowledgeServiceConfig
from julee_ceap.domain.values.seed import DocumentSeed


@runtime_checkable
class SystemDataService(Protocol):
    """The entities a system should start with."""

    async def knowledge_service_configs(self) -> tuple[KnowledgeServiceConfig, ...]:
        """Every knowledge service configuration the system starts with.

        Returns:
            The configurations, built and ready to save
        """
        ...

    async def knowledge_service_queries(self) -> tuple[KnowledgeServiceQuery, ...]:
        """Every knowledge service query the system starts with.

        Returns:
            The queries, built and ready to save
        """
        ...

    async def assembly_specifications(self) -> tuple[AssemblySpecification, ...]:
        """Every assembly specification the system starts with.

        Returns:
            The specifications, built and ready to save
        """
        ...

    async def example_documents(self) -> tuple[DocumentSeed, ...]:
        """Every example document the system starts with, and its content.

        Seeds rather than documents: a document names its content by
        hash, and the hash is only known once the content is stored.

        Returns:
            What each document should be, and the bytes it is of
        """
        ...
