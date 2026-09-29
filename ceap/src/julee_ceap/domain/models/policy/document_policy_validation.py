"""
DocumentPolicyValidation domain models for the Capture, Extract, Assemble,
Publish workflow.

This module contains the DocumentPolicyValidation domain object that
represents
the result of validating a document against a policy configuration in the CEAP
workflow system.

A DocumentPolicyValidation captures the complete validation process including:
- The document being validated and the policy used
- Actual validation scores achieved against policy criteria
- Optional transformation results and post-transformation scores
- Status tracking throughout the validation lifecycle

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from julee.core.values.text import NonEmptyText


class DocumentPolicyValidationStatus(StrEnum):
    """Status of a document policy validation process."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATION_COMPLETE = "validation_complete"
    TRANSFORMATION_REQUIRED = "transformation_required"
    TRANSFORMATION_IN_PROGRESS = "transformation_in_progress"
    TRANSFORMATION_COMPLETE = "transformation_complete"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


@dataclass(frozen=True, kw_only=True)
class DocumentPolicyValidation:
    """Represents the validation of a document against a policy configuration.

    A DocumentPolicyValidation tracks the complete lifecycle of validating
    a document against policy criteria. It includes:

    1. Initial validation: Document is scored against policy validation
       queries
    2. Optional transformation: If policy includes transformation queries and
       initial validation fails, transformations are applied
    3. Re-validation: Transformed document is re-scored against policy
       criteria
    4. Final determination: Pass/fail based on final validation scores

    The validation process supports both validation-only policies and policies
    that include transformations for document quality improvement.
    """

    # Core validation identification
    validation_id: str
    """Unique identifier for this validation instance."""
    input_document_id: NonEmptyText
    """ID of the document being validated against the policy."""
    policy_id: NonEmptyText
    """ID of the policy configuration used for validation."""

    # Validation process status
    status: DocumentPolicyValidationStatus = DocumentPolicyValidationStatus.PENDING

    # Initial validation results
    validation_scores: tuple[tuple[NonEmptyText, int], ...] = ()
    """List of (knowledge_service_query_id, actual_score) tuples representing the scores achieved during initial validation. Scores are between 0 and 100."""

    # Transformation results (if applicable)
    transformed_document_id: NonEmptyText | None = None
    """ID of the document after transformations have been applied. Only present if the policy includes transformation queries and they were executed."""
    post_transform_validation_scores: tuple[tuple[NonEmptyText, int], ...] | None = None
    """List of (knowledge_service_query_id, actual_score) tuples representing scores achieved after transformation. Only present if transformations were applied and re-validation occurred."""

    # Validation metadata
    started_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    """When the validation process was initiated."""
    completed_at: datetime | None = None
    """When the validation process completed."""
    error_message: NonEmptyText | None = None
    """Error message if validation process failed."""

    # Results summary
    passed: bool | None = None
    """Whether the document passed policy validation. None while validation is in progress, True/False when complete."""

    def __post_init__(self) -> None:
        """Check both sets of scores.

        No query scored twice, and every score a percentage. An empty
        tuple is valid: a validation that has not run yet has no
        scores, and None on the post-transform set means the transform
        has not run.

        Raises:
            ValueError: If either set is malformed
        """
        self._refuse_bad_score_tuples(self.validation_scores, "validation_scores")
        if self.post_transform_validation_scores is not None:
            self._refuse_bad_score_tuples(
                self.post_transform_validation_scores,
                "post_transform_validation_scores",
            )

    @classmethod
    def _refuse_bad_score_tuples(
        cls, scores: tuple[tuple[NonEmptyText, int], ...], field_name: str
    ) -> None:
        """Raise if these scores break a rule; say nothing otherwise.

        It used to return a rebuilt tuple, because it stripped each
        query id on the way through. NonEmptyText does that, so there is
        nothing to hand back and the name says so (#306).
        """
        query_ids_seen: set[str] = set()

        for item in scores:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError(
                    f"Each item in {field_name} must be a 2-tuple of "
                    f"(query_id, actual_score)"
                )

            query_id, actual_score = item

            # Validate query ID
            # Check for duplicate query IDs within this field
            if query_id in query_ids_seen:
                raise ValueError(f"Duplicate query ID '{query_id}' in {field_name}")
            query_ids_seen.add(query_id)

            # Validate actual score
            if not isinstance(actual_score, int):
                raise ValueError(
                    f"Actual score in {field_name} must be an integer between 0 and 100"
                )
            if actual_score < 0 or actual_score > 100:
                raise ValueError(
                    f"Actual score {actual_score} in {field_name} must be "
                    f"between 0 and 100"
                )
