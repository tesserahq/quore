from enum import Enum


class CredentialType(str, Enum):
    """Enum for credential types."""

    GITHUB_PAT = "github_pat"
    GITLAB_PAT = "gitlab_pat"
    SSH_KEY = "ssh_key"
