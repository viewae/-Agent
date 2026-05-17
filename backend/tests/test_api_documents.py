import io

from fastapi.testclient import TestClient


class TestDocumentUpload:
    def test_upload_txt_success(self, client: TestClient, mock_embedding, mock_vector_store, mock_get_chroma):
        resp = client.post(
            "/api/documents/upload",
            files={"file": ("test.txt", io.BytesIO(b"Hello World"), "text/plain")},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["code"] == 201
        assert data["data"]["filename"] == "test.txt"
        assert data["data"]["file_type"] == "txt"

    def test_upload_invalid_extension(self, client: TestClient, mock_embedding, mock_vector_store, mock_get_chroma):
        resp = client.post(
            "/api/documents/upload",
            files={"file": ("test.exe", io.BytesIO(b"bad"), "application/octet-stream")},
        )
        assert resp.status_code == 422

    def test_upload_empty_filename(self, client: TestClient):
        resp = client.post(
            "/api/documents/upload",
            files={"file": ("", io.BytesIO(b""), "text/plain")},
        )
        assert resp.status_code == 422


class TestDocumentList:
    def test_list_empty(self, client: TestClient, mock_embedding, mock_vector_store, mock_get_chroma):
        resp = client.get("/api/documents/list")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data["data"]
        assert "total" in data["data"]

    def test_list_with_data(self, client: TestClient, mock_embedding, mock_vector_store, mock_get_chroma):
        client.post("/api/documents/upload", files={"file": ("a.txt", io.BytesIO(b"test"), "text/plain")})
        resp = client.get("/api/documents/list")
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["total"] >= 1


class TestDocumentDelete:
    def test_delete_not_found(self, client: TestClient):
        resp = client.delete("/api/documents/9999")
        assert resp.status_code == 404
