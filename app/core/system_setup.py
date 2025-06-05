import os
from typing import List
from app.config import get_settings
from app.schemas.system import ValidationStep, ValidationStatus


class SystemSetup:
    """Handles system-level validations and setup."""

    @staticmethod
    def validate() -> List[ValidationStep]:
        """Perform all system-level validations and return their status."""
        steps: List[ValidationStep] = []

        # Validate credential master key
        credential_step = SystemSetup._validate_credential_master_key()
        steps.append(credential_step)

        # Validate Rollbar access token
        rollbar_step = SystemSetup._validate_rollbar_token()
        steps.append(rollbar_step)

        # Add more validation steps here as needed
        # steps.extend(SystemSetup._validate_database_connection())
        # steps.extend(SystemSetup._validate_redis_connection())
        # etc.

        return steps

    @staticmethod
    def _validate_credential_master_key() -> ValidationStep:
        """Validate the credential master key."""
        settings = get_settings()
        master_key = settings.credential_master_key

        if not master_key:
            return ValidationStep(
                name="Credential Master Key",
                status=ValidationStatus.ERROR,
                message="Credential master key is not set",
            )

        try:
            # Try to create a Fernet instance with the key to validate it
            from cryptography.fernet import Fernet

            Fernet(master_key.encode())
            return ValidationStep(
                name="Credential Master Key",
                status=ValidationStatus.OK,
                message="Credential master key validated successfully",
            )
        except Exception as e:
            return ValidationStep(
                name="Credential Master Key",
                status=ValidationStatus.ERROR,
                message=f"Invalid credential master key: {str(e)}",
            )

    @staticmethod
    def _validate_rollbar_token() -> ValidationStep:
        """Validate the Rollbar access token."""
        settings = get_settings()
        token = settings.rollbar_access_token

        if not token:
            return ValidationStep(
                name="Rollbar Access Token",
                status=ValidationStatus.ERROR,
                message="Rollbar access token is not set",
            )

        # Rollbar tokens are typically 32 characters long
        if len(token) < 32:
            return ValidationStep(
                name="Rollbar Access Token",
                status=ValidationStatus.ERROR,
                message="Invalid Rollbar access token format",
            )

        return ValidationStep(
            name="Rollbar Access Token",
            status=ValidationStatus.OK,
            message="Rollbar access token validated successfully",
        )
