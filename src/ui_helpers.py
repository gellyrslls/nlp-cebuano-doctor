"""UI helper functions and sample datasets for Streamlit application."""
import json
from pathlib import Path
from typing import Dict, List, Any, Union

from src.domain.pipeline import CebuanoDoctorPipeline
from src.domain.provider import MockModelProvider, ModelProvider
from src.providers.ollama_provider import OllamaProvider
from src.storage import load_run


SAMPLE_PROMPTS: Dict[str, str] = {
    "1. Tension Headache (TC Library)": "Bay, grabeha na gyud aning labad sa akong ulo oy. Sukad pa gyud ni ganinang hapon samtang ga-review mi sa TC library. Mura bitaw'g gipugos og bakos akong agtang sa kahuot, nya magsakit pud akong mata kon motan-aw ko'g screen sa laptop. Makatabang ba kaha ang Biogesic ani o kinahanglan na ni nako ipahuway og piyong kadiyot?",
    "2. Panuhot (Carcar City Aunt)": "Dong, maayong hapon. Mangutana unta ko ba, kay kining akong abaga ug likod mura man gud og gipanuhot og maayo sukad kagahapon. Nanikig gyud akong liog unya dunay mga bukol-bukol o lusay-lusay sa akong gusok nga pwerte gyung sakita kon hikapon, mura'g naay dinalang hangin sa sulod. Mahilot ra ba kaha ni og lana nga naay luy-a?",
    "3. Pasmo & Kabuhi (IT Park BPO)": "Doc, maayong buntag. Magpatambag unta ko bahin aning akong gibati karon. Nag-night shift man gud ko sa IT Park, unya sige ra ko'g laktaw-laktaw og kaon kay busy kaayo ang queue sa calls, puro ra kape ug energy drink akong nasulod sa tiyan. Karon, mura na gyud ko'g gipasmo kay nagkurog akong mga kamot, bugnaw kaayo akong singot, unya nagkabuhi akong kuto-kuto.",
    "4. Kalibanga (Fuente Pungko-pungko)": "Doc / Bay, mangayo unta ko'g advice. Sukad pa gyud kagabii pagkahuman nakog kaon sa pungko-pungko, gikalibanga na gyud ko'g taman. Makapito na ko balik-balik sa cr sukad ganinang kaadlawon, puros gyud watery stool nga yellowish ug walay klarong porma, unya grabe kaayo ang abdominal cramping o pamalaybalay sa tiyan. Mag-start na ba ko'g ciprofloxacin?",
    "5. Pneumonia / Chest Pain (SRP)": "Maayong adlaw, doc. Pwerteng guola na gyud nako kay hapit na duha ka semana kining akong ubo nga wala gyuy lurang-lurang. Sukad sa miaging adlaw, misamot gyud ang hilanat, niabot na'g 39.2°C akong hilanat sa thermometer unya magkurog ko sa katugnaw. Ang plema dalag nga nagsagol og tayaon, unya mura'g gidunggab og kutsilyo kining kilid sa akong dughan.",
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

    json_files = sorted(dir_path.glob("*.json"), reverse=True)
    records = []
    for f in json_files:
        try:
            records.append(load_run(f))
        except Exception:
            continue
    records.sort(key=lambda r: r.get("timestamp", ""), reverse=True)
    return records[:limit]
