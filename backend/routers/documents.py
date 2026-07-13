"""문서 업로드, 목록, 삭제 API."""

from __future__ import annotations

import os
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, Response, UploadFile, status
from pydantic import BaseModel

from backend.services.models import DocumentRecord, DocumentStatus
from backend.services.parse_service import DocumentParseError
from backend.services.pipeline import DocumentPipeline, default_pipeline


router = APIRouter(prefix="/api/documents", tags=["documents"])


class DocumentCreateResponse(BaseModel):
    """문서 업로드 응답."""

    documentId: str
    status: DocumentStatus


class DocumentListItem(BaseModel):
    """문서 목록 응답 항목."""

    documentId: str
    filename: str
    status: DocumentStatus
    pageCount: int
    chunkCount: int
    failReason: str | None
    uploadedAt: datetime
    indexedAt: datetime | None


def get_document_pipeline() -> DocumentPipeline:
    """문서 파이프라인 의존성을 반환합니다."""

    return default_pipeline


def to_list_item(record: DocumentRecord) -> DocumentListItem:
    """내부 문서 모델을 API 응답 모델로 변환합니다."""

    if record.uploaded_at is None:
        raise RuntimeError("uploaded_at is required")
    return DocumentListItem(
        documentId=record.document_id,
        filename=record.filename,
        status=record.status,
        pageCount=record.page_count,
        chunkCount=record.chunk_count,
        failReason=record.fail_reason,
        uploadedAt=record.uploaded_at,
        indexedAt=record.indexed_at,
    )


@router.post("", response_model=DocumentCreateResponse, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    pipeline: DocumentPipeline = Depends(get_document_pipeline),
) -> DocumentCreateResponse:
    """문서 업로드 후 파싱·색인 작업을 시작합니다."""

    content = await file.read()
    max_upload_mb = int(os.getenv("MAX_UPLOAD_MB", "20"))
    if len(content) > max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=400, detail={"error": "file_too_large"})
    try:
        record = pipeline.create_processing_record(file.filename or "document")
    except DocumentParseError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc

    background_tasks.add_task(pipeline.process_existing, record.document_id, content, file.content_type)
    return DocumentCreateResponse(documentId=record.document_id, status=record.status)


@router.get("", response_model=list[DocumentListItem])
def list_documents(pipeline: DocumentPipeline = Depends(get_document_pipeline)) -> list[DocumentListItem]:
    """색인 문서 목록을 조회합니다."""

    return [to_list_item(record) for record in pipeline.store.list()]


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_document(document_id: str, pipeline: DocumentPipeline = Depends(get_document_pipeline)) -> Response:
    """문서 메타데이터와 벡터를 삭제합니다."""

    if not pipeline.delete(document_id):
        raise HTTPException(status_code=404, detail={"error": "document_not_found"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
