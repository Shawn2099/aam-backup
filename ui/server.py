"""FastAPI status page server."""

import httpx
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Backup Status")

templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))
templates.env.cache = None  # Disable template caching


@app.get("/health")
async def health():
    """Health check endpoint for NSSM monitoring and external tools.

    Returns:
        JSON with service status and timestamp.
    """
    prefect_api_url = "http://127.0.0.1:4200/api"
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
    prefect_api_url = "http://127.0.0.1:4200/api"

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
    """Trigger an immediate backup run via Prefect API."""
    prefect_api_url = "http://127.0.0.1:4200/api"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            # Get deployment ID
            resp = await client.get(
                f"{prefect_api_url}/deployments",
                params={
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
