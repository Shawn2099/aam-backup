"""FastAPI status page server."""

import httpx
import json
import yaml
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Backup Status")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.cache = None  # Disable template caching


def _load_config() -> dict:
    """Load config.yaml and return as dict."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path) as f:
                return yaml.safe_load(f)
        except Exception:
            pass
    return {}


def _load_prefect_api_url() -> str:
    """Load Prefect API URL from config.yaml, falling back to default."""
    config = _load_config()
    return config.get("ui", {}).get(
        "prefect_api_url", "http://127.0.0.1:4200/api"
    )


def _get_backup_destinations() -> dict:
    """Return backup destination status from config (no Pydantic needed for UI)."""
    config = _load_config()
    lan = config.get("lan_backup", {})
    cloud = config.get("cloud_backup", {})
    paths = config.get("paths", {})

    lan_enabled = lan.get("enabled", True)
    cloud_enabled = cloud.get("enabled", True)
    any_enabled = lan_enabled or cloud_enabled
    all_disabled = not any_enabled

    warning = None
    if all_disabled:
        warning = "Both LAN and Cloud backup are disabled. No data will be backed up."

    return {
        "lan": {
            "enabled": lan_enabled,
            "label": "LAN Backup",
            "destination": paths.get("lan_destination", ""),
        },
        "cloud": {
            "enabled": cloud_enabled,
            "label": "Cloud Backup",
            "provider": cloud.get("provider", "gcs"),
            "bucket": cloud.get("bucket", ""),
        },
        "any_enabled": any_enabled,
        "all_disabled": all_disabled,
        "warning": warning,
    }


@app.get("/health")
async def health():
    """Health check endpoint for Servy monitoring and external tools."""
    prefect_api_url = _load_prefect_api_url()
    prefect_healthy = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{prefect_api_url}/health")
            prefect_healthy = resp.status_code == 200
    except Exception:
        pass

    status = "healthy" if prefect_healthy else "degraded"
    return JSONResponse({
        "status": status,
        "prefect_api": "connected" if prefect_healthy else "unavailable",
        "service": "backup-ui",
    })


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the status page with last run info and next scheduled run."""
    prefect_api_url = _load_prefect_api_url()
    destinations = _get_backup_destinations()

    last_run = None
    next_run = None
    in_progress = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get last flow run
            resp = await client.post(
                f"{prefect_api_url}/flow_runs/filter",
                json={
                    "flow_runs": {"flow": {"name": {"any_": ["nightly-backup"]}}},
                    "sort": "START_TIME_DESC",
                    "limit": 1,
                },
            )
            if resp.status_code == 200:
                runs = resp.json()
                if runs:
                    last_run = runs[0]
                    in_progress = last_run.get("state_name") == "Running"

            # Get deployment schedule
            resp = await client.post(
                f"{prefect_api_url}/deployments/filter",
                json={
                    "deployments": {"name": {"any_": ["nightly-backup-production"]}},
                },
            )
            if resp.status_code == 200:
                deployments = resp.json()
                if deployments:
                    next_run = deployments[0]

    except Exception:
        pass  # UI gracefully degrades if Prefect is unavailable

    return templates.TemplateResponse(
        request=request,
        name="status.html",
        context={
            "last_run": last_run,
            "next_run": next_run,
            "in_progress": in_progress,
            "prefect_api_url": prefect_api_url,
            "destinations": destinations,
        },
    )


@app.get("/config", response_class=JSONResponse)
async def get_config():
    """Return backup destination configuration status."""
    return _get_backup_destinations()


@app.post("/trigger")
async def trigger_backup():
    """Trigger an immediate backup run via Prefect API."""
    prefect_api_url = _load_prefect_api_url()

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get deployment ID
            resp = await client.post(
                f"{prefect_api_url}/deployments/filter",
                json={
                    "deployments": {"name": {"any_": ["nightly-backup-production"]}},
                },
            )
            if resp.status_code != 200 or not resp.json():
                return {"status": "error", "message": "Deployment not found"}

            deployment_id = resp.json()[0]["id"]

            # Create flow run
            resp = await client.post(
                f"{prefect_api_url}/flow_runs",
                json={"deployment_id": deployment_id},
            )
            if resp.status_code == 201:
                return {"status": "ok", "message": "Backup started"}
            return {"status": "error", "message": "Failed to create flow run"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.get("/metrics")
async def get_metrics():
    """Return latest backup metrics including capacity info."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    log_dir = None
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            log_dir = config.get("paths", {}).get("log_directory")
        except Exception:
            pass

    if not log_dir:
        return {"status": "error", "message": "Could not determine log directory"}

    metrics_file = Path(log_dir) / "backup_metrics.jsonl"
    if not metrics_file.exists():
        return {"status": "no_data"}

    # Read last line for latest metrics
    try:
        with open(metrics_file) as f:
            lines = f.readlines()
            if not lines:
                return {"status": "no_data"}
            latest = json.loads(lines[-1])
    except Exception as e:
        return {"status": "error", "message": str(e)}

    capacity = latest.get("capacity", {})
    lan_free_gb = capacity.get("lan_free_bytes", 0) / (1024 ** 3) if capacity.get("lan_free_bytes") else 0
    total_source_gb = capacity.get("total_source_bytes", 0) / (1024 ** 3) if capacity.get("total_source_bytes") else 0

    lan_data = latest.get("lan", {})
    cloud_data = latest.get("cloud", {})

    return {
        "status": "ok",
        "timestamp": latest.get("timestamp"),
        "overall_status": latest.get("overall_status"),
        "duration_seconds": latest.get("duration_seconds"),
        "capacity": {
            "lan_free_gb": round(lan_free_gb, 1),
            "total_source_gb": round(total_source_gb, 1),
            "total_file_count": capacity.get("total_file_count", 0),
        },
        "scan": latest.get("scan", {}),
        "lan": {
            "files_copied": lan_data.get("files_copied", 0),
            "bytes_copied": lan_data.get("bytes_copied", 0),
            "files_failed": lan_data.get("files_failed", 0),
            "checksum_verified": lan_data.get("checksum_verified", 0),
            "checksum_mismatches": lan_data.get("checksum_mismatches", 0),
        },
        "cloud": cloud_data,
    }
