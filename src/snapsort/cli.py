"""snapsort CLI."""

from __future__ import annotations

import shutil
from pathlib import Path

import typer

from .core import bucket_for, file_sha256, read_exif_datetime, resolve_date, unique_target

app = typer.Typer(add_completion=False, help="Organize photos/files into YYYY/MM by date.")


@app.callback()
def _main() -> None:
    """snapsort — organize photos/files into YYYY/MM by capture date."""



@app.command()
def organize(
    src: Path = typer.Argument(..., exists=True, file_okay=False, help="Source folder"),
    dst: Path = typer.Argument(..., file_okay=False, help="Destination root"),
    move: bool = typer.Option(False, "--move", help="Move instead of copy"),
    dedupe: bool = typer.Option(True, "--dedupe/--no-dedupe", help="Skip identical duplicates"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview without touching files"),
) -> None:
    """Sort every file under SRC into DST/YYYY/MM based on capture date."""
    seen_hashes: set[str] = set()
    planned = 0
    skipped = 0
    duplicates = 0

    for path in sorted(p for p in src.rglob("*") if p.is_file()):
        digest = file_sha256(path)
        if dedupe and digest in seen_hashes:
            duplicates += 1
            continue
        seen_hashes.add(digest)

        when = resolve_date(read_exif_datetime(path), path.stat().st_mtime)
        target_dir = dst / bucket_for(when)
        name = unique_target(path.name, lambda n, d=target_dir: (d / n).exists())
        target = target_dir / name

        verb = "MOVE" if move else "COPY"
        typer.echo(f"{verb} {path}  ->  {target}")
        planned += 1
        if dry_run:
            continue

        target_dir.mkdir(parents=True, exist_ok=True)
        if move:
            shutil.move(str(path), str(target))
        else:
            shutil.copy2(str(path), str(target))

    typer.echo("")
    prefix = "(dry-run) " if dry_run else ""
    summary = f"{prefix}{planned} organized, {duplicates} duplicate(s) skipped, {skipped} error(s)"
    typer.secho(summary, fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
