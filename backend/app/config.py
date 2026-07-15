import os
from typing import Union

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _env_list_validator(v: Union[str, list[str]]) -> list[str]:
    if isinstance(v, list):
        return v
    import json
    try:
        return json.loads(v)
    except (json.JSONDecodeError, TypeError):
        return [s.strip() for s in v.split(",")]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "智能文档问答与任务执行 Agent"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    DATABASE_URL: str = "sqlite:///./app.db"

    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024
    ALLOWED_EXTENSIONS: list[str] = ["pdf", "docx", "txt"]

    # LLM Provider: "openai" or "deepseek"
    LLM_PROVIDER: str = "openai"

    # OpenAI Chat
    OPENAI_MODEL: str = "gpt-4o"

    # DeepSeek (OpenAI-compatible API)
    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_MODEL: str = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"

    # Embedding Provider: "openai" or "dashscope"
    EMBEDDING_PROVIDER: str = "openai"

    # OpenAI Embedding
    OPENAI_API_KEY: str = ""
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"
    OPENAI_EMBEDDING_DIM: int = 1536

    # DashScope Embedding (阿里百炼，兼容 OpenAI API)
    DASHSCOPE_API_KEY: str = ""
    DASHSCOPE_EMBEDDING_MODEL: str = "text-embedding-v2"
    DASHSCOPE_EMBEDDING_DIM: int = 1536
    DASHSCOPE_BASE_URL: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"

    # ChromaDB
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # Text Chunking
    CHUNK_SIZE: int = 500
    CHUNK_OVERLAP: int = 100
    TOP_K_RETRIEVAL: int = 5

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60

    # Chat History
    MAX_CHAT_HISTORY_ROUNDS: int = 5
    MAX_CONTEXT_TOKENS: int = 6000

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


settings = Settings()
