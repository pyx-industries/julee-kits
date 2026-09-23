"""What every HCD repository can do, on top of julee's base.

Two things are true of every entity in this kit and of nothing in the
kernel, so they are declared once here rather than seven times below.

An HCD entity is authored in a document, so a repository can be asked
which entities came from a given document, and told to forget them —
that is what an incremental documentation build does when a file is
re-read.

And an HCD entity can be removed. julee's BaseRepository describes a
store that is written to and read from; it has no delete, because a
processing pipeline does not remove what it has recorded. A solution
being written down does: a persona nobody kept is deleted, not archived.
"""

from typing import Protocol, TypeVar, runtime_checkable

from julee.repositories.base import BaseRepository
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class HcdRepository(BaseRepository[T], Protocol[T]):
    """A repository of entities read out of, and written back into, documents."""

    async def delete(self, entity_id: str) -> bool:
        """Remove one entity.

        Args:
            entity_id: Identifier of the entity to remove

        Returns:
            True if an entity was removed, False if there was none
        """
        ...

    async def clear(self) -> None:
        """Forget everything.

        A Sphinx build starts from an empty repository each time it reads
        the whole project, rather than from whatever the last build left.
        """
        ...

    async def get_by_docname(self, docname: str) -> list[T]:
        """Every entity read out of one document.

        Args:
            docname: RST document name

        Returns:
            The entities that document defined
        """
        ...

    async def clear_by_docname(self, docname: str) -> int:
        """Forget everything one document defined.

        An incremental build re-reads a changed document, and what that
        document said before must go before what it says now arrives.

        Args:
            docname: RST document name

        Returns:
            How many entities were removed
        """
        ...
