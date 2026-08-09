"""Embedding generation using sentence-transformers."""
import numpy as np
from typing import List
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generates dense vector embeddings for curriculum text."""

    def __init__(self):
        self._model = None
        self._dim = 384  # all-MiniLM-L6-v2 dimension

    def _load_model(self):
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                settings = get_settings()
                logger.info("loading_embedding_model", model=settings.embedding_model)
                self._model = SentenceTransformer(settings.embedding_model)
                self._dim = self._model.get_sentence_embedding_dimension()
                logger.info("embedding_model_loaded", dimension=self._dim)
            except Exception as e:
                logger.error("embedding_model_load_failed", error=str(e))
                raise

    def encode(self, texts: List[str]) -> np.ndarray:
        self._load_model()
        embeddings = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        return embeddings.astype("float32")

    def encode_single(self, text: str) -> np.ndarray:
        return self.encode([text])[0]

    @property
    def dimension(self) -> int:
        return self._dim


# Singleton
embedding_generator = EmbeddingGenerator()
