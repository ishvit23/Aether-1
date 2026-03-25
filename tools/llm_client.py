"""Network wrapper to invoke local inference engines like Ollama."""

import json
import logging
import urllib.request

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for executing local LLM prompts synchronously via HTTP."""

    def __init__(
        self, endpoint: str = "http://localhost:11434/api/generate", model: str = "llama3"
    ):
        self.endpoint = endpoint
        self.model = model

    def generate(self, prompt: str, system: str = "") -> str:
        """Execute a blocking inference request to the text-generation endpoint."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": False,
            "format": "json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=data, headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode("utf-8"))
                return str(result.get("response", "{}"))
        except Exception as e:
            logger.error(f"LLM API Request failed: {e}")
            return "{}"
