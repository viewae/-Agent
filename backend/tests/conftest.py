import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

# Ensure backend/app is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["OPENAI_API_KEY"] = "sk-test"
os.environ["DEEPSEEK_API_KEY"] = "sk-test"
os.environ["DASHSCOPE_API_KEY"] = "sk-test"
os.environ["RATE_LIMIT_ENABLED"] = "false"


@pytest.fixture
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db():
    session = MagicMock()
    return session


@pytest.fixture
def mock_embedding():
    with patch("app.services.embedding_service.EmbeddingService") as m:
        instance = m.return_value
        instance.embed.return_value = [0.1] * 1536
        instance.embed_batch.return_value = [[0.1] * 1536]
        yield instance


@pytest.fixture
def mock_vector_store():
    with patch("app.services.vector_store_service.VectorStoreService") as m:
        instance = m.return_value
        instance.query.return_value = []
        instance.add_documents.return_value = None
        instance.delete_by_document_id.return_value = None
        instance.count.return_value = 0
        yield instance


@pytest.fixture
def mock_get_chroma():
    with patch("app.services.vector_store_service.get_chroma_client"):
        yield


@pytest.fixture
def mock_llm():
    with patch("app.utils.llm_client.get_chat_client") as m:
        client_mock = MagicMock()
        m.return_value = client_mock
        yield client_mock


@pytest.fixture
def app_with_mocks(mock_embedding, mock_vector_store, mock_get_chroma, mock_llm):
    from app.main import app
    yield app
