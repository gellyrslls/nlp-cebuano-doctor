"""Tests for run storage and JSON persistence."""
import json
from pathlib import Path
from src.domain.models import ConsultationResult, StageMetrics
from src.storage import save_run, load_run, generate_run_filename, slugify


def test_save_run_creates_valid_json_artifact(tmp_path: Path):
    metrics = StageMetrics(
        translation_en_ms=120.5,
        medical_inference_ms=450.2,
        translation_ceb_ms=110.1,
        total_turnaround_ms=680.8,
    )
    result = ConsultationResult(
        chief_complaint="Gisakit akong tiyan",
        english_translation="I have a stomachache",
        english_medical_guidance="Drink clean water and rest.",
        cebuano_medical_guidance="Inom ug limpyong tubig ug pahuway.",
        metrics=metrics,
        status="success",
    )

    saved_path = save_run(result, runs_dir=tmp_path)

    assert saved_path.exists()
    assert saved_path.suffix == ".json"
    assert saved_path.parent == tmp_path

    # Verify JSON content matches result
    data = json.loads(saved_path.read_text(encoding="utf-8"))
    assert data["chief_complaint"] == "Gisakit akong tiyan"
    assert data["english_translation"] == "I have a stomachache"
    assert data["cebuano_medical_guidance"] == "Inom ug limpyong tubig ug pahuway."
    assert data["metrics"]["total_turnaround_ms"] == 680.8
    assert data["status"] == "success"


def test_slugify_and_filename_handling():
    assert slugify("Mura ko'g gipanuhot!") == "mura_kog_gipanuhot"
    assert slugify("   ") == "run"
    assert slugify("a" * 50) == "a" * 30

    fn = generate_run_filename("2026-09-16T12:00:00+00:00", "Sakit akong dughan?")
    assert fn.startswith("20260916_120000_")
    assert fn.endswith(".json")
    assert "sakit_akong_dughan" in fn


def test_load_run_returns_persisted_dict(tmp_path: Path):
    result = ConsultationResult(
        chief_complaint="Lipong akong ulo",
        cebuano_medical_guidance="Pahuway sa.",
    )
    saved_path = save_run(result, runs_dir=tmp_path)
    loaded = load_run(saved_path)

    assert loaded["chief_complaint"] == "Lipong akong ulo"
    assert loaded["cebuano_medical_guidance"] == "Pahuway sa."
    assert loaded["status"] == "success"
