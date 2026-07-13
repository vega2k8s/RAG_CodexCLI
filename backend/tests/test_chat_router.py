"""채팅 API 테스트."""

from __future__ import annotations

import json

from fastapi.testclient import TestClient

from backend.main import app
from backend.routers.chat import get_answer_streamer, get_rag_invoker


class FakeAnswerStreamer:
    """테스트용 답변 스트리밍 변환기."""

    def stream(self, answer: str):
        for token in answer.split():
            yield token


def fake_rag_invoker(question: str, max_retries: int | None):
    """테스트용 RAG 실행 함수."""

    return {
        "answer": f"{question} 답변",
        "sources": [{"documentName": "sales.pdf", "page": 3}],
        "grounded": True,
        "groundness_decision": "grounded",
    }


def make_client() -> TestClient:
    """의존성을 격리한 테스트 클라이언트를 생성합니다."""

    app.dependency_overrides[get_rag_invoker] = lambda: fake_rag_invoker
    app.dependency_overrides[get_answer_streamer] = lambda: FakeAnswerStreamer()
    return TestClient(app)


def test_chat_streams_tokens_and_final_sources() -> None:
    client = make_client()

    with client.stream("POST", "/api/chat", json={"question": "3분기 매출은?", "conversationId": "conv-1"}) as response:
        body = response.read().decode("utf-8")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")
    assert "event: token" in body
    assert "event: final" in body
    final_payload = _event_payload(body, "final")
    assert final_payload["answer"] == "3분기 매출은? 답변"
    assert final_payload["sources"] == [{"documentName": "sales.pdf", "page": 3}]
    assert final_payload["grounded"] is True
    assert final_payload["conversationId"] == "conv-1"
    app.dependency_overrides.clear()


def test_chat_rejects_empty_question() -> None:
    client = make_client()

    response = client.post("/api/chat", json={"question": "   "})

    assert response.status_code == 400
    assert response.json()["detail"]["error"] == "empty_question"
    app.dependency_overrides.clear()


def _event_payload(body: str, event_name: str) -> dict:
    lines = body.splitlines()
    for index, line in enumerate(lines):
        if line == f"event: {event_name}":
            return json.loads(lines[index + 1].removeprefix("data: "))
    raise AssertionError(f"{event_name} event not found")
