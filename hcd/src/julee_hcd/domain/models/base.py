"""What every authored HCD entity carries besides its own content.

A persona, an epic, a journey and the rest are written in RST and read
back out of it, so each one remembers which document it came from and
the prose that surrounded it. That is the same five fields every time,
which is why they live here rather than being restated seven times.

An entity derived from code rather than authored — a story read out of a
feature file — still has them, because it may later be written back into
a document alongside the ones that were authored.
"""

from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Authored:
    """An entity a person wrote into a document, and can be written back.

    The RST fields exist so a round-trip is lossless: reading a document
    into entities and writing it out again should give back the document,
    including the parts this kit does not model.

    Keyword-only, and so is every entity built on it. Its five fields all
    have defaults and every entity adds required ones after them, which a
    positional dataclass refuses. Nothing constructs one positionally.
    """

    solution_slug: str = ""
    """Slug of the solution this belongs to, for a site documenting more
    than one."""

    docname: str = ""
    """RST document this was read from, for incremental builds."""

    page_title: str = ""
    """Title of the document, when it differs from the entity's own."""

    preamble_rst: str = ""
    """Verbatim RST that preceded the directive, kept for round-trip."""

    epilogue_rst: str = ""
    """Verbatim RST that followed the directive, kept for round-trip."""
