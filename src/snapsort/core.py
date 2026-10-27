"""Pure, testable helpers — no filesystem side effects except explicit hashing."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import datetime
from pathlib import Path

IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".tiff", ".heic", ".webp", ".gif"}


def bucket_for(dt: datetime) -> str:
    """Return the 'YYYY/MM' folder for a datetime."""
    return f"{dt.year:04d}/{dt.month:02d}"


def parse_exif_datetime(value: str | None) -> datetime | None:
    """Parse an EXIF 'YYYY:MM:DD HH:MM:SS' string; None if absent/invalid."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y:%m:%d %H:%M:%S")
    except (ValueError, TypeError):
        return None


def resolve_date(exif_value: str | None, mtime: float) -> datetime:
    """Prefer a valid EXIF capture date; otherwise fall back to file mtime."""
    return parse_exif_datetime(exif_value) or datetime.fromtimestamp(mtime)


def file_sha256(path: Path, chunk: int = 65536) -> str:
    """Streaming SHA-256 of a file's contents."""
    h = hashlib.sha256()
    with path.open("rb") as fh:
        while data := fh.read(chunk):
            h.update(data)
    return h.hexdigest()


def unique_target(name: str, taken: Callable[[str], bool]) -> str:
    """Return `name`, or 'stem (n).ext' avoiding collisions per `taken`."""
    if not taken(name):
        return name
    p = Path(name)
    stem, suffix = p.stem, p.suffix
    n = 1
    while taken(candidate := f"{stem} ({n}){suffix}"):
        n += 1
    return candidate


def read_exif_datetime(path: Path) -> str | None:
    """Lazy-load Pillow to read DateTimeOriginal; None if unavailable."""
    if path.suffix.lower() not in IMAGE_SUFFIXES:
        return None
    try:
        from PIL import Image  # noqa: PLC0415

        with Image.open(path) as img:
            exif = img.getexif()
            # DateTimeOriginal (36867) / DateTimeDigitized (36868) live in the Exif
            # sub-IFD (pointer 0x8769); DateTime (306) in IFD0 is only the last edit.
            sub = exif.get_ifd(0x8769)
            return sub.get(36867) or sub.get(36868) or exif.get(306)
    except Exception:
        return None
