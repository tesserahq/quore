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
        # Mock the Settings class
        mock_settings = mock.Mock(spec=Settings)
        mock_settings.credential_master_key = (
            "dGhpc2lzYXRlc3RrZXlmb3JjcmVkZW50aWFsZW5jcnlwdGlvbg=="
        )
        mock_settings.rollbar_access_token = (
            "test-rollbar-token-that-is-long-enough-to-be-valid"
        )
        monkeypatch.setattr("app.core.system_setup.get_settings", lambda: mock_settings)

        yield mock_settings

    def test_validate_credential_master_key(self, setup_test_env):
        """Test validation of credential master key."""
        mock_settings = setup_test_env
        # Set credential master key to None
        mock_settings.credential_master_key = None

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 2
        assert steps[0].status == ValidationStatus.ERROR
        assert steps[0].name == "Credential Master Key"
        assert "not set" in steps[0].message.lower()

    def test_validate_rollbar_token(self, setup_test_env):
        """Test validation of Rollbar access token."""
        mock_settings = setup_test_env
        # Set Rollbar token to None
        mock_settings.rollbar_access_token = None

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 2
        assert steps[1].status == ValidationStatus.ERROR
        assert steps[1].name == "Rollbar Access Token"
        assert "not set" in steps[1].message.lower()

    def test_all_validations_pass(self, setup_test_env):
        """Test that all validations pass when all requirements are met."""
        with mock.patch("cryptography.fernet.Fernet") as mock_fernet:
            mock_fernet.return_value = mock.Mock()
            steps = SystemSetup.validate()

            # Check that all steps pass
            assert len(steps) == 2
            for step in steps:
                assert step.status == ValidationStatus.OK
