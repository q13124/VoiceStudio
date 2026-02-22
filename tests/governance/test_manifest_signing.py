"""
Tests for manifest signing and release management.
"""


class TestManifestSigning:
    """Test manifest signing functionality."""

    def test_sign_manifest(self, manifest_signer):
        """Test signing a manifest."""
        content = {"prompt": "You are a helpful assistant"}

        signed = manifest_signer.sign(
            manifest_type="prompt_template",
            name="base_prompt",
            version="1.0.0",
            content=content,
            signed_by="admin",
        )

        assert signed.signature != ""
        assert signed.content_hash != ""
        assert signed.signed_by == "admin"

    def test_verify_valid_signature(self, manifest_signer):
        """Test verifying a valid signature."""
        content = {"prompt": "Test prompt"}

        signed = manifest_signer.sign(
            manifest_type="prompt_template",
            name="test",
            version="1.0.0",
            content=content,
            signed_by="admin",
        )

        is_valid, reason = manifest_signer.verify(signed, content)

        assert is_valid
        assert "valid" in reason.lower()

    def test_detect_tampered_content(self, manifest_signer):
        """Test detection of tampered content."""
        original_content = {"prompt": "Original prompt"}
        tampered_content = {"prompt": "Tampered prompt"}

        signed = manifest_signer.sign(
            manifest_type="prompt_template",
            name="test",
            version="1.0.0",
            content=original_content,
            signed_by="admin",
        )

        is_valid, reason = manifest_signer.verify(signed, tampered_content)

        assert not is_valid
        assert "mismatch" in reason.lower() or "modified" in reason.lower()

    def test_detect_tampered_signature(self, manifest_signer):
        """Test detection of tampered signature."""
        content = {"prompt": "Test"}

        signed = manifest_signer.sign(
            manifest_type="prompt_template",
            name="test",
            version="1.0.0",
            content=content,
            signed_by="admin",
        )

        # Tamper with signature
        signed.signature = "tampered" + signed.signature[8:]

        is_valid, reason = manifest_signer.verify(signed, content)

        assert not is_valid
        assert "tampered" in reason.lower() or "failed" in reason.lower()


class TestReleaseManager:
    """Test release manager functionality."""

    def test_publish_bundle(self, release_manager):
        """Test publishing a bundle."""
        from agent.release_manager import BundleType, ReleaseChannel

        bundle = release_manager.publish(
            bundle_type=BundleType.PROMPT_TEMPLATE,
            name="assistant_prompt",
            version="1.0.0",
            content={"prompt": "You are helpful"},
            channel=ReleaseChannel.STABLE,
            changelog="Initial release",
        )

        assert bundle.bundle_id is not None
        assert bundle.is_active
        assert bundle.version == "1.0.0"

    def test_get_active_bundle(self, release_manager):
        """Test getting the active bundle."""
        from agent.release_manager import BundleType, ReleaseChannel

        release_manager.publish(
            bundle_type=BundleType.POLICY_BUNDLE,
            name="base_policy",
            version="1.0.0",
            content={"rules": []},
            channel=ReleaseChannel.STABLE,
        )

        active = release_manager.get_active(
            bundle_type=BundleType.POLICY_BUNDLE,
            name="base_policy",
            channel=ReleaseChannel.STABLE,
        )

        assert active is not None
        assert active.version == "1.0.0"

    def test_version_history(self, release_manager):
        """Test getting version history."""
        from agent.release_manager import BundleType, ReleaseChannel

        # Publish multiple versions
        for i in range(3):
            release_manager.publish(
                bundle_type=BundleType.TOOL_DEFINITION,
                name="file_tools",
                version=f"1.{i}.0",
                content={"version": i},
                channel=ReleaseChannel.STABLE,
            )

        history = release_manager.get_history(
            bundle_type=BundleType.TOOL_DEFINITION,
            name="file_tools",
            channel=ReleaseChannel.STABLE,
        )

        assert len(history) == 3

    def test_rollback(self, release_manager):
        """Test rollback functionality."""
        from agent.release_manager import BundleType, ReleaseChannel

        # Publish versions
        release_manager.publish(
            bundle_type=BundleType.PROMPT_TEMPLATE,
            name="test",
            version="1.0.0",
            content={"v": 1},
            channel=ReleaseChannel.STABLE,
        )
        release_manager.publish(
            bundle_type=BundleType.PROMPT_TEMPLATE,
            name="test",
            version="2.0.0",
            content={"v": 2},
            channel=ReleaseChannel.STABLE,
        )

        # Current active should be 2.0.0
        active = release_manager.get_active(
            BundleType.PROMPT_TEMPLATE, "test", ReleaseChannel.STABLE
        )
        assert active.version == "2.0.0"

        # Rollback
        rolled_back = release_manager.rollback(
            BundleType.PROMPT_TEMPLATE, "test", ReleaseChannel.STABLE
        )

        assert rolled_back is not None
        assert rolled_back.version == "1.0.0"

        # Active should now be 1.0.0
        active = release_manager.get_active(
            BundleType.PROMPT_TEMPLATE, "test", ReleaseChannel.STABLE
        )
        assert active.version == "1.0.0"

    def test_promote_bundle(self, release_manager):
        """Test promoting a bundle between channels."""
        from agent.release_manager import BundleType, ReleaseChannel

        # Publish to nightly
        release_manager.publish(
            bundle_type=BundleType.PROMPT_TEMPLATE,
            name="new_feature",
            version="1.0.0",
            content={"feature": "new"},
            channel=ReleaseChannel.NIGHTLY,
        )

        # Promote to stable
        promoted = release_manager.promote(
            bundle_type=BundleType.PROMPT_TEMPLATE,
            name="new_feature",
            from_channel=ReleaseChannel.NIGHTLY,
            to_channel=ReleaseChannel.STABLE,
        )

        assert promoted is not None
        assert promoted.channel == ReleaseChannel.STABLE

    def test_verify_bundle(self, release_manager):
        """Test bundle verification."""
        from agent.release_manager import BundleType, ReleaseChannel

        bundle = release_manager.publish(
            bundle_type=BundleType.POLICY_BUNDLE,
            name="test",
            version="1.0.0",
            content={"policy": "test"},
            channel=ReleaseChannel.STABLE,
        )

        is_valid = release_manager.verify_bundle(bundle)
        assert is_valid
