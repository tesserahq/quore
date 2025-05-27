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

        # Validate plugin environment
        plugin_step = SystemSetup._validate_plugin_environment()
        steps.append(plugin_step)

        # Add more validation steps here as needed
        # steps.extend(SystemSetup._validate_database_connection())
        # steps.extend(SystemSetup._validate_redis_connection())
        # etc.

        return steps

    @staticmethod
    def _validate_plugin_environment() -> ValidationStep:
        """Validate and setup the plugin environment."""
        settings = get_settings()
        plugins_dir = settings.plugins_dir

        try:
            # Only create directory if it doesn't exist
            if not os.path.exists(plugins_dir):
                os.makedirs(plugins_dir)

            # Ensure the directory is writable
            if not os.access(plugins_dir, os.W_OK):
                return ValidationStep(
                    name="Plugin Environment",
                    status=ValidationStatus.ERROR,
                    message=f"Plugin directory {plugins_dir} is not writable",
                )

            return ValidationStep(
                name="Plugin Environment",
                status=ValidationStatus.OK,
                message="Plugin environment validated successfully",
            )
        except Exception as e:
            return ValidationStep(
                name="Plugin Environment", status=ValidationStatus.ERROR, message=str(e)
            )
