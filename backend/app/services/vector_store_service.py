from __future__ import annotations

import logging

import chromadb

from app.config import settings

logger = logging.getLogger(__name__)

COLLECTION_NAME = "document_chunks"

_client: chromadb.PersistentClient | None = None


def get_chroma_client() -> chromadb.PersistentClient:
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
    return _client


class VectorStoreService:
    def __init__(self):
        self._client = get_chroma_client()
        self._collection = self._client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict],
    ) -> None:
        self._collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas,
        )

    def query(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        where_filter: dict | None = None,
    ) -> list[dict]:
        kwargs = {
            "query_embeddings": [query_embedding],
            "n_results": top_k,
        }
        if where_filter:
            kwargs["where"] = where_filter

        results = self._collection.query(**kwargs)

        hits = []
        if results["ids"] and results["ids"][0]:
            for i, chroma_id in enumerate(results["ids"][0]):
                hits.append({
                    "id": chroma_id,
                    "document": results["documents"][0][i] if results["documents"] else "",
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0,
                })
        return hits

    def delete_by_document_id(self, document_id: int) -> None:
        try:
            self._collection.delete(
                where={"document_id": document_id}
            )
        except Exception:
            logger.exception("Failed to delete vectors for document %d", document_id)

    def delete_by_ids(self, ids: list[str]) -> None:
        if not ids:
            return
        try:
            self._collection.delete(ids=ids)
        except Exception:
            logger.exception("Failed to delete vectors by ids")

    def count(self) -> int:
        return self._collection.count()
