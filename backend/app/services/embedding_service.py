from __future__ import annotations

import hashlib
import importlib.util
import logging
from functools import lru_cache

from app.core.config import settings
from app.services.text_processing import cosine_similarity, tokenize_for_matching

logger = logging.getLogger(__name__)


class EmbeddingProvider:
    def encode(self, text: str) -> list[float]:
        raise NotImplementedError

    def similarity(self, left: str, right: str) -> float:
        return cosine_similarity(self.encode(left), self.encode(right))


class HashingEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int) -> None:
        self.dimensions = dimensions

    def encode(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        tokens = tokenize_for_matching(text)
        if not tokens:
            return vector
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = -1.0 if digest[4] % 2 else 1.0
            vector[index] += sign

        norm = sum(value * value for value in vector) ** 0.5
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class SentenceTransformerEmbeddingProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None

    def _get_model(self):
        if self._model is None:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, text: str) -> list[float]:
        model = self._get_model()
        vector = model.encode(text, normalize_embeddings=True)
        return [float(value) for value in vector.tolist()]


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    preferred = settings.embedding_backend.lower()
    if preferred in {"auto", "sentence-transformers", "sentence_transformers"}:
        if importlib.util.find_spec("sentence_transformers") is not None:
            return SentenceTransformerEmbeddingProvider(settings.embedding_model_name)
        logger.warning("sentence-transformers is unavailable; falling back to hashing embeddings")
    return HashingEmbeddingProvider(settings.embedding_dimensions)
