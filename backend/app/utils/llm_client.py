from openai import OpenAI

from app.config import settings


def get_chat_client() -> OpenAI:
    if settings.LLM_PROVIDER == "deepseek":
        return OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url=settings.DEEPSEEK_BASE_URL,
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_chat_model() -> str:
    if settings.LLM_PROVIDER == "deepseek":
        return settings.DEEPSEEK_MODEL
    return settings.OPENAI_MODEL


def get_embedding_client() -> OpenAI:
    if settings.EMBEDDING_PROVIDER == "dashscope":
        return OpenAI(
            api_key=settings.DASHSCOPE_API_KEY,
            base_url=settings.DASHSCOPE_BASE_URL,
        )
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def get_embedding_model() -> str:
    if settings.EMBEDDING_PROVIDER == "dashscope":
        return settings.DASHSCOPE_EMBEDDING_MODEL
    return settings.OPENAI_EMBEDDING_MODEL


def get_embedding_dim() -> int:
    if settings.EMBEDDING_PROVIDER == "dashscope":
        return settings.DASHSCOPE_EMBEDDING_DIM
    return settings.OPENAI_EMBEDDING_DIM
