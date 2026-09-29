"""The messages extract assemble data takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel

from julee_ceap.domain.models import (
    Assembly,
)


class ExtractAssembleDataRequest(BaseModel):
    document_id: str
    assembly_specification_id: str


class ExtractAssembleDataResponse(BaseModel):
    assembly: Assembly
