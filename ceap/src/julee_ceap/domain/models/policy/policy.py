"""
Policy domain models for the Capture, Extract, Assemble,
Publish workflow.

This module contains the Policy domain object that represents
policy configurations in the CEAP workflow system.

A Policy defines validation criteria and optional transformations
for documents. It includes validation scores that must be met and optional
transformation queries that can be applied to improve document quality.

All domain models use Pydantic BaseModel for validation, serialization,
and type safety, following the patterns established in the sample project.
"""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from julee.core.values.text import Name, NonEmptyText


class PolicyStatus(StrEnum):
    """Status of a policy configuration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


@dataclass(frozen=True, kw_only=True)
class Policy:
    """Policy configuration that defines validation and
    transformation criteria for documents.

    A Policy represents a set of quality criteria that documents
    must meet. It includes validation scores that are calculated using
    knowledge service queries, and optional transformation queries that can
    be applied to improve document quality before re-validation.

    The policy operates in two modes:

    1. Validation-only: Calculates scores and passes/fails based on criteria
    2. Validation with transformation: Calculates scores, applies
       transformations, then re-calculates scores for final pass/fail

    """

    # Core policy identification
    policy_id: NonEmptyText
    """Unique identifier for this policy."""
    title: Name
    """Human-readable title for the policy."""
    description: NonEmptyText
    """Detailed description of what this policy validates and optionally transforms."""

    # Policy configuration
    status: PolicyStatus = PolicyStatus.ACTIVE
    validation_scores: tuple[tuple[NonEmptyText, int], ...]
    """List of (knowledge_service_query_id, required_score) tuples where required_score is between 0 and 100. All scores must be met or exceeded for the policy to pass."""
    transformation_queries: tuple[NonEmptyText, ...] | None = None
    """Optional list of knowledge service query IDs for transformations to apply before re-validation. If not provided or empty, policy operates in validation-only mode."""

    # Policy metadata
    version: NonEmptyText = NonEmptyText("0.1.0")
    """Policy version."""
    created_at: datetime | None = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Check the scores and the transformation queries.

        These were two field_validator methods, both pure checks.

        Raises:
            ValueError: If either is malformed
        """
        self._refuse_bad_scores(self.validation_scores)
        self._refuse_duplicate_queries(self.transformation_queries)

    @staticmethod
    def _refuse_bad_scores(
        v: tuple[tuple[NonEmptyText, int], ...],
    ) -> None:
        """What a score list must be, beyond being a list of scores.

        A rule, not a normalisation: the list cannot be empty, no query
        may be scored twice, and a score is a percentage. What used to
        be here as well — stripping each query id and rebuilding the
        tuple around it — is NonEmptyText's now (#306).
        """
        if not isinstance(v, (list, tuple)):
            raise ValueError("Validation scores must be a list")

        if not v:
            raise ValueError("Validation scores list cannot be empty")

        query_ids_seen = set()

        for item in v:
            if not isinstance(item, tuple) or len(item) != 2:
                raise ValueError(
                    "Each validation score must be a 2-tuple of "
                    "(query_id, required_score)"
                )

            query_id, required_score = item

            # Check for duplicate query IDs
            if query_id in query_ids_seen:
                raise ValueError(
                    f"Duplicate query ID '{query_id}' in validation scores"
                )
            query_ids_seen.add(query_id)

            # Validate required score
            if not isinstance(required_score, int):
                raise ValueError("Required score must be an integer between 0 and 100")
            if required_score < 0 or required_score > 100:
                raise ValueError(
                    f"Required score {required_score} must be between 0 and 100"
                )

    @staticmethod
    def _refuse_duplicate_queries(v: tuple[NonEmptyText, ...] | None) -> None:
        """No query may be named twice. The rest is the element type."""
        if v is None:
            return

        if not isinstance(v, (list, tuple)):
            raise ValueError("Transformation queries must be a list or None")

        query_ids_seen: set[str] = set()
        for query_id in v:
            if query_id in query_ids_seen:
                raise ValueError(
                    f"Duplicate query ID '{query_id}' in transformation queries"
                )
            query_ids_seen.add(query_id)

    @property
    def is_validation_only(self) -> bool:
        """Check if this policy operates in validation-only mode.

        Returns True if no transformation queries are defined or if the
        transformation queries list is empty.
        """
        return not self.transformation_queries

    @property
    def has_transformations(self) -> bool:
        """Check if this policy includes transformation queries.

        Returns True if transformation queries are defined and non-empty.
        """
        return not self.is_validation_only
