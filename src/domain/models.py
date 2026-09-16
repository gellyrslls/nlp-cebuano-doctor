"""Domain models for Cebuano Doctor."""
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any


@dataclass
class StageMetrics:
    """Latency metrics recorded per stage in milliseconds."""
    translation_en_ms: float = 0.0
    medical_inference_ms: float = 0.0
    translation_ceb_ms: float = 0.0
    total_turnaround_ms: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ConsultationResult:
    """End-to-end result returned by the circular pipeline."""
    chief_complaint: str
    english_translation: str = ""
    english_medical_guidance: str = ""
    cebuano_medical_guidance: str = ""
    metrics: StageMetrics = field(default_factory=StageMetrics)
    status: str = "success"
    error_message: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
