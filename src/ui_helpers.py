"""UI helper functions and sample datasets for Streamlit application."""
import json
from pathlib import Path
from typing import Dict, List, Any, Union

from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider, ModelProvider
from src.providers.ollama_provider import OllamaProvider
from src.storage import load_run


SAMPLE_PROMPTS: Dict[str, str] = {
    "Panuhot (Cold exposure / muscle spasm)": "Mura ko'g gipanuhot sa akong likod ug abaga human nauwanan.",
    "Pasmo (Hunger weakness / gastritis)": "Gipasmo ko kay wala nakapamahaw, nagkurog akong kamot ug nagsakit akong tiyan.",
    "Kalibanga (Acute watery diarrhea)": "Gisakit akong tiyan unya sige ko'g kalibanga sukad ganinang buntag.",
    "Pamaol (Delayed onset muscle soreness)": "Grabe ang pamaol sa akong tibuok lawas human sa bug-at nga trabaho.",
    "Hilanat & Ubo (Fever with cough)": "Gihilantan ko ug giubo nga dunay plema sulod sa duha ka adlaw.",
    "Bughat (Relapse from premature exertion)": "Gibughat ko kay nanilhig dayon bisan bag-o pa lang naayo sa hilanat.",
}


def get_pipeline(
    mock: bool = False,
    translation_model: str = "gemma4:e2b",
    medical_model: str = "alibayram/medgemma",
) -> CebuanoDoctorPipeline:
    """Create a configured CebuanoDoctorPipeline."""
    provider: ModelProvider
    if mock:
        provider = MockModelProvider(simulated_latency_s=0.01)
    else:
        provider = OllamaProvider()

    return CebuanoDoctorPipeline(
        provider=provider,
        translation_model=translation_model,
        medical_model=medical_model,
    )


def list_recent_runs(
    runs_dir: Union[Path, str] = "evaluations/runs",
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Return recent consultation runs sorted newest first."""
    dir_path = Path(runs_dir)
    if not dir_path.exists():
        return []

    json_files = sorted(dir_path.glob("*.json"), key=lambda f: f.stat().st_mtime, reverse=True)
    records = []
    for f in json_files[:limit]:
        try:
            records.append(load_run(f))
        except Exception:
            continue
    return records
