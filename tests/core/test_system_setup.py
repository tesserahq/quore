import os
import pytest
from app.core.system_setup import SystemSetup
from app.config import get_settings
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

        # Mock the settings before they are loaded
        monkeypatch.setenv("PLUGINS_DIR", test_plugins_dir)

        yield test_plugins_dir

        # Cleanup after each test - only remove the test-specific directory
        if os.path.exists(test_plugins_dir):
            os.chmod(test_plugins_dir, 0o755)  # Make sure it's writable before removal
            os.rmdir(test_plugins_dir)

    def test_validate_creates_plugins_directory(self, setup_test_env):
        """Test that validate creates the plugins directory if it doesn't exist."""
        test_plugins_dir = setup_test_env

        # Run validation
        steps = SystemSetup.validate()

        # Check that the directory was created
        assert os.path.exists(test_plugins_dir)
        assert os.path.isdir(test_plugins_dir)
        assert len(steps) == 1
        assert steps[0].status == ValidationStatus.OK

    def test_validate_uses_existing_plugins_directory(self, setup_test_env):
        """Test that validate uses an existing plugins directory."""
        test_plugins_dir = setup_test_env
        os.makedirs(test_plugins_dir, exist_ok=True)
        os.chmod(test_plugins_dir, 0o755)  # Ensure it's writable

        # Run validation
        steps = SystemSetup.validate()

        # Check that the directory still exists
        assert os.path.exists(test_plugins_dir)
        assert os.path.isdir(test_plugins_dir)
        assert len(steps) == 1
        assert steps[0].status == ValidationStatus.OK

    def test_validate_returns_error_on_unwritable_directory(self, setup_test_env):
        """Test that validate returns error status if directory is not writable."""
        test_plugins_dir = setup_test_env
        os.makedirs(test_plugins_dir, exist_ok=True)

        # Make the directory read-only
        os.chmod(test_plugins_dir, 0o444)  # Read-only

        # Run validation
        steps = SystemSetup.validate()

        # Check validation result
        assert len(steps) == 1
        assert steps[0].status == ValidationStatus.ERROR
        assert "not writable" in steps[0].message

        # Make writable again for cleanup
        os.chmod(test_plugins_dir, 0o755)
