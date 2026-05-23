"""E2E Prefect Flow Runner - validates full nightly_backup() flow with ephemeral server.

Usage:
    C:\BackupAgent\venv\Scripts\python.exe e2e_prefect_runner.py C:\BackupAgent\config.yaml
"""

import sys
import os
import subprocess
import time
import urllib.request
from pathlib import Path
import shutil

sys.path.insert(0, str(Path(__file__).parent))

RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def header(text: str) -> None:
    print(f"\n{CYAN}{'='*60}{RESET}")
    print(f"{BOLD}{CYAN}{text}{RESET}")
    print(f"{CYAN}{'='*60}{RESET}")


def ok(text: str) -> None:
    print(f"  {GREEN}PASS{RESET}  {text}")


def fail(text: str) -> None:
    print(f"  {RED}FAIL{RESET}  {text}")


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"

    os.environ["PREFECT_HOME"] = r"C:\BackupAgent\prefect"
    os.environ["PREFECT_SERVER_ALLOW_EPHEMERAL_MODE"] = "true"
    os.environ["PREFECT_API_URL"] = "http://127.0.0.1:4200/api"

    from core.config_loader import load_config
    config = load_config(config_path)

    # Clean state
    header("CLEAN STATE")
    db_path = Path(config.paths.database_path)
    if db_path.exists():
        db_path.unlink()
    for suffix in ["-wal", "-shm"]:
        p = Path(str(db_path) + suffix)
        if p.exists():
            p.unlink()
    ok("Cleaned manifest.db + WAL/SHM")

    lan_dest = Path(config.paths.lan_destination)
    if lan_dest.exists():
        for item in lan_dest.iterdir():
            if item.is_dir():
                shutil.rmtree(str(item))
            else:
                item.unlink()
        ok(f"Cleaned LAN destination: {lan_dest}")
    else:
        lan_dest.mkdir(parents=True, exist_ok=True)

    # Start Prefect server
    header("START PREFECT SERVER")
    print("  Starting prefect server on 127.0.0.1:4200...")
    server = subprocess.Popen(
        [r"C:\BackupAgent\venv\Scripts\prefect.exe", "server", "start",
         "--host", "0.0.0.0", "--port", "4200"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=os.environ.copy(),
    )

    # Wait for server to be ready
    ready = False
    for i in range(40):
        time.sleep(2)
        try:
            resp = urllib.request.urlopen("http://127.0.0.1:4200/api/health", timeout=3)
            if resp.status == 200:
                print(f"  Server ready after {(i+1)*2}s")
                ready = True
                break
        except Exception:
            print(".", end="", flush=True)
    print()

    if not ready:
        fail("Prefect server failed to start!")
        out, err = server.communicate(timeout=10)
        if out:
            print(out.decode(errors="replace")[-1000:])
        if err:
            print(err.decode(errors="replace")[-1000:])
        server.terminate()
        return 1

    try:
        # Run the flow
        header("RUN NIGHTLY BACKUP FLOW")
        print(f"  Config: {config_path}")
        from flow import nightly_backup
        result = nightly_backup(config_path)
        ok(f"Flow result: {result}")
        return 0

    except Exception as e:
        fail(f"Flow failed: {e}")
        return 1

    finally:
        header("STOP PREFECT SERVER")
        server.terminate()
        try:
            server.wait(timeout=15)
            ok("Server stopped")
        except subprocess.TimeoutExpired:
            server.kill()
            ok("Server killed")


if __name__ == "__main__":
    sys.exit(main())
