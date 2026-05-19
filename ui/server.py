"""FastAPI status page server."""

import asyncio
import httpx
import json
import os
import subprocess
import sys
import threading
import yaml
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Backup Status")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.cache = None  # Disable template caching

_backup_running = False
_backup_status = "idle"


def _load_prefect_api_url() -> str:
    """Load Prefect API URL from config.yaml, falling back to default."""
    config_path = Path(__file__).parent.parent / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path) as f:
                config = yaml.safe_load(f)
            return config.get("ui", {}).get(
                "prefect_api_url", "http://127.0.0.1:4200/api"
            )
        except Exception:
            pass
    return "http://127.0.0.1:4200/api"


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

    last_run = None
    next_run = None
    in_progress = False

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Get last flow run
            resp = await client.get(
                f"{prefect_api_url}/flow_runs",
                params={
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
            resp = await client.get(
                f"{prefect_api_url}/deployments",
                params={
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
        },
    )


@app.post("/trigger")
async def trigger_backup():
    """Trigger an immediate backup run by executing flow.py directly."""
    global _backup_running, _backup_status

    if _backup_running:
        return {"status": "error", "message": "Backup already running"}

    project_root = Path(__file__).parent.parent
    python_exe = sys.executable
    flow_path = str(project_root / "flow.py")

    def run_backup():
        global _backup_running, _backup_status
        _backup_running = True
        _backup_status = "running"
        try:
            env = os.environ.copy()
            env["PREFECT_API_URL"] = _load_prefect_api_url()
            env["PYTHONPATH"] = str(project_root)
            env["PATH"] = str(Path(python_exe).parent) + os.pathsep + env.get("PATH", "")
            result = subprocess.run(
                [python_exe, flow_path],
                cwd=str(project_root),
                env=env,
                capture_output=True,
                text=True,
                timeout=3600,
            )
            _backup_status = "completed" if result.returncode == 0 else f"failed (rc={result.returncode})"
        except subprocess.TimeoutExpired:
            _backup_status = "timeout"
        except Exception as e:
            _backup_status = f"error: {e}"
        finally:
            _backup_running = False

    threading.Thread(target=run_backup, daemon=True).start()
    return {"status": "ok", "message": "Backup started", "debug": {"python": python_exe, "flow": flow_path}}


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
