"""System and Environment Diagnostic Doctor for Cebuano Doctor."""
import os
import sys
import shutil
import platform
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from src.providers.ollama_provider import OllamaProvider


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()


def run_diagnostics(host: str = "http://localhost:11434") -> int:
    """Run full system diagnostics and print formatted report."""
    console.print(Panel.fit("[bold cyan][Doctor] Cebuano Doctor System Diagnostics[/bold cyan]", border_style="cyan"))

    # 1. Host & Platform
    table_env = Table(title="1. System Environment", show_header=True, header_style="bold magenta")
    table_env.add_column("Component", style="cyan")
    table_env.add_column("Status / Value", style="white")

    table_env.add_row("Operating System", f"{platform.system()} {platform.release()} ({platform.machine()})")
    table_env.add_row("Python Version", f"{sys.version.split()[0]} ({platform.python_implementation()})")

    # Storage Check
    for drive in ["C:\\", "D:\\"]:
        if os.path.exists(drive):
            total, used, free = shutil.disk_usage(drive)
            free_gb = round(free / (1024 ** 3), 2)
            total_gb = round(total / (1024 ** 3), 2)
            color = "green" if free_gb > 15 else "yellow" if free_gb > 8 else "red"
            table_env.add_row(f"Storage ({drive})", f"[{color}]{free_gb} GB free[/{color}] of {total_gb} GB")

    ollama_models_env = os.environ.get("OLLAMA_MODELS")
    if not ollama_models_env and platform.system() == "Windows":
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
                ollama_models_env, _ = winreg.QueryValueEx(key, "OLLAMA_MODELS")
        except Exception:
            ollama_models_env = None

    ollama_path_str = ollama_models_env or "Not set (defaulting to C: drive)"
    table_env.add_row("OLLAMA_MODELS Path", f"[bold green]{ollama_path_str}[/bold green]")
    console.print(table_env)
    console.print()

    # 2. Ollama Connectivity & Models
    provider = OllamaProvider(host=host)
    table_ollama = Table(title="2. Ollama & AI Models", show_header=True, header_style="bold magenta")
    table_ollama.add_column("Check", style="cyan")
    table_ollama.add_column("Status", style="white")
    table_ollama.add_column("Details / Action", style="dim")

    is_online = provider.is_healthy()
    if is_online:
        table_ollama.add_row("Ollama Daemon", "[bold green]ONLINE[/bold green]", f"Connected to {host}")
        models = provider.list_models()
        model_str = ", ".join(models) if models else "[yellow]No models found yet[/yellow]"
        table_ollama.add_row("Installed Models", str(len(models)), model_str)

        has_gemma = any("gemma" in m.lower() for m in models)
        has_med = any("medgemma" in m.lower() or "medical" in m.lower() for m in models)

        table_ollama.add_row(
            "Translation Model (Gemma)",
            "[bold green]INSTALLED[/bold green]" if has_gemma else "[bold red]MISSING[/bold red]",
            "Ready" if has_gemma else "Run: ollama pull gemma4:e2b"
        )
        table_ollama.add_row(
            "Medical Model (MedGemma)",
            "[bold green]INSTALLED[/bold green]" if has_med else "[bold red]MISSING[/bold red]",
            "Ready" if has_med else "Run: ollama pull alibayram/medgemma"
        )
    else:
        table_ollama.add_row("Ollama Daemon", "[bold red]OFFLINE / NOT RUNNING[/bold red]", f"Cannot connect to {host}")
        table_ollama.add_row("How to Fix", "Start Ollama", "Launch Ollama app from Start Menu or run 'ollama serve'")

    console.print(table_ollama)
    console.print()

    if not is_online:
        console.print("[yellow][*] Note: You can still test the entire system right now in mock mode using:[/yellow]")
        console.print("   [bold green]python -m src.cli --mock[/bold green]\n")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(run_diagnostics())
