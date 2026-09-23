"""The handler protocol the repositories call."""

from typing import Protocol, TypeVar, runtime_checkable

from julee_hcd.domain.models.base import Authored

# A handler only ever receives an entity, so it is contravariant in T.
T_contra = TypeVar("T_contra", bound=Authored, contravariant=True)


@runtime_checkable
class EntityHandler(Protocol[T_contra]):
    """Something to do after an entity is saved or deleted."""

    async def handle(self, entity: T_contra) -> None:
        """React to the entity having been saved or deleted.

        Args:
            entity: The entity that was saved, or that was deleted
        """
        ...
