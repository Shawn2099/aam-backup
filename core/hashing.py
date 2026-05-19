import hashlib
from pathlib import Path
import xxhash


def compute_checksum(file_path: Path) -> str:
    """Compute xxHash64 checksum for a file.

    Uses Python 3.11+ hashlib.file_digest to avoid manual chunk-reading.

    Args:
        file_path: Path to the file.

    Returns:
        16-character hex string.
    """
    with open(file_path, "rb") as f:
        # mypy expects a hashlib _HashObject; ignore the type difference with xxhash
        digest = hashlib.file_digest(f, lambda: xxhash.xxh64())  # type: ignore[arg-type, return-value]
        return digest.hexdigest()
