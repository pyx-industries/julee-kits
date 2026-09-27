"""What content_of promises, asked of both implementations.

A document names its content; it does not carry it. ``content_of`` is
how a caller gets the bytes, and the two things it must guarantee are
the two ways reading content has gone wrong in this estate:

- **julee#124** — one ContentStream handed to two readers, where the
  second got an empty result in production and the full content in the
  tests, because the double's stream never ran out.
- **julee#90** — a caller rewinding a stream that is a socket and
  cannot be rewound, which works against a BytesIO and raises against
  MinIO.

Both are answered by the same property: every call opens a new stream,
at its start. So both implementations are asked, in one set of
assertions rather than two that can drift apart — the shape julee#298
settled on for FakeMinioClient itself.
"""

import io

import pytest
from julee.core.entities.content_stream import ContentStream
from julee.integrations.minio.testing import FakeMinioClient

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.domain.repositories.document import DocumentRepository
from julee_ceap.infrastructure.repositories.memory.document import (
    MemoryDocumentRepository,
)
from julee_ceap.infrastructure.repositories.minio.document import (
    MinioDocumentRepository,
)

pytestmark = pytest.mark.unit

CONTENT = b"a document, or something like one"


@pytest.fixture(params=["memory", "minio"])
def repository(request: pytest.FixtureRequest) -> DocumentRepository:
    """Each implementation of the port, asked the same questions."""
    if request.param == "memory":
        return MemoryDocumentRepository()
    return MinioDocumentRepository(FakeMinioClient())


async def a_stored_document(
    repository: DocumentRepository, content: bytes = CONTENT
) -> Document:
    """Content in the store, and a document naming it.

    In that order, which is the order the shape requires: content is
    addressed by what it is, so it has to be stored before anything can
    name it.
    """
    await repository.store_content(ContentStream(io.BytesIO(content)))
    return Document(
        document_id="doc-1",
        original_filename="spec.txt",
        content_type="text/plain",
        size_bytes=len(content),
        content_multihash=content_multihash(content),
        status=DocumentStatus.CAPTURED,
    )


class TestReadingContentThroughThePort:
    @pytest.mark.asyncio
    async def test_it_gives_back_what_was_stored(
        self, repository: DocumentRepository
    ) -> None:
        document = await a_stored_document(repository)
        await repository.save(document)

        assert (await repository.content_of(document)).read() == CONTENT

    @pytest.mark.asyncio
    async def test_each_call_gives_a_stream_of_its_own(
        self, repository: DocumentRepository
    ) -> None:
        """julee#124: one stream handed to two readers left the second
        with nothing. Asking twice is the answer, and it only works if
        asking twice is cheap and complete."""
        document = await a_stored_document(repository)
        await repository.save(document)

        first = await repository.content_of(document)
        second = await repository.content_of(document)
        first.read()

        assert second.read() == CONTENT

    @pytest.mark.asyncio
    async def test_the_stream_starts_at_the_start(
        self, repository: DocumentRepository
    ) -> None:
        """julee#90: callers used to seek(0) before reading, which works
        on a BytesIO and raises on a response off a socket. Nothing has
        to seek if nothing is second-hand."""
        document = await a_stored_document(repository)
        await repository.save(document)

        stream = await repository.content_of(document)

        assert stream.read() == CONTENT

    @pytest.mark.asyncio
    async def test_content_named_but_not_stored_is_an_error(
        self, repository: DocumentRepository
    ) -> None:
        """Metadata naming content that is not there is an integrity
        failure, not an empty result. A partial write looks like this."""
        document = await a_stored_document(repository)
        await repository.save(document)
        never_stored = document.evolve(content_multihash=content_multihash(b"other"))

        with pytest.raises(ValueError, match="names content"):
            await repository.content_of(never_stored)
