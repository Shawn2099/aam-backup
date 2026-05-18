"""ManifestDB — SQLite operations with thread-safe writes via threading.Lock."""

import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import text

from models.manifest_model import Base, FileManifest, create_engine_with_wal


class DatabaseError(Exception):
    """Raised when a database operation fails."""
    pass


# Current schema version — increment when adding columns
SCHEMA_VERSION = 1


class ManifestDB:
    """Thread-safe SQLite manifest database wrapper.

    All write operations acquire an internal threading.Lock.
    WAL mode is enforced on every connection.
    """

    def __init__(self, database_path: str | Path):
        self._database_path = str(Path(database_path))
        self._lock = threading.Lock()
        self._engine = create_engine_with_wal(f"sqlite:///{self._database_path}")
        Base.metadata.create_all(self._engine)
        self._ensure_schema_version()

    def _ensure_schema_version(self):
        """Ensure the database schema matches the expected version.

        Creates a schema_version table if it doesn't exist, and runs
        migrations if the stored version is behind the current version.
        """
        session = self._get_session()
        try:
            # Create schema_version table if it doesn't exist
            session.execute(text("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY,
                    version INTEGER NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """))
            session.commit()

            # Get current version
            row = session.execute(text("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")).fetchone()
            current_version = row[0] if row else 0

            if current_version < SCHEMA_VERSION:
                self._run_migrations(session, current_version, SCHEMA_VERSION)

            # Update version record
            now = datetime.now(timezone.utc).isoformat()
            session.execute(text(
                "INSERT INTO schema_version (version, updated_at) VALUES (:v, :t)"
            ), {"v": SCHEMA_VERSION, "t": now})
            session.commit()

        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def _run_migrations(self, session, from_version: int, to_version: int):
        """Run schema migrations from from_version to to_version."""
        migrations = {
            0: self._migrate_v1,
            # Add future migrations here:
            # 1: self._migrate_v2,
        }

        for version in range(from_version, to_version):
            migrate_fn = migrations.get(version)
            if migrate_fn:
                migrate_fn(session)

    def _migrate_v1(self, session):
        """Migration to v1: initial schema (already created by SQLAlchemy)."""
        pass

    def _get_session(self):
        """Get a new session. Caller must close it."""
        from sqlalchemy.orm import sessionmaker
        Session = sessionmaker(bind=self._engine)
        return Session()

    def get_entry(self, relative_path: str) -> FileManifest | None:
        """Get a manifest entry by relative path. Thread-safe read (no lock needed)."""
        session = self._get_session()
        try:
            return session.query(FileManifest).filter_by(
                relative_path=relative_path
            ).first()
        finally:
            session.close()

    def upsert_entry(
        self,
        relative_path: str,
        file_size: int,
        last_modified_timestamp: float,
        checksum: str = "pending",
    ) -> FileManifest:
        """Insert or update a manifest entry. Acquires write lock."""
        with self._lock:
            session = self._get_session()
            try:
                entry = session.query(FileManifest).filter_by(
                    relative_path=relative_path
                ).first()

                if entry is None:
                    entry = FileManifest(
                        file_id=str(uuid.uuid4()),
                        relative_path=relative_path,
                        file_size=file_size,
                        last_modified_timestamp=last_modified_timestamp,
                        checksum=checksum,
                        last_seen_at=datetime.now(timezone.utc).isoformat(),
                    )
                    session.add(entry)
                else:
                    entry.file_size = file_size
                    entry.last_modified_timestamp = last_modified_timestamp
                    entry.checksum = checksum
                    entry.last_seen_at = datetime.now(timezone.utc).isoformat()

                session.commit()
                session.refresh(entry)
                return entry
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def update_last_seen(self, relative_path: str) -> bool:
        """Update last_seen_at for an existing entry. Acquires write lock.

        Returns True if entry was found and updated, False if not found.
        """
        with self._lock:
            session = self._get_session()
            try:
                entry = session.query(FileManifest).filter_by(
                    relative_path=relative_path
                ).first()
                if entry is None:
                    return False
                entry.last_seen_at = datetime.now(timezone.utc).isoformat()
                session.commit()
                return True
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def batch_mark_lan_backed_up(self, relative_paths: list[str]) -> int:
        """Mark multiple files as backed up to LAN. Acquires write lock.

        Returns number of rows updated.
        """
        if not relative_paths:
            return 0

        with self._lock:
            session = self._get_session()
            try:
                now = datetime.now(timezone.utc).isoformat()
                count = session.query(FileManifest).filter(
                    FileManifest.relative_path.in_(relative_paths)
                ).update(
                    {
                        FileManifest.backed_up_to_lan: 1,
                        FileManifest.last_backed_up_lan: now,
                    },
                    synchronize_session="fetch",
                )
                session.commit()
                return count
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def batch_mark_cloud_backed_up(self, relative_paths: list[str]) -> int:
        """Mark multiple files as backed up to cloud. Acquires write lock.

        Returns number of rows updated.
        """
        if not relative_paths:
            return 0

        with self._lock:
            session = self._get_session()
            try:
                now = datetime.now(timezone.utc).isoformat()
                count = session.query(FileManifest).filter(
                    FileManifest.relative_path.in_(relative_paths)
                ).update(
                    {
                        FileManifest.backed_up_to_cloud: 1,
                        FileManifest.last_backed_up_cloud: now,
                    },
                    synchronize_session="fetch",
                )
                session.commit()
                return count
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def delete_entry(self, relative_path: str) -> bool:
        """Delete a manifest entry. Acquires write lock.

        Returns True if entry was found and deleted, False if not found.
        """
        with self._lock:
            session = self._get_session()
            try:
                result = session.query(FileManifest).filter_by(
                    relative_path=relative_path
                ).delete()
                session.commit()
                return result > 0
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()

    def get_all_paths(self) -> set[str]:
        """Get all relative paths in the manifest. Thread-safe read (no lock needed)."""
        session = self._get_session()
        try:
            rows = session.query(FileManifest.relative_path).all()
            return {row[0] for row in rows}
        finally:
            session.close()

    def get_all_entries(self) -> dict[str, FileManifest]:
        """Load all manifest entries into memory as a dict.

        Returns:
            Dict mapping relative_path → FileManifest object.
            Thread-safe read (no lock needed).

        Use this for bulk lookups during scanning to avoid 200K+ individual queries.
        """
        session = self._get_session()
        try:
            rows = session.query(FileManifest).all()
            return {entry.relative_path: entry for entry in rows}
        finally:
            session.close()

    def close(self):
        """Dispose the engine. Call when shutting down."""
        self._engine.dispose()

    def maintenance(self, max_size_mb: int = 500) -> dict:
        """Perform SQLite maintenance: VACUUM, WAL checkpoint, size check.

        Should be called periodically (e.g., after each successful backup run)
        to prevent database bloat from 200K+ daily writes.

        Args:
            max_size_mb: Alert threshold for database file size.

        Returns:
            Dict with maintenance results: {"vacuumed": bool, "checkpointed": bool,
            "size_mb": float, "size_warning": bool}.
        """
        result = {"vacuumed": False, "checkpointed": False, "size_mb": 0.0, "size_warning": False}

        try:
            db_file = Path(self._database_path)
            if not db_file.exists():
                return result

            # Check size before maintenance
            size_mb = db_file.stat().st_size / (1024 ** 2)
            result["size_mb"] = round(size_mb, 1)
            result["size_warning"] = size_mb > max_size_mb

            # WAL checkpoint — flush WAL to main database
            with self._lock:
                session = self._get_session()
                try:
                    session.execute(text("PRAGMA wal_checkpoint(TRUNCATE)"))
                    session.commit()
                    result["checkpointed"] = True
                except Exception:
                    session.rollback()
                finally:
                    session.close()

            # VACUUM — reclaim unused space
            with self._lock:
                session = self._get_session()
                try:
                    session.execute(text("VACUUM"))
                    session.commit()
                    result["vacuumed"] = True
                except Exception:
                    session.rollback()
                finally:
                    session.close()

            # Check size after maintenance
            result["size_mb"] = round(db_file.stat().st_size / (1024 ** 2), 1)

        except Exception:
            pass  # Maintenance is non-critical — never fail the flow

        return result
