"""Tests for 5-prompt automated evaluation suite and benchmark runner."""
from pathlib import Path
from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider
from src.evaluate import (
    BENCHMARK_PROMPTS,
    run_evaluation,
    generate_benchmark_markdown,
    main,
)


def test_benchmark_prompts_dataset_coverage():
    assert len(BENCHMARK_PROMPTS) >= 5

    categories = {p["category"] for p in BENCHMARK_PROMPTS}
    assert len(categories) >= 3

    all_cebuano = " ".join(p["cebuano_text"].lower() for p in BENCHMARK_PROMPTS)
    for idiom in ["panuhot", "pasmo", "kalibanga", "pamaol", "hilanat"]:
        assert idiom in all_cebuano, f"Expected {idiom} in benchmark dataset"


def test_run_evaluation_aggregates_metrics():
    pipeline = CebuanoDoctorPipeline(provider=MockModelProvider(simulated_latency_s=0.001))
    results = run_evaluation(pipeline, prompts=BENCHMARK_PROMPTS[:2])

    assert len(results["cases"]) == 2
    assert "summary_stats" in results
    stats = results["summary_stats"]
    assert stats["avg_total_ms"] > 0
    assert stats["avg_stage1_ms"] > 0
    assert stats["avg_stage2_ms"] > 0
    assert stats["avg_stage3_ms"] > 0
    assert stats["success_rate_percent"] == 100.0


def test_generate_benchmark_markdown():
    pipeline = CebuanoDoctorPipeline(provider=MockModelProvider(simulated_latency_s=0.001))
    eval_data = run_evaluation(pipeline, prompts=BENCHMARK_PROMPTS[:2])
    md = generate_benchmark_markdown(eval_data)

    assert "# Evaluation & Benchmark Report" in md
    assert "Latency & Turnaround Summary" in md
    assert "Prompt 1" in md or "Prompt 2" in md
    assert "Gemma 4" in md
    assert "MedGemma" in md


def test_evaluate_cli_main(tmp_path: Path):
    output_path = tmp_path / "benchmark_report.md"
    runs_dir = tmp_path / "runs"

    exit_code = main([
        "--mock",
        "--output", str(output_path),
        "--save-dir", str(runs_dir),
    ])

    assert exit_code == 0
    assert output_path.exists()
    content = output_path.read_text(encoding="utf-8")
    assert len(content) > 500
    assert "Panuhot" in content or "panuhot" in content
    # Check runs saved
    saved_runs = list(runs_dir.glob("*.json"))
    assert len(saved_runs) == len(BENCHMARK_PROMPTS)
