"""System seed data, read from fixture files shipped with the kit.

yaml, json and pathlib live here. They were imported by a use case,
along with eight methods that read files and built entities from what
they found — work that was always an adapter's.

Building the entities here rather than handing back parsed dicts is what
closes a class of bug the old code carried: every field went across as
whatever the file held, so a field declared ``NonEmptyText`` got a plain
str and ``assembly_types`` got a list where its annotation says tuple.
Pydantic converted both on the way in. A frozen dataclass does not, so
they are built as what they are, here, once.
"""

import json
import logging
from collections.abc import Mapping
from dataclasses import fields
from pathlib import Path
from typing import Any

import yaml
from julee.core.observability import log_extra
from julee.core.values.text import Name, NonEmptyText
from julee.core.witnesses.clock import ClockWitness, SystemClockWitness
from pydantic import TypeAdapter

from julee_ceap.domain.models.assembly_specification import (
    AssemblySpecification,
    AssemblySpecificationStatus,
    KnowledgeServiceQuery,
)
from julee_ceap.domain.models.knowledge_service_config import (
    KnowledgeServiceConfig,
    ServiceApi,
)
from julee_ceap.domain.values.query_metadata import QueryMetadata
from julee_ceap.domain.values.schema import JsonSchema
from julee_ceap.domain.values.seed import DocumentSeed

logger = logging.getLogger(__name__)

FIXTURES = Path(__file__).parent.parent.parent.parent / "fixtures"
"""Where the kit keeps the data a system starts with."""


class FixtureSystemDataService:
    """A SystemDataService reading the kit's own fixture files."""

    def __init__(
        self,
        fixtures: Path | None = None,
        clock_witness: ClockWitness | None = None,
    ) -> None:
        """Start against a fixture directory.

        Args:
            fixtures: Where to read from. Defaults to the kit's own.
            clock_witness: What to stamp entities with. Defaults to the
                system clock.
        """
        self._fixtures = fixtures or FIXTURES
        self._clock: ClockWitness = clock_witness or SystemClockWitness()

    async def knowledge_service_configs(self) -> tuple[KnowledgeServiceConfig, ...]:
        """Every knowledge service configuration the system starts with.

        Returns:
            The configurations, built and ready to save

        Raises:
            ValueError: If a configuration names a service API that is
                not one
        """
        now = self._clock.now()
        found = []
        for entry in self._read("knowledge_service_configs.yaml", "knowledge_services"):
            try:
                api = ServiceApi(entry["service_api"])
            except ValueError as not_an_api:
                raise ValueError(
                    f"Invalid service_api {entry['service_api']!r}. Must be "
                    f"one of: {[api.value for api in ServiceApi]}"
                ) from not_an_api
            found.append(
                KnowledgeServiceConfig(
                    knowledge_service_id=NonEmptyText(entry["knowledge_service_id"]),
                    name=Name(entry["name"]),
                    description=NonEmptyText(entry["description"]),
                    service_api=api,
                    created_at=now,
                    updated_at=now,
                )
            )
        logger.debug(
            "Read knowledge service configs", extra=log_extra(count=len(found))
        )
        return tuple(found)

    async def knowledge_service_queries(self) -> tuple[KnowledgeServiceQuery, ...]:
        """Every knowledge service query the system starts with.

        Returns:
            The queries, built and ready to save
        """
        now = self._clock.now()
        found = tuple(
            KnowledgeServiceQuery(
                query_id=NonEmptyText(entry["query_id"]),
                name=Name(entry["name"]),
                knowledge_service_id=NonEmptyText(entry["knowledge_service_id"]),
                prompt=NonEmptyText(entry["prompt"]),
                assistant_prompt=entry["assistant_prompt"],
                query_metadata=_query_metadata(entry.get("query_metadata")),
                created_at=now,
                updated_at=now,
            )
            for entry in self._read(
                "knowledge_service_queries.yaml", "knowledge_service_queries"
            )
        )
        logger.debug(
            "Read knowledge service queries", extra=log_extra(count=len(found))
        )
        return found

    async def assembly_specifications(self) -> tuple[AssemblySpecification, ...]:
        """Every assembly specification the system starts with.

        A status the file does not recognise falls back to active, as it
        did before, rather than refusing the whole fixture.

        Returns:
            The specifications, built and ready to save
        """
        now = self._clock.now()
        found = []
        for entry in self._read(
            "assembly_specifications.json", "assembly_specifications"
        ):
            found.append(
                AssemblySpecification(
                    assembly_specification_id=NonEmptyText(
                        entry["assembly_specification_id"]
                    ),
                    name=Name(entry["name"]),
                    applicability=NonEmptyText(entry["applicability"]),
                    jsonschema=JsonSchema(entry["jsonschema"]),
                    knowledge_service_queries={
                        pointer: NonEmptyText(query)
                        for pointer, query in entry.get(
                            "knowledge_service_queries", {}
                        ).items()
                    },
                    status=_a_status(entry.get("status")),
                    version=NonEmptyText(entry.get("version", "1.0")),
                    created_at=now,
                    updated_at=now,
                )
            )
        logger.debug("Read assembly specifications", extra=log_extra(count=len(found)))
        return tuple(found)

    async def example_documents(self) -> tuple[DocumentSeed, ...]:
        """Every example document the system starts with, and its content.

        Returns:
            What each document should be, and the bytes it is of

        Raises:
            FileNotFoundError: If a document names content that is not
                shipped beside it
        """
        found = []
        for entry in self._read("documents.yaml", "documents"):
            found.append(
                DocumentSeed(
                    document_id=NonEmptyText(entry["document_id"]),
                    original_filename=NonEmptyText(entry["original_filename"]),
                    content_type=NonEmptyText(entry["content_type"]),
                    content=self._content_of(entry),
                )
            )
        logger.debug("Read example documents", extra=log_extra(count=len(found)))
        return tuple(found)

    def _read(self, filename: str, key: str) -> list[dict[str, Any]]:
        """The entries one fixture file lists under one key.

        Each file is a mapping with a single key naming what it holds, so
        the key is given rather than guessed: a file whose key is
        misspelled should be reported, not read as empty.

        Args:
            filename: The file to read, relative to the fixtures directory
            key: The top-level key the entries sit under

        Returns:
            One mapping per entry

        Raises:
            FileNotFoundError: If the file is not there
            ValueError: If it is not readable, or lists nothing under that key
        """
        path = self._fixtures / filename
        if not path.exists():
            raise FileNotFoundError(f"Fixture file not found: {path}")
        text = path.read_text(encoding="utf-8")
        try:
            data = json.loads(text) if path.suffix == ".json" else yaml.safe_load(text)
        except (yaml.YAMLError, json.JSONDecodeError) as unreadable:
            raise ValueError(
                f"Fixture file {path} is not readable: {unreadable}"
            ) from unreadable
        entries = data.get(key) if isinstance(data, dict) else None
        if not isinstance(entries, list):
            raise ValueError(f"Fixture file {path} must hold a list under {key!r}")
        return entries

    def _content_of(self, entry: dict[str, Any]) -> bytes:
        """The bytes a document entry names.

        An entry either carries its content inline or is named after a
        file shipped beside the fixtures.

        Args:
            entry: One document entry

        Returns:
            The content

        Raises:
            FileNotFoundError: If it names a file that is not there
        """
        inline = entry.get("content")
        if isinstance(inline, str):
            return inline.encode("utf-8")
        if inline is not None:
            return bytes(inline)
        path = self._fixtures / str(entry["original_filename"])
        if not path.exists():
            raise FileNotFoundError(
                f"Fixture file {path} not found for document {entry['document_id']}"
            )
        return path.read_bytes()


def _a_status(written: str | None) -> AssemblySpecificationStatus:
    """The status a fixture asked for, or active.

    Args:
        written: What the file said, if it said anything

    Returns:
        The status, defaulting to active for a value that is not one
    """
    if written is None:
        return AssemblySpecificationStatus.ACTIVE
    try:
        return AssemblySpecificationStatus(written)
    except ValueError:
        logger.warning(
            "Fixture names a status that is not one; using active",
            extra=log_extra(status=written),
        )
        return AssemblySpecificationStatus.ACTIVE


def _query_metadata(written: Mapping[str, object] | None) -> QueryMetadata:
    """How a fixture's query asked to be run.

    The shipped files set max_tokens and temperature. A key that is not
    one of the three is dropped with a warning rather than silently, so
    a typo in a fixture is visible — the old open mapping would have
    carried ``temperture: 0.1`` all the way to the adapter, which would
    have ignored it just as quietly.

    Args:
        written: The query_metadata mapping a fixture entry carried

    Returns:
        The value the domain speaks, empty if the fixture said nothing
    """
    if not written:
        return QueryMetadata()
    named = {f.name for f in fields(QueryMetadata)}
    unknown = sorted(set(written) - named)
    if unknown:
        logger.warning(
            "Fixture names query metadata nothing reads; ignoring",
            extra=log_extra(unknown=unknown),
        )
    return TypeAdapter(QueryMetadata).validate_python(
        {k: v for k, v in written.items() if k in named}
    )
