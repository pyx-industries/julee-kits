"""What content_of promises, asked of both implementations.

A document names its content; it does not carry it. ``content_of`` is
how a caller gets the bytes, and it returns bytes — which is what
settles the two ways reading content has gone wrong here:

- **julee#124** — one ContentStream handed to two readers, where the
  second got an empty result in production and the full content in the
  tests, because the double's stream never ran out.
- **julee#90** — a caller rewinding a stream that is a socket and
  cannot be rewound, which works against a BytesIO and raises against
  MinIO.

Both were properties of a stream. Bytes can be read by two callers and
need no rewinding, so neither is expressible any more (julee-kits#89).
The tests below stay because the guarantees still have to hold: what
comes back is the content, and it comes back every time it is asked
for.

Both implementations are asked, in one set of assertions rather than
two that can drift apart — the shape julee#298 settled on for
FakeMinioClient itself.
"""

from dataclasses import replace

import pytest
from julee.core.values.text import NonEmptyText
from julee.integrations.minio.testing import FakeMinioClient

from julee_ceap.domain.models.document import Document, DocumentStatus
from julee_ceap.domain.repositories.document import DocumentRepository
from julee_ceap.domain.values.multihash import (
    ContentMultihash,
    content_multihash,
)
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
    await repository.store_content(content)
    return Document(
        document_id=NonEmptyText("doc-1"),
        original_filename=NonEmptyText("spec.txt"),
        content_type=NonEmptyText("text/plain"),
        size_bytes=len(content),
        content_multihash=ContentMultihash(content_multihash(content)),
        status=DocumentStatus.CAPTURED,
    )


class TestReadingContentThroughThePort:
    @pytest.mark.asyncio
    async def test_it_gives_back_what_was_stored(
        self, repository: DocumentRepository
    ) -> None:
        document = await a_stored_document(repository)
        await repository.save(document)

        assert await repository.content_of(document) == CONTENT

    @pytest.mark.asyncio
    async def test_each_call_gives_a_stream_of_its_own(
        self, repository: DocumentRepository
    ) -> None:
        """julee#124: one stream handed to two readers left the second
        with nothing.

        Reading the first no longer takes anything from the second,
        because bytes are not consumed by being read. Both are still
        asked for, and both still checked, so a repository that started
        handing back something spendable would fail here.
        """
        document = await a_stored_document(repository)
        await repository.save(document)

        first = await repository.content_of(document)
        second = await repository.content_of(document)

        assert first == CONTENT
        assert second == CONTENT

    @pytest.mark.asyncio
    async def test_the_whole_content_comes_back(
        self, repository: DocumentRepository
    ) -> None:
        """julee#90: callers used to seek(0) before reading, which works
        on a BytesIO and raises on a response off a socket.

        There is nothing to seek. What comes back is the content, all of
        it, and a repository that returned a prefix would fail here.
        """
        document = await a_stored_document(repository)
        await repository.save(document)

        content = await repository.content_of(document)

        assert content == CONTENT

    @pytest.mark.asyncio
    async def test_content_named_but_not_stored_is_an_error(
        self, repository: DocumentRepository
    ) -> None:
        """Metadata naming content that is not there is an integrity
        failure, not an empty result. A partial write looks like this."""
        document = await a_stored_document(repository)
        await repository.save(document)
        never_stored = replace(
            document, content_multihash=ContentMultihash(content_multihash(b"other"))
        )

        with pytest.raises(ValueError, match="names content"):
            await repository.content_of(never_stored)
