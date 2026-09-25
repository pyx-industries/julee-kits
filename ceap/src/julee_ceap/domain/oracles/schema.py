from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SchemaOracle(Protocol):
    """Where a JSON Schema named by URL is fetched from.

    An oracle rather than a repository (ADR 016): it is bound to no entity
    of this context, because what comes back is the schema author's JSON
    and not something CEAP has modelled. Calling it a repository would
    claim an aggregate it does not have.

    Reached from workflow code through an activity. It performs I/O, so
    its answer can differ between replays.
    """

    async def fetch(self, url: str) -> dict[str, Any]:
        """Fetch and return the JSON document at url."""
        ...
