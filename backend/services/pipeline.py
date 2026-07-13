"""문서 업로드부터 색인까지 연결하는 파이프라인."""

from __future__ import annotations

import os
import uuid

from backend.services.document_store import DocumentStore
from backend.services.embedding_service import EmbeddingClient, FaissVectorStore, UpstageEmbeddingClient, make_chunks
from backend.services.models import DocumentRecord
from backend.services.parse_service import DocumentParser, UpstageDocumentParser, validate_supported_file


class DocumentPipeline:
    """문서 파싱, 청크 분할, 임베딩, 색인을 순차 실행합니다."""

    def __init__(
        self,
        parser: DocumentParser,
        embedder: EmbeddingClient,
        store: DocumentStore | None = None,
        vector_store: FaissVectorStore | None = None,
    ) -> None:
        self.parser = parser
        self.embedder = embedder
        self.store = store or DocumentStore()
        self.vector_store = vector_store or FaissVectorStore()

    def submit(self, filename: str, content: bytes, content_type: str | None = None) -> DocumentRecord:
        """문서를 등록하고 즉시 파싱·색인 파이프라인을 실행합니다."""

        file_type = validate_supported_file(filename)
        document_id = str(uuid.uuid4())
        record = self.store.add_processing(document_id=document_id, filename=filename, file_type=file_type)
        try:
            parsed = self.parser.parse(content, filename, content_type)
            chunks = make_chunks(document_id, filename, parsed.markdown)
            embeddings = self.embedder.embed_texts([chunk.content for chunk in chunks])
            self.vector_store.add(chunks, embeddings)
            return self.store.mark_indexed(document_id, parsed.page_count, len(chunks))
        except Exception as exc:
            self.store.mark_failed(document_id, str(exc))
            raise

    def create_processing_record(self, filename: str) -> DocumentRecord:
        """백그라운드 처리 전 문서 메타데이터를 먼저 생성합니다."""

        file_type = validate_supported_file(filename)
        return self.store.add_processing(document_id=str(uuid.uuid4()), filename=filename, file_type=file_type)

    def process_existing(self, document_id: str, content: bytes, content_type: str | None = None) -> None:
        """이미 등록된 문서를 파싱·색인합니다."""

        record = self.store.get(document_id)
        if record is None:
            return
        try:
            parsed = self.parser.parse(content, record.filename, content_type)
            chunks = make_chunks(document_id, record.filename, parsed.markdown)
            embeddings = self.embedder.embed_texts([chunk.content for chunk in chunks])
            self.vector_store.add(chunks, embeddings)
            self.store.mark_indexed(document_id, parsed.page_count, len(chunks))
        except Exception as exc:
            self.store.mark_failed(document_id, str(exc))

    def delete(self, document_id: str) -> bool:
        """문서 메타데이터와 벡터를 함께 삭제합니다."""

        deleted = self.store.delete(document_id)
        if deleted:
            self.vector_store.delete_document(document_id)
        return deleted


def build_default_pipeline() -> DocumentPipeline:
    """운영 기본 파이프라인을 생성합니다."""

    dimension = int(os.getenv("VECTOR_DIMENSION", "4096"))
    return DocumentPipeline(
        parser=UpstageDocumentParser(),
        embedder=UpstageEmbeddingClient(),
        vector_store=FaissVectorStore(dimension=dimension),
    )


default_pipeline = build_default_pipeline()
