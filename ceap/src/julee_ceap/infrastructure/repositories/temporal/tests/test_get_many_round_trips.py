"""A KnowledgeServiceQuery, several at once, through ceap's own proxy.

ExtractAssembleDataUseCase fetched its queries one get() at a time,
under a comment saying get_many's dict[str, KnowledgeServiceQuery |
None] came back from Temporal as dicts. It did, and the cause was the
workflow proxy decorator in julee refusing to hand a container type to
the converter. The use case calls get_many again now, and this is the
test that ceap's real proxy and activity names carry the real entity
-- Name, NonEmptyText and a QueryMetadata inside it -- across a real
WorkflowEnvironment and back as itself.

Not a unit test: the activity runs, the payload crosses, the converter
decodes. A mock of any of those would answer what it was told to.
"""

import uuid
from collections.abc import AsyncIterator
from dataclasses import dataclass

import pytest
from julee.core.values.text import Name, NonEmptyText
from julee.integrations.temporal.activities import collect_activities_from_instances
from julee.integrations.temporal.decorators import temporal_activity_registration
from temporalio import workflow
from temporalio.client import Client
from temporalio.contrib.pydantic import pydantic_data_converter
from temporalio.testing import WorkflowEnvironment
from temporalio.worker import Worker

from julee_ceap.domain.models.assembly_specification.knowledge_service_query import (
    KnowledgeServiceQuery,
)
from julee_ceap.domain.repositories.knowledge_service_query import (
    KnowledgeServiceQueryRepository,
)
from julee_ceap.domain.values.query_metadata import QueryMetadata
from julee_ceap.infrastructure.repositories.memory.knowledge_service_query import (
    MemoryKnowledgeServiceQueryRepository,
)
from julee_ceap.infrastructure.repositories.temporal.activity_names import (
    KNOWLEDGE_SERVICE_QUERY_ACTIVITY_BASE,
)
from julee_ceap.infrastructure.repositories.temporal.proxies import (
    WorkflowKnowledgeServiceQueryRepositoryProxy,
)

pytestmark = pytest.mark.integration

TASK_QUEUE = "ceap-get-many"


@temporal_activity_registration(KNOWLEDGE_SERVICE_QUERY_ACTIVITY_BASE)
class TemporalMemoryKnowledgeServiceQueryRepository(
    MemoryKnowledgeServiceQueryRepository
):
    """The memory repository behind the same activity names the worker uses."""


@dataclass(frozen=True)
class WhatCameBack:
    """What the workflow was handed for each id it asked for."""

    types: dict[str, str]
    names: dict[str, str]
    max_tokens: dict[str, int | None]


@workflow.defn
class AskForQueries:
    """get_many through the proxy, reporting the types and a field or two."""

    @workflow.run
    async def run(self, query_ids: list[str]) -> WhatCameBack:
        repo: KnowledgeServiceQueryRepository = (
            WorkflowKnowledgeServiceQueryRepositoryProxy()  # type: ignore[abstract]
        )
        found = await repo.get_many(query_ids)
        return WhatCameBack(
            types={k: type(v).__name__ for k, v in found.items()},
            names={k: str(v.name) for k, v in found.items() if v is not None},
            max_tokens={
                k: v.query_metadata.max_tokens
                for k, v in found.items()
                if v is not None
            },
        )


@pytest.fixture
async def env() -> AsyncIterator[WorkflowEnvironment]:
    """A time-skipping Temporal with the converter ceap's worker uses."""
    async with await WorkflowEnvironment.start_time_skipping(
        data_converter=pydantic_data_converter
    ) as started:
        yield started


async def test_get_many_hands_back_the_entities(env: WorkflowEnvironment) -> None:
    """Two real queries and one missing id, in one call."""
    repo = TemporalMemoryKnowledgeServiceQueryRepository()
    for query_id, tokens in (("q-1", 100), ("q-2", 200)):
        await repo.save(
            KnowledgeServiceQuery(
                query_id=NonEmptyText(query_id),
                name=Name(f"Query {query_id}"),
                knowledge_service_id=NonEmptyText("ks-1"),
                prompt=NonEmptyText("Extract the title"),
                query_metadata=QueryMetadata(max_tokens=tokens),
            )
        )
    client: Client = env.client

    async with Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[AskForQueries],
        activities=collect_activities_from_instances(repo),
    ):
        got = await client.execute_workflow(
            AskForQueries.run,
            ["q-1", "q-2", "nobody"],
            id=f"ask-{uuid.uuid4()}",
            task_queue=TASK_QUEUE,
        )

    assert got.types == {
        "q-1": "KnowledgeServiceQuery",
        "q-2": "KnowledgeServiceQuery",
        "nobody": "NoneType",
    }
    assert got.names == {"q-1": "Query q-1", "q-2": "Query q-2"}
    assert got.max_tokens == {"q-1": 100, "q-2": 200}
