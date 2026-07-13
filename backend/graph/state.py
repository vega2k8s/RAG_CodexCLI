"""LangGraph RAG 상태 정의."""

from __future__ import annotations

from typing import Literal, TypedDict

from backend.services.groundness_service import GroundnessDecision
from backend.services.models import SearchResult


QuestionDecision = Literal["valid", "invalid"]
RetrievalDecision = Literal["sufficient", "insufficient"]


class RAGState(TypedDict, total=False):
    """Self-Correcting RAG 그래프에서 공유하는 상태."""

    question: str
    original_question: str
    search_query: str
    rewritten_question: str
    contexts: list[SearchResult]
    answer: str
    question_decision: QuestionDecision
    retrieval_decision: RetrievalDecision
    groundness_decision: GroundnessDecision
    retry_count: int
    max_retries: int
    grounded: bool
    sources: list[dict[str, object]]
    error: str | None
