"""Q&A 채팅 API."""

from __future__ import annotations

import json
import os
from collections.abc import Callable, Iterable
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.graph.graph import invoke_rag
from backend.graph.state import RAGState
from backend.services.llm_service import UpstageAnswerGenerator


router = APIRouter(prefix="/api/chat", tags=["chat"])

RAGInvoker = Callable[[str, int | None], RAGState]


class ChatRequest(BaseModel):
    """채팅 질문 요청."""

    question: str
    conversationId: str | None = None


def get_rag_invoker() -> RAGInvoker:
    """RAG 그래프 실행 의존성을 반환합니다."""

    return invoke_rag


def get_answer_streamer() -> UpstageAnswerGenerator:
    """답변 스트리밍 변환기를 반환합니다."""

    return UpstageAnswerGenerator()


@router.post("")
def chat(
    request: ChatRequest,
    rag_invoker: RAGInvoker = Depends(get_rag_invoker),
    answer_streamer: UpstageAnswerGenerator = Depends(get_answer_streamer),
) -> StreamingResponse:
    """질문을 받아 RAG 그래프를 실행하고 SSE로 답변을 스트리밍합니다."""

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail={"error": "empty_question"})

    max_retries = int(os.getenv("MAX_RETRY_COUNT", "2"))

    def event_stream() -> Iterable[str]:
        yield _sse_event("status", {"message": "rag_started"})
        try:
            result = rag_invoker(question, max_retries)
        except Exception as exc:
            yield _sse_event("error", {"error": "rag_failed", "detail": str(exc)})
            return

        answer = str(result.get("answer", ""))
        for token in answer_streamer.stream(answer):
            yield _sse_event("token", {"token": token})

        yield _sse_event(
            "final",
            {
                "answer": answer,
                "sources": result.get("sources", []),
                "grounded": bool(result.get("grounded", False)),
                "groundness": result.get("groundness_decision"),
                "conversationId": request.conversationId,
            },
        )

    return StreamingResponse(event_stream(), media_type="text/event-stream")


def _sse_event(event: str, payload: dict[str, Any]) -> str:
    """SSE 이벤트 문자열을 생성합니다."""

    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"
