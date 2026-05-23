"""E2E Core Pipeline Runner — validates scan + robocopy + manifest + verify.

No Prefect. No Prefect imports. No GCS. Pure core pipeline validation.

Usage:
    C:\BackupAgent\venv\Scripts\python.exe e2e_core_runner.py C:\BackupAgent\config.yaml
"""

import sys
import shutil
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from core.config_loader import load_config
from core.scanner import scan_drive
from core.robocopy import run_robocopy
from core.manifest_db import ManifestDB


RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
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


def warn(text: str) -> None:
    print(f"  {YELLOW}WARN{RESET}  {text}")


def check(condition: bool, label: str) -> bool:
    if condition:
        ok(label)
    else:
        fail(label)
    return condition


def main() -> int:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    failures = 0

    # ── Load Config ──────────────────────────────────────────────
    header("LOAD CONFIG")
    print(f"  Config: {config_path}")
    config = load_config(config_path)
    ok(f"Firm: {config.firm.name}")
    ok(f"Source: {config.paths.source_drive}")
    ok(f"LAN dest: {config.paths.lan_destination}")
    ok(f"LAN enabled: {config.lan_backup.enabled}")

    # ── Clean State ──────────────────────────────────────────────
    header("CLEAN STATE")
    db_path = Path(config.paths.database_path)
    if db_path.exists():
        db_path.unlink()
        ok(f"Deleted manifest.db")
    else:
        ok("manifest.db not present (fresh start)")

    wal_path = Path(str(db_path) + "-wal")
    shm_path = Path(str(db_path) + "-shm")
    for p in [wal_path, shm_path]:
        if p.exists():
            p.unlink()

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
        ok(f"Created LAN destination: {lan_dest}")

    # ── Init ManifestDB ──────────────────────────────────────────
    header("INIT ManifestDB")
    db = ManifestDB(config.paths.database_path)
    ok("ManifestDB created, WAL mode active")

    # ── Scan Source ──────────────────────────────────────────────
    header("SCAN SOURCE DRIVE")
    print(f"  Walking: {config.paths.source_drive}")
    result = scan_drive(config, db, is_full_rescan=False)
    ok(f"Total files: {result.total_file_count}")
    ok(f"New files: {len(result.new_files)}")
    ok(f"Modified: {len(result.modified_files)}")
    ok(f"Unchanged: {result.unchanged_count}")
    ok(f"Deleted: {len(result.deleted_files)}")
    ok(f"Source bytes: {result.total_source_bytes:,}")

    if result.new_files:
        print(f"\n  {CYAN}New files:{RESET}")
        for f in result.new_files:
            print(f"    + {f.relative_path}  ({f.file_size} bytes)")
    if result.modified_files:
        print(f"\n  {CYAN}Modified files:{RESET}")
        for f in result.modified_files:
            print(f"    ~ {f.relative_path}  ({f.file_size} bytes)")

    # ── Run Robocopy ─────────────────────────────────────────────
    header("ROBOCOPY /MIR")
    print(f"  Source: {config.paths.source_drive}")
    print(f"  Dest:   {config.paths.lan_destination}")
    robocopy_result = run_robocopy(config, result, db)
    ok(f"Exit code: {robocopy_result.exit_code}")
    ok(f"Status: {robocopy_result.status}")
    ok(f"Files copied: {robocopy_result.files_copied}")
    ok(f"Files failed: {robocopy_result.files_failed}")
    ok(f"Retries: {robocopy_result.retry_count}")

    if robocopy_result.status == "LAN_FAILED":
        fail("Robocopy reported failure!")
        print(f"  {RED}Output (last 2000 chars):{RESET}")
        print(f"  {robocopy_result.output[-2000:]}")
        failures += 1

    # ── Verify LAN Mirror ────────────────────────────────────────
    header("VERIFY LAN MIRROR")
    source = Path(config.paths.source_drive)

    # Build source file map: relative_path -> FileInfo
    source_files: dict[str, int] = {}
    for root, dirs, files in source.walk():
        dirs[:] = [d for d in dirs]
        for fname in files:
            fpath = root / fname
            try:
                rel = str(fpath.relative_to(source))
                source_files[rel] = fpath.stat().st_size
            except OSError:
                pass

    # Build LAN file map
    lan_files: dict[str, int] = {}
    for root, dirs, files in lan_dest.walk():
        dirs[:] = [d for d in dirs]
        for fname in files:
            fpath = root / fname
            try:
                rel = str(fpath.relative_to(lan_dest))
                lan_files[rel] = fpath.stat().st_size
            except OSError:
                pass

    ok(f"Source file count: {len(source_files)}")
    ok(f"LAN file count: {len(lan_files)}")

    # File count check
    if check(len(lan_files) >= len(source_files), "LAN file count >= source file count"):
        extra = len(lan_files) - len(source_files)
        if extra > 0:
            # Robocopy /MIR with /XD "System Volume Information" means extra
            # LAN-only files are suspicious unless they're expected exclusions
            warn(f"LAN has {extra} extra file(s) (should be excluded folders)")
            extra_files = set(lan_files.keys()) - set(source_files.keys())
            for ef in sorted(extra_files):
                warn(f"  Extra on LAN: {ef}")
    else:
        missing_count = len(source_files) - len(lan_files)
        fail(f"LAN missing {missing_count} file(s) vs source")
        missing = set(source_files.keys()) - set(lan_files.keys())
        for m in sorted(missing):
            fail(f"  Missing on LAN: {m}")
        failures += 1

    # Size match check
    size_mismatches = 0
    for rel, src_size in source_files.items():
        if rel in lan_files:
            if lan_files[rel] != src_size:
                if size_mismatches < 10:
                    fail(f"Size mismatch: {rel} (src={src_size}, lan={lan_files[rel]})")
                size_mismatches += 1

    if size_mismatches == 0:
        ok("All matched files have correct sizes")
    else:
        fail(f"{size_mismatches} file(s) have size mismatches")
        failures += 1

    # ── Verify Manifest ──────────────────────────────────────────
    header("VERIFY MANIFEST")
    entries = db.get_all_entries()
    ok(f"Manifest entries: {len(entries)}")

    backed_up_lan = sum(1 for e in entries.values() if e.backed_up_to_lan)
    ok(f"Marked LAN-backed-up: {backed_up_lan}")

    if backed_up_lan < len(entries):
        not_backed = [e.relative_path for e in entries.values() if not e.backed_up_to_lan]
        warn(f"{len(not_backed)} entries not marked LAN-backed-up")

    # ── Full Rescan (verify nothing changed after successful backup) ──
    header("POST-BACKUP RESCAN")
    result2 = scan_drive(config, db, is_full_rescan=False)
    ok(f"Changed after backup: {result2.total_changed} files")
    if result2.total_changed > 0:
        warn(f"{result2.total_changed} files changed between backup and rescan (possible live system)")
        for f in result2.new_files:
            warn(f"  New: {f.relative_path}")
        for f in result2.modified_files:
            warn(f"  Modified: {f.relative_path}")

    # ── Cleanup ──────────────────────────────────────────────────
    db.close()
    ok("ManifestDB closed")

    # ── Summary ──────────────────────────────────────────────────
    header("RESULTS")
    if failures == 0:
        print(f"\n  {GREEN}{BOLD}ALL CHECKS PASSED{RESET}\n")
        return 0
    else:
        print(f"\n  {RED}{BOLD}{failures} CHECK(S) FAILED{RESET}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
