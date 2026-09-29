"""What a query may say about how it wants to be run.

It was ``Mapping[str, Any]``, and the Any was the whole problem: a
driven port carrying it says the domain has no idea what crosses it.
These tests pin the three knobs that are actually read, and the shape
the persisted fixtures are already written in.
"""

import pytest
from pydantic import TypeAdapter

from julee_ceap.domain.values.query_metadata import QueryMetadata

pytestmark = pytest.mark.unit


class TestWhatItHolds:
    """Three knobs, each optional."""

    def test_it_says_nothing_by_default(self) -> None:
        """A query that does not tune anything leaves it to the adapter."""
        metadata = QueryMetadata()

        assert metadata.model is None
        assert metadata.max_tokens is None
        assert metadata.temperature is None

    def test_it_holds_what_the_fixtures_set(self) -> None:
        """max_tokens and temperature are what the shipped queries use."""
        metadata = QueryMetadata(max_tokens=3000, temperature=0.1)

        assert metadata.max_tokens == 3000
        assert metadata.temperature == 0.1

    def test_two_with_the_same_contents_are_the_same_one(self) -> None:
        """It is a value (ADR 018), so equality is by contents."""
        assert QueryMetadata(max_tokens=10) == QueryMetadata(max_tokens=10)


class TestPersistedShape:
    """What is already in MinIO must still load."""

    def test_it_round_trips(self) -> None:
        """Through the adapter the repositories serialise with."""
        adapter = TypeAdapter(QueryMetadata)
        original = QueryMetadata(model="claude-sonnet-4-5", max_tokens=4000)

        assert adapter.validate_json(adapter.dump_json(original)) == original

    def test_it_reads_the_shape_the_fixtures_are_written_in(self) -> None:
        """The stored objects are a plain mapping of these keys."""
        found = TypeAdapter(QueryMetadata).validate_python(
            {"max_tokens": 3000, "temperature": 0.1}
        )

        assert found == QueryMetadata(max_tokens=3000, temperature=0.1)

    def test_an_empty_mapping_reads_as_nothing_set(self) -> None:
        """Queries persisted before this carried {} rather than null."""
        assert TypeAdapter(QueryMetadata).validate_python({}) == QueryMetadata()
