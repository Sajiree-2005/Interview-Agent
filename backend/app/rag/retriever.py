"""Curriculum retriever using pre-computed TF-IDF embeddings."""
import json
import os
import numpy as np
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from app.services.curriculum_service import curriculum_service
from app.core.config import get_settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _cosine_similarity(query: np.ndarray, embeddings: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between query and all embeddings."""
    return np.dot(embeddings, query)


class CurriculumRetriever:
    """Retrieves relevant curriculum days using pre-computed TF-IDF embeddings."""
    
    def __init__(self):
        self._embeddings: Optional[np.ndarray] = None
        self._day_numbers: List[int] = []
        self._chunks: List[str] = []
        self._vectorizer: Optional[TfidfVectorizer] = None
        self._initialized = False
        
    def build_index(self) -> "CurriculumRetriever":
        """Load pre-computed embeddings and build query vectorizer."""
        if self._initialized:
            return self
            
        curriculum_service.load()
        days = curriculum_service.get_all_days()
        
        # Load pre-computed embeddings
        data_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        embeddings_path = os.path.join(data_dir, "data", "curriculum_embeddings.npy")
        day_map_path = os.path.join(data_dir, "data", "curriculum_day_map.json")
        
        self._embeddings = np.load(embeddings_path).astype("float32")
        with open(day_map_path, "r", encoding="utf-8") as f:
            self._day_numbers = json.load(f)
        
        # Build texts for the vectorizer
        texts = []
        for day in days:
            text = curriculum_service.get_day_text_for_embedding(day)
            texts.append(text)
        self._chunks = texts
        
        # Fit TF-IDF vectorizer on same corpus for query encoding
        self._vectorizer = TfidfVectorizer(max_features=384, stop_words='english')
        self._vectorizer.fit(texts)
        
        self._initialized = True
        logger.info("retriever_loaded", days=len(self._day_numbers), dim=self._embeddings.shape[1])
        return self
    
    def retrieve(self, query: str, top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """Retrieve most relevant curriculum days for a query."""
        if not self._initialized:
            self.build_index()
        
        if self._embeddings is None or len(self._embeddings) == 0:
            return []
        
        settings = get_settings()
        k = top_k or settings.top_k_retrieval
        
        # Encode query with same TF-IDF vectorizer
        query_vec = self._vectorizer.transform([query]).toarray().astype("float32")
        query_vec = query_vec[0]
        # L2 normalize
        norm = np.linalg.norm(query_vec)
        if norm > 0:
            query_vec = query_vec / norm
        
        scores = _cosine_similarity(query_vec, self._embeddings)
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