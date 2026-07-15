from typing import Optional, Union

from openai import OpenAI

from app.config import settings

# Singleton caches — avoid creating new OpenAI clients on every request
_chat_client: Optional[OpenAI] = None
_chat_model: Optional[str] = None
_embedding_client: Optional[OpenAI] = None
_embedding_model: Optional[str] = None
_embedding_dim: Optional[int] = None


def get_chat_client() -> OpenAI:
    global _chat_client
    if _chat_client is None:
        if settings.LLM_PROVIDER == "deepseek":
            _chat_client = OpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL,
            )
        else:
            _chat_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _chat_client


def get_chat_model() -> str:
    global _chat_model
    if _chat_model is None:
        if settings.LLM_PROVIDER == "deepseek":
            _chat_model = settings.DEEPSEEK_MODEL
        else:
            _chat_model = settings.OPENAI_MODEL
    return _chat_model


def get_embedding_client() -> OpenAI:
    global _embedding_client
    if _embedding_client is None:
        if settings.EMBEDDING_PROVIDER == "dashscope":
            _embedding_client = OpenAI(
                api_key=settings.DASHSCOPE_API_KEY,
                base_url=settings.DASHSCOPE_BASE_URL,
            )
        else:
            _embedding_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _embedding_client


def get_embedding_model() -> str:
    global _embedding_model
    if _embedding_model is None:
        if settings.EMBEDDING_PROVIDER == "dashscope":
            _embedding_model = settings.DASHSCOPE_EMBEDDING_MODEL
        else:
            _embedding_model = settings.OPENAI_EMBEDDING_MODEL
    return _embedding_model


def get_embedding_dim() -> int:
    global _embedding_dim
    if _embedding_dim is None:
        if settings.EMBEDDING_PROVIDER == "dashscope":
            _embedding_dim = settings.DASHSCOPE_EMBEDDING_DIM
        else:
            _embedding_dim = settings.OPENAI_EMBEDDING_DIM
    return _embedding_dim
