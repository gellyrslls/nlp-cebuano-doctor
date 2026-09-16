"""Interactive Rich CLI runner for Cebuano Doctor."""
import argparse
import sys
from pathlib import Path
from typing import Optional, Sequence, Union

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from src.domain.models import ConsultationResult
from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider, ModelProvider
from src.providers.ollama_provider import OllamaProvider
from src.storage import save_run


def parse_args(args: Optional[Sequence[str]] = None) -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Cebuano Doctor: Three-Stage Circular Translation & Medical Reasoning Runner"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        default=False,
        help="Run using offline MockModelProvider without connecting to Ollama.",
    )
    parser.add_argument(
        "--query",
        type=str,
        default=None,
        help="Single Cebuano chief complaint to run non-interactively.",
    )
    parser.add_argument(
        "--model-translate",
        type=str,
        default="gemma4:e2b",
        help="Ollama model for translation stages (default: gemma4:e2b).",
    )
    parser.add_argument(
        "--model-medical",
        type=str,
        default="alibayram/medgemma",
        help="Ollama model for clinical medical inference (default: alibayram/medgemma).",
    )
    parser.add_argument(
        "--save-dir",
        type=str,
        default="evaluations/runs",
        help="Directory to persist structured run logs (default: evaluations/runs).",
    )
    return parser.parse_args(args)


def render_consultation_panels(
    result: ConsultationResult,
    console: Console,
    saved_path: Optional[Path] = None,
) -> None:
    """Render structured rich panels for each stage of consultation."""
    console.print()

    # Chief Complaint Panel
    complaint_text = Text(result.chief_complaint, style="bold white")
    console.print(
        Panel(
            complaint_text,
            title="[bold cyan]Chief Complaint (Cebuano)[/bold cyan]",
            border_style="cyan",
            expand=True,
        )
    )

    if result.status == "error":
        err_text = Text(result.error_message or "An unexpected error occurred.", style="bold red")
        console.print(
            Panel(
                err_text,
                title="[bold red]Consultation Error[/bold red]",
                border_style="red",
                expand=True,
            )
        )
        if saved_path:
            console.print(f"[dim]Saved error run to: {saved_path}[/dim]")
        return

    # Stage 1: Cebuano -> English Clinical Translation
    t1_title = f"[bold yellow]Stage 1: English Clinical Translation ({result.metrics.translation_en_ms:.1f} ms)[/bold yellow]"
    console.print(
        Panel(
            Text(result.english_translation, style="bright_white"),
            title=t1_title,
            subtitle="[yellow]Gemma 4 (NLU)[/yellow]",
            border_style="yellow",
            expand=True,
        )
    )

    # Stage 2: English Medical Inference
    t2_title = f"[bold green]Stage 2: MedGemma Clinical Guidance ({result.metrics.medical_inference_ms:.1f} ms)[/bold green]"
    console.print(
        Panel(
            Text(result.english_medical_guidance, style="bright_white"),
            title=t2_title,
            subtitle="[green]MedGemma (Inference)[/green]",
            border_style="green",
            expand=True,
        )
    )

    # Stage 3: Back-translation to Cebuano
    t3_title = f"[bold bright_cyan]Stage 3: Cebuano Patient Response ({result.metrics.translation_ceb_ms:.1f} ms)[/bold bright_cyan]"
    console.print(
        Panel(
            Text(result.cebuano_medical_guidance, style="bold bright_cyan"),
            title=t3_title,
            subtitle="[bright_cyan]Gemma 4 (NLG)[/bright_cyan]",
            border_style="bright_cyan",
            expand=True,
        )
    )

    # Latency Breakdown Table
    table = Table(title="[bold magenta]Latency Breakdown & Performance[/bold magenta]", expand=True)
    table.add_column("Pipeline Stage", style="cyan")
    table.add_column("Component", style="dim")
    table.add_column("Latency (ms)", justify="right", style="bold green")

    table.add_row("1. Cebuano -> English NLU", "Gemma 4", f"{result.metrics.translation_en_ms:.1f} ms")
    table.add_row("2. Clinical Medical Reasoning", "MedGemma", f"{result.metrics.medical_inference_ms:.1f} ms")
    table.add_row("3. English -> Cebuano NLG", "Gemma 4", f"{result.metrics.translation_ceb_ms:.1f} ms")
    table.add_row("Total Turnaround Time", "End-to-End", f"{result.metrics.total_turnaround_ms:.1f} ms", style="bold yellow")
    console.print(table)

    if saved_path:
        console.print(f"[dim]Saved run to: {saved_path}[/dim]")


def run_consultation(
    query: str,
    pipeline: CebuanoDoctorPipeline,
    console: Optional[Console] = None,
    save_dir: Optional[Union[Path, str]] = "evaluations/runs",
) -> ConsultationResult:
    """Run a single consultation query through pipeline, render results, and save artifact."""
    c = console or Console()
    with c.status("[bold green]Executing 3-stage circular medical pipeline...[/bold green]", spinner="dots"):
        result = pipeline.run(query)

    saved_path = None
    if save_dir:
        try:
            saved_path = save_run(result, runs_dir=save_dir)
        except Exception as exc:
            c.print(f"[bold red]Failed to save run artifact:[/bold red] {exc}")

    render_consultation_panels(result, c, saved_path=saved_path)
    return result


def main(args: Optional[Sequence[str]] = None) -> int:
    """CLI entrypoint supporting both single-query execution and interactive loop."""
    options = parse_args(args)
    console = Console()

    provider: ModelProvider
    if options.mock:
        provider = MockModelProvider(simulated_latency_s=0.01)
    else:
        provider = OllamaProvider()

    pipeline = CebuanoDoctorPipeline(
        provider=provider,
        translation_model=options.model_translate,
        medical_model=options.model_medical,
    )

    # Single non-interactive query mode
    if options.query is not None:
        result = run_consultation(
            query=options.query,
            pipeline=pipeline,
            console=console,
            save_dir=options.save_dir,
        )
        return 0 if result.status == "success" else 1

    # Interactive continuous REPL mode
    provider_desc = "Mock (Offline Testing)" if options.mock else f"Ollama ({options.model_translate} + {options.model_medical})"
    console.print(
        Panel.fit(
            f"[bold cyan]Cebuano Doctor (Doktor sa Sugbo)[/bold cyan]\n"
            f"[dim]3-Stage Circular Translation & Medical Reasoning Pipeline[/dim]\n\n"
            f"[yellow]Engine:[/yellow] {provider_desc}\n"
            f"[yellow]Persistence:[/yellow] {options.save_dir}\n\n"
            f"Type your symptoms in Cebuano (e.g., 'Gisakit akong tiyan unya gikalibanga ko').\n"
            f"Type [bold red]'exit'[/bold red] or [bold red]'q'[/bold red] to quit.",
            border_style="cyan",
            title="[bold green]CS 5101 NLP Consultation[/bold green]",
        )
    )

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]Ipatin-aw ang imong gibati (o 'q' para mobiya)[/bold cyan]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Naundang ang konsultasyon. Amping kanunay![/yellow]")
            break

        cleaned = (user_input or "").strip()
        if not cleaned:
            continue

        if cleaned.lower() in ("q", "quit", "exit", "gawas"):
            console.print("[green]Salamat! Pag-amping kanunay sa imong panglawas.[/green]")
            break

        run_consultation(
            query=cleaned,
            pipeline=pipeline,
            console=console,
            save_dir=options.save_dir,
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
