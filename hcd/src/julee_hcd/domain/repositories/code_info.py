"""CodeInfoRepository protocol."""

from typing import Protocol, runtime_checkable

from julee.core.entities.bounded_context_info import BoundedContextInfo
from julee.repositories.base import RepositoryOf


@runtime_checkable
class CodeInfoRepository(RepositoryOf[BoundedContextInfo], Protocol):
    """Where the bounded contexts discovered in the code are read from.

    Filled by scanning the solution's source for the layers ADR 001
    describes, so nothing here is authored and nothing is saved.

    ``RepositoryOf`` rather than ``BaseRepository``: there is no CRUD
    here, and the two were the same thing until ``RepositoryOf`` split
    saying what a repository holds from offering to write it.

    ``BoundedContextInfo`` is a kernel entity, which doctrine counted as
    no entity at all until julee #237 — so this read as bound to nothing,
    indistinguishable from a protocol holding nothing. Declaring it is
    what makes the binding checkable rather than merely true.
    """

    async def list_all(self) -> list[BoundedContextInfo]:
        """Every bounded context found in the code."""
        ...
