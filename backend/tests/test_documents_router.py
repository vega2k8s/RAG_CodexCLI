"""문서 API 테스트."""

from __future__ import annotations

from fastapi.testclient import TestClient

from backend.main import app
from backend.routers.documents import get_document_pipeline
from backend.services.embedding_service import EMBEDDING_DIMENSION, FaissVectorStore
from backend.services.models import ParsedDocument
from backend.services.pipeline import DocumentPipeline


class FakeParser:
    """테스트용 문서 파서."""

    def parse(self, content: bytes, filename: str, content_type: str | None = None) -> ParsedDocument:
        return ParsedDocument(markdown="| 항목 | 값 |\n|---|---|\n| 샘플 | 1 |", page_count=1)


class FakeEmbedder:
    """테스트용 임베딩 클라이언트."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (EMBEDDING_DIMENSION - 1) for _ in texts]


def make_client() -> tuple[TestClient, DocumentPipeline]:
    """테스트 클라이언트와 격리된 파이프라인을 생성합니다."""

    pipeline = DocumentPipeline(parser=FakeParser(), embedder=FakeEmbedder(), vector_store=FaissVectorStore())
    app.dependency_overrides[get_document_pipeline] = lambda: pipeline
    return TestClient(app), pipeline


def test_upload_supported_formats_and_list_indexed_documents() -> None:
    client, pipeline = make_client()

    for filename in ("sample.pdf", "sample.docx", "sample.html"):
        response = client.post("/api/documents", files={"file": (filename, b"content", "application/octet-stream")})
        assert response.status_code == 202
        assert response.json()["status"] == "processing"

    documents = client.get("/api/documents").json()
    assert [document["status"] for document in documents] == ["indexed", "indexed", "indexed"]
    assert pipeline.vector_store.chunk_count == 3
    app.dependency_overrides.clear()


def test_delete_document_removes_indexed_vectors() -> None:
    client, pipeline = make_client()
    response = client.post("/api/documents", files={"file": ("sample.pdf", b"content", "application/pdf")})
    document_id = response.json()["documentId"]

    delete_response = client.delete(f"/api/documents/{document_id}")

    assert delete_response.status_code == 204
    assert client.get("/api/documents").json() == []
    assert pipeline.vector_store.chunk_count == 0
    app.dependency_overrides.clear()


def test_upload_rejects_unsupported_format() -> None:
    client, _pipeline = make_client()

    response = client.post("/api/documents", files={"file": ("sample.exe", b"binary", "application/octet-stream")})

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "unsupported_format"
    app.dependency_overrides.clear()
