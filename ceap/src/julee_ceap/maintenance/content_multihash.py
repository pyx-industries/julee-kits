"""Telling a legacy content name from a current one, and fixing it.

Before #44, CEAP stored ``1220`` followed by sha256(sha256(content)) —
the ``multihash`` library hashes its argument, and it was being handed a
digest. It now stores ``1220`` followed by sha256(content).

The two are the same shape, so **a stored value cannot be classified by
looking at it**. It can be classified by looking at the content, and
that is what makes this migratable without anyone deciding anything: the
content bucket is keyed by the value under question and holds the
content, so every object answers for itself.

Four properties make it safe to run unattended:

*Decidable.* Exactly one of the two candidates matches a given object,
because a match of both would need sha256(c) == sha256(sha256(c)).

*Idempotent.* An object already stored under its current name is
classified CURRENT and skipped, so re-running does nothing.

*Additive.* The content is written under its new name before any
metadata is rewritten, and nothing is deleted. An interrupted run leaves
a store that still resolves by the old names.

*Self-verifying.* Afterwards, every content object's name is the sha256
multihash of the bytes stored under it, which is a property the store
can be asked about rather than a claim the migration makes.

Nothing here talks to MinIO. :mod:`julee_ceap.maintenance.migrate` does
that, and calls these.
"""

import hashlib
from collections.abc import Iterable, Mapping
from enum import StrEnum

from julee_ceap.domain.models.document.multihash import (
    SHA2_256_PREFIX,
    content_multihash,
)

__all__ = [
    "Naming",
    "classify",
    "legacy_content_multihash",
    "metadata_rewrites",
    "unresolved_content_names",
]


class Naming(StrEnum):
    """What a stored object's name says about when it was written."""

    CURRENT = "current"
    """The sha256 multihash of its content. Nothing to do."""

    LEGACY = "legacy"
    """The pre-#44 double hash. Its content needs a second name."""

    UNKNOWN = "unknown"
    """Neither. Reported and never touched: something else wrote it, or
    the bytes under the name are not the bytes that named it."""


def legacy_content_multihash(content: bytes) -> str:
    """The name this content had before #44.

    ``multihash.encode(digest, SHA2_256)`` hashed the digest it was
    given, so the stored value was the multihash of the digest rather
    than of the content.

    Args:
        content: The document's bytes

    Returns:
        The hex-encoded value the old code would have written
    """
    digest = hashlib.sha256(content).digest()
    return SHA2_256_PREFIX + hashlib.sha256(digest).hexdigest()


def classify(stored_name: str, content: bytes) -> Naming:
    """Which naming an object was stored under.

    Args:
        stored_name: The object's key in the content bucket
        content: The bytes stored under it

    Returns:
        CURRENT, LEGACY, or UNKNOWN
    """
    if stored_name == content_multihash(content):
        return Naming.CURRENT
    if stored_name == legacy_content_multihash(content):
        return Naming.LEGACY
    return Naming.UNKNOWN


def metadata_rewrites(
    documents: Iterable[tuple[str, str]],
    renamings: Mapping[str, str],
) -> list[tuple[str, str, str]]:
    """Which documents point at a name that has been superseded.

    Args:
        documents: Document id paired with its stored content_multihash
        renamings: Legacy name to current name, from the content pass

    Returns:
        Document id, the name it holds, and the name it should hold
    """
    return [
        (document_id, stored, renamings[stored])
        for document_id, stored in documents
        if stored in renamings
    ]


def unresolved_content_names(
    documents: Iterable[tuple[str, str]],
    content_names: Iterable[str],
) -> list[str]:
    """Documents naming content the store does not have.

    The check to run after a migration, and the reason it can be run
    unattended: it asks the store rather than trusting the run.

    Args:
        documents: Document id paired with its stored content_multihash
        content_names: Every key in the content bucket

    Returns:
        One sentence per document whose content cannot be found
    """
    available = set(content_names)
    return [
        f"{document_id} names content {stored}, which the store does not hold"
        for document_id, stored in documents
        if stored not in available
    ]
