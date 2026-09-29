from typing import Protocol, runtime_checkable

from julee_ceap.domain.models.schema import JsonSchema


@runtime_checkable
class SchemaOracle(Protocol):
    """Where a JSON Schema named by URL is fetched from.

    An oracle rather than a repository (ADR 016): it is bound to no
    entity, because a schema is a value this context reads rather than an
    aggregate it keeps. Calling it a repository would claim an aggregate
    it does not have.

    It returned ``dict[str, Any]``, and the docstring said that was
    because a fetched schema is "not something CEAP has modelled". It is
    modelled now — :class:`~julee_ceap.domain.models.schema.JsonSchema` —
    which is what let the Any go.

    Reached from workflow code through an activity. It performs I/O, so
    its answer can differ between replays.
    """

    async def fetch(self, url: str) -> JsonSchema:
        """Fetch and return the schema at url.

        Args:
            url: Where the schema is published

        Returns:
            The schema as fetched
        """
        ...
