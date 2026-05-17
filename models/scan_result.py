"""Dataclasses for scan results."""

from dataclasses import dataclass, field


@dataclass
class FileInfo:
    """Represents a single file found during scanning."""

    relative_path: str
    file_size: int
    last_modified_timestamp: float
    checksum: str = ""


@dataclass
class ScanResult:
    """Output of the scan_drive() function."""

    new_files: list[FileInfo] = field(default_factory=list)
    modified_files: list[FileInfo] = field(default_factory=list)
    deleted_files: list[str] = field(default_factory=list)
    unchanged_count: int = 0
    cannot_read: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.new_files or self.modified_files or self.deleted_files)

    @property
    def total_changed(self) -> int:
        return len(self.new_files) + len(self.modified_files) + len(self.deleted_files)
