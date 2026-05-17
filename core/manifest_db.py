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
