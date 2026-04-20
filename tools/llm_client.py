"""Network wrapper to invoke local inference engines like Ollama."""

import json
import logging
import urllib.request

logger = logging.getLogger(__name__)


class LLMClient:
    """Wrapper for executing local LLM prompts synchronously via HTTP."""

    def __init__(
        self, endpoint: str = "http://localhost:11434/api/generate", model: str = "llama3.2:3b"
    ):
        self.endpoint = endpoint
        self.model = model

    def generate(self, prompt: str, system: str = "") -> str:
        """Execute a blocking inference request to the text-generation endpoint."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system,
            "stream": True,
            "format": "json",
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=data, headers={"Content-Type": "application/json"}
        )

        try:
            import sys

            full_response = ""
            print(f"\n[STREAM] Awaiting link to '{self.model}'...\n")
            with urllib.request.urlopen(req, timeout=600) as response:
                for line in response:
                    if not line:
                        continue
                    chunk = json.loads(line.decode("utf-8"))
                    text = chunk.get("response", "")
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    full_response += text
            print("\n")
            return full_response
        except Exception as e:
            logger.error(f"LLM API Request failed: {e}")
            return "{}"
