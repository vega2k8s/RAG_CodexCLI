"""Self-Correcting RAG 그래프 노드 구현."""

from __future__ import annotations

from typing import Protocol

from backend.graph.state import RAGState
from backend.services.embedding_service import EmbeddingClient, FaissVectorStore
from backend.services.groundness_service import GroundnessChecker
from backend.services.llm_service import AnswerGenerator


class QueryRewriter(Protocol):
    """질문과 검색 쿼리 재작성 인터페이스."""

    def rewrite_question(self, question: str, retry_count: int) -> str:
        """답변 검증 실패 후 질문을 재작성합니다."""

    def rewrite_search_query(self, question: str, retry_count: int) -> str:
        """검색 결과 부족 시 검색 쿼리를 재작성합니다."""


class SimpleQueryRewriter:
    """외부 LLM 없이 동작하는 기본 재작성기."""

    def rewrite_question(self, question: str, retry_count: int) -> str:
        return f"{question}\n문서에 명시된 근거만 사용해 다시 답하세요. 재시도 {retry_count}회."

    def rewrite_search_query(self, question: str, retry_count: int) -> str:
        return f"{question} 핵심 근거 재검색 {retry_count}"


class RAGNodes:
    """LangGraph에 등록할 8개 노드 묶음."""

    def __init__(
        self,
        embedder: EmbeddingClient,
        vector_store: FaissVectorStore,
        answer_generator: AnswerGenerator,
        groundness_checker: GroundnessChecker,
        query_rewriter: QueryRewriter | None = None,
        top_k: int = 4,
        min_score: float = 0.0,
    ) -> None:
        self.embedder = embedder
        self.vector_store = vector_store
        self.answer_generator = answer_generator
        self.groundness_checker = groundness_checker
        self.query_rewriter = query_rewriter or SimpleQueryRewriter()
        self.top_k = top_k
        self.min_score = min_score

    def assess_question(self, state: RAGState) -> RAGState:
        """질문이 비어 있지 않은지 평가합니다."""

        question = state.get("question", "").strip()
        if not question:
            return {"question_decision": "invalid", "error": "empty_question"}
        return {
            "question": question,
            "original_question": state.get("original_question") or question,
            "search_query": state.get("search_query") or question,
            "question_decision": "valid",
            "retry_count": state.get("retry_count", 0),
        }

    def rewrite_question(self, state: RAGState) -> RAGState:
        """Groundness 실패 후 답변용 질문을 재작성합니다."""

        retry_count = state.get("retry_count", 0) + 1
        rewritten = self.query_rewriter.rewrite_question(state["original_question"], retry_count)
        return {"question": rewritten, "rewritten_question": rewritten, "search_query": rewritten, "retry_count": retry_count}

    def retrieve_documents(self, state: RAGState) -> RAGState:
        """검색 쿼리로 관련 문서 청크를 검색합니다."""

        query = state.get("search_query") or state["question"]
        query_embedding = self.embedder.embed_texts([query])[0]
        contexts = self.vector_store.search(query_embedding, top_k=self.top_k, min_score=self.min_score)
        return {"contexts": contexts}

    def grade_retrieval(self, state: RAGState) -> RAGState:
        """검색 결과가 답변 생성에 충분한지 평가합니다."""

        contexts = state.get("contexts", [])
        if contexts:
            return {"retrieval_decision": "sufficient", "error": None}
        return {"retrieval_decision": "insufficient", "error": "no_relevant_context"}

    def rewrite_search_query(self, state: RAGState) -> RAGState:
        """검색 결과 부족 시 검색 쿼리를 재작성합니다."""

        retry_count = state.get("retry_count", 0) + 1
        rewritten = self.query_rewriter.rewrite_search_query(state["original_question"], retry_count)
        return {"search_query": rewritten, "retry_count": retry_count}

    def generate_answer(self, state: RAGState) -> RAGState:
        """검색 근거를 사용해 답변을 생성합니다."""

        answer = self.answer_generator.generate(state["question"], state.get("contexts", []))
        return {"answer": answer}

    def evaluate_answer(self, state: RAGState) -> RAGState:
        """생성 답변의 Groundness를 검증합니다."""

        decision = self.groundness_checker.check(
            state.get("original_question") or state["question"],
            state.get("answer", ""),
            state.get("contexts", []),
        )
        return {
            "groundness_decision": decision,
            "grounded": decision == "grounded",
            "sources": _build_sources(state.get("contexts", [])),
        }

    def diagnose_failure(self, state: RAGState) -> RAGState:
        """재시도 초과 또는 입력 오류 시 정직한 실패 응답을 만듭니다."""

        error = state.get("error") or "groundness_failed"
        if error == "empty_question":
            answer = "질문을 입력해 주세요."
        elif error == "no_relevant_context":
            answer = "근거를 찾을 수 없음: 색인된 문서에서 관련 내용을 찾지 못했습니다."
        else:
            answer = "확실한 답변을 찾지 못했습니다. 제공된 문서 근거만으로는 확인 불가합니다."
        return {
            "answer": answer,
            "grounded": False,
            "groundness_decision": state.get("groundness_decision", "notGrounded"),
            "sources": _build_sources(state.get("contexts", [])),
            "error": error,
        }


def _build_sources(contexts: list) -> list[dict[str, object]]:
    seen: set[tuple[str, int]] = set()
    sources: list[dict[str, object]] = []
    for result in contexts:
        key = (result.chunk.document_name, result.chunk.page)
        if key in seen:
            continue
        seen.add(key)
        sources.append(
            {
                "documentId": result.chunk.document_id,
                "documentName": result.chunk.document_name,
                "page": result.chunk.page,
                "chunkId": result.chunk.chunk_id,
                "score": result.score,
            }
        )
    return sources
