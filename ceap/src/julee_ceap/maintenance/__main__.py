"""``python -m julee_ceap.maintenance`` — content naming maintenance.

    julee-ceap-maintenance survey    report, change nothing
    julee-ceap-maintenance migrate   give legacy content its current name

``survey`` is the one to run first, and the one to run on a schedule: it
answers "is this deployment still on the pre-#44 naming?" by reading the
store rather than by trusting a version marker.

``migrate`` is safe to run unattended — idempotent, additive, and it
verifies against the store afterwards rather than against its own
bookkeeping. It deletes nothing, so the legacy objects remain until
somebody decides to reap them.
"""

import argparse
import logging
import os
import sys

from julee.integrations.minio.client import MinioClient
from minio import Minio

from julee_ceap.maintenance.migrate import migrate, survey

__all__ = ["main"]


def _client() -> MinioClient:
    """The store this deployment points at, from the usual environment."""
    return Minio(
        endpoint=os.environ.get("MINIO_ENDPOINT", "localhost:9000"),
        access_key=os.environ.get("MINIO_ACCESS_KEY", "minioadmin"),
        secret_key=os.environ.get("MINIO_SECRET_KEY", "minioadmin"),
        secure=os.environ.get("MINIO_SECURE", "false").lower() == "true",
    )


def main(argv: list[str] | None = None) -> int:
    """Parse arguments and run.

    Returns:
        0 if nothing needs migrating or the migration succeeded, 1 if a
        survey found legacy objects, 2 if a migration failed
    """
    parser = argparse.ArgumentParser(prog="julee-ceap-maintenance")
    commands = parser.add_subparsers(dest="command", required=True)

    commands.add_parser(
        "survey",
        help="report how content is named here; writes nothing. Exits 1 "
        "if anything still carries the pre-#44 name, so it drops into a "
        "deployment check without ceremony",
    )
    migration = commands.add_parser(
        "migrate", help="give legacy content its current name; deletes nothing"
    )
    migration.add_argument(
        "--dry-run",
        action="store_true",
        help="report what would change and change nothing",
    )

    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO, format="%(message)s")

    client = _client()

    if args.command == "survey":
        found = survey(client)
        print(f"content objects: {found.summary()}")
        if found.unknown:
            print(
                f"{len(found.unknown)} object(s) named after neither their "
                f"content nor the pre-#44 double hash; left alone"
            )
        if found.orphaned_legacy:
            print(
                f"{len(found.orphaned_legacy)} legacy object(s) nothing "
                f"points at any more; safe to reap by hand"
            )
        if found.needs_migration:
            print(
                f"{len(found.referenced_legacy)} object(s) are still "
                f"referenced under the old name"
            )
            return 1
        print("nothing depends on the old naming")
        return 0

    try:
        migrate(client, dry_run=args.dry_run)
    except RuntimeError as failure:
        print(f"error: {failure}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
