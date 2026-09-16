"""Tests for OllamaProvider error handling and health checks."""
import unittest
from src.providers.ollama_provider import OllamaProvider


class TestOllamaProvider(unittest.TestCase):
    def test_offline_host_is_not_healthy(self):
        # Port 59999 should not be running Ollama
        provider = OllamaProvider(host="http://localhost:59999", timeout_s=1.0)
        assert provider.is_healthy() is False
        assert provider.list_models() == []

    def test_offline_generate_raises_connection_error(self):
        provider = OllamaProvider(host="http://localhost:59999", timeout_s=1.0)
        with self.assertRaises(ConnectionError) as ctx:
            provider.generate(model="gemma4:e2b", prompt="Hello")
        assert "Cannot connect to Ollama" in str(ctx.exception)


if __name__ == "__main__":
    unittest.main()
