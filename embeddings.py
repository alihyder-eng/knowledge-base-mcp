from __future__ import annotations

import time
from typing import Literal

from google import genai
from google.genai import types

from config import Settings

TaskType = Literal["RETRIEVAL_DOCUMENT", "RETRIEVAL_QUERY"]

# Gemini batches embed_content calls server-side per request, but the API
# still caps how many contents you can pack into one call.
_MAX_BATCH = 100
_MAX_RETRIES = 3


class GeminiEmbedder:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = genai.Client(api_key=settings.gemini_api_key)

    def _embed_batch(self, texts: list[str], task_type: TaskType) -> list[list[float]]:
        last_err: Exception | None = None
        for attempt in range(_MAX_RETRIES):
            try:
                result = self.client.models.embed_content(
                    model=self.settings.gemini_embed_model,
                    contents=texts,
                    config=types.EmbedContentConfig(
                        task_type=task_type,
                        output_dimensionality=self.settings.embed_dim,
                    ),
                )
                return [e.values for e in result.embeddings]
            except Exception as e:  # noqa: BLE001 - retry on any transient API error
                last_err = e
                time.sleep(1.5 * (attempt + 1))
        raise RuntimeError(f"Gemini embedding call failed after retries: {last_err}")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed chunks that are being written into the index."""
        out: list[list[float]] = []
        for i in range(0, len(texts), _MAX_BATCH):
            batch = texts[i : i + _MAX_BATCH]
            out.extend(self._embed_batch(batch, "RETRIEVAL_DOCUMENT"))
        return out

    def embed_query(self, text: str) -> list[float]:
        """Embed a single incoming search query."""
        return self._embed_batch([text], "RETRIEVAL_QUERY")[0]
