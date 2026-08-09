"""Application configuration and environment management."""
import os
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Keys
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4o-mini"
    eval_model: str = "gpt-4o-mini"

    # App behavior
    app_env: str = "development"
    log_level: str = "INFO"
    max_questions: int = 10
    min_curriculum_days: int = 4
    min_questions: int = 8

    # RAG
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    top_k_retrieval: int = 3

    # Paths
    curriculum_path: str = "data/curriculum.json"
    candidates_path: str = "data/candidates.json"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
