"""The messages initialize system data takes and returns.

A request is what a driving adapter hands in and a response is
what it serialises back out, so both are pydantic models. This
is the one package of the bounded context that imports pydantic
(ADR 001).
"""

from pydantic import BaseModel


class InitializeSystemDataRequest(BaseModel):
    pass


class InitializeSystemDataResponse(BaseModel):
    pass
