"""SQLAlchemy model for the file manifest database."""

from sqlalchemy import BigInteger, Column, Index, Integer, REAL, Text, create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

PENDING_CHECKSUM = "pending"
"""Sentinel value for files whose checksum has not been computed yet."""


class Base(DeclarativeBase):
    pass


class FileManifest(Base):
    __tablename__ = "file_manifest"

    file_id = Column(Text, primary_key=True)
    relative_path = Column(Text, nullable=False, unique=True)
    file_size = Column(BigInteger, nullable=False)
    last_modified_timestamp = Column(REAL, nullable=False)
    checksum = Column(Text, nullable=False, default=PENDING_CHECKSUM)
    last_seen_at = Column(Text, nullable=False)
    last_backed_up_lan = Column(Text, nullable=True)
    last_backed_up_cloud = Column(Text, nullable=True)
    backed_up_to_lan = Column(Integer, nullable=False, default=0)
    backed_up_to_cloud = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        Index("idx_manifest_relative_path", "relative_path"),
        Index("idx_manifest_last_seen", "last_seen_at"),
    )


def create_engine_with_wal(database_url: str):
    """Create SQLAlchemy engine with WAL mode enforced on every connection."""
    engine = create_engine(
        database_url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )

    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        result = cursor.fetchone()
        if result[0] != "wal":
            raise RuntimeError(f"Failed to set WAL mode, got: {result[0]}")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.execute("PRAGMA cache_size=10000")
        cursor.close()

    return engine


def init_db(database_path: str):
    """Initialize the database and return (engine, Session)."""
    db_url = f"sqlite:///{database_path}"
    engine = create_engine_with_wal(db_url)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return engine, Session
