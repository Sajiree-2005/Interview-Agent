"""Embedding generation - uses pre-computed curriculum embeddings."""
import numpy as np
from typing import List
from app.core.logging import get_logger

logger = get_logger(__name__)


class EmbeddingGenerator:
    """Generates embeddings using pre-computed arrays (no model loading at runtime)."""
    
    def __init__(self):
        self._dim = 384
        
    def encode(self, texts: List[str]) -> np.ndarray:
        """Not used at runtime - embeddings are pre-computed."""
        raise NotImplementedError("Embeddings are pre-computed. Use retriever.load_precomputed().")
    
    def encode_single(self, text: str) -> np.ndarray:
        raise NotImplementedError("Embeddings are pre-computed. Use retriever.load_precomputed().")
    
    @property
    def dimension(self) -> int:
        return self._dim


# Singleton
embedding_generator = EmbeddingGenerator()