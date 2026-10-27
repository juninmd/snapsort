import os

from typer.testing import CliRunner

from snapsort import cli
from snapsort.cli import app

runner = CliRunner()


def _make(tmp_path):
    src = tmp_path / "in"
    for sub, text in (("a", "1"), ("b", "2")):
        f = src / sub / "IMG.jpg"
        f.parent.mkdir(parents=True)
        f.write_text(text)
        os.utime(f, (1715299200, 1715299200))  # 2024-05-10 UTC
    return src


def test_dry_run_plan_matches_real_run(tmp_path):
    src = _make(tmp_path)
    dry = runner.invoke(app, ["organize", str(src), str(tmp_path / "out"), "--dry-run"])
    assert dry.exit_code == 0
    targets = [ln.split("->")[1].strip() for ln in dry.output.splitlines() if "->" in ln]
    assert len(set(targets)) == 2
    assert any("IMG (1).jpg" in t for t in targets)


def test_no_dedupe_does_not_hash(tmp_path, monkeypatch):
    src = _make(tmp_path)

    def boom(*_a, **_k):
        raise AssertionError("hashed with --no-dedupe")

    monkeypatch.setattr(cli, "file_sha256", boom)
    res = runner.invoke(app, ["organize", str(src), str(tmp_path / "out"), "--no-dedupe"])
    assert res.exit_code == 0
