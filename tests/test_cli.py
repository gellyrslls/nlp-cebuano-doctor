"""Tests for interactive Rich CLI runner and arguments."""
import pytest
from src.cli import parse_args


def test_parse_args_defaults():
    args = parse_args([])
    assert args.mock is False
    assert args.query is None
    assert args.model_translate == "gemma4:e2b"
    assert args.model_medical == "alibayram/medgemma"
    assert args.save_dir == "evaluations/runs"


def test_parse_args_custom_values():
    args = parse_args([
        "--mock",
        "--chief-complaint", "Sakit akong likod",
        "--model-translate", "custom:translate",
        "--model-medical", "custom:med",
        "--save-dir", "test_runs",
    ])
    assert args.mock is True
    assert args.chief_complaint == "Sakit akong likod"
    assert args.query == "Sakit akong likod"
    assert args.model_translate == "custom:translate"
    assert args.model_medical == "custom:med"
    assert args.save_dir == "test_runs"


def test_parse_args_backwards_compatible_query():
    args = parse_args(["--query", "Gisakit akong dughan"])
    assert args.chief_complaint == "Gisakit akong dughan"
    assert args.query == "Gisakit akong dughan"


def test_run_consultation_executes_renders_and_saves(tmp_path):
    from rich.console import Console
    from src.cli import run_consultation
    from src.domain.pipeline import CebuanoDoctorPipeline
    from src.domain.provider import MockModelProvider

    provider = MockModelProvider(simulated_latency_s=0.001)
    pipeline = CebuanoDoctorPipeline(provider=provider)
    console = Console(record=True, width=100)

    result = run_consultation(
        query="Sakit akong tiyan",
        pipeline=pipeline,
        console=console,
        save_dir=tmp_path,
    )

    assert result.status == "success"
    assert result.chief_complaint == "Sakit akong tiyan"
    assert len(result.cebuano_medical_guidance) > 0

    # Verify console rendering
    output = console.export_text()
    assert "Stage 1" in output
    assert "English Clinical Translation" in output
    assert "Stage 2" in output
    assert "MedGemma Clinical Guidance" in output
    assert "Stage 3" in output
    assert "Cebuano Patient Response" in output
    assert "Latency Breakdown" in output
    assert "Saved run to" in output

    # Verify JSON run persisted
    saved_files = list(tmp_path.glob("*.json"))
    assert len(saved_files) == 1
    assert "sakit_akong_tiyan" in saved_files[0].name


def test_run_consultation_error_handling(tmp_path):
    from rich.console import Console
    from src.cli import run_consultation
    from src.domain.pipeline import CebuanoDoctorPipeline
    from src.domain.provider import MockModelProvider

    pipeline = CebuanoDoctorPipeline(provider=MockModelProvider())
    console = Console(record=True, width=100)

    result = run_consultation(
        query="",
        pipeline=pipeline,
        console=console,
        save_dir=tmp_path,
    )

    assert result.status == "error"
    output = console.export_text()
    assert "Error" in output or "Consultation Error" in output


def test_main_non_interactive_query(tmp_path):
    from src.cli import main

    ret = main(["--mock", "--query", "Gisakit akong hawak", "--save-dir", str(tmp_path)])
    assert ret == 0

    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1
    assert "gisakit_akong_hawak" in saved[0].name


def test_main_interactive_quit_immediately(monkeypatch, tmp_path):
    from rich.prompt import Prompt
    from src.cli import main

    monkeypatch.setattr(Prompt, "ask", lambda *args, **kwargs: "q")
    ret = main(["--mock", "--save-dir", str(tmp_path)])
    assert ret == 0
    assert len(list(tmp_path.glob("*.json"))) == 0


def test_main_interactive_query_then_quit(monkeypatch, tmp_path):
    from rich.prompt import Prompt
    from src.cli import main

    inputs = iter(["Gikalibanga ko", "exit"])
    monkeypatch.setattr(Prompt, "ask", lambda *args, **kwargs: next(inputs))

    ret = main(["--mock", "--save-dir", str(tmp_path)])
    assert ret == 0
    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1
    assert "gikalibanga_ko" in saved[0].name


def test_parse_args_stage_flags():
    args_default = parse_args([])
    assert args_default.stages == [1, 2, 3]

    args_custom = parse_args(["--stage", "1", "3"])
    assert args_custom.stages == [1, 3]

    args_single = parse_args(["--stages", "2"])
    assert args_single.stages == [2]


def test_run_consultation_selective_stage_inspection(tmp_path):
    from rich.console import Console
    from src.cli import run_consultation
    from src.domain.pipeline import CebuanoDoctorPipeline
    from src.domain.provider import MockModelProvider

    pipeline = CebuanoDoctorPipeline(provider=MockModelProvider())
    console = Console(record=True, width=100)

    result = run_consultation(
        query="Sakit akong tiyan",
        pipeline=pipeline,
        console=console,
        save_dir=tmp_path,
        stages=[1],
    )

    assert result.status == "success"
    output = console.export_text()
    assert "Stage 1" in output
    assert "English Clinical Translation" in output
    assert "Stage 2: MedGemma Clinical Guidance" not in output
    assert "Stage 3: Cebuano Patient Response" not in output

    # Full run artifact must still be saved
    saved = list(tmp_path.glob("*.json"))
    assert len(saved) == 1


