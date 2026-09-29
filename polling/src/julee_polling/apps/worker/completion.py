"""What one run of the pipeline leaves for the next one.

Temporal hands a scheduled workflow its previous run's result, and this
pipeline uses that as the baseline it compares against: the hash and
content it last saw. So this is the pipeline talking to its future self,
across deploys, through workflow history.

It was ``dict[str, Any]``, written in one place and read in another with
``.get()``. That fails silently and in the worst direction: a key
renamed on the writing side reads back as no baseline at all, which
makes every run report new data and notify again. Nothing would have
said so.

Not in dtos/: that package holds the messages a use case takes and
returns. This is the pipeline's own record, and no caller reads it.

The field names and nesting are exactly what was written before, because
completions already in Temporal's history have to keep loading. Strict
about the half that is read back and lenient about the half that is
not, so an older completion still yields its baseline.
"""

from pydantic import BaseModel, ConfigDict


class PollingRecord(BaseModel):
    """What the endpoint was seen to hold.

    This is the half the next run reads.
    """

    model_config = ConfigDict(frozen=True)

    content_hash: str | None
    """The hash of what was seen, or None if nothing was."""
    content: str
    """What was seen, as text. Empty when there was nothing."""
    polled_at: str
    """When it was polled."""


class DetectionRecord(BaseModel):
    """What was made of it.

    Written for whoever reads the history; never read back. Every field
    has a default for that reason: a completion written by an older
    version, before handoff was reported, must still yield its baseline
    rather than being refused over a half nothing reads.
    """

    model_config = ConfigDict(frozen=True)

    has_new_data: bool = False
    """Whether this run found anything new."""
    current_hash: str | None = None
    """The baseline this run recorded, which may be the previous one."""
    handoff: str = ""
    """What became of the obligation to notify."""
    handoff_info: tuple[str, ...] = ()
    """What the handler said about it."""


class PipelineCompletion(BaseModel):
    """One run's result, as Temporal stores it."""

    model_config = ConfigDict(frozen=True)

    polling_result: PollingRecord
    """The baseline. Required, because this is the half that is read
    back: if a rename makes it stop fitting, that must be loud."""
    detection_result: DetectionRecord = DetectionRecord()
    endpoint_id: str = ""
    completed_at: str = ""
