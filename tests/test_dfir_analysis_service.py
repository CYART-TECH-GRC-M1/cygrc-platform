from pathlib import Path

import pytest

from backend.core.config import settings
from backend.services.dfir_analysis_service import (
    DfirAnalysisError,
    run_volatility_analysis,
)


def test_analysis_fails_when_evidence_root_is_not_configured(monkeypatch):
    monkeypatch.setattr(settings, "DFIR_EVIDENCE_ROOT", None)
    monkeypatch.setattr(settings, "VOLATILITY3_EXECUTABLE", None)

    with pytest.raises(DfirAnalysisError, match="evidence root"):
        run_volatility_analysis("memory.raw", "windows.info")


def test_unapproved_plugin_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "DFIR_EVIDENCE_ROOT", "unused")
    monkeypatch.setattr(settings, "VOLATILITY3_EXECUTABLE", "unused")

    with pytest.raises(DfirAnalysisError, match="not approved"):
        run_volatility_analysis("memory.raw", "custom.unknown")


def test_evidence_outside_root_is_rejected(tmp_path, monkeypatch):
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()

    outside_file = tmp_path / "outside.raw"
    outside_file.write_bytes(b"sample memory data")

    executable = tmp_path / "vol.exe"
    executable.write_bytes(b"placeholder")

    monkeypatch.setattr(
        settings, "DFIR_EVIDENCE_ROOT", str(evidence_root)
    )
    monkeypatch.setattr(
        settings, "VOLATILITY3_EXECUTABLE", str(executable)
    )

    with pytest.raises(DfirAnalysisError, match="inside"):
        run_volatility_analysis(str(outside_file), "windows.info")


def test_missing_evidence_is_rejected(tmp_path, monkeypatch):
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()

    executable = tmp_path / "vol.exe"
    executable.write_bytes(b"placeholder")

    monkeypatch.setattr(
        settings, "DFIR_EVIDENCE_ROOT", str(evidence_root)
    )
    monkeypatch.setattr(
        settings, "VOLATILITY3_EXECUTABLE", str(executable)
    )

    with pytest.raises(DfirAnalysisError, match="does not exist"):
        run_volatility_analysis(
            str(evidence_root / "missing.raw"), "windows.info"
        )


def test_analysis_rejects_empty_evidence(tmp_path, monkeypatch):
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()

    evidence_file = evidence_root / "empty.raw"
    evidence_file.write_bytes(b"")

    executable = tmp_path / "vol.exe"
    executable.write_bytes(b"placeholder")

    monkeypatch.setattr(
        settings, "DFIR_EVIDENCE_ROOT", str(evidence_root)
    )
    monkeypatch.setattr(
        settings, "VOLATILITY3_EXECUTABLE", str(executable)
    )

    with pytest.raises(DfirAnalysisError, match="empty"):
        run_volatility_analysis(str(evidence_file), "windows.info")


def test_analysis_rejects_missing_executable(tmp_path, monkeypatch):
    evidence_root = tmp_path / "evidence"
    evidence_root.mkdir()

    evidence_file = evidence_root / "memory.raw"
    evidence_file.write_bytes(b"sample memory data")

    monkeypatch.setattr(
        settings, "DFIR_EVIDENCE_ROOT", str(evidence_root)
    )
    monkeypatch.setattr(
        settings,
        "VOLATILITY3_EXECUTABLE",
        str(tmp_path / "missing-vol.exe"),
    )

    with pytest.raises(DfirAnalysisError, match="not found"):
        run_volatility_analysis(str(evidence_file), "windows.info")