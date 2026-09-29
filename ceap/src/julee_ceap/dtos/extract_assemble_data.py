"""The messages extract assemble data takes and returns.

A request is what a driving adapter hands in and a response is what it
serialises back out, so both are pydantic models. This is the one
package of the bounded context that imports pydantic (ADR 001).

The response described the assembly by holding one: ``assembly:
Assembly``. A response is a message, and a message that is a wrapper
around an entity has not been created *from* it — the entity's shape is
the message's shape, and a driving adapter reading the message depends
on the domain.

That matters more here than at the API, because ExtractAssembleWorkflow
returned it and Temporal writes a workflow's result into history. The
entity's shape became a durable contract, replayed long after the code
that wrote it.
"""

from pydantic import BaseModel

from julee_ceap.domain.models import Assembly, AssemblyStatus


class ExtractAssembleDataRequest(BaseModel):
    document_id: str
    assembly_specification_id: str


class ExtractAssembleDataResponse(BaseModel):
    """What came of assembling a document.

    The three things a caller acts on: what was made, what came out of
    it, and whether it got there.
    """

    assembly_id: str
    assembled_document_id: str | None
    status: AssemblyStatus

    @classmethod
    def of(cls, assembly: Assembly) -> "ExtractAssembleDataResponse":
        """The message for one assembly.

        Args:
            assembly: The entity to describe

        Returns:
            What the caller is told
        """
        return cls(
            assembly_id=str(assembly.assembly_id),
            assembled_document_id=(
                str(assembly.assembled_document_id)
                if assembly.assembled_document_id
                else None
            ),
            status=assembly.status,
        )
