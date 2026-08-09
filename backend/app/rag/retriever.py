"""Numpy-based curriculum retriever (FAISS-free for maximum compatibility)."""
import numpy as np
from typing import List, Dict, Any, Optional
from app.rag.embeddings import embedding_generator
from app.services.curriculum_service import curriculum_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _cosine_similarity(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query and all embeddings."""
    # Both are L2-normalized, so dot product = cosine similarity
    return np.dot(embeddings, query)


class CurriculumRetriever:
    """Retrieves relevant curriculum days using dense vector search (numpy-based)."""

    def __init__(self):
        self._embeddings: Optional[np.ndarray] = None
        self._day_numbers: List[int] = []
        self._chunks: List[str] = []
        self._initialized = False

    def build_index(self) -> "CurriculumRetriever":
        """Build index from curriculum data."""
        if self._initialized:
            return self

        curriculum_service.load()
        days = curriculum_service.get_all_days()

        texts = []
        day_nums = []
        for day in days:
            text = curriculum_service.get_day_text_for_embedding(day)
            texts.append(text)
            day_nums.append(day.day)

        if not texts:
            logger.warning("no_curriculum_texts_found")
            return self

        self._embeddings = embedding_generator.encode(texts)
        self._day_numbers = day_nums
        self._chunks = texts
        self._initialized = True

        logger.info("retriever_index_built", days=len(day_nums), dim=self._embeddings.shape[1])
        return self

    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve most relevant curriculum days for a query."""
        if not self._initialized:
            self.build_index()

        if self._embeddings is None or len(self._embeddings) == 0:
            return []

        settings = get_settings()
        k = top_k or settings.top_k_retrieval

        query_embedding = embedding_generator.encode_single(query)

        scores = _cosine_similarity(query_embedding, self._embeddings)
        top_indices = np.argsort(scores)[::-1][:k]

        results = []
        for idx in top_indices:
            idx = int(idx)
            day_num = self._day_numbers[idx]
            day = curriculum_service.get_day(day_num)
            if day:
                results.append({
                    "day": day_num,
                    "title": day.title,
                    "type": day.type,
                    "score": float(scores[idx]),
                    "text": self._chunks[idx][:500],
                })

        logger.debug("retrieval_completed", query=query[:50], results=len(results))
        return results

    def retrieve_for_topic(self, topic: str, top_k: int = 2) -> List[Dict[str, Any]]:
        """Retrieve curriculum context for a specific topic."""
        return self.retrieve(topic, top_k=top_k)

    def get_context_string(self, query: str, top_k: Optional[int] = None) -> str:
        """Get a formatted context string for LLM prompting."""
        results = self.retrieve(query, top_k=top_k)
        lines = []
        for r in results:
            lines.append(f"Day {r['day']}: {r['title']} [{r['type']}]\n{r['text']}")
        return "\n\n---\n\n".join(lines)


# Singleton
retriever = CurriculumRetriever()
