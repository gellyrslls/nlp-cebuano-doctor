"""Storage and persistence utilities for consultation runs."""
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Union, Dict, Any

from src.domain.models import ConsultationResult


def slugify(text: str, max_length: int = 30) -> str:
    """Convert text into a filesystem-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_-]+", "_", text)
    slug = text.strip("_")
    return slug[:max_length] if slug else "run"


def generate_run_filename(timestamp_str: str, chief_complaint: str) -> str:
    """Generate standardized filename: <timestamp>_<slug>.json."""
    try:
        dt = datetime.fromisoformat(timestamp_str)
        ts = dt.strftime("%Y%m%d_%H%M%S")
    except Exception:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    slug = slugify(chief_complaint)
    return f"{ts}_{slug}.json"


def save_run(
    result: ConsultationResult,
    runs_dir: Union[Path, str] = "evaluations/runs",
) -> Path:
    """Persist ConsultationResult into structured JSON file."""
    dir_path = Path(runs_dir)
    dir_path.mkdir(parents=True, exist_ok=True)

    filename = generate_run_filename(result.timestamp, result.chief_complaint)
    file_path = dir_path / filename

    data = result.to_dict()
    file_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return file_path


def load_run(file_path: Union[Path, str]) -> Dict[str, Any]:
    """Load consultation run data from JSON file."""
    path = Path(file_path)
    return json.loads(path.read_text(encoding="utf-8"))
