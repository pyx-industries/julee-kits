"""What the API says its entities are.

A response is a message, not a record (see responses.py). That only
holds if something checks it: the failure mode is silent, because
answering with the entity works perfectly until the day the entity
changes and a client breaks.

So each response's fields are written down here. A field added to an
entity cannot change what a client is told without also changing this
file, which is what a contract is. Twice now an entity change has
altered the JSON — a value object on AssemblySpecification, then
QueryMetadata on KnowledgeServiceQuery — and neither time did a test
say so.
"""

from datetime import UTC, datetime

import pytest
from julee.core.entities.text import Name, NonEmptyText
from pydantic import BaseModel

from julee_ceap.apps.api.responses import (
    AssemblySpecificationResponse,
    DocumentResponse,
    KnowledgeServiceConfigResponse,
    KnowledgeServiceQueryResponse,
    QueryMetadataResponse,
)
from julee_ceap.domain.models.assembly_specification.knowledge_service_query import (
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.models.knowledge_service_config import (
    KnowledgeServiceConfig,
    ServiceApi,
)
from julee_ceap.domain.values.multihash import ContentMultihash, content_multihash
from julee_ceap.domain.values.query_metadata import QueryMetadata

pytestmark = pytest.mark.unit


class TestTheContract:
    """The fields each response names, written down.

    Not read off the entity: reading it off would make this test agree
    with whatever the entity says, which is the coupling it exists to
    prevent.
    """

    @pytest.mark.parametrize(
        ("response", "expected"),
        [
            (
                DocumentResponse,
                (
                    "document_id",
                    "original_filename",
                    "content_type",
                    "size_bytes",
                    "content_multihash",
                    "status",
                    "knowledge_service_id",
                    "assembly_types",
                    "additional_metadata",
                    "created_at",
                    "updated_at",
                ),
            ),
            (
                KnowledgeServiceConfigResponse,
                (
                    "knowledge_service_id",
                    "name",
                    "description",
                    "service_api",
                    "created_at",
                    "updated_at",
                ),
            ),
            (
                KnowledgeServiceQueryResponse,
                (
                    "query_id",
                    "name",
                    "knowledge_service_id",
                    "prompt",
                    "query_metadata",
                    "assistant_prompt",
                    "created_at",
                    "updated_at",
                ),
            ),
            (
                QueryMetadataResponse,
                ("model", "max_tokens", "temperature"),
            ),
            (
                AssemblySpecificationResponse,
                (
                    "assembly_specification_id",
                    "name",
                    "applicability",
                    "jsonschema",
                    "status",
                    "knowledge_service_queries",
                    "version",
                    "created_at",
                    "updated_at",
                ),
            ),
        ],
        ids=lambda v: v.__name__ if isinstance(v, type) else "",
    )
    def test_it_names_these_and_no_others(
        self, response: type[BaseModel], expected: tuple[str, ...]
    ) -> None:
        """Change this and you have changed the API."""
        assert tuple(response.model_fields) == expected


class TestWhatGoesOnTheWire:
    """The domain's checked strings do not."""

    def a_document(self) -> Document:
        """One document, as the repository would hand it back.

        Returns:
            The entity
        """
        return Document(
            document_id=NonEmptyText("doc-1"),
            original_filename=NonEmptyText("minutes.txt"),
            content_type=NonEmptyText("text/plain"),
            size_bytes=5,
            content_multihash=ContentMultihash(content_multihash(b"hello")),
            status=DocumentStatus.CAPTURED,
        )

    def test_a_document_id_goes_out_as_a_string(self) -> None:
        """NonEmptyText is how this context checks; a client does not."""
        found = DocumentResponse.of(self.a_document())

        assert type(found.document_id) is str
        assert found.document_id == "doc-1"

    def test_a_multihash_goes_out_as_a_string(self) -> None:
        """ContentMultihash is a value object, not a wire type."""
        document = self.a_document()

        found = DocumentResponse.of(document)

        assert type(found.content_multihash) is str
        assert found.content_multihash == str(document.content_multihash)

    def test_a_service_name_goes_out_as_a_string(self) -> None:
        """Name, likewise."""
        found = KnowledgeServiceConfigResponse.of(
            KnowledgeServiceConfig(
                knowledge_service_id=NonEmptyText("anthropic-1"),
                name=Name("Anthropic"),
                description=NonEmptyText("A knowledge service"),
                service_api=ServiceApi.ANTHROPIC,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        )

        assert type(found.name) is str
        assert found.name == "Anthropic"

    def test_a_query_s_tuning_goes_out_named(self) -> None:
        """All three knobs, so a missing one is not ambiguous."""
        found = KnowledgeServiceQueryResponse.of(
            KnowledgeServiceQuery(
                query_id=NonEmptyText("q-1"),
                name=Name("Extract the title"),
                knowledge_service_id=NonEmptyText("anthropic-1"),
                prompt=NonEmptyText("Extract the title"),
                query_metadata=QueryMetadata(max_tokens=100),
            )
        )

        assert found.query_metadata.max_tokens == 100
        assert found.query_metadata.model is None
        assert found.query_metadata.temperature is None
