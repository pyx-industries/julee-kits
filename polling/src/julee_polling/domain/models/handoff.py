"""What became of the obligation to notify.

Finding new data puts the poller under an obligation to tell whoever
holds that role. It has no business knowing what they do about it —
screen it, file it, ignore it — only whether it managed to tell them.

So there are three outcomes and they are about the handoff, never
about the work that follows it.
"""

from enum import StrEnum


class Handoff(StrEnum):
    """Whether the obligation to notify was discharged."""

    NOT_NEEDED = "not_needed"
    """There was nothing to tell: no new data, or no usable poll."""

    DISCHARGED = "discharged"
    """They were told, and answered.

    Covers every answer. *Wilco* and *unable* are both replies from
    someone who received the message, and the difference between them
    is theirs to act on, not ours.
    """

    FAILED = "failed"
    """They were not told.

    The obligation stands, so nothing downstream may treat this poll
    as done.
    """
