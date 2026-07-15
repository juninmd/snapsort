# 📸 snapsort

Organize a messy folder of photos/files into a tidy `YYYY/MM` tree by **capture date** — read from **EXIF** when available, falling back to file mtime. **Hash-based dedupe** skips byte-identical copies, and collisions are renamed `name (1).ext` instead of overwritten.

Point it at your camera dump / WhatsApp media / Downloads and get a clean archive.

## Install & run
```bash
uv sync                       # or: uv sync --extra exif   (enables EXIF reading via Pillow)
uv run snapsort organize ~/Downloads ~/Pictures/Archive --dry-run
uv run snapsort organize ~/Downloads ~/Pictures/Archive --move
```

## Options
| flag | meaning |
|------|---------|
| `--move` | move instead of copy (default: copy) |
| `--dedupe/--no-dedupe` | skip byte-identical duplicates (default: on) |
| `--dry-run` | print the plan, touch nothing |

EXIF reading is optional: without the `exif` extra (Pillow), snapsort just uses mtime — no crash.

## Dev
```bash
uv sync --group dev
uv run ruff check .
uv run pytest -q
```

Pure logic (date bucketing, EXIF parsing, hashing, collision-safe naming) lives in `snapsort/core.py` and is fully unit-tested.

MIT.
