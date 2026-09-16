"""Live Ollama provider using local HTTP REST API / official client."""
from typing import Optional, List, Dict, Any
import json
import httpx


class OllamaProvider:
    """Connects to local Ollama daemon for inference."""

    def __init__(self, host: str = "http://localhost:11434", timeout_s: float = 120.0) -> None:
        self.host = host.rstrip("/")
        self.timeout_s = timeout_s

    def is_healthy(self) -> bool:
        """Check if local Ollama daemon is reachable."""
        try:
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{self.host}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    is_available = is_healthy

    def list_models(self) -> List[str]:
        """List tags of all locally downloaded models."""
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"{self.host}/api/tags")
                if res.status_code == 200:
                    data = res.json()
                    return [m.get("name", "") for m in data.get("models", [])]
        except Exception:
            pass
        return []

    def has_model(self, model_name: str) -> bool:
        """Check if a specific model tag is installed locally."""
        installed = self.list_models()
        query = model_name.lower()
        for m in installed:
            m_lower = m.lower()
            if query == m_lower or query in m_lower or m_lower.startswith(query):
                return True
        return False

    def generate(self, model: str, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate text from Ollama endpoint."""
        endpoint = f"{self.host}/api/generate"
        payload: Dict[str, Any] = {
            "model": model,
            "prompt": prompt,
            "stream": False,
        }
        if system_prompt:
            payload["system"] = system_prompt

        try:
            with httpx.Client(timeout=self.timeout_s) as client:
                response = client.post(endpoint, json=payload)

            if response.status_code == 200:
                data = response.json()
                return data.get("response", "").strip()
            elif response.status_code == 404:
                raise RuntimeError(
                    f"Model '{model}' not found in Ollama. "
                    f"Please run 'ollama pull {model}' to install it on Drive D."
                )
            else:
                raise RuntimeError(
                    f"Ollama returned HTTP error {response.status_code}: {response.text}"
                )

        except (httpx.ConnectError, httpx.ConnectTimeout):
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.host}.\n"
                "Please make sure Ollama is installed and running on your laptop.\n"
                "To start Ollama, open the Ollama desktop app or run 'ollama serve' in a terminal."
            )
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Ollama timed out while generating response from '{model}' after {self.timeout_s}s."
            )
