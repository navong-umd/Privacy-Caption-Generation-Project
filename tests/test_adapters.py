"""Offline tests for adapters (F-Droid index resolution — no network)."""
from __future__ import annotations

from adapters.fetch_fdroid import resolve_apk_names

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
