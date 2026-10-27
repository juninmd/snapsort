from datetime import datetime

from snapsort.core import (
    bucket_for,
    file_sha256,
    parse_exif_datetime,
    resolve_date,
    unique_target,
)


def test_bucket_for():
    assert bucket_for(datetime(2026, 7, 5, 14, 0)) == "2026/07"
    assert bucket_for(datetime(1999, 12, 31)) == "1999/12"


def test_parse_exif_datetime():
    assert parse_exif_datetime("2026:07:05 14:30:00") == datetime(2026, 7, 5, 14, 30, 0)
    assert parse_exif_datetime(None) is None
    assert parse_exif_datetime("garbage") is None


def test_resolve_date_prefers_exif_then_mtime():
    mtime = datetime(2020, 1, 1).timestamp()
    assert resolve_date("2026:07:05 00:00:00", mtime) == datetime(2026, 7, 5)
    assert resolve_date(None, mtime) == datetime(2020, 1, 1)


def test_unique_target_avoids_collisions():
    existing = {"a.jpg", "a (1).jpg"}
    assert unique_target("b.jpg", lambda n: n in existing) == "b.jpg"
    assert unique_target("a.jpg", lambda n: n in existing) == "a (2).jpg"


def test_file_sha256(tmp_path):
    f = tmp_path / "x.bin"
    f.write_bytes(b"hello world")
    # sha256("hello world")
    assert file_sha256(f) == "b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"


def test_read_exif_prefers_capture_date_over_edit_date(tmp_path):
    import pytest

    Image = pytest.importorskip("PIL.Image")
    from snapsort.core import read_exif_datetime

    img = Image.new("RGB", (4, 4))
    exif = Image.Exif()
    exif[306] = "2024:01:01 00:00:00"
    exif.get_ifd(0x8769)[36867] = "2019:03:10 10:00:00"
    path = tmp_path / "p.jpg"
    img.save(path, exif=exif)
    assert read_exif_datetime(path) == "2019:03:10 10:00:00"
