"""문서 메타데이터 인메모리 저장소."""

from __future__ import annotations

from datetime import datetime, timezone
from threading import Lock

from backend.services.models import DocumentRecord, DocumentStatus


class DocumentStore:
    """문서 메타데이터를 프로세스 메모리에 보관합니다."""

    def __init__(self) -> None:
        self._records: dict[str, DocumentRecord] = {}
        self._lock = Lock()

    def add_processing(self, document_id: str, filename: str, file_type: str) -> DocumentRecord:
        """처리중 문서를 등록합니다."""

        record = DocumentRecord(
            document_id=document_id,
            filename=filename,
            file_type=file_type,
            status=DocumentStatus.PROCESSING,
        )
        with self._lock:
            self._records[document_id] = record
        return record

    def mark_indexed(self, document_id: str, page_count: int, chunk_count: int) -> DocumentRecord:
        """문서를 색인 완료 상태로 변경합니다."""

        with self._lock:
            record = self._records[document_id]
            record.status = DocumentStatus.INDEXED
            record.page_count = page_count
            record.chunk_count = chunk_count
            record.fail_reason = None
            record.indexed_at = datetime.now(timezone.utc)
            return record

    def mark_failed(self, document_id: str, reason: str) -> DocumentRecord:
        """문서를 실패 상태로 변경합니다."""

        with self._lock:
            record = self._records[document_id]
            record.status = DocumentStatus.FAILED
            record.fail_reason = reason
            return record

    def list(self) -> list[DocumentRecord]:
        """업로드 순서대로 문서 목록을 반환합니다."""

        with self._lock:
            return sorted(self._records.values(), key=lambda record: record.uploaded_at or datetime.min.replace(tzinfo=timezone.utc))

    def get(self, document_id: str) -> DocumentRecord | None:
        """문서 ID로 메타데이터를 조회합니다."""

        with self._lock:
            return self._records.get(document_id)

    def delete(self, document_id: str) -> bool:
        """문서 메타데이터를 삭제합니다."""

        with self._lock:
            return self._records.pop(document_id, None) is not None
