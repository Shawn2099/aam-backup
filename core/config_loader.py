"""Configuration loader — reads YAML, validates with Pydantic, retrieves credentials."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from models.config_model import AppConfig


class ConfigurationError(Exception):
    """Raised when configuration is invalid or credentials cannot be retrieved."""

    def __init__(self, message: str, field: str | None = None):
        self.field = field
        super().__init__(message)


def load_config(config_path: str | Path) -> AppConfig:
    """Load and validate configuration from YAML file.

    Args:
        config_path: Path to config.yaml.

    Returns:
        Validated AppConfig instance.

    Raises:
        ConfigurationError: If config file is missing, invalid YAML, or validation fails.
    """
    config_path = Path(config_path)
    if not config_path.exists():
        raise ConfigurationError(f"Config file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw: dict[str, Any] = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in config file: {e}")

    if not isinstance(raw, dict):
        raise ConfigurationError("Config file must be a YAML mapping")

    try:
        return AppConfig(**raw)
    except ValidationError as e:
        errors = []
        for error in e.errors():
            loc = ".".join(str(part) for part in error["loc"])
            errors.append(f"{loc}: {error['msg']}")
        raise ConfigurationError(
            "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )


def get_gcs_key_path(credential_name: str) -> str:
    """Retrieve GCS service account key path from Windows Credential Manager.

    Args:
        credential_name: Name of the credential in Credential Manager.

    Returns:
        Full path to the GCS service account JSON key file.

    Raises:
        ConfigurationError: If credential is not found.
    """
    try:
        import keyring
        key_path = keyring.get_password("BackupAgent", credential_name)
    except Exception as e:
        raise ConfigurationError(
            f"Failed to retrieve credential '{credential_name}' from Windows Credential Manager: {e}"
        )

    if key_path is None:
        raise ConfigurationError(
            f"Credential '{credential_name}' not found in Windows Credential Manager"
        )

    return key_path
