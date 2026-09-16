"""Tests for CebuanoDoctorPipeline seam."""
from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider


def test_empty_complaint_returns_error():
    pipeline = CebuanoDoctorPipeline(provider=MockModelProvider())
    result = pipeline.run("")
    assert result.status == "error"
    assert "empty" in result.error_message.lower()


def test_circular_pipeline_runs_successfully():
    provider = MockModelProvider(simulated_latency_s=0.005)
    pipeline = CebuanoDoctorPipeline(provider=provider)

    complaint = "Gipaningot ko ug nagsakit akong tiyan unya gikalibanga ko."
    result = pipeline.run(complaint)

    assert result.status == "success"
    assert result.chief_complaint == complaint
    assert len(result.english_translation) > 0
    assert len(result.english_medical_guidance) > 0
    assert len(result.cebuano_medical_guidance) > 0

    # Ensure all 3 stages were called in sequence
    assert len(provider.call_history) == 3
    assert provider.call_history[0]["model"] == pipeline.translation_model
    assert provider.call_history[1]["model"] == pipeline.medical_model
    assert provider.call_history[2]["model"] == pipeline.translation_model


def test_stage_metrics_measured():
    provider = MockModelProvider(simulated_latency_s=0.005)
    pipeline = CebuanoDoctorPipeline(provider=provider)

    result = pipeline.run("Sakit akong ulo.")

    assert result.status == "success"
    assert result.metrics.translation_en_ms > 0
    assert result.metrics.medical_inference_ms > 0
    assert result.metrics.translation_ceb_ms > 0
    assert result.metrics.total_turnaround_ms >= (
        result.metrics.translation_en_ms +
        result.metrics.medical_inference_ms +
        result.metrics.translation_ceb_ms
    ) * 0.8  # Allow slight timing tolerance


def test_provider_error_handled_gracefully():
    class BrokenProvider:
        def generate(self, model: str, prompt: str, system_prompt=None) -> str:
            raise ConnectionError("Ollama daemon is unreachable.")

    pipeline = CebuanoDoctorPipeline(provider=BrokenProvider())
    result = pipeline.run("Hilanat ug ubo.")

    assert result.status == "error"
    assert "unreachable" in result.error_message
    assert result.metrics.total_turnaround_ms >= 0


def test_cultural_idiom_passed_to_stage1():
    provider = MockModelProvider()
    pipeline = CebuanoDoctorPipeline(provider=provider)

    result = pipeline.run("Mura ko'g gipanuhot sa likod.")

    assert result.status == "success"
    assert "bodily aches" in result.english_translation.lower() or "cold" in result.english_translation.lower()


def test_pipeline_run_automatically_persists_artifact(tmp_path):
    import json

    provider = MockModelProvider()
    pipeline = CebuanoDoctorPipeline(provider=provider, runs_dir=tmp_path)
    result = pipeline.run("Gisakit akong ulo.")

    assert result.status == "success"
    run_files = list(tmp_path.glob("*.json"))
    assert len(run_files) == 1

    saved_data = json.loads(run_files[0].read_text(encoding="utf-8"))
    assert saved_data["chief_complaint"] == "Gisakit akong ulo."
    assert saved_data["status"] == "success"
