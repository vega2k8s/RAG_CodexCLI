"""LangGraph RAG 그래프 테스트."""

from __future__ import annotations

from backend.graph.graph import build_rag_graph
from backend.graph.nodes import RAGNodes
from backend.services.embedding_service import EMBEDDING_DIMENSION, FaissVectorStore
from backend.services.models import DocumentChunk


class FakeEmbedder:
    """테스트용 임베딩 클라이언트."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        return [[1.0] + [0.0] * (EMBEDDING_DIMENSION - 1) for _ in texts]


class FakeAnswerGenerator:
    """호출 횟수를 기록하는 테스트용 답변 생성기."""

    def __init__(self) -> None:
        self.calls: list[str] = []

    def generate(self, question: str, contexts: list) -> str:
        self.calls.append(question)
        return "3분기 매출은 10M입니다."

    def stream(self, answer: str):
        yield answer


class FakeGroundnessChecker:
    """지정된 판정을 순서대로 반환하는 테스트용 검증기."""

    def __init__(self, decisions: list[str]) -> None:
        self.decisions = decisions
        self.calls = 0

    def check(self, question: str, answer: str, contexts: list):
        decision = self.decisions[min(self.calls, len(self.decisions) - 1)]
        self.calls += 1
        return decision


def build_vector_store() -> FaissVectorStore:
    """검색 가능한 테스트 벡터 스토어를 생성합니다."""

    vector_store = FaissVectorStore()
    chunk = DocumentChunk(
        chunk_id="chunk-1",
        document_id="doc-1",
        document_name="sales.pdf",
        page=3,
        content="3분기 매출은 10M입니다.",
    )
    vector_store.add([chunk], [[1.0] + [0.0] * (EMBEDDING_DIMENSION - 1)])
    return vector_store


def test_rag_graph_passes_normal_grounded_path() -> None:
    vector_store = build_vector_store()
    answer_generator = FakeAnswerGenerator()
    groundness_checker = FakeGroundnessChecker(["grounded"])
    graph = build_rag_graph(
        RAGNodes(
            embedder=FakeEmbedder(),
            vector_store=vector_store,
            answer_generator=answer_generator,
            groundness_checker=groundness_checker,
        )
    )

    result = graph.invoke({"question": "3분기 매출은?", "max_retries": 2})

    assert result["grounded"] is True
    assert result["groundness_decision"] == "grounded"
    assert result["answer"] == "3분기 매출은 10M입니다."
    assert result["sources"][0]["documentName"] == "sales.pdf"
    assert answer_generator.calls == ["3분기 매출은?"]


def test_rag_graph_retries_when_groundness_fails_then_passes() -> None:
    vector_store = build_vector_store()
    answer_generator = FakeAnswerGenerator()
    groundness_checker = FakeGroundnessChecker(["notGrounded", "grounded"])
    graph = build_rag_graph(
        RAGNodes(
            embedder=FakeEmbedder(),
            vector_store=vector_store,
            answer_generator=answer_generator,
            groundness_checker=groundness_checker,
        )
    )

    result = graph.invoke({"question": "3분기 매출은?", "max_retries": 2})

    assert result["grounded"] is True
    assert result["retry_count"] == 1
    assert groundness_checker.calls == 2
    assert len(answer_generator.calls) == 2
    assert "문서에 명시된 근거만 사용해 다시 답하세요" in answer_generator.calls[1]


def test_rag_graph_returns_honest_message_when_no_context_found() -> None:
    graph = build_rag_graph(
        RAGNodes(
            embedder=FakeEmbedder(),
            vector_store=FaissVectorStore(),
            answer_generator=FakeAnswerGenerator(),
            groundness_checker=FakeGroundnessChecker(["grounded"]),
        )
    )

    result = graph.invoke({"question": "없는 내용은?", "max_retries": 1})

    assert result["grounded"] is False
    assert result["error"] == "no_relevant_context"
    assert "근거를 찾을 수 없음" in result["answer"]
