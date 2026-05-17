"""Prefect task: load configuration."""

from pathlib import Path

from prefect import task

from core.config_loader import load_config, get_gcs_key_path
from models.config_model import AppConfig


@task(name="load_config_task", tags=["setup"], retries=0)
def load_config_task(config_path: str) -> tuple[AppConfig, str]:
    """Load and validate configuration, retrieve GCS key path.

    Args:
        config_path: Path to config.yaml.

    Returns:
        Tuple of (AppConfig, gcs_key_path).
    """
    config = load_config(config_path)
    gcs_key_path = get_gcs_key_path(config.cloud_credentials.credential_name)
    return config, gcs_key_path
