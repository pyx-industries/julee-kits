"""The messages PollDataUseCase takes and returns.

A request is what a driving adapter hands in and a response is what it
serialises back out, so both are pydantic models and both are
validated at the edge. This is the one package of the bounded context
that imports pydantic (ADR 001).
"""

from pydantic import BaseModel, ConfigDict

from julee_polling.domain.models.polling_config import PollingConfig


class PollDataRequest(BaseModel):
    """Input for PollDataUseCase."""

    model_config = ConfigDict(frozen=True)

    config: PollingConfig
    previous_completion: dict | None = None


class PollDataResponse(BaseModel):
    """Output for PollDataUseCase."""

    model_config = ConfigDict(frozen=True)

    endpoint_id: str
    content_hash: str
    content: str
    polled_at: str
    new_items_found: bool
    items_processed: int
