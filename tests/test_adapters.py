"""Offline tests for adapters (F-Droid index resolution — no network)."""
from __future__ import annotations

from adapters.fetch_androzoo import get_api_key, pick_from_rows
from adapters.fetch_fdroid import resolve_apk_names
from pplib.io_utils import load_dotenv, redact

_INDEX = {
    "apps": [{"packageName": "com.a.app", "suggestedVersionCode": 100}],
    "packages": {
        "com.a.app": [
            {"versionCode": 90, "apkName": "com.a.app_90.apk"},
            {"versionCode": 100, "apkName": "com.a.app_100.apk"},
        ],
        "com.b.noSuggested": [
            {"versionCode": 5, "apkName": "com.b_5.apk"},
            {"versionCode": 7, "apkName": "com.b_7.apk"},
        ],
    },
}


def test_resolve_prefers_suggested_version():
    out = resolve_apk_names(_INDEX, ["com.a.app"])
    assert out["com.a.app"] == "com.a.app_100.apk"


def test_resolve_falls_back_to_newest():
    out = resolve_apk_names(_INDEX, ["com.b.noSuggested"])
    assert out["com.b.noSuggested"] == "com.b_7.apk"   # max versionCode


def test_resolve_missing_package_is_none():
    out = resolve_apk_names(_INDEX, ["com.not.here"])
    assert out["com.not.here"] is None


# ---- AndroZoo (offline) ----
_AZ_ROWS = [
    {"sha256": "AAA", "pkg_name": "com.x", "vercode": "10"},
    {"sha256": "BBB", "pkg_name": "com.x", "vercode": "20"},  # newer
    {"sha256": "CCC", "pkg_name": "com.y", "vercode": "3"},
]


def test_androzoo_pick_highest_vercode():
    out = pick_from_rows(_AZ_ROWS, ["com.x", "com.y"])
    assert out["com.x"]["sha256"] == "BBB"   # highest vercode wins
    assert out["com.y"]["sha256"] == "CCC"
    assert "com.z" not in pick_from_rows(_AZ_ROWS, ["com.z"])


_AZ_SIZED = [
    {"sha256": "SMALL_OLD", "pkg_name": "com.x", "vercode": "10", "apk_size": str(5_000_000)},
    {"sha256": "MID", "pkg_name": "com.x", "vercode": "20", "apk_size": str(20_000_000)},
    {"sha256": "HUGE_NEW", "pkg_name": "com.x", "vercode": "30", "apk_size": str(200_000_000)},
]


def test_androzoo_size_cap_picks_newest_under_cap():
    # cap 25MB -> newest version <= 25MB is MID (vc20), not the 200MB newest
    out = pick_from_rows(_AZ_SIZED, ["com.x"], max_mb=25)
    assert out["com.x"]["sha256"] == "MID"


def test_androzoo_size_cap_falls_back_to_smallest():
    # cap 1MB -> nothing under cap -> smallest available (5MB)
    out = pick_from_rows(_AZ_SIZED, ["com.x"], max_mb=1)
    assert out["com.x"]["sha256"] == "SMALL_OLD"


def test_redact_hides_apikey():
    masked = redact("https://androzoo.uni.lu/api/download?apikey=SECRET123&sha256=H")
    assert "SECRET123" not in masked and "apikey=***" in masked


def test_load_dotenv_sets_env_without_returning_values(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('FOO_KEY="hunter2"\n# comment\nBAR=baz\n', encoding="utf-8")
    monkeypatch.delenv("FOO_KEY", raising=False)
    names = load_dotenv(env)
    assert names == ["FOO_KEY", "BAR"]       # names only, never values
    import os
    assert os.environ["FOO_KEY"] == "hunter2"


def test_get_api_key_reads_env(monkeypatch):
    monkeypatch.setenv("ANDRO_ZOO_KEY", "k-123")
    assert get_api_key() == "k-123"
