"""What a PollingResult is when Temporal hands it back.

``PollingResult.content`` is bytes, and bytes do not survive JSON. So
the entity carried a validator that turned a list of integers back into
bytes, with a comment saying Temporal may serialise them that way.

That was a serialisation concern living in a domain entity, and it was
a workaround: the workflow proxy called ``execute_activity`` without
``result_type``, so the converter was given no type, answered with a
dict, and the bytes arrived as whatever JSON could carry. julee 0.11.3
passes the type, and the converter reconstructs the bytes itself.

These tests are what the validator's removal rests on (julee-kits#68,
pyx-industries/julee#142). Without them the removal would be protected
only incidentally — by ``hashlib.sha256`` raising TypeError somewhere
inside the pipeline tests — which is a long way from the code that
would be wrong.
"""

import pytest
from temporalio.contrib.pydantic import pydantic_data_converter

from julee_polling.domain.values.polling_config import PollingResult

pytestmark = pytest.mark.unit

# What a polled endpoint returns in practice, and what this can carry.
# Not arbitrary binary: see the last class in this module.
CONTENT = b'{"items": [1, 2, 3], "next": null}\n'


async def round_trip(result: PollingResult) -> PollingResult:
    """A PollingResult through the converter and back, with its type.

    Args:
        result: The entity to encode

    Returns:
        What the converter makes of it, decoding into PollingResult
    """
    payloads = await pydantic_data_converter.encode([result])
    decoded = await pydantic_data_converter.decode(payloads, [PollingResult])
    # decode answers list[Any]: what it gives back is the question these
    # tests are asking, so the assertions do the narrowing rather than
    # an annotation asserting the answer in advance.
    returned: PollingResult = decoded[0]
    return returned


class TestContentSurvivesTheBoundary:
    """The property the deleted validator was compensating for."""

    @pytest.mark.asyncio
    async def test_content_comes_back_as_bytes(self) -> None:
        """Not a list of integers, and not a string."""
        returned = await round_trip(PollingResult(success=True, content=CONTENT))

        assert isinstance(returned.content, bytes)

    @pytest.mark.asyncio
    async def test_content_comes_back_unchanged(self) -> None:
        returned = await round_trip(PollingResult(success=True, content=CONTENT))

        assert returned.content == CONTENT

    @pytest.mark.asyncio
    async def test_the_whole_entity_comes_back(self) -> None:
        """A dict would satisfy neither of the assertions above by
        accident: it has no attributes at all. This says which failure a
        reader is looking at."""
        returned = await round_trip(PollingResult(success=True, content=CONTENT))

        assert isinstance(returned, PollingResult)

    @pytest.mark.asyncio
    async def test_empty_content_comes_back_as_empty_bytes(self) -> None:
        """b"" is falsy, and a coercion written around truthiness would
        have turned it into something else."""
        returned = await round_trip(PollingResult(success=True, content=b""))

        assert returned.content == b""

    @pytest.mark.asyncio
    async def test_polled_at_comes_back_as_a_datetime(self) -> None:
        """The same property, for the other field JSON cannot carry. The
        use case calls .isoformat() on it."""
        returned = await round_trip(PollingResult(success=True, content=CONTENT))

        assert returned.polled_at.tzinfo is not None


class TestContentThatIsNotText:
    """A limitation this found, older than the change that found it.

    ``content`` is annotated bytes and holds whatever an endpoint
    returned. Pydantic serialises bytes to JSON as utf-8 text, so
    content that is not valid utf-8 — a gzip body, an image, protobuf —
    cannot be encoded at all, and the failure is on the way out rather
    than on the way back.

    The validator deleted in julee-kits#68 never helped with this: it
    ran on the way in. So this is neither caused nor fixed here, and it
    is pinned rather than left to be rediscovered. Tracked in
    julee-kits#73.
    """

    @pytest.mark.asyncio
    async def test_binary_content_cannot_cross_the_boundary_yet(self) -> None:
        """Delete this test when julee-kits#73 makes it wrong."""
        png = b"\x89PNG\r\n\x1a\n\xff\xd8"

        with pytest.raises(Exception, match="utf-8"):
            await round_trip(PollingResult(success=True, content=png))
