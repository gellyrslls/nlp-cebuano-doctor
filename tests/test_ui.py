"""Tests for Streamlit UI helpers and application components."""
from pathlib import Path
from src.domain.models import ConsultationResult
from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider
from src.storage import save_run
from src.ui_helpers import SAMPLE_PROMPTS, get_pipeline, list_recent_runs


def test_sample_prompts_contain_cultural_idioms():
    assert len(SAMPLE_PROMPTS) >= 4
    keys_text = " ".join(SAMPLE_PROMPTS.keys()).lower()
    values_text = " ".join(SAMPLE_PROMPTS.values()).lower()
    assert "panuhot" in keys_text or "panuhot" in values_text
    assert "pasmo" in keys_text or "pasmo" in values_text
    assert "kalibanga" in keys_text or "kalibanga" in values_text


def test_get_pipeline_creates_mock_or_ollama():
    mock_pipeline = get_pipeline(mock=True, translation_model="test:trans", medical_model="test:med")
    assert isinstance(mock_pipeline, CebuanoDoctorPipeline)
    assert isinstance(mock_pipeline.provider, MockModelProvider)
    assert mock_pipeline.translation_model == "test:trans"
    assert mock_pipeline.medical_model == "test:med"


def test_list_recent_runs_orders_correctly(tmp_path: Path):
    r1 = ConsultationResult(chief_complaint="Complaint 1", timestamp="2026-09-16T10:00:00+00:00")
    r2 = ConsultationResult(chief_complaint="Complaint 2", timestamp="2026-09-16T11:00:00+00:00")

    save_run(r1, runs_dir=tmp_path)
    save_run(r2, runs_dir=tmp_path)

    runs = list_recent_runs(runs_dir=tmp_path, limit=5)
    assert len(runs) == 2
    # Should be sorted newest first
    assert runs[0]["chief_complaint"] == "Complaint 2"
    assert runs[1]["chief_complaint"] == "Complaint 1"


def test_streamlit_app_loads_successfully():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    assert not at.exception
    # Verify title or header is present
    titles = [t.value for t in at.title]
    assert any("Cebuano Doctor" in t or "Doktor sa Sugbo" in t for t in titles)


def test_streamlit_app_executes_consultation_flow():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path))
    at.run()

    # Enter a symptom into the text area
    assert len(at.text_area) > 0
    at.text_area[0].input("Gisakit akong tiyan").run()

    # Click the consultation button
    consult_buttons = [b for b in at.button if "Sugdi" in b.label]
    assert len(consult_buttons) == 1
    consult_buttons[0].click().run()

    assert not at.exception
    # Ensure success message with guidance was rendered
    assert len(at.success) > 0
    assert any("doktor" in s.value.lower() or "tambag" in s.value.lower() or "base sa" in s.value.lower() for s in at.success)

    # Ensure metrics were displayed
    assert len(at.metric) == 4


def test_streamlit_app_live_mode_uncheck_mock():
    from streamlit.testing.v1 import AppTest

    app_path = Path(__file__).parent.parent / "app.py"
    at = AppTest.from_file(str(app_path), default_timeout=10)
    at.run(timeout=10)

    # Uncheck mock mode to toggle live Ollama check
    assert len(at.checkbox) > 0
    at.checkbox[0].uncheck().run(timeout=10)

    assert not at.exception


