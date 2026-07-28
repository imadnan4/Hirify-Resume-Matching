from __future__ import annotations

import hashlib
import logging
import threading
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
    """Degraded fallback when no ML embedding library is available.

    Uses randomized hashing to produce pseudo-embeddings. These vectors
    are NOT semantically meaningful — they provide only coarse lexical
    similarity. Always prefer FastEmbedProvider for production use.
    """
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


class FastEmbedProvider(EmbeddingProvider):
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self._model = None
        self._model_lock = threading.Lock()

    def _get_model(self):
        if self._model is None:
            with self._model_lock:
                if self._model is None:
                    from fastembed import TextEmbedding

                    self._model = TextEmbedding(model_name=self.model_name)
        return self._model

    def encode(self, text: str) -> list[float]:
        model = self._get_model()
        embeddings = list(model.embed([text]))
        if not embeddings:
            return [0.0] * settings.embedding_dimensions
        vector = [float(value) for value in embeddings[0]]
        if len(vector) != settings.embedding_dimensions:
            raise RuntimeError(
                f"Model '{self.model_name}' produced {len(vector)}-dim embeddings, "
                f"expected {settings.embedding_dimensions} (check EMBEDDING_DIMENSIONS)"
            )
        return vector


@lru_cache(maxsize=1)
def get_embedding_provider() -> EmbeddingProvider:
    preferred = settings.embedding_backend.lower()
    if preferred in {"auto", "fastembed"}:
        try:
            import fastembed  # noqa: F401

            logger.info("Using FastEmbed provider with model %s", settings.embedding_model_name)
            return FastEmbedProvider(settings.embedding_model_name)
        except ImportError:
            logger.warning("fastembed is unavailable; falling back to hashing embeddings")
    return HashingEmbeddingProvider(settings.embedding_dimensions)


# Text-hash → embedding cache (process-local, bounded to MAX_CACHE_SIZE entries)
_embedding_cache: dict[str, list[float]] = {}
_MAX_CACHE_SIZE = 2048
_cache_lock = threading.Lock()


def cached_encode(provider: EmbeddingProvider, text: str) -> list[float]:
    cache_key = hashlib.sha256(text.encode("utf-8")).hexdigest()
    with _cache_lock:
        if cache_key in _embedding_cache:
            return _embedding_cache[cache_key]
    result = provider.encode(text)
    with _cache_lock:
        if len(_embedding_cache) >= _MAX_CACHE_SIZE:
            _embedding_cache.pop(next(iter(_embedding_cache)))
        _embedding_cache[cache_key] = result
        return result
