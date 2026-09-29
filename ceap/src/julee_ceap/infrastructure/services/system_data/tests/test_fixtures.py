"""What the kit's own fixture files yield, read by the adapter.

Against the real files, on purpose. These questions were asked of the use
case, which read the files itself; they moved here with the reading. A
double would only restate the fixtures, and what is worth knowing is
whether the files the kit ships are readable and build entities that hold
together.
"""

from pathlib import Path

import pytest
from julee.core.values.text import Name, NonEmptyText

from julee_ceap.domain.models.assembly_specification import (
    AssemblySpecification,
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.knowledge_service_config import KnowledgeServiceConfig
from julee_ceap.domain.values.schema import JsonSchema
from julee_ceap.domain.values.seed import DocumentSeed
from julee_ceap.infrastructure.services.system_data import FixtureSystemDataService

pytestmark = pytest.mark.unit


@pytest.fixture
def service() -> FixtureSystemDataService:
    """The adapter, reading the kit's own fixtures."""
    return FixtureSystemDataService()


class TestKnowledgeServiceConfigs:
    """What the configuration fixture yields."""

    async def test_it_yields_some(self, service: FixtureSystemDataService) -> None:
        """A fixture file that yields nothing would let every test below
        pass by finding nothing to check."""
        assert await service.knowledge_service_configs()

    async def test_each_is_a_configuration(
        self, service: FixtureSystemDataService
    ) -> None:
        """Entities, not the parsed file."""
        found = await service.knowledge_service_configs()

        assert all(isinstance(c, KnowledgeServiceConfig) for c in found)

    async def test_their_text_fields_are_value_objects(
        self, service: FixtureSystemDataService
    ) -> None:
        """The reason this moved.

        The use case passed whatever the YAML held, and pydantic made a
        NonEmptyText of it on the way in. A frozen dataclass does not, so
        a plain str would be stored and never checked.
        """
        first = (await service.knowledge_service_configs())[0]

        assert isinstance(first.knowledge_service_id, NonEmptyText)
        assert isinstance(first.name, Name)
        assert isinstance(first.description, NonEmptyText)

    async def test_no_two_share_an_id(self, service: FixtureSystemDataService) -> None:
        """Two configurations with one id means one silently wins."""
        found = await service.knowledge_service_configs()

        ids = [c.knowledge_service_id for c in found]
        assert len(set(ids)) == len(ids)


class TestKnowledgeServiceQueries:
    """What the query fixture yields."""

    async def test_it_yields_some(self, service: FixtureSystemDataService) -> None:
        """As above: nothing would make the rest vacuous."""
        assert await service.knowledge_service_queries()

    async def test_each_is_a_query(self, service: FixtureSystemDataService) -> None:
        """Entities, not the parsed file."""
        found = await service.knowledge_service_queries()

        assert all(isinstance(q, KnowledgeServiceQuery) for q in found)

    async def test_their_text_fields_are_value_objects(
        self, service: FixtureSystemDataService
    ) -> None:
        """Same reason as the configurations."""
        first = (await service.knowledge_service_queries())[0]

        assert isinstance(first.query_id, NonEmptyText)
        assert isinstance(first.name, Name)
        assert isinstance(first.prompt, NonEmptyText)

    async def test_each_names_a_service_that_is_configured(
        self, service: FixtureSystemDataService
    ) -> None:
        """A query naming no configured service can never run.

        The two fixtures are read separately and nothing joins them, so
        this is the only thing that would notice a typo in either.
        """
        configured = {
            c.knowledge_service_id for c in await service.knowledge_service_configs()
        }

        for query in await service.knowledge_service_queries():
            assert query.knowledge_service_id in configured


class TestAssemblySpecifications:
    """What the specification fixture yields, read as JSON."""

    async def test_it_yields_some(self, service: FixtureSystemDataService) -> None:
        """The one fixture that is JSON rather than YAML."""
        assert await service.assembly_specifications()

    async def test_each_is_a_specification(
        self, service: FixtureSystemDataService
    ) -> None:
        """Entities, not the parsed file."""
        found = await service.assembly_specifications()

        assert all(isinstance(s, AssemblySpecification) for s in found)

    async def test_the_schema_is_a_schema(
        self, service: FixtureSystemDataService
    ) -> None:
        """Not the mapping the file held."""
        first = (await service.assembly_specifications())[0]

        assert isinstance(first.jsonschema, JsonSchema)
        assert first.jsonschema.document

    async def test_each_query_it_names_exists(
        self, service: FixtureSystemDataService
    ) -> None:
        """A pointer mapped to a query id that is not a query is a
        specification that cannot be assembled."""
        queries = {q.query_id for q in await service.knowledge_service_queries()}

        for specification in await service.assembly_specifications():
            for named in specification.knowledge_service_queries.values():
                assert named in queries


class TestExampleDocuments:
    """What the document fixture yields."""

    async def test_it_yields_some(self, service: FixtureSystemDataService) -> None:
        """As above."""
        assert await service.example_documents()

    async def test_each_is_a_seed(self, service: FixtureSystemDataService) -> None:
        """Seeds rather than documents: a document names its content by
        hash, and the hash is only known once the content is stored."""
        found = await service.example_documents()

        assert all(isinstance(seed, DocumentSeed) for seed in found)

    async def test_each_carries_its_content(
        self, service: FixtureSystemDataService
    ) -> None:
        """An empty seed would make a zero-byte document, which the
        Document entity refuses."""
        for seed in await service.example_documents():
            assert seed.content

    async def test_their_text_fields_are_value_objects(
        self, service: FixtureSystemDataService
    ) -> None:
        """Same reason as the rest."""
        first = (await service.example_documents())[0]

        assert isinstance(first.document_id, NonEmptyText)
        assert isinstance(first.original_filename, NonEmptyText)


class TestAFixtureDirectoryThatIsWrong:
    """What happens when the files are not what they should be."""

    async def test_a_missing_file_is_reported_with_its_path(
        self, tmp_path: Path
    ) -> None:
        """So whoever has to fix it knows where to look."""
        service = FixtureSystemDataService(fixtures=tmp_path)

        with pytest.raises(FileNotFoundError, match="knowledge_service_configs.yaml"):
            await service.knowledge_service_configs()

    async def test_a_file_that_is_not_readable_is_reported(
        self, tmp_path: Path
    ) -> None:
        """Malformed YAML names the file rather than raising from yaml."""
        (tmp_path / "knowledge_service_configs.yaml").write_text("not: [valid: yaml")
        service = FixtureSystemDataService(fixtures=tmp_path)

        with pytest.raises(ValueError, match="is not readable"):
            await service.knowledge_service_configs()

    async def test_a_file_holding_something_other_than_a_list_is_reported(
        self, tmp_path: Path
    ) -> None:
        """A scalar where a list belongs would otherwise iterate its
        characters."""
        (tmp_path / "knowledge_service_configs.yaml").write_text(
            "knowledge_services: not-a-list"
        )
        service = FixtureSystemDataService(fixtures=tmp_path)

        with pytest.raises(ValueError, match="must hold a list"):
            await service.knowledge_service_configs()

    async def test_a_service_api_that_is_not_one_is_refused(
        self, tmp_path: Path
    ) -> None:
        """Naming the allowed values, since the file is hand-written."""
        (tmp_path / "knowledge_service_configs.yaml").write_text(
            "knowledge_services:\n"
            "  - knowledge_service_id: k\n"
            "    name: K\n"
            "    description: D\n"
            "    service_api: not-an-api\n"
        )
        service = FixtureSystemDataService(fixtures=tmp_path)

        with pytest.raises(ValueError, match="Invalid service_api"):
            await service.knowledge_service_configs()
