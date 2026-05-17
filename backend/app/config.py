import json
import os

from dotenv import load_dotenv

load_dotenv()


def _env_list(key: str, default: list[str]) -> list[str]:
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return json.loads(val)
    except json.JSONDecodeError:
        return [v.strip() for v in val.split(",")]


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "智能文档问答与任务执行 Agent")
    APP_VERSION: str = os.getenv("APP_VERSION", "0.1.0")
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", str(50 * 1024 * 1024)))
    ALLOWED_EXTENSIONS: list[str] = _env_list("ALLOWED_EXTENSIONS", ["pdf", "docx", "txt"])

    # LLM Provider: "openai" or "deepseek"
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openai")

    # OpenAI Chat
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # DeepSeek (OpenAI-compatible API)
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    # Embedding Provider: "openai" or "dashscope"
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "openai")

    # OpenAI Embedding
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    OPENAI_EMBEDDING_DIM: int = int(os.getenv("OPENAI_EMBEDDING_DIM", "1536"))

    # DashScope Embedding (阿里百炼，兼容 OpenAI API)
    DASHSCOPE_API_KEY: str = os.getenv("DASHSCOPE_API_KEY", "")
    DASHSCOPE_EMBEDDING_MODEL: str = os.getenv("DASHSCOPE_EMBEDDING_MODEL", "text-embedding-v2")
    DASHSCOPE_EMBEDDING_DIM: int = int(os.getenv("DASHSCOPE_EMBEDDING_DIM", "1536"))
    DASHSCOPE_BASE_URL: str = os.getenv("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")

    # ChromaDB
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Text Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    TOP_K_RETRIEVAL: int = int(os.getenv("TOP_K_RETRIEVAL", "5"))

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "true").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Chat History
    MAX_CHAT_HISTORY_ROUNDS: int = int(os.getenv("MAX_CHAT_HISTORY_ROUNDS", "5"))
    MAX_CONTEXT_TOKENS: int = int(os.getenv("MAX_CONTEXT_TOKENS", "6000"))

    CORS_ORIGINS: list[str] = _env_list("CORS_ORIGINS", ["http://localhost:5173"])


settings = Settings()
