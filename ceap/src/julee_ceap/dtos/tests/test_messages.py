"""What a use case's response says, and what it does not.

Both responses used to hold the entity: ``assembly: Assembly``,
``validation: DocumentPolicyValidation``. Nothing tested either — every
test called the inner method, so execute(), which is the door the
Temporal workflows go through, had no coverage at all.

The fields are written down rather than read off the entity. Reading
them off would make this agree with whatever the entity says, which is
the coupling it exists to prevent: Temporal writes a workflow's result
into history, so the entity's shape was a durable contract replayed
long after the code that wrote it.
"""

from datetime import UTC, datetime

import pytest
from julee.core.values.text import NonEmptyText
from pydantic import BaseModel

from julee_ceap.domain.models.assembly.assembly import Assembly, AssemblyStatus
from julee_ceap.domain.models.policy.document_policy_validation import (
    DocumentPolicyValidation,
    DocumentPolicyValidationStatus,
)
from julee_ceap.dtos.extract_assemble_data import ExtractAssembleDataResponse
from julee_ceap.dtos.validate_document import ValidateDocumentResponse

pytestmark = pytest.mark.unit


def an_assembly(assembled_document_id: str | None = "assembled-1") -> Assembly:
    """One assembly, as the use case would have made it.

    Args:
        assembled_document_id: What came out, or None if nothing did

    Returns:
        The entity
    """
    return Assembly(
        assembly_id=NonEmptyText("assembly-1"),
        assembly_specification_id=NonEmptyText("spec-1"),
        input_document_id=NonEmptyText("doc-1"),
        execution_id=NonEmptyText("run-1"),
        status=AssemblyStatus.COMPLETED,
        assembled_document_id=(
            NonEmptyText(assembled_document_id) if assembled_document_id else None
        ),
        created_at=datetime.now(UTC),
    )


def a_validation(passed: bool | None = True) -> DocumentPolicyValidation:
    """One validation, as the use case would have made it.

    Args:
        passed: The verdict, or None if it has not reached one

    Returns:
        The entity
    """
    return DocumentPolicyValidation(
        validation_id="validation-1",
        input_document_id=NonEmptyText("doc-1"),
        policy_id=NonEmptyText("policy-1"),
        status=DocumentPolicyValidationStatus.PASSED,
        passed=passed,
    )


class TestTheContract:
    """The fields each message names."""

    @pytest.mark.parametrize(
        ("response", "expected"),
        [
            (
                ExtractAssembleDataResponse,
                ("assembly_id", "assembled_document_id", "status"),
            ),
            (
                ValidateDocumentResponse,
                ("validation_id", "status", "passed", "transformed_document_id"),
            ),
        ],
        ids=lambda v: v.__name__ if isinstance(v, type) else "",
    )
    def test_it_names_these_and_no_others(
        self, response: type[BaseModel], expected: tuple[str, ...]
    ) -> None:
        """Change this and you have changed what a workflow returns."""
        assert tuple(response.model_fields) == expected

    def test_neither_carries_an_entity(self) -> None:
        """The defect this replaced, stated as a test.

        A field annotated with a domain entity is the entity's shape
        wearing the message's name.
        """
        entities = {Assembly, DocumentPolicyValidation}

        for response in (ExtractAssembleDataResponse, ValidateDocumentResponse):
            annotated = {f.annotation for f in response.model_fields.values()}
            assert not (annotated & entities), (
                f"{response.__name__} carries an entity: {annotated & entities}"
            )


class TestWhatAnAssemblyReports:
    """ExtractAssembleDataResponse.of"""

    def test_it_says_what_was_made(self) -> None:
        """The id a caller polls the workflow for."""
        assert ExtractAssembleDataResponse.of(an_assembly()).assembly_id == "assembly-1"

    def test_it_says_what_came_out(self) -> None:
        """The assembled document, which is the point of assembling."""
        found = ExtractAssembleDataResponse.of(an_assembly())

        assert found.assembled_document_id == "assembled-1"

    def test_an_assembly_that_produced_nothing_says_so(self) -> None:
        """None rather than an empty string, which reads as a real id."""
        found = ExtractAssembleDataResponse.of(an_assembly(assembled_document_id=None))

        assert found.assembled_document_id is None

    def test_the_ids_go_out_as_plain_strings(self) -> None:
        """NonEmptyText is how this context checks, not what it sends."""
        found = ExtractAssembleDataResponse.of(an_assembly())

        assert type(found.assembly_id) is str
        assert type(found.assembled_document_id) is str


class TestWhatAValidationReports:
    """ValidateDocumentResponse.of"""

    def test_it_says_which_validation(self) -> None:
        """The id a caller polls the workflow for."""
        found = ValidateDocumentResponse.of(a_validation())

        assert found.validation_id == "validation-1"

    def test_it_says_the_verdict(self) -> None:
        """Which is the thing a caller acts on."""
        assert ValidateDocumentResponse.of(a_validation(passed=False)).passed is False

    def test_no_verdict_yet_is_not_a_failure(self) -> None:
        """None and False are different answers and must stay different."""
        assert ValidateDocumentResponse.of(a_validation(passed=None)).passed is None
