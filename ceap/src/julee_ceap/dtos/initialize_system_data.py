"""The messages initialize system data takes and returns.

A request is what a driving adapter hands in and a response is what it
serialises back out, so both are pydantic models. This is the one
package of the bounded context that imports pydantic (ADR 001).
"""

from pydantic import BaseModel


class InitializeSystemDataRequest(BaseModel):
    """Input for InitializeSystemDataUseCase.

    Nothing: what a system starts with is the system data service's to
    say, not a caller's.
    """


class Seeded(BaseModel):
    """How many of one kind of thing were created, and how many were there."""

    created: int
    already_there: int

    @property
    def total(self) -> int:
        """How many the service offered."""
        return self.created + self.already_there


class InitializeSystemDataResponse(BaseModel):
    """Output for InitializeSystemDataUseCase.

    This was empty, and the use case wrote what it had done into 39 log
    lines instead. A caller could not tell a run that created everything
    from one that found everything already there — which is the one thing
    it wants to know when initialising twice.

    A use case reports; an adapter logs (ADR 017).
    """

    knowledge_service_configs: Seeded
    knowledge_service_queries: Seeded
    example_documents: Seeded
    assembly_specifications: Seeded

    @property
    def created_anything(self) -> bool:
        """Whether this run changed the system at all."""
        return any(
            seeded.created
            for seeded in (
                self.knowledge_service_configs,
                self.knowledge_service_queries,
                self.example_documents,
                self.assembly_specifications,
            )
        )
