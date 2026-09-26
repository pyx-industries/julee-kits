"""Tests for running the content naming migration against a store.

A fake MinIO rather than a mock, so these say what the store ends up
holding rather than which calls were made.
"""

import io
import json

import pytest
from julee.integrations.minio.testing import FakeMinioClient

from julee_ceap.domain.models.document.multihash import content_multihash
from julee_ceap.maintenance.content_multihash import legacy_content_multihash
from julee_ceap.maintenance.migrate import (
    CONTENT_BUCKET,
    METADATA_BUCKET,
    migrate,
    survey,
)

pytestmark = pytest.mark.unit

CONTENT = b"This is test content for document storage"
OTHER = b"Some entirely different content"


@pytest.fixture
def client() -> FakeMinioClient:
    fake = FakeMinioClient()
    fake.make_bucket(CONTENT_BUCKET)
    fake.make_bucket(METADATA_BUCKET)
    return fake


def put(fake: FakeMinioClient, bucket: str, name: str, data: bytes) -> None:
    fake.put_object(
        bucket_name=bucket,
        object_name=name,
        data=io.BytesIO(data),
        length=len(data),
    )


def a_document(fake: FakeMinioClient, document_id: str, multihash: str) -> None:
    raw = json.dumps(
        {
            "document_id": document_id,
            "original_filename": "test.txt",
            "content_type": "text/plain",
            "size_bytes": 41,
            "content_multihash": multihash,
            "status": "captured",
        }
    ).encode("utf-8")
    put(fake, METADATA_BUCKET, document_id, raw)


def stored_multihash(fake: FakeMinioClient, document_id: str) -> str:
    response = fake.get_object(bucket_name=METADATA_BUCKET, object_name=document_id)
    try:
        value: str = json.loads(response.read())["content_multihash"]
        return value
    finally:
        response.close()
        response.release_conn()


def content_names(fake: FakeMinioClient) -> set[str]:
    return {obj.object_name for obj in fake.list_objects(bucket_name=CONTENT_BUCKET)}


class TestSurveying:
    def test_a_store_written_after_the_fix_needs_nothing(
        self, client: FakeMinioClient
    ) -> None:
        put(client, CONTENT_BUCKET, content_multihash(CONTENT), CONTENT)

        found = survey(client)

        assert not found.needs_migration
        assert len(found.current) == 1

    def test_a_store_written_before_the_fix_is_detected(
        self, client: FakeMinioClient
    ) -> None:
        """The question the operator actually has: is this deployment on
        the old naming? Answered by reading, not by a version marker."""
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))

        found = survey(client)

        assert found.needs_migration
        assert found.renamings == {
            legacy_content_multihash(CONTENT): content_multihash(CONTENT)
        }

    def test_a_half_migrated_store_reports_both(self, client: FakeMinioClient) -> None:
        put(client, CONTENT_BUCKET, content_multihash(CONTENT), CONTENT)
        put(client, CONTENT_BUCKET, legacy_content_multihash(OTHER), OTHER)

        found = survey(client)

        assert len(found.current) == 1
        assert len(found.legacy) == 1

    def test_an_object_named_after_neither_is_reported_not_touched(
        self, client: FakeMinioClient
    ) -> None:
        put(client, CONTENT_BUCKET, "1220" + "f" * 64, CONTENT)

        found = survey(client)

        assert found.unknown == ("1220" + "f" * 64,)
        assert not found.needs_migration

    def test_surveying_writes_nothing(self, client: FakeMinioClient) -> None:
        """So it is safe against production and safe on a schedule."""
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        before = content_names(client)

        survey(client)

        assert content_names(client) == before


class TestMigrating:
    def test_the_content_gains_its_current_name(self, client: FakeMinioClient) -> None:
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))

        migrate(client)

        assert content_multihash(CONTENT) in content_names(client)

    def test_the_document_is_repointed(self, client: FakeMinioClient) -> None:
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))

        migrate(client)

        assert stored_multihash(client, "doc-1") == content_multihash(CONTENT)

    def test_nothing_is_deleted(self, client: FakeMinioClient) -> None:
        """The legacy object stays, so an interrupted or mistaken run is
        recoverable and the old names still resolve."""
        legacy = legacy_content_multihash(CONTENT)
        put(client, CONTENT_BUCKET, legacy, CONTENT)
        a_document(client, "doc-1", legacy)

        migrate(client)

        assert legacy in content_names(client)

    def test_running_it_twice_changes_nothing_the_second_time(
        self, client: FakeMinioClient
    ) -> None:
        """Idempotent, because the second run classifies the new object
        as CURRENT and finds no legacy name to act on."""
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))

        migrate(client)
        after_first = (content_names(client), stored_multihash(client, "doc-1"))
        migrate(client)

        assert (content_names(client), stored_multihash(client, "doc-1")) == after_first

    def test_a_run_interrupted_after_the_content_copy_completes_later(
        self, client: FakeMinioClient
    ) -> None:
        """Content is written before metadata is repointed, so a store
        stopped in between still resolves by the old name and a re-run
        finishes the job."""
        legacy = legacy_content_multihash(CONTENT)
        put(client, CONTENT_BUCKET, legacy, CONTENT)
        put(client, CONTENT_BUCKET, content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy)

        migrate(client)

        assert stored_multihash(client, "doc-1") == content_multihash(CONTENT)

    def test_two_documents_sharing_content_both_move(
        self, client: FakeMinioClient
    ) -> None:
        legacy = legacy_content_multihash(CONTENT)
        put(client, CONTENT_BUCKET, legacy, CONTENT)
        a_document(client, "doc-1", legacy)
        a_document(client, "doc-2", legacy)

        migrate(client)

        assert stored_multihash(client, "doc-1") == content_multihash(CONTENT)
        assert stored_multihash(client, "doc-2") == content_multihash(CONTENT)

    def test_a_document_already_current_is_not_disturbed(
        self, client: FakeMinioClient
    ) -> None:
        current = content_multihash(OTHER)
        put(client, CONTENT_BUCKET, current, OTHER)
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-current", current)
        a_document(client, "doc-legacy", legacy_content_multihash(CONTENT))

        migrate(client)

        assert stored_multihash(client, "doc-current") == current

    def test_a_dry_run_changes_nothing(self, client: FakeMinioClient) -> None:
        legacy = legacy_content_multihash(CONTENT)
        put(client, CONTENT_BUCKET, legacy, CONTENT)
        a_document(client, "doc-1", legacy)

        found = migrate(client, dry_run=True)

        assert found.needs_migration
        assert content_names(client) == {legacy}
        assert stored_multihash(client, "doc-1") == legacy

    def test_a_store_needing_nothing_is_left_entirely_alone(
        self, client: FakeMinioClient
    ) -> None:
        current = content_multihash(CONTENT)
        put(client, CONTENT_BUCKET, current, CONTENT)
        a_document(client, "doc-1", current)

        migrate(client)

        assert content_names(client) == {current}
        assert stored_multihash(client, "doc-1") == current


class TestAfterwards:
    def test_every_content_object_is_named_by_its_own_bytes(
        self, client: FakeMinioClient
    ) -> None:
        """The property that makes the result checkable without trusting
        the migration: ask the store, not the run."""
        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        put(client, CONTENT_BUCKET, legacy_content_multihash(OTHER), OTHER)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))
        a_document(client, "doc-2", legacy_content_multihash(OTHER))

        migrate(client)

        for document_id, content in [("doc-1", CONTENT), ("doc-2", OTHER)]:
            assert stored_multihash(client, document_id) == content_multihash(content)
            assert stored_multihash(client, document_id) in content_names(client)


class TestTheCommand:
    """The exit statuses a deployment check reads."""

    def test_survey_exits_nonzero_when_the_old_naming_is_present(
        self, client: FakeMinioClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """So `julee-ceap-maintenance survey` can gate a deploy."""
        from julee_ceap.maintenance import __main__

        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))
        monkeypatch.setattr(__main__, "_client", lambda: client)

        assert __main__.main(["survey"]) == 1

    def test_survey_exits_zero_on_a_current_store(
        self, client: FakeMinioClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from julee_ceap.maintenance import __main__

        put(client, CONTENT_BUCKET, content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", content_multihash(CONTENT))
        monkeypatch.setattr(__main__, "_client", lambda: client)

        assert __main__.main(["survey"]) == 0

    def test_survey_exits_zero_on_an_empty_store(
        self, client: FakeMinioClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from julee_ceap.maintenance import __main__

        monkeypatch.setattr(__main__, "_client", lambda: client)

        assert __main__.main(["survey"]) == 0

    def test_migrate_exits_zero_and_leaves_a_current_store(
        self, client: FakeMinioClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from julee_ceap.maintenance import __main__

        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))
        monkeypatch.setattr(__main__, "_client", lambda: client)

        assert __main__.main(["migrate"]) == 0
        assert __main__.main(["survey"]) == 0

    def test_a_dry_run_leaves_the_survey_still_objecting(
        self, client: FakeMinioClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from julee_ceap.maintenance import __main__

        put(client, CONTENT_BUCKET, legacy_content_multihash(CONTENT), CONTENT)
        a_document(client, "doc-1", legacy_content_multihash(CONTENT))
        monkeypatch.setattr(__main__, "_client", lambda: client)

        assert __main__.main(["migrate", "--dry-run"]) == 0
        assert __main__.main(["survey"]) == 1
