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

from datetime import UTC, datetime
from enum import StrEnum

from julee.core.entities.entity import Entity
from julee.core.entities.text import Name, NonEmptyText
from pydantic import Field, field_validator


class PolicyStatus(StrEnum):
    """Status of a policy configuration."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    DRAFT = "draft"
    DEPRECATED = "deprecated"


class Policy(Entity):
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
    policy_id: NonEmptyText = Field(description="Unique identifier for this policy")
    title: Name = Field(description="Human-readable title for the policy")
    description: NonEmptyText = Field(
        description="Detailed description of what this policy validates "
        "and optionally transforms"
    )

    # Policy configuration
    status: PolicyStatus = PolicyStatus.ACTIVE
    validation_scores: tuple[tuple[NonEmptyText, int], ...] = Field(
        description="List of (knowledge_service_query_id, required_score) "
        "tuples where required_score is between 0 and 100. All scores "
        "must be met or exceeded for the policy to pass"
    )
    transformation_queries: tuple[NonEmptyText, ...] | None = Field(
        default=None,
        description="Optional list of knowledge service query IDs for "
        "transformations to apply before re-validation. If not provided "
        "or empty, policy operates in validation-only mode",
    )

    # Policy metadata
    version: NonEmptyText = Field(
        default=NonEmptyText("0.1.0"), description="Policy version"
    )
    created_at: datetime | None = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime | None = Field(default=None)

    @field_validator("validation_scores")
    @classmethod
    def validation_scores_must_be_valid(
        cls, v: tuple[tuple[NonEmptyText, int], ...]
    ) -> tuple[tuple[NonEmptyText, int], ...]:
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

        return v

    @field_validator("transformation_queries")
    @classmethod
    def transformation_queries_must_be_valid(
        cls, v: tuple[NonEmptyText, ...] | None
    ) -> tuple[NonEmptyText, ...] | None:
        """No query may be named twice. The rest is the element type."""
        if v is None:
            return v

        if not isinstance(v, (list, tuple)):
            raise ValueError("Transformation queries must be a list or None")

        query_ids_seen: set[str] = set()
        for query_id in v:
            if query_id in query_ids_seen:
                raise ValueError(
                    f"Duplicate query ID '{query_id}' in transformation queries"
                )
            query_ids_seen.add(query_id)

        return v

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
