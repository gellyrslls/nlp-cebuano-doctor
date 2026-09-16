"""Three-Stage Circular Pipeline for Cebuano Doctor."""
import time
from pathlib import Path
from typing import Optional, Union
from src.domain.models import ConsultationResult, StageMetrics
from src.domain.provider import ModelProvider, MockModelProvider
from src.storage import save_run


from src.domain.prompts import (
    STAGE1_TRANSLATION_PROMPT,
    STAGE2_MEDICAL_PROMPT,
    STAGE3_BACK_TRANSLATION_PROMPT,
    format_stage1_prompt,
    format_stage2_prompt,
    format_stage3_prompt,
)


class CebuanoDoctorPipeline:
    """The primary circular translation and medical reasoning pipeline."""

    def __init__(
        self,
        provider: Optional[ModelProvider] = None,
        translation_model: str = "gemma4:e2b",
        medical_model: str = "alibayram/medgemma",
        runs_dir: Optional[Union[Path, str]] = "evaluations/runs",
        auto_save: bool = True,
    ) -> None:
        self.provider = provider or MockModelProvider()
        self.translation_model = translation_model
        self.medical_model = medical_model
        self.runs_dir = runs_dir
        self.auto_save = auto_save

    def run(self, chief_complaint: str) -> ConsultationResult:
        """Execute the 3-stage circular consultation pipeline."""
        complaint = (chief_complaint or "").strip()
        if not complaint:
            return ConsultationResult(
                chief_complaint="",
                status="error",
                error_message="Chief complaint cannot be empty."
            )

        start_total = time.perf_counter()
        metrics = StageMetrics()

        try:
            # Stage 1: Translate Cebuano to English (Gemma 4)
            t1_start = time.perf_counter()
            english_translation = self.provider.generate(
                model=self.translation_model,
                prompt=format_stage1_prompt(complaint),
                system_prompt=STAGE1_TRANSLATION_PROMPT,
            ).strip()
            metrics.translation_en_ms = round((time.perf_counter() - t1_start) * 1000, 2)

            # Stage 2: Medical Consultation (MedGemma)
            t2_start = time.perf_counter()
            english_guidance = self.provider.generate(
                model=self.medical_model,
                prompt=format_stage2_prompt(english_translation),
                system_prompt=STAGE2_MEDICAL_PROMPT,
            ).strip()
            metrics.medical_inference_ms = round((time.perf_counter() - t2_start) * 1000, 2)

            # Stage 3: Translate English to Cebuano (Gemma 4)
            t3_start = time.perf_counter()
            cebuano_guidance = self.provider.generate(
                model=self.translation_model,
                prompt=format_stage3_prompt(english_guidance),
                system_prompt=STAGE3_BACK_TRANSLATION_PROMPT,
            ).strip()
            metrics.translation_ceb_ms = round((time.perf_counter() - t3_start) * 1000, 2)

            metrics.total_turnaround_ms = round((time.perf_counter() - start_total) * 1000, 2)

            result = ConsultationResult(
                chief_complaint=complaint,
                english_translation=english_translation,
                english_medical_guidance=english_guidance,
                cebuano_medical_guidance=cebuano_guidance,
                metrics=metrics,
                status="success",
            )
            if self.auto_save and self.runs_dir:
                try:
                    save_run(result, runs_dir=self.runs_dir)
                except Exception:
                    pass
            return result

        except Exception as exc:
            metrics.total_turnaround_ms = round((time.perf_counter() - start_total) * 1000, 2)
            result = ConsultationResult(
                chief_complaint=complaint,
                metrics=metrics,
                status="error",
                error_message=str(exc),
            )
            if self.auto_save and self.runs_dir:
                try:
                    save_run(result, runs_dir=self.runs_dir)
                except Exception:
                    pass
            return result
