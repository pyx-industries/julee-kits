"""Running the content naming migration against a MinIO store.

The decisions live in :mod:`julee_ceap.maintenance.content_multihash`.
This reads and writes, and is the only part that needs a store to
exercise.

Two operations, and the first is the one to reach for:

``survey`` reads every content object, classifies it, and reports. It
writes nothing, so it is safe against production and safe to run on a
schedule to answer "is this deployment still on the old naming?".

``migrate`` writes each legacy object's content under its current name
and repoints the metadata that referred to it. It deletes nothing: the
legacy objects stay until someone reaps them, which is what makes an
interrupted or mistaken run recoverable.
"""

import io
import json
import logging
from dataclasses import dataclass, field

from julee.integrations.minio.client import MinioClient

from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.maintenance.content_multihash import (
    Naming,
    classify,
    metadata_rewrites,
    unresolved_content_names,
)

__all__ = ["Survey", "migrate", "survey"]

logger = logging.getLogger("julee_ceap.maintenance.migrate")

CONTENT_BUCKET = "documents-content"
METADATA_BUCKET = "documents"


@dataclass(frozen=True)
class Survey:
    """What one pass over both buckets found."""

    current: tuple[str, ...] = ()
    legacy: tuple[str, ...] = ()
    unknown: tuple[str, ...] = ()
    renamings: dict[str, str] = field(default_factory=dict)
    """Legacy name to the name its content should be stored under."""

    documents: tuple[tuple[str, str], ...] = ()
    """Document id paired with the content name it holds."""

    @property
    def referenced_legacy(self) -> tuple[str, ...]:
        """Legacy names a document still points at.

        The migration is additive, so a migrated store keeps its legacy
        objects. "Are there old objects?" would therefore never come
        back clean, and is not the question anyone has. The question is
        whether anything still depends on the old naming.
        """
        held = {stored for _, stored in self.documents}
        return tuple(name for name in self.legacy if name in held)

    @property
    def orphaned_legacy(self) -> tuple[str, ...]:
        """Legacy objects nothing points at any more. Safe to reap, by
        hand, once somebody is satisfied the migration held."""
        held = {stored for _, stored in self.documents}
        return tuple(name for name in self.legacy if name not in held)

    @property
    def needs_migration(self) -> bool:
        return bool(self.referenced_legacy)

    def summary(self) -> str:
        return (
            f"{len(self.current)} current, {len(self.legacy)} legacy "
            f"({len(self.referenced_legacy)} still referenced), "
            f"{len(self.unknown)} unrecognised"
        )


def _object_names(client: MinioClient, bucket: str) -> list[str]:
    return [obj.object_name for obj in client.list_objects(bucket_name=bucket)]


def _read(client: MinioClient, bucket: str, name: str) -> bytes:
    response = client.get_object(bucket_name=bucket, object_name=name)
    try:
        data: bytes = response.read()
        return data
    finally:
        response.close()
        response.release_conn()


def _documents(client: MinioClient) -> tuple[tuple[str, str], ...]:
    """Each document id with the content name it holds."""
    found = []
    for document_id in _object_names(client, METADATA_BUCKET):
        raw = json.loads(_read(client, METADATA_BUCKET, document_id))
        stored = raw.get("content_multihash")
        if isinstance(stored, str):
            found.append((document_id, stored))
    return tuple(found)


def survey(client: MinioClient) -> Survey:
    """Classify every content object and read what points at it.

    Writes nothing, so it is safe against production and safe to run on
    a schedule.

    Args:
        client: The store to read

    Returns:
        What was found, including the renaming each legacy object needs
    """
    current: list[str] = []
    legacy: list[str] = []
    unknown: list[str] = []
    renamings: dict[str, str] = {}

    for name in _object_names(client, CONTENT_BUCKET):
        content = _read(client, CONTENT_BUCKET, name)
        match classify(name, content):
            case Naming.CURRENT:
                current.append(name)
            case Naming.LEGACY:
                legacy.append(name)
                renamings[name] = content_multihash(content)
            case Naming.UNKNOWN:
                unknown.append(name)

    return Survey(
        current=tuple(current),
        legacy=tuple(legacy),
        unknown=tuple(unknown),
        renamings=renamings,
        documents=_documents(client),
    )


def migrate(client: MinioClient, *, dry_run: bool = False) -> Survey:
    """Give every legacy object its current name and repoint metadata.

    Additive: content is written under the new name before any metadata
    changes, and nothing is deleted. Safe to interrupt and safe to
    repeat — a second run surveys CURRENT and does nothing.

    Args:
        client: The store to migrate
        dry_run: Report what would change and change nothing

    Returns:
        The survey the migration acted on

    Raises:
        RuntimeError: If a document still names content the store does
            not hold once the migration has run
    """
    found = survey(client)
    logger.info("Content survey: %s", found.summary())

    if found.unknown:
        logger.warning(
            "Leaving %d object(s) alone: their name is neither the sha256 "
            "multihash of their content nor the pre-#44 double hash. %s",
            len(found.unknown),
            ", ".join(sorted(found.unknown)[:5]),
        )

    if not found.needs_migration:
        logger.info("Nothing to migrate: no document names a legacy object")
        return found

    rewrites = metadata_rewrites(found.documents, found.renamings)

    if dry_run:
        logger.info(
            "Dry run: would copy %d object(s) and repoint %d document(s)",
            len(found.legacy),
            len(rewrites),
        )
        return found

    # Content first. A document repointed before its content exists
    # under the new name would be unresolvable for as long as the run
    # took, and unrecoverable if the run stopped in between.
    for legacy_name in found.legacy:
        content = _read(client, CONTENT_BUCKET, legacy_name)
        client.put_object(
            bucket_name=CONTENT_BUCKET,
            object_name=found.renamings[legacy_name],
            data=io.BytesIO(content),
            length=len(content),
        )

    for document_id, stored, wanted in rewrites:
        raw = json.loads(_read(client, METADATA_BUCKET, document_id))
        raw["content_multihash"] = wanted
        encoded = json.dumps(raw).encode("utf-8")
        client.put_object(
            bucket_name=METADATA_BUCKET,
            object_name=document_id,
            data=io.BytesIO(encoded),
            length=len(encoded),
            content_type="application/json",
        )
        logger.info("Repointed %s from %s to %s", document_id, stored, wanted)

    # Ask the store, not the run. A migration that reports success by
    # counting its own writes is a check sharing the writer's route.
    after = [(document_id, wanted) for document_id, _, wanted in rewrites] + [
        (document_id, stored)
        for document_id, stored in found.documents
        if stored not in found.renamings
    ]
    if missing := unresolved_content_names(
        after, _object_names(client, CONTENT_BUCKET)
    ):
        raise RuntimeError(
            "Migration finished with documents naming content that is not "
            "in the store:\n" + "\n".join(f"  {m}" for m in missing)
        )

    logger.info(
        "Migrated %d object(s), repointed %d document(s). The legacy "
        "objects are still there; nothing was deleted.",
        len(found.legacy),
        len(rewrites),
    )
    return found
