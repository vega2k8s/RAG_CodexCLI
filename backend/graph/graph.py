"""LangGraph Self-Correcting RAG 그래프 조립."""

from __future__ import annotations

import os
from typing import Literal

from langgraph.graph import END, START, StateGraph

from backend.graph.nodes import RAGNodes
from backend.graph.state import RAGState
from backend.services.embedding_service import FaissVectorStore, UpstageEmbeddingClient
from backend.services.groundness_service import UpstageGroundnessChecker
from backend.services.llm_service import UpstageAnswerGenerator
from backend.services.pipeline import default_pipeline


def route_after_question_assessment(state: RAGState) -> Literal["retrieve_documents", "diagnose_failure"]:
    """질문 평가 결과에 따라 검색 또는 실패 진단으로 분기합니다."""

    if state.get("question_decision") == "valid":
        return "retrieve_documents"
    return "diagnose_failure"


def route_after_retrieval_grade(state: RAGState) -> Literal["generate_answer", "rewrite_search_query", "diagnose_failure"]:
    """검색 결과 평가 후 답변 생성, 재검색, 실패 진단으로 분기합니다."""

    if state.get("retrieval_decision") == "sufficient":
        return "generate_answer"
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "rewrite_search_query"
    return "diagnose_failure"


def route_after_groundness(state: RAGState) -> Literal["end", "rewrite_question", "diagnose_failure"]:
    """Groundness 판정 후 종료, 재답변, 실패 진단으로 분기합니다."""

    if state.get("groundness_decision") == "grounded":
        return "end"
    if state.get("retry_count", 0) < state.get("max_retries", 2):
        return "rewrite_question"
    return "diagnose_failure"


def build_rag_graph(nodes: RAGNodes):
    """8개 노드와 조건부 엣지를 가진 RAG 그래프를 생성합니다."""

    workflow = StateGraph(RAGState)
    workflow.add_node("assess_question", nodes.assess_question)
    workflow.add_node("rewrite_question", nodes.rewrite_question)
    workflow.add_node("retrieve_documents", nodes.retrieve_documents)
    workflow.add_node("grade_retrieval", nodes.grade_retrieval)
    workflow.add_node("rewrite_search_query", nodes.rewrite_search_query)
    workflow.add_node("generate_answer", nodes.generate_answer)
    workflow.add_node("evaluate_answer", nodes.evaluate_answer)
    workflow.add_node("diagnose_failure", nodes.diagnose_failure)

    workflow.add_edge(START, "assess_question")
    workflow.add_conditional_edges(
        "assess_question",
        route_after_question_assessment,
        {"retrieve_documents": "retrieve_documents", "diagnose_failure": "diagnose_failure"},
    )
    workflow.add_edge("retrieve_documents", "grade_retrieval")
    workflow.add_conditional_edges(
        "grade_retrieval",
        route_after_retrieval_grade,
        {
            "generate_answer": "generate_answer",
            "rewrite_search_query": "rewrite_search_query",
            "diagnose_failure": "diagnose_failure",
        },
    )
    workflow.add_edge("rewrite_search_query", "retrieve_documents")
    workflow.add_edge("generate_answer", "evaluate_answer")
    workflow.add_conditional_edges(
        "evaluate_answer",
        route_after_groundness,
        {"end": END, "rewrite_question": "rewrite_question", "diagnose_failure": "diagnose_failure"},
    )
    workflow.add_edge("rewrite_question", "retrieve_documents")
    workflow.add_edge("diagnose_failure", END)
    return workflow.compile()


def invoke_rag(question: str, max_retries: int | None = None) -> RAGState:
    """기본 파이프라인 색인을 사용해 RAG 그래프를 실행합니다."""

    nodes = RAGNodes(
        embedder=UpstageEmbeddingClient(),
        vector_store=default_pipeline.vector_store,
        answer_generator=UpstageAnswerGenerator(),
        groundness_checker=UpstageGroundnessChecker(),
    )
    graph = build_rag_graph(nodes)
    retry_limit = max_retries if max_retries is not None else int(os.getenv("MAX_RETRY_COUNT", "2"))
    return graph.invoke({"question": question, "max_retries": retry_limit})


def build_default_rag_graph(vector_store: FaissVectorStore | None = None):
    """운영 기본 의존성으로 RAG 그래프를 생성합니다."""

    nodes = RAGNodes(
        embedder=UpstageEmbeddingClient(),
        vector_store=vector_store or default_pipeline.vector_store,
        answer_generator=UpstageAnswerGenerator(),
        groundness_checker=UpstageGroundnessChecker(),
    )
    return build_rag_graph(nodes)
