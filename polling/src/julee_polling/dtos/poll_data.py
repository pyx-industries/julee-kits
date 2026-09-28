"""The messages PollDataUseCase takes and returns.

A request is what a driving adapter hands in and a response is what it
serialises back out, so both are pydantic models and both are
validated at the edge. This is the one package of the bounded context
that imports pydantic (ADR 001).
"""

from pydantic import BaseModel, ConfigDict

from julee_polling.domain.models.handoff import Handoff
from julee_polling.domain.models.polling_config import PollingConfig


class PollDataRequest(BaseModel):
    """Input for PollDataUseCase.

    The previous run arrives already read. A driving adapter knows
    where it keeps its own history — for the Temporal pipeline that is
    the last completion result — and the use case only needs what was
    seen last time, not the shape the runner stores it in.
    """

    model_config = ConfigDict(frozen=True)

    config: PollingConfig
    previous_hash: str | None = None
    previous_content: bytes | None = None


class PollDataResponse(BaseModel):
    """Output for PollDataUseCase.

    Reports what happened and decides nothing. Whether a poll counts
    as done is the caller's call, and ``handoff`` is what it needs to
    make it.
    """

    model_config = ConfigDict(frozen=True)

    endpoint_id: str
    content_hash: str | None
    content: str
    polled_at: str
    polled_successfully: bool
    new_items_found: bool
    items_notified: int
    handoff: Handoff
    handoff_info: tuple[str, ...] = ()
