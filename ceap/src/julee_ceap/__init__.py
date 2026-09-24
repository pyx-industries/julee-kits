"""CEAP: capture, extract, assemble, publish.

A julee kit. It takes documents in, extracts what a knowledge service can
find in them, assembles that against a specification, validates the result
against a policy, and publishes it — each step durable, and each step
recorded.

Install it, then adopt it::

    [tool.julee]
    kits = ["ceap"]

The pipeline's parts are imported from their own modules rather than from
here, so that a Temporal workflow does not pull in non-deterministic code
by importing the package::

    from julee_ceap.usecases.extract_assemble_data import (
        ExtractAssembleDataUseCase,
    )
    from julee_ceap.domain.models.document.document import Document
"""

from julee.core.entities.kit import Kit

kit = Kit(
    slug="ceap",
    name="Capture, Extract, Assemble, Publish",
    package="julee_ceap",
    contributes={
        "fastapi.routers": "julee_ceap.apps.api.app:app",
        "temporal.pipelines": "julee_ceap.apps.worker",
        # The classes, not the modules holding them: a solution is told
        # what there is rather than importing a module and guessing which
        # of its names qualify.
        "temporal.activities": (
            "julee_ceap.infrastructure.repositories.temporal"
            ".activities:ACTIVITY_CLASSES",
            "julee_ceap.infrastructure.services.temporal"
            ".activities:ACTIVITY_CLASSES",
        ),
    },
)

__all__ = ["kit"]
