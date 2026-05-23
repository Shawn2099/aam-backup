"""FastAPI status page server."""

import json
import sqlite3
import time
import yaml
from pathlib import Path

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.exceptions import HTTPException as StarletteHTTPException

app = FastAPI(title="Backup Status")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.cache = None

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "config.yaml"
DEFAULT_PREFECT_API_URL = "http://127.0.0.1:4200/api"
DEFAULT_HTTPX_TIMEOUT = 5.0
TRIGGER_TIMEOUT = 10.0
TRIGGER_RATE_LIMIT_SECONDS = 30.0

_trigger_last_called: float = 0.0
_config_cache: dict | None = None
_config_cache_time: float = 0.0
CONFIG_CACHE_TTL = 5.0


# ---------------------------------------------------------------------------
# Exception handlers — prevent internal traceback leaks
# ---------------------------------------------------------------------------

@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(HTTPException)
async def fastapi_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_config() -> dict:
    """Load config.yaml with caching to avoid repeated disk reads."""
    global _config_cache, _config_cache_time
    now = time.monotonic()
    if _config_cache is not None and (now - _config_cache_time) < CONFIG_CACHE_TTL:
        return _config_cache
    if DEFAULT_CONFIG_PATH.exists():
        try:
            with open(DEFAULT_CONFIG_PATH, encoding="utf-8") as f:
                _config_cache = yaml.safe_load(f) or {}
        except Exception:
            _config_cache = {}
    else:
        _config_cache = {}
    _config_cache_time = now
    return _config_cache


def _load_prefect_api_url() -> str:
    config = _load_config()
    return config.get("ui", {}).get("prefect_api_url", DEFAULT_PREFECT_API_URL)


def _get_backup_destinations() -> dict:
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


def _get_manifest_info(db_path: str) -> dict:
    """Safely query manifest DB for file count and size."""
    result = {}
    db_file = Path(db_path)
    if not db_file.exists():
        return {"exists": False}

    try:
        result["size_mb"] = round(db_file.stat().st_size / (1024 ** 2), 1)
        result["exists"] = True
    except Exception:
        return {"error": "unavailable"}

    try:
        conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        cursor = conn.execute("SELECT COUNT(*) as cnt FROM file_manifest")
        row = cursor.fetchone()
        result["file_count"] = row["cnt"] if row else 0
    except Exception:
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

    return result


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/health")
async def health():
    prefect_api_url = _load_prefect_api_url()
    prefect_healthy = False

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
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
    prefect_api_url = _load_prefect_api_url()
    destinations = _get_backup_destinations()

    last_run = None
    next_run = None
    in_progress = False

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
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
        pass

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
    return _get_backup_destinations()


@app.post("/trigger")
async def trigger_backup():
    global _trigger_last_called
    now = time.monotonic()
    if now - _trigger_last_called < TRIGGER_RATE_LIMIT_SECONDS:
        raise HTTPException(status_code=429, detail="Rate limited. Please wait before triggering again.")
    _trigger_last_called = now

    prefect_api_url = _load_prefect_api_url()

    try:
        async with httpx.AsyncClient(timeout=TRIGGER_TIMEOUT) as client:
            resp = await client.post(
                f"{prefect_api_url}/deployments/filter",
                json={
                    "deployments": {"name": {"any_": ["nightly-backup-production"]}},
                },
            )
            if resp.status_code != 200 or not resp.json():
                return {"status": "error", "message": "Deployment not found"}

            deployment_id = resp.json()[0]["id"]

            resp = await client.post(
                f"{prefect_api_url}/flow_runs",
                json={"deployment_id": deployment_id},
            )
            if resp.status_code == 201:
                return {"status": "ok", "message": "Backup started"}
            return {"status": "error", "message": "Failed to create flow run"}

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Prefect API unavailable: {e}")


@app.get("/metrics")
async def get_metrics():
    config = _load_config()
    log_dir = config.get("paths", {}).get("log_directory")
    if not log_dir:
        return {"status": "error", "message": "Could not determine log directory"}

    metrics_file = Path(log_dir) / "backup_metrics.jsonl"
    if not metrics_file.exists():
        return {"status": "no_data"}

    try:
        with open(metrics_file, encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return {"status": "no_data"}
            latest = json.loads(lines[-1])
    except Exception:
        return {"status": "error", "message": "Failed to read metrics data"}

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


@app.get("/api/system")
async def get_system_status():
    import shutil

    config = _load_config()
    paths = config.get("paths", {})

    result = {"source": {}, "lan": {}, "manifest": {}}

    source_drive = paths.get("source_drive", "")
    if source_drive:
        try:
            usage = shutil.disk_usage(source_drive)
            result["source"] = {
                "free_gb": round(usage.free / (1024 ** 3), 1),
                "total_gb": round(usage.total / (1024 ** 3), 1),
                "used_pct": round(usage.used / usage.total * 100, 0),
            }
        except Exception:
            result["source"] = {"error": "unavailable"}

    lan_dest = paths.get("lan_destination", "")
    if lan_dest and config.get("lan_backup", {}).get("enabled", True):
        try:
            usage = shutil.disk_usage(lan_dest)
            result["lan"] = {
                "free_gb": round(usage.free / (1024 ** 3), 1),
                "total_gb": round(usage.total / (1024 ** 3), 1),
                "used_pct": round(usage.used / usage.total * 100, 0),
            }
        except Exception:
            result["lan"] = {"error": "unavailable"}

    db_path = paths.get("database_path", "")
    if db_path:
        result["manifest"] = _get_manifest_info(db_path)
    else:
        result["manifest"] = {"error": "unavailable"}

    return result


@app.get("/api/history")
async def get_run_history(limit: int = 7):
    prefect_api_url = _load_prefect_api_url()

    try:
        async with httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT) as client:
            resp = await client.post(
                f"{prefect_api_url}/flow_runs/filter",
                json={
                    "flow_runs": {"flow": {"name": {"any_": ["nightly-backup"]}}},
                    "sort": "START_TIME_DESC",
                    "limit": limit,
                },
            )
            if resp.status_code == 200:
                runs = resp.json()
                return {
                    "runs": [
                        {
                            "id": r["id"],
                            "state_name": r.get("state_name"),
                            "start_time": r.get("start_time"),
                            "end_time": r.get("end_time"),
                            "total_run_time": r.get("total_run_time"),
                        }
                        for r in runs
                    ],
                    "count": len(runs),
                }
    except Exception:
        pass

    return {"runs": [], "count": 0}
