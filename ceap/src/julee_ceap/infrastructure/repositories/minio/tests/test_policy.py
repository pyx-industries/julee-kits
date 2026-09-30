"""
Tests for MinioPolicyRepository implementation.

This module provides comprehensive tests for the Minio-based policy repository
implementation, using the fake client to avoid external dependencies during
testing.
"""

from dataclasses import replace
from datetime import UTC, datetime

import pytest
from julee.core.values.text import Name, NonEmptyText
from julee.integrations.minio.testing import FakeMinioClient

from julee_ceap.domain.models.policy.policy import Policy, PolicyStatus
from julee_ceap.infrastructure.repositories.minio.policy import (
    MinioPolicyRepository,
)

pytestmark = pytest.mark.unit


@pytest.fixture
def fake_client() -> FakeMinioClient:
    """Create a fresh fake Minio client for each test."""
    return FakeMinioClient()


@pytest.fixture
def policy_repo(fake_client: FakeMinioClient) -> MinioPolicyRepository:
    """Create policy repository with fake client."""
    return MinioPolicyRepository(fake_client)


@pytest.fixture
def sample_policy() -> Policy:
    """Create a sample policy for testing."""
    return Policy(
        policy_id=NonEmptyText("policy-test-123"),
        title=Name("Content Quality Policy"),
        description=NonEmptyText("Validates content meets quality standards"),
        status=PolicyStatus.ACTIVE,
        validation_scores=(
            (NonEmptyText("quality-check-query"), 80),
            (NonEmptyText("completeness-check"), 90),
        ),
        transformation_queries=(
            NonEmptyText("improve-quality"),
            NonEmptyText("fix-grammar"),
        ),
        version=NonEmptyText("1.0.0"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


@pytest.fixture
def validation_only_policy() -> Policy:
    """Create a validation-only policy (no transformations) for testing."""
    return Policy(
        policy_id=NonEmptyText("policy-validation-only"),
        title=Name("Validation Only Policy"),
        description=NonEmptyText("Only validates content without transformations"),
        status=PolicyStatus.ACTIVE,
        validation_scores=((NonEmptyText("basic-validation"), 70),),
        transformation_queries=(),  # Empty tuple - validation only
        version=NonEmptyText("1.0.0"),
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )


class TestMinioPolicyRepositoryBasicOperations:
    """Test basic CRUD operations on policies."""

    @pytest.mark.asyncio
    async def test_save_and_get_policy(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test saving and retrieving a policy."""
        # Save policy
        await policy_repo.save(sample_policy)

        # Retrieve policy
        retrieved = await policy_repo.get(sample_policy.policy_id)

        assert retrieved is not None
        assert retrieved.policy_id == sample_policy.policy_id
        assert retrieved.title == sample_policy.title
        assert retrieved.description == sample_policy.description
        assert retrieved.status == sample_policy.status
        assert retrieved.validation_scores == sample_policy.validation_scores
        assert retrieved.transformation_queries == sample_policy.transformation_queries
        assert retrieved.version == sample_policy.version

    @pytest.mark.asyncio
    async def test_get_nonexistent_policy(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test retrieving a non-existent policy returns None."""
        result = await policy_repo.get("nonexistent-policy")
        assert result is None

    @pytest.mark.asyncio
    async def test_generate_id(self, policy_repo: MinioPolicyRepository) -> None:
        """Test generating unique policy IDs."""
        id1 = await policy_repo.generate_id()
        id2 = await policy_repo.generate_id()

        assert isinstance(id1, str)
        assert isinstance(id2, str)
        assert id1 != id2
        assert len(id1) > 0
        assert len(id2) > 0
        assert id1.startswith("policy-")
        assert id2.startswith("policy-")


class TestMinioPolicyRepositoryPolicyTypes:
    """Test handling of different policy types."""

    @pytest.mark.asyncio
    async def test_validation_only_policy(
        self,
        policy_repo: MinioPolicyRepository,
        validation_only_policy: Policy,
    ) -> None:
        """Test storing and retrieving validation-only policy."""
        # Save validation-only policy
        await policy_repo.save(validation_only_policy)

        # Retrieve and verify
        retrieved = await policy_repo.get(validation_only_policy.policy_id)
        assert retrieved is not None
        assert retrieved.is_validation_only is True
        assert retrieved.has_transformations is False
        assert retrieved.transformation_queries == ()

    @pytest.mark.asyncio
    async def test_transformation_policy(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test storing and retrieving policy with transformations."""
        # Save transformation policy
        await policy_repo.save(sample_policy)

        # Retrieve and verify
        retrieved = await policy_repo.get(sample_policy.policy_id)
        assert retrieved is not None
        assert retrieved.is_validation_only is False
        assert retrieved.has_transformations is True
        assert retrieved.transformation_queries is not None
        assert len(retrieved.transformation_queries) == 2
        assert "improve-quality" in retrieved.transformation_queries
        assert "fix-grammar" in retrieved.transformation_queries

    @pytest.mark.asyncio
    async def test_policy_with_none_transformations(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test policy with None transformation queries."""
        policy = Policy(
            policy_id=NonEmptyText("policy-none-transforms"),
            title=Name("Policy with None Transformations"),
            description=NonEmptyText("Policy where transformation_queries is None"),
            validation_scores=((NonEmptyText("test-query"), 75),),
            transformation_queries=None,  # Explicitly None
        )

        await policy_repo.save(policy)
        retrieved = await policy_repo.get(policy.policy_id)

        assert retrieved is not None
        assert retrieved.transformation_queries is None
        assert retrieved.is_validation_only is True
        assert retrieved.has_transformations is False


class TestMinioPolicyRepositoryUpdates:
    """Test policy update operations."""

    @pytest.mark.asyncio
    async def test_update_policy_status(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test updating policy status."""
        # Save initial policy
        await policy_repo.save(sample_policy)

        # Update status
        sample_policy = replace(sample_policy, status=PolicyStatus.INACTIVE)
        await policy_repo.save(sample_policy)

        # Verify update
        retrieved = await policy_repo.get(sample_policy.policy_id)
        assert retrieved is not None
        assert retrieved.status == PolicyStatus.INACTIVE

    @pytest.mark.asyncio
    async def test_update_policy_validation_scores(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test updating policy validation scores."""
        # Save initial policy
        await policy_repo.save(sample_policy)

        # Update validation scores
        sample_policy = replace(
            sample_policy,
            validation_scores=(
                (NonEmptyText("new-quality-check"), 85),
                (NonEmptyText("advanced-validation"), 95),
            ),
        )
        await policy_repo.save(sample_policy)

        # Verify update
        retrieved = await policy_repo.get(sample_policy.policy_id)
        assert retrieved is not None
        assert len(retrieved.validation_scores) == 2
        assert (NonEmptyText("new-quality-check"), 85) in retrieved.validation_scores
        assert (NonEmptyText("advanced-validation"), 95) in retrieved.validation_scores

    @pytest.mark.asyncio
    async def test_update_transformation_queries(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test updating transformation queries."""
        # Save initial policy
        await policy_repo.save(sample_policy)

        # Update transformation queries
        sample_policy = replace(
            sample_policy, transformation_queries=(NonEmptyText("new-transform"),)
        )
        await policy_repo.save(sample_policy)

        # Verify update
        retrieved = await policy_repo.get(sample_policy.policy_id)
        assert retrieved is not None
        assert retrieved.transformation_queries == ("new-transform",)
        assert retrieved.has_transformations is True

    @pytest.mark.asyncio
    async def test_save_updates_timestamp(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test that save operations update the updated_at timestamp."""
        original_updated_at = sample_policy.updated_at

        # Save policy
        await policy_repo.save(sample_policy)

        # Retrieve and check timestamp was updated
        retrieved = await policy_repo.get(sample_policy.policy_id)
        assert retrieved is not None
        assert retrieved.updated_at is not None
        assert original_updated_at is not None
        assert retrieved.updated_at > original_updated_at


class TestMinioPolicyRepositoryComplexScenarios:
    """Test complex scenarios and edge cases."""

    @pytest.mark.asyncio
    async def test_policy_with_complex_validation_scores(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test policy with many validation scores."""
        policy = Policy(
            policy_id=NonEmptyText("complex-policy"),
            title=Name("Complex Validation Policy"),
            description=NonEmptyText("Policy with multiple validation criteria"),
            validation_scores=(
                (NonEmptyText("grammar-check"), 80),
                (NonEmptyText("completeness-check"), 85),
                (NonEmptyText("accuracy-check"), 90),
                (NonEmptyText("style-check"), 75),
                (NonEmptyText("readability-check"), 70),
            ),
            transformation_queries=(NonEmptyText("improve-all-aspects"),),
        )

        await policy_repo.save(policy)
        retrieved = await policy_repo.get("complex-policy")

        assert retrieved is not None
        assert len(retrieved.validation_scores) == 5
        assert retrieved.has_transformations is True
        assert retrieved.transformation_queries is not None
        assert len(retrieved.transformation_queries) == 1

    @pytest.mark.asyncio
    async def test_complete_policy_lifecycle(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test complete policy lifecycle from creation to deprecation."""
        # Generate new policy ID
        policy_id = await policy_repo.generate_id()

        # Create and save initial policy
        policy = Policy(
            policy_id=NonEmptyText(policy_id),
            title=Name("Lifecycle Test Policy"),
            description=NonEmptyText("Testing full lifecycle"),
            status=PolicyStatus.DRAFT,
            validation_scores=((NonEmptyText("lifecycle-check"), 80),),
            transformation_queries=(NonEmptyText("lifecycle-transform"),),
            version=NonEmptyText("0.1.0"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await policy_repo.save(policy)

        # Activate policy
        policy = replace(
            policy, status=PolicyStatus.ACTIVE, version=NonEmptyText("1.0.0")
        )
        await policy_repo.save(policy)

        # Deprecate policy
        policy = replace(policy, status=PolicyStatus.DEPRECATED)
        await policy_repo.save(policy)

        # Verify can still be retrieved
        retrieved = await policy_repo.get(policy_id)
        assert retrieved is not None
        assert retrieved.status == PolicyStatus.DEPRECATED

    @pytest.mark.asyncio
    async def test_multiple_policies_independence(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test that multiple policies are stored and retrieved
        independently."""
        # Create multiple policies
        policy1 = Policy(
            policy_id=NonEmptyText("policy-test-1"),
            title=Name("First Policy"),
            description=NonEmptyText("First test policy"),
            validation_scores=((NonEmptyText("check-1"), 80),),
        )

        policy2 = Policy(
            policy_id=NonEmptyText("policy-test-2"),
            title=Name("Second Policy"),
            description=NonEmptyText("Second test policy"),
            validation_scores=((NonEmptyText("check-2"), 90),),
            transformation_queries=(NonEmptyText("transform-2"),),
        )

        # Save both policies
        await policy_repo.save(policy1)
        await policy_repo.save(policy2)

        # Retrieve both and verify independence
        retrieved1 = await policy_repo.get("policy-test-1")
        retrieved2 = await policy_repo.get("policy-test-2")

        assert retrieved1 is not None
        assert retrieved2 is not None
        assert retrieved1.policy_id == "policy-test-1"
        assert retrieved2.policy_id == "policy-test-2"
        assert retrieved1.title == "First Policy"
        assert retrieved2.title == "Second Policy"
        assert retrieved1.is_validation_only is True
        assert retrieved2.has_transformations is True

        # Update one policy and verify the other is unchanged
        policy1 = replace(policy1, title=Name("Updated First Policy"))
        await policy_repo.save(policy1)

        retrieved1_updated = await policy_repo.get("policy-test-1")
        retrieved2_unchanged = await policy_repo.get("policy-test-2")

        assert retrieved1_updated is not None
        assert retrieved2_unchanged is not None
        assert retrieved1_updated.title == "Updated First Policy"
        assert retrieved2_unchanged.title == "Second Policy"

    @pytest.mark.asyncio
    async def test_policy_with_unicode_content(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test policy with unicode content survives roundtrip."""
        unicode_policy = Policy(
            policy_id=NonEmptyText("unicode-policy"),
            title=Name("Política de Calidad 品質ポリシー"),
            description=NonEmptyText("Política con contenido unicode 🚀📝 и кириллица"),
            validation_scores=(
                (NonEmptyText("验证查询"), 85),  # Chinese
                (NonEmptyText("проверка"), 90),  # Russian
            ),
            transformation_queries=(
                NonEmptyText("transformación"),
                NonEmptyText("преобразование"),
            ),
            version=NonEmptyText("1.0.0"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Save and retrieve
        await policy_repo.save(unicode_policy)
        retrieved = await policy_repo.get("unicode-policy")

        assert retrieved is not None
        assert retrieved.title == "Política de Calidad 品質ポリシー"
        assert "unicode 🚀📝 и кириллица" in retrieved.description
        assert ("验证查询", 85) in retrieved.validation_scores
        assert ("проверка", 90) in retrieved.validation_scores
        assert retrieved.transformation_queries is not None
        assert "transformación" in retrieved.transformation_queries
        assert "преобразование" in retrieved.transformation_queries


class TestMinioPolicyRepositoryIdempotency:
    """Test idempotent operations."""

    @pytest.mark.asyncio
    async def test_save_idempotency(
        self,
        policy_repo: MinioPolicyRepository,
        sample_policy: Policy,
    ) -> None:
        """Test that saving the same policy multiple times is idempotent."""
        # Save policy first time
        await policy_repo.save(sample_policy)

        # Get the policy to check initial state
        retrieved1 = await policy_repo.get(sample_policy.policy_id)
        assert retrieved1 is not None
        first_updated_at = retrieved1.updated_at

        # Save same policy again (should update timestamp but maintain data)
        await policy_repo.save(sample_policy)

        # Verify policy is still there with updated timestamp
        retrieved2 = await policy_repo.get(sample_policy.policy_id)
        assert retrieved2 is not None
        assert retrieved2.policy_id == sample_policy.policy_id
        assert retrieved2.title == sample_policy.title
        assert retrieved2.validation_scores == sample_policy.validation_scores
        assert retrieved2.transformation_queries == sample_policy.transformation_queries
        assert retrieved2.updated_at is not None
        assert first_updated_at is not None
        assert retrieved2.updated_at > first_updated_at


class TestMinioPolicyRepositoryRoundtrip:
    """Test full round-trip scenarios."""

    @pytest.mark.asyncio
    async def test_full_policy_lifecycle_success(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test complete successful policy lifecycle."""
        # Generate new policy ID
        policy_id = await policy_repo.generate_id()

        # Create and save initial policy
        policy = Policy(
            policy_id=NonEmptyText(policy_id),
            title=Name("Round-trip Test Policy"),
            description=NonEmptyText("Testing complete policy round-trip"),
            status=PolicyStatus.DRAFT,
            validation_scores=((NonEmptyText("round-trip-check"), 85),),
            transformation_queries=(NonEmptyText("round-trip-transform"),),
            version=NonEmptyText("0.1.0"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        await policy_repo.save(policy)

        # Activate policy
        policy = replace(
            policy, status=PolicyStatus.ACTIVE, version=NonEmptyText("1.0.0")
        )
        await policy_repo.save(policy)

        # Final verification
        retrieved = await policy_repo.get(policy_id)
        assert retrieved is not None
        assert retrieved.status == PolicyStatus.ACTIVE
        assert retrieved.version == "1.0.0"
        assert retrieved.has_transformations is True
        assert len(retrieved.validation_scores) == 1
        assert retrieved.validation_scores[0] == (NonEmptyText("round-trip-check"), 85)

    @pytest.mark.asyncio
    async def test_policy_json_serialization_roundtrip(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test that policy JSON serialization/deserialization works
        correctly."""
        # Create policy with all field types
        policy = Policy(
            policy_id=NonEmptyText("json-test-policy"),
            title=Name("JSON Test Policy"),
            description=NonEmptyText("Testing JSON serialization"),
            status=PolicyStatus.ACTIVE,
            validation_scores=(
                (NonEmptyText("test-1"), 80),
                (NonEmptyText("test-2"), 90),
                (NonEmptyText("test-3"), 75),
            ),
            transformation_queries=(
                NonEmptyText("transform-1"),
                NonEmptyText("transform-2"),
            ),
            version=NonEmptyText("2.0.0"),
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # Save and retrieve
        await policy_repo.save(policy)
        retrieved = await policy_repo.get("json-test-policy")

        # Verify all fields survived serialization
        assert retrieved is not None
        assert retrieved.policy_id == policy.policy_id
        assert retrieved.title == policy.title
        assert retrieved.description == policy.description
        assert retrieved.status == policy.status
        assert retrieved.validation_scores == policy.validation_scores
        assert retrieved.transformation_queries == policy.transformation_queries
        assert retrieved.version == policy.version
        assert retrieved.created_at is not None
        assert retrieved.updated_at is not None

        # Verify computed properties work
        assert retrieved.is_validation_only is False
        assert retrieved.has_transformations is True


class TestMinioPolicyRepositoryErrorHandling:
    """Test error handling scenarios."""

    @pytest.mark.asyncio
    async def test_empty_string_id_handling(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test handling of empty string policy ID."""
        result = await policy_repo.get("")
        assert result is None

    @pytest.mark.asyncio
    async def test_special_characters_in_id(
        self, policy_repo: MinioPolicyRepository
    ) -> None:
        """Test handling policy IDs with special characters."""
        special_id = "policy-test-with-dashes-and-numbers-123"

        policy = Policy(
            policy_id=NonEmptyText(special_id),
            title=Name("Special ID Policy"),
            description=NonEmptyText("Policy with special characters in ID"),
            validation_scores=((NonEmptyText("test-check"), 80),),
        )

        await policy_repo.save(policy)
        retrieved = await policy_repo.get(special_id)

        assert retrieved is not None
        assert retrieved.policy_id == special_id
        assert retrieved.title == "Special ID Policy"
