import os
import pytest
from unittest import mock
from app.core.system_setup import SystemSetup
from app.config import Settings
from app.schemas.system import ValidationStatus


class TestSystemSetup:
    @pytest.fixture(autouse=True)
    def setup_test_env(self, monkeypatch):
        """Setup test environment before each test."""
        # Create a temporary directory in the current working directory
        tmp_dir = os.path.join(os.getcwd(), "tmp")
        test_plugins_dir = os.path.join(tmp_dir, "tests_plugins")

        # Ensure tmp directory exists and is writable
        os.makedirs(tmp_dir, exist_ok=True)
        os.chmod(tmp_dir, 0o755)  # Ensure tmp directory is writable

        # Mock the Settings class
        mock_settings = mock.Mock(spec=Settings)
        mock_settings.plugins_dir = test_plugins_dir
        mock_settings.credential_master_key = (
            "dGhpc2lzYXRlc3RrZXlmb3JjcmVkZW50aWFsZW5jcnlwdGlvbg=="
        )
        mock_settings.rollbar_access_token = (
            "test-rollbar-token-that-is-long-enough-to-be-valid"
        )
        monkeypatch.setattr("app.core.system_setup.get_settings", lambda: mock_settings)

        yield test_plugins_dir, mock_settings

        # Cleanup after each test - only remove the test-specific directory
        if os.path.exists(test_plugins_dir):
            os.chmod(test_plugins_dir, 0o755)  # Make sure it's writable before removal
            os.rmdir(test_plugins_dir)

    def test_validate_creates_plugins_directory(self, setup_test_env):
        """Test that validate creates the plugins directory if it doesn't exist."""
        test_plugins_dir, _ = setup_test_env

        # Run validation
        steps = SystemSetup.validate()

        # Check that the directory was created
        assert os.path.exists(test_plugins_dir)
        assert os.path.isdir(test_plugins_dir)
        assert len(steps) == 3  # Now we have 3 validation steps
        assert steps[0].status == ValidationStatus.OK
        assert steps[0].name == "Plugin Environment"

    def test_validate_uses_existing_plugins_directory(self, setup_test_env):
        """Test that validate uses an existing plugins directory."""
        test_plugins_dir, _ = setup_test_env
        os.makedirs(test_plugins_dir, exist_ok=True)
        os.chmod(test_plugins_dir, 0o755)  # Ensure it's writable

        # Run validation
        steps = SystemSetup.validate()

        # Check that the directory still exists
        assert os.path.exists(test_plugins_dir)
        assert os.path.isdir(test_plugins_dir)
        assert len(steps) == 3  # Now we have 3 validation steps
        assert steps[0].status == ValidationStatus.OK
        assert steps[0].name == "Plugin Environment"

    def test_validate_returns_error_on_unwritable_directory(self, setup_test_env):
        """Test that validate returns error status if directory is not writable."""
        test_plugins_dir, _ = setup_test_env
        os.makedirs(test_plugins_dir, exist_ok=True)

        # Make the directory read-only
        os.chmod(test_plugins_dir, 0o444)  # Read-only

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 3  # Now we have 3 validation steps
        assert steps[0].status == ValidationStatus.ERROR
        assert steps[0].name == "Plugin Environment"
        assert "not writable" in steps[0].message

        # Make writable again for cleanup
        os.chmod(test_plugins_dir, 0o755)

    def test_validate_credential_master_key(self, setup_test_env):
        """Test validation of credential master key."""
        _, mock_settings = setup_test_env
        # Set credential master key to None
        mock_settings.credential_master_key = None

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 3
        assert steps[1].status == ValidationStatus.ERROR
        assert steps[1].name == "Credential Master Key"
        assert "not set" in steps[1].message.lower()

    def test_validate_rollbar_token(self, setup_test_env):
        """Test validation of Rollbar access token."""
        _, mock_settings = setup_test_env
        # Set Rollbar token to None
        mock_settings.rollbar_access_token = None

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 3
        assert steps[2].status == ValidationStatus.ERROR
        assert steps[2].name == "Rollbar Access Token"
        assert "not set" in steps[2].message.lower()

    def test_all_validations_pass(self, setup_test_env):
        """Test that all validations pass when all requirements are met."""
        with mock.patch("cryptography.fernet.Fernet") as mock_fernet:
            mock_fernet.return_value = mock.Mock()
            steps = SystemSetup.validate()

            # Check that all steps pass
            assert len(steps) == 3
            for step in steps:
                assert step.status == ValidationStatus.OK
