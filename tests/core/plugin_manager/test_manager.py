import os
import shutil
import tempfile
import subprocess
from unittest.mock import patch, MagicMock
from uuid import uuid4
import pytest
from sqlalchemy.orm import Session

from app.core.plugin_manager.manager import PluginManager
from app.models.plugin import Plugin
from app.models.credential import Credential
from app.constants.credentials import CredentialType


@pytest.fixture
def temp_plugins_dir():
    """Create a temporary directory for plugins."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_db():
    """Create a mock database session."""
    return MagicMock(spec=Session)


@pytest.fixture
def mock_plugin():
    """Create a mock plugin."""
    return Plugin(
        id=uuid4(),
        workspace_id=uuid4(),
        name="Test Plugin",
        repository_url="https://github.com/test/repo.git",
        version="v1.0.0",
    )


@pytest.fixture
def mock_plugin_with_ssh():
    """Create a mock plugin with SSH repository."""
    return Plugin(
        id=uuid4(),
        workspace_id=uuid4(),
        name="Test SSH Plugin",
        repository_url="git@github.com:test/repo.git",
        version="v1.0.0",
    )


@pytest.fixture
def mock_credential():
    """Create a mock credential."""
    return Credential(
        id=uuid4(),
        name="Test Credential",
        type=CredentialType.GITHUB_PAT,
        encrypted_data=b"encrypted_data",
    )


class TestPluginManager:
    def test_download_public_repo(self, mock_db, mock_plugin, temp_plugins_dir):
        """Test cloning a public repository."""
        with patch(
            "app.services.plugin_registry.PluginRegistryService"
        ) as mock_service:
            mock_service.return_value.get_plugin.return_value = mock_plugin
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.plugins_dir = temp_plugins_dir
                plugin_dir = os.path.join(
                    temp_plugins_dir, str(mock_plugin.workspace_id), str(mock_plugin.id)
                )
                with patch(
                    "app.core.path_manager.PathManager.get_plugin_dir",
                    return_value=plugin_dir,
                ):
                    # Patch apply_git_credentials to return the expected command and env
                    with patch(
                        "app.core.plugin_manager.manager.apply_git_credentials"
                    ) as mock_apply_git_credentials:
                        expected_cmd = ["git", "clone", mock_plugin.repository_url]
                        expected_env = os.environ.copy()
                        mock_apply_git_credentials.return_value = (
                            expected_cmd.copy(),
                            expected_env,
                        )
                        # Ensure PluginManager uses the actual test plugin object
                        with patch(
                            "app.core.plugin_manager.manager.PluginRegistryService.get_plugin",
                            return_value=mock_plugin,
                        ):
                            manager = PluginManager(mock_db, mock_plugin.id)
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

                            def run_side_effect(cmd, env=None, check=None):
                                print(
                                    f"subprocess.run called with: {cmd}, env: {env}, check: {check}"
                                )
                                if cmd[:2] == ["git", "clone"]:
                                    os.makedirs(manager.plugin_dir, exist_ok=True)
                                return MagicMock(returncode=0)

                            with patch("subprocess.run") as mock_run:
                                mock_run.side_effect = run_side_effect
                                manager.clone_repository()
                                mock_run.assert_any_call(
                                    [
                                        "git",
                                        "clone",
                                        mock_plugin.repository_url,
                                        manager.plugin_dir,
                                    ],
                                    env=expected_env,
                                    check=True,
                                )
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

    def test_download_with_credentials(
        self, mock_db, mock_plugin, mock_credential, temp_plugins_dir
    ):
        """Test cloning a repository with credentials."""
        mock_plugin.credential_id = mock_credential.id
        with patch(
            "app.services.plugin_registry.PluginRegistryService"
        ) as mock_service:
            mock_service.return_value.get_plugin.return_value = mock_plugin
            with patch(
                "app.services.credential.CredentialService"
            ) as mock_cred_service:
                mock_cred_service.return_value.get_credential_fields.return_value = {
                    "token": "test_token"
                }
                with patch("app.config.get_settings") as mock_settings:
                    mock_settings.return_value.plugins_dir = temp_plugins_dir
                    plugin_dir = os.path.join(
                        temp_plugins_dir,
                        str(mock_plugin.workspace_id),
                        str(mock_plugin.id),
                    )
                    with patch(
                        "app.core.path_manager.PathManager.get_plugin_dir",
                        return_value=plugin_dir,
                    ):
                        with patch(
                            "app.core.plugin_manager.manager.apply_git_credentials"
                        ) as mock_apply_git_credentials:
                            expected_url = mock_plugin.repository_url.replace(
                                "https://", "https://test_token@"
                            )
                            expected_cmd = ["git", "clone", expected_url]
                            expected_env = os.environ.copy()
                            mock_apply_git_credentials.return_value = (
                                expected_cmd.copy(),
                                expected_env,
                            )
                            manager = PluginManager(mock_db, mock_plugin.id)
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

                            def run_side_effect(cmd, env=None, check=None):
                                if cmd[:2] == ["git", "clone"]:
                                    os.makedirs(manager.plugin_dir, exist_ok=True)
                                return MagicMock(returncode=0)

                            with patch("subprocess.run") as mock_run:
                                mock_run.side_effect = run_side_effect
                                manager.clone_repository()
                                mock_run.assert_any_call(
                                    ["git", "clone", expected_url, manager.plugin_dir],
                                    env=expected_env,
                                    check=True,
                                )
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

    def test_download_with_ssh(
        self, mock_db, mock_plugin_with_ssh, mock_credential, temp_plugins_dir
    ):
        """Test cloning a repository with SSH credentials."""
        mock_plugin_with_ssh.credential_id = mock_credential.id
        with patch(
            "app.services.plugin_registry.PluginRegistryService"
        ) as mock_service:
            mock_service.return_value.get_plugin.return_value = mock_plugin_with_ssh
            with patch(
                "app.services.credential.CredentialService"
            ) as mock_cred_service:
                mock_cred_service.return_value.get_credential_fields.return_value = {
                    "private_key": "test_private_key"
                }
                with patch("app.config.get_settings") as mock_settings:
                    mock_settings.return_value.plugins_dir = temp_plugins_dir
                    plugin_dir = os.path.join(
                        temp_plugins_dir,
                        str(mock_plugin_with_ssh.workspace_id),
                        str(mock_plugin_with_ssh.id),
                    )
                    with patch(
                        "app.core.path_manager.PathManager.get_plugin_dir",
                        return_value=plugin_dir,
                    ):
                        with patch(
                            "app.core.plugin_manager.manager.apply_git_credentials"
                        ) as mock_apply_git_credentials:
                            expected_cmd = [
                                "git",
                                "clone",
                                mock_plugin_with_ssh.repository_url,
                            ]
                            expected_env = MagicMock()
                            mock_apply_git_credentials.return_value = (
                                expected_cmd.copy(),
                                expected_env,
                            )
                            manager = PluginManager(mock_db, mock_plugin_with_ssh.id)
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

                            def run_side_effect(cmd, env=None, check=None):
                                if cmd[:2] == ["git", "clone"]:
                                    os.makedirs(manager.plugin_dir, exist_ok=True)
                                return MagicMock(returncode=0)

                            with patch("subprocess.run") as mock_run:
                                mock_run.side_effect = run_side_effect
                                manager.clone_repository()
                                mock_run.assert_any_call(
                                    [
                                        "git",
                                        "clone",
                                        mock_plugin_with_ssh.repository_url,
                                        manager.plugin_dir,
                                    ],
                                    env=expected_env,
                                    check=True,
                                )
                            if os.path.exists(manager.plugin_dir):
                                shutil.rmtree(manager.plugin_dir)

    def test_download_cleanup_existing(self, mock_db, mock_plugin, temp_plugins_dir):
        """Test that existing repository is cleaned up before cloning."""
        with patch(
            "app.services.plugin_registry.PluginRegistryService"
        ) as mock_service:
            mock_service.return_value.get_plugin.return_value = mock_plugin
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.plugins_dir = temp_plugins_dir
                plugin_dir = os.path.join(
                    temp_plugins_dir, str(mock_plugin.workspace_id), str(mock_plugin.id)
                )
                with patch(
                    "app.core.path_manager.PathManager.get_plugin_dir",
                    return_value=plugin_dir,
                ):
                    with patch(
                        "app.core.plugin_manager.manager.apply_git_credentials"
                    ) as mock_apply_git_credentials:
                        expected_cmd = ["git", "clone", mock_plugin.repository_url]
                        expected_env = os.environ.copy()
                        mock_apply_git_credentials.return_value = (
                            expected_cmd.copy(),
                            expected_env,
                        )
                        manager = PluginManager(mock_db, mock_plugin.id)
                        os.makedirs(manager.plugin_dir, exist_ok=True)
                        with open(
                            os.path.join(manager.plugin_dir, "test.txt"), "w"
                        ) as f:
                            f.write("test")

                        def run_side_effect(cmd, env=None, check=None):
                            if cmd[:2] == ["git", "clone"]:
                                os.makedirs(manager.plugin_dir, exist_ok=True)
                            return MagicMock(returncode=0)

                        with patch("subprocess.run") as mock_run:
                            mock_run.side_effect = run_side_effect
                            manager.clone_repository()
                            assert not os.path.exists(
                                os.path.join(manager.plugin_dir, "test.txt")
                            )
                        if os.path.exists(manager.plugin_dir):
                            shutil.rmtree(manager.plugin_dir)

    def test_download_error_handling(self, mock_db, mock_plugin, temp_plugins_dir):
        """Test error handling during repository cloning."""
        # Mock the plugin service
        with patch(
            "app.services.plugin_registry.PluginRegistryService"
        ) as mock_service:
            mock_service.return_value.get_plugin.return_value = mock_plugin

            # Mock the settings
            with patch("app.config.get_settings") as mock_settings:
                mock_settings.return_value.plugins_dir = temp_plugins_dir

                # Create the plugin manager
                manager = PluginManager(mock_db, mock_plugin.id)

                # Create the plugin directory
                os.makedirs(manager.plugin_dir, exist_ok=True)

                # Mock subprocess.run to raise an error
                with patch("subprocess.run") as mock_run:
                    mock_run.side_effect = subprocess.CalledProcessError(1, "git clone")

                    # Verify that the error is properly propagated
                    with pytest.raises(RuntimeError) as exc_info:
                        manager.clone_repository()
                    assert "Failed to download plugin" in str(exc_info.value)

                # Clean up
                if os.path.exists(manager.plugin_dir):
                    shutil.rmtree(manager.plugin_dir)
