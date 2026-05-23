"""Prefect task: load configuration."""


from prefect import task
from prefect.logging import get_run_logger
from prefect.exceptions import MissingContextError

from core.config_loader import load_config, get_gcs_key_path
from core.logging_setup import get_task_logger
from models.config_model import AppConfig


@task(
    name="load_config_task",
    tags=["setup"],
    retries=2,
    retry_delay_seconds=[10, 30],
    task_run_name="load-config",
)
def load_config_task(config_path: str) -> tuple[AppConfig, str]:
    """Load and validate configuration, retrieve GCS key path.

    Args:
        config_path: Path to config.yaml.

    Returns:
        Tuple of (AppConfig, gcs_key_path).
    """
    logger = get_task_logger()
    logger.info(f"Loading configuration from {config_path}")

    config = load_config(config_path)

    if config.cloud_backup.enabled:
        gcs_key_path = get_gcs_key_path(config.cloud_credentials.credential_name)
    else:
        gcs_key_path = ""

    logger.info(f"Configuration loaded for firm: {config.firm.name}")
    return config, gcs_key_path
