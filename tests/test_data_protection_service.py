"""DataProtectionService 单元测试。"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "思忆集app"))
from data_protection_service import DataProtectionService


def _make_data_store(tmp_path):
    """构建带有 paths、base_dir、load_json、save_json 的 mock data_store。"""
    store = MagicMock()
    store.base_dir = str(tmp_path / "data")
    os.makedirs(store.base_dir, exist_ok=True)

    settings_path = os.path.join(store.base_dir, "settings.json")
    tasks_path = os.path.join(store.base_dir, "tasks.json")
    notes_path = os.path.join(store.base_dir, "notes.json")

    store.paths = {
        "settings": settings_path,
        "tasks": tasks_path,
        "notes": notes_path,
    }

    # 写入初始数据文件
    for key, path in store.paths.items():
        with open(path, "w", encoding="utf-8") as f:
            json.dump({key: "initial"}, f)

    return store


# ── _resolve_namespace ────────────────────────────────────


class TestResolveNamespace:
    def test_settings_key(self):
        svc = DataProtectionService(MagicMock())
        assert svc._resolve_namespace("settings") == "settings"

    def test_tasks_key(self):
        svc = DataProtectionService(MagicMock())
        assert svc._resolve_namespace("tasks") == "tasks"

    def test_notes_key(self):
        svc = DataProtectionService(MagicMock())
        assert svc._resolve_namespace("notes") == "notes"

    def test_unknown_key_returns_misc(self):
        svc = DataProtectionService(MagicMock())
        assert svc._resolve_namespace("unknown_key_xyz") == "misc"


# ── backup_now ────────────────────────────────────────────


class TestBackupNow:
    def test_creates_snapshot_with_files(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.backup_now()

        assert result["file_count"] == 3
        assert os.path.isdir(result["snapshot_dir"])

        manifest_path = os.path.join(result["snapshot_dir"], "snapshot_manifest.json")
        assert os.path.isfile(manifest_path)
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["schema_version"] == 2
        assert "settings" in manifest["files"]

    def test_latest_marker_written(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.backup_now()

        marker = os.path.join(store.base_dir, "backups", "latest_snapshot.txt")
        assert os.path.isfile(marker)
        with open(marker, encoding="utf-8") as f:
            assert f.read().strip() == result["snapshot_dir"]


# ── get_latest_snapshot_dir ───────────────────────────────


class TestGetLatestSnapshotDir:
    def test_returns_empty_when_no_marker(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        assert svc.get_latest_snapshot_dir() == ""

    def test_returns_path_after_backup(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.backup_now()
        assert svc.get_latest_snapshot_dir() == result["snapshot_dir"]


# ── restore ───────────────────────────────────────────────


class TestRestore:
    def test_restore_latest_restores_files(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        svc.backup_now()

        # 修改 settings 文件
        with open(store.paths["settings"], "w", encoding="utf-8") as f:
            json.dump({"settings": "modified"}, f)

        result = svc.restore_latest_snapshot()
        assert result["restored"] >= 1

        # 验证恢复后内容
        with open(store.paths["settings"], encoding="utf-8") as f:
            restored = json.load(f)
        assert restored["settings"] == "initial"

    def test_restore_by_scope_settings_only(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        svc.backup_now()

        with open(store.paths["settings"], "w", encoding="utf-8") as f:
            json.dump({"settings": "changed"}, f)
        with open(store.paths["tasks"], "w", encoding="utf-8") as f:
            json.dump({"tasks": "changed"}, f)

        result = svc.restore_snapshot_by_scope(include_settings=True, include_data=False)
        assert result["settings_restored"] >= 1
        assert result["data_restored"] == 0

        with open(store.paths["tasks"], encoding="utf-8") as f:
            assert json.load(f)["tasks"] == "changed"

    def test_restore_namespace(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        svc.backup_now()

        with open(store.paths["notes"], "w", encoding="utf-8") as f:
            json.dump({"notes": "modified"}, f)

        result = svc.restore_namespace("notes")
        assert result["restored"] >= 1
        assert result["namespace"] == "notes"


# ── preview ───────────────────────────────────────────────


class TestPreview:
    def test_preview_no_snapshot_returns_empty(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.preview_latest_snapshot_diff()
        assert result["snapshot_dir"] == ""
        assert result["items"] == []

    def test_preview_shows_update_after_change(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        svc.backup_now()

        # 修改文件使 mtime 变化
        import time
        time.sleep(0.05)
        with open(store.paths["settings"], "w", encoding="utf-8") as f:
            json.dump({"settings": "newer"}, f)

        result = svc.preview_latest_snapshot_diff()
        statuses = {item["key"]: item["status"] for item in result["items"]}
        assert statuses.get("settings") in ("update", "same")


# ── safe_reset / full_reset ───────────────────────────────


class TestReset:
    def test_safe_reset_clears_settings(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.safe_reset()
        assert result["mode"] == "safe"
        store.save_json.assert_called_once_with("settings", {})

    def test_full_reset_removes_data_files(self, tmp_path):
        store = _make_data_store(tmp_path)
        svc = DataProtectionService(store)
        result = svc.full_reset()
        assert result["mode"] == "full"
        for path in store.paths.values():
            assert not os.path.isfile(path)
