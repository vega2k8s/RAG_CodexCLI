"""문서 파싱·색인 파이프라인 테스트."""

from __future__ import annotations

import pytest

from backend.services.embedding_service import EMBEDDING_DIMENSION, FaissVectorStore
from backend.services.models import DocumentStatus, ParsedDocument
from backend.services.parse_service import DocumentParseError
from backend.services.pipeline import DocumentPipeline


class FakeParser:
    """테스트용 문서 파서."""

    def parse(self, content: bytes, filename: str, content_type: str | None = None) -> ParsedDocument:
        if filename.endswith(".broken"):
            raise DocumentParseError("parse_failed")
        return ParsedDocument(markdown="# 제목\n\n| 분기 | 매출 |\n|---|---|\n| Q1 | 10M |", page_count=1)


class FakeEmbedder:
    """테스트용 임베딩 클라이언트."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (EMBEDDING_DIMENSION - 1) for _ in texts]


def build_pipeline() -> DocumentPipeline:
    """테스트 파이프라인을 생성합니다."""

    return DocumentPipeline(parser=FakeParser(), embedder=FakeEmbedder(), vector_store=FaissVectorStore())


def test_submit_parses_chunks_embeds_and_indexes_document() -> None:
    pipeline = build_pipeline()

    record = pipeline.submit("sample.pdf", b"%PDF-1.4", "application/pdf")

    assert record.status == DocumentStatus.INDEXED
    assert record.page_count == 1
    assert record.chunk_count == 1
    assert pipeline.vector_store.chunk_count == 1


def test_duplicate_uploads_are_managed_as_distinct_documents() -> None:
    pipeline = build_pipeline()

    first = pipeline.submit("same.pdf", b"first", "application/pdf")
    second = pipeline.submit("same.pdf", b"second", "application/pdf")

    assert first.document_id != second.document_id
    assert len(pipeline.store.list()) == 2
    assert pipeline.vector_store.chunk_count == 2


def test_delete_document_removes_vectors() -> None:
    pipeline = build_pipeline()
    record = pipeline.submit("sample.pdf", b"%PDF-1.4", "application/pdf")

    deleted = pipeline.delete(record.document_id)

    assert deleted is True
    assert pipeline.store.get(record.document_id) is None
    assert pipeline.vector_store.chunk_count == 0


def test_unsupported_format_fails_before_indexing() -> None:
    pipeline = build_pipeline()

    with pytest.raises(DocumentParseError, match="unsupported_format"):
        pipeline.submit("sample.exe", b"binary", "application/octet-stream")

    assert pipeline.vector_store.chunk_count == 0
