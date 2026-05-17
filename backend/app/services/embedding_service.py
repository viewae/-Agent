import logging
import time

from app.config import settings
from app.utils.llm_client import get_embedding_client, get_embedding_dim, get_embedding_model

logger = logging.getLogger(__name__)

BATCH_LIMIT = 2048
MAX_RETRIES = 3


class EmbeddingService:
    def __init__(self):
        self._client = get_embedding_client()
        self._model = get_embedding_model()
        self._dim = get_embedding_dim()
        self._use_dimensions = settings.EMBEDDING_PROVIDER == "openai"

    def embed(self, text: str) -> list[float]:
        resp = self._client.embeddings.create(
            **self._build_params(text),
        )
        return resp.data[0].embedding

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        all_embeddings = []
        for i in range(0, len(texts), BATCH_LIMIT):
            batch = texts[i : i + BATCH_LIMIT]
            batch_embs = self._embed_with_retry(batch)
            all_embeddings.extend(batch_embs)
        return all_embeddings

    def _build_params(self, text_or_texts):
        params = {
            "model": self._model,
            "input": text_or_texts,
        }
        if self._use_dimensions:
            params["dimensions"] = self._dim
        return params

    def _embed_with_retry(self, texts: list[str]) -> list[list[float]]:
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._client.embeddings.create(
                    **self._build_params(texts),
                )
                return [d.embedding for d in resp.data]
            except Exception as e:
                last_error = e
                logger.warning("Embedding attempt %d failed: %s", attempt + 1, e)
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
        raise last_error
