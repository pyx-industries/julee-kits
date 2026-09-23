"""CodeInfoRepository protocol."""

from typing import Protocol, runtime_checkable

from julee.core.entities.bounded_context_info import BoundedContextInfo


@runtime_checkable
class CodeInfoRepository(Protocol):
    """Where the bounded contexts discovered in the code are read from.

    Filled by scanning the solution's source for the layers ADR 001
    describes, so nothing here is authored and nothing is saved.
    """

    async def list_all(self) -> list[BoundedContextInfo]:
        """Every bounded context found in the code."""
        ...
