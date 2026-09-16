"""Model provider abstractions and mock implementation."""
from typing import Protocol, Optional
import time


class ModelProvider(Protocol):
    """Abstract interface for LLM execution."""

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate a response given a model tag and prompt."""
        ...


class MockModelProvider:
    """Deterministic mock provider for unit testing and offline development."""

    def __init__(self, simulated_latency_s: float = 0.01) -> None:
        self.simulated_latency_s = simulated_latency_s
        self.call_history = []

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        if self.simulated_latency_s > 0:
            time.sleep(self.simulated_latency_s)

        self.call_history.append({"model": model, "prompt": prompt, "system_prompt": system_prompt})
        lower_prompt = prompt.lower()

        sys_lower = (system_prompt or "").lower()

        # Stage 1: Cebuano to English translation
        if "clinical english" in sys_lower:
            if "panuhot" in lower_prompt:
                return "The patient is experiencing bodily aches and abdominal bloating attributed to sudden cold exposure."
            elif "ulo" in lower_prompt or "headache" in lower_prompt:
                return "The patient has a severe throbbing headache."
            elif "tiyan" in lower_prompt or "kalibanga" in lower_prompt:
                return "The patient suffers from sharp abdominal cramps and frequent watery diarrhea."
            return f"Patient clinical complaint in English: {prompt}"

        # Stage 2: MedGemma Medical Consultation
        if "medgemma" in model.lower() or "clinical ai" in sys_lower or "medical guidance" in sys_lower:
            return (
                "Based on the reported symptoms, this could be related to acute gastroenteritis or muscular tension. "
                "Recommendation: Ensure adequate oral hydration with electrolytes, rest in a comfortable environment, "
                "and monitor for red flags such as high fever or severe dehydration. Consult a physician if symptoms worsen."
            )

        # Stage 3: English to Cebuano translation
        if ("cebuano" in sys_lower or "bisaya" in sys_lower) and ("translate" in sys_lower or "communicator" in sys_lower):
            return (
                "Base sa imong mga gipamati, posibleng gumikan kini sa impeksyon sa tiyan o pamaol sa kaunoran. "
                "Tambag: Paimna og daghang tubig nga dunay oral rehydration salts, pahuway sa tarung, ug bantayi kung dunay taas nga hilanat. "
                "Kon magkagrabe ang imong gibati, pakigkita gilayon sa labing duol nga doktor o health center."
            )

        # Default fallback
        return f"[Mock response from {model}]: {prompt}"
