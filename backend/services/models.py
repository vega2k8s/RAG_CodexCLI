"""문서 파이프라인에서 공유하는 데이터 모델."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum


class DocumentStatus(str, Enum):
    """문서 처리 상태."""

    PROCESSING = "processing"
    INDEXED = "indexed"
    FAILED = "failed"


@dataclass(slots=True)
class ParsedDocument:
    """파싱된 문서 결과."""

    markdown: str
    page_count: int


@dataclass(slots=True)
class DocumentRecord:
    """문서 메타데이터."""

    document_id: str
    filename: str
    file_type: str
    status: DocumentStatus
    page_count: int = 0
    chunk_count: int = 0
    fail_reason: str | None = None
    uploaded_at: datetime | None = None
    indexed_at: datetime | None = None

    def __post_init__(self) -> None:
        if self.uploaded_at is None:
            self.uploaded_at = datetime.now(timezone.utc)


@dataclass(slots=True)
class DocumentChunk:
    """벡터 스토어에 저장되는 문서 청크."""

    chunk_id: str
    document_id: str
    document_name: str
    page: int
    content: str


@dataclass(slots=True)
class SearchResult:
    """검색된 문서 청크와 유사도 점수."""

    chunk: DocumentChunk
    score: float
