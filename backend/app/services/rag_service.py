from __future__ import annotations

import json
import logging

from app.config import settings
from app.services.embedding_service import EmbeddingService
from app.services.vector_store_service import VectorStoreService
from app.utils.llm_client import get_chat_client, get_chat_model

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """你是一个专业的文档问答助手。请严格基于提供的文档内容回答问题。
- 如果文档中有相关信息，请准确引用并标注来源。
- 如果文档中没有相关信息，请明确说明"文档中未找到相关信息"。
- 回答应清晰、准确、简洁。"""


class RAGService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = get_chat_client()
            cls._instance._chat_model = get_chat_model()
            cls._instance._embedding = EmbeddingService()
            cls._instance._vector = VectorStoreService()
        return cls._instance

    def __init__(self):
        pass  # initialization done in __new__

    def _trim_history(self, chat_history: list[dict] | None) -> list[dict]:
        if not chat_history:
            return []
        rounds = settings.MAX_CHAT_HISTORY_ROUNDS
        msgs_per_round = 2
        max_msgs = rounds * msgs_per_round
        trimmed = chat_history[-max_msgs:] if len(chat_history) > max_msgs else chat_history

        token_est = sum(len(m.get("content", "")) for m in trimmed)
        while token_est > settings.MAX_CONTEXT_TOKENS * 0.7 and len(trimmed) >= msgs_per_round:
            trimmed = trimmed[msgs_per_round:]
            token_est = sum(len(m.get("content", "")) for m in trimmed)
        return trimmed

    def _build_context_and_sources(
        self, query: str, document_ids: list[int] | None
    ) -> tuple[str, list[dict]]:
        query_embedding = self._embedding.embed(query)
        where = None
        if document_ids:
            where = {"document_id": {"$in": document_ids}}

        hits = self._vector.query(
            query_embedding,
            top_k=settings.TOP_K_RETRIEVAL,
            where_filter=where,
        )

        context_parts = []
        sources = []
        for h in hits:
            meta = h["metadata"]
            context_parts.append(
                f"[来源: {meta.get('filename', 'unknown')}, "
                f"片段 {meta.get('chunk_index', 0)}]\n{h['document']}"
            )
            sources.append({
                "document_id": meta.get("document_id", 0),
                "filename": meta.get("filename", "unknown"),
                "chunk_index": meta.get("chunk_index", 0),
                "excerpt": h["document"][:300],
                "relevance": round(1 - h.get("distance", 0), 4),
            })

        context = "\n\n---\n\n".join(context_parts) if context_parts else "暂无相关文档内容"
        return context, sources

    def _build_messages(self, query, context, history):
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(history)
        messages.append({
            "role": "user",
            "content": f"## 文档内容\n{context}\n\n## 问题\n{query}",
        })
        return messages

    def answer(
        self,
        query: str,
        document_ids: list[int] | None = None,
        chat_history: list[dict] | None = None,
    ) -> dict:
        context, sources = self._build_context_and_sources(query, document_ids)
        history = self._trim_history(chat_history)
        messages = self._build_messages(query, context, history)

        try:
            resp = self._client.chat.completions.create(
                model=self._chat_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
            )
            answer = resp.choices[0].message.content
        except Exception:
            logger.exception("LLM call failed")
            answer = "抱歉，生成回答时出现错误，请重试。"

        return {"answer": answer, "sources": sources}

    def answer_stream(
        self,
        query: str,
        document_ids: list[int] | None = None,
        chat_history: list[dict] | None = None,
    ):
        context, sources = self._build_context_and_sources(query, document_ids)
        history = self._trim_history(chat_history)
        messages = self._build_messages(query, context, history)

        try:
            stream = self._client.chat.completions.create(
                model=self._chat_model,
                messages=messages,
                temperature=0.3,
                max_tokens=2000,
                stream=True,
            )
            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield f"data: {json.dumps({'content': delta.content}, ensure_ascii=False)}\n\n"
            yield f"data: {json.dumps({'sources': sources}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
        except Exception:
            logger.exception("LLM stream failed")
            yield f"data: {json.dumps({'error': '生成回答时出现错误'}, ensure_ascii=False)}\n\n"
            yield "data: [DONE]\n\n"
