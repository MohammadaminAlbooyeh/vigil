"""Tests for utils/model_version module."""

import pytest
import json
from pathlib import Path
from src.utils.model_version import ModelVersion, ModelVersionManager


class TestModelVersion:
    def test_to_dict_contains_all_keys(self):
        version = ModelVersion("v1", {"accuracy": 0.85}, {"n_estimators": 100})
        d = version.to_dict()
        assert d["version_id"] == "v1"
        assert d["metrics"]["accuracy"] == 0.85
        assert d["metadata"]["n_estimators"] == 100
        assert "timestamp" in d

    def test_from_dict_restores_version(self):
        data = {
            "version_id": "v2",
            "timestamp": "2024-01-01T00:00:00",
            "metrics": {"accuracy": 0.90},
            "metadata": {"max_depth": 10},
        }
        version = ModelVersion.from_dict(data)
        assert version.version_id == "v2"
        assert version.timestamp == "2024-01-01T00:00:00"
        assert version.metrics["accuracy"] == 0.90

    def test_from_dict_default_metadata(self):
        data = {"version_id": "v3", "metrics": {"accuracy": 0.88}}
        version = ModelVersion.from_dict(data)
        assert version.metadata == {}


class TestModelVersionManager:
    def test_init_creates_empty_history(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        assert manager.get_latest_version() is None

    def test_add_version_returns_id(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        version_id = manager.add_version({"accuracy": 0.85})
        assert version_id.startswith("v_")

    def test_add_version_saves_to_file(self, tmp_path):
        versions_file = tmp_path / "versions.json"
        manager = ModelVersionManager(versions_file)
        manager.add_version({"accuracy": 0.85})
        assert versions_file.exists()
        with open(versions_file) as f:
            data = json.load(f)
        assert len(data["versions"]) == 1

    def test_get_latest_version(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        v1 = manager.add_version({"accuracy": 0.80})
        v2 = manager.add_version({"accuracy": 0.90})
        latest = manager.get_latest_version()
        assert latest.version_id == v2

    def test_get_version_by_id(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        v1 = manager.add_version({"accuracy": 0.80})
        found = manager.get_version(v1)
        assert found is not None
        assert found.version_id == v1

    def test_get_nonexistent_version(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        assert manager.get_version("nonexistent") is None

    def test_get_best_version(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        manager.add_version({"accuracy": 0.80, "f1_score": 0.75})
        v2 = manager.add_version({"accuracy": 0.90, "f1_score": 0.85})
        best = manager.get_best_version(metric="accuracy")
        assert best.version_id == v2

    def test_get_best_version_empty(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        assert manager.get_best_version() is None

    def test_load_versions_from_existing_file(self, tmp_path):
        versions_file = tmp_path / "versions.json"
        manager1 = ModelVersionManager(versions_file)
        manager1.add_version({"accuracy": 0.85})
        manager1.add_version({"accuracy": 0.90})

        manager2 = ModelVersionManager(versions_file)
        assert len(manager2.versions) == 2
        assert manager2.get_latest_version().metrics["accuracy"] == 0.90

    def test_compare_versions(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        v1 = manager.add_version({"accuracy": 0.80, "f1_score": 0.75})
        v2 = manager.add_version({"accuracy": 0.90, "f1_score": 0.85})
        comparison = manager.compare_versions(v1, v2)
        assert abs(comparison["accuracy"]["difference"] - 0.10) < 1e-10
        assert comparison["accuracy"]["improvement"] is True

    def test_compare_nonexistent_versions(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        v1 = manager.add_version({"accuracy": 0.80})
        comparison = manager.compare_versions(v1, "nonexistent")
        assert comparison == {}

    def test_get_version_history(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        for i in range(5):
            manager.add_version({"accuracy": 0.80 + i * 0.02})
        history = manager.get_version_history(metric="accuracy", limit=3)
        assert len(history) == 3

    def test_get_version_history_returns_latest_last(self, tmp_path):
        manager = ModelVersionManager(tmp_path / "versions.json")
        v1 = manager.add_version({"accuracy": 0.80})
        v2 = manager.add_version({"accuracy": 0.85})
        history = manager.get_version_history(limit=10)
        assert history[-1]["version_id"] == v2

    def test_generate_version_id_format(self):
        version_id = ModelVersionManager._generate_version_id({"accuracy": 0.85})
        assert version_id.startswith("v_")
        parts = version_id.split("_")
        assert len(parts) >= 3

    def test_corrupted_file_handling(self, tmp_path):
        versions_file = tmp_path / "versions.json"
        versions_file.write_text("{invalid json}")
        manager = ModelVersionManager(versions_file)
        assert len(manager.versions) == 0
