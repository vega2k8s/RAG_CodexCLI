"""Solar Pro 3 답변 생성 서비스."""

from __future__ import annotations

import os
from typing import Iterable, Protocol

import requests

from backend.services.models import SearchResult


class AnswerGenerationError(RuntimeError):
    """답변 생성 실패."""


class AnswerGenerator(Protocol):
    """RAG 답변 생성기 인터페이스."""

    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        """질문과 검색 근거를 바탕으로 답변을 생성합니다."""

    def stream(self, answer: str) -> Iterable[str]:
        """완성된 답변을 스트리밍 토큰 형태로 변환합니다."""


class UpstageAnswerGenerator:
    """OpenAI 호환 Chat Completions 형식의 Solar 답변 생성기."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base_url: str | None = None,
        model: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        self.api_base_url = api_base_url or os.getenv("UPSTAGE_API_BASE_URL", "https://api.upstage.ai/v1")
        self.model = model or os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro3-preview")
        self.timeout = timeout

    def generate(self, question: str, contexts: list[SearchResult]) -> str:
        if not self.api_key:
            raise AnswerGenerationError("missing_upstage_api_key")
        response = requests.post(
            f"{self.api_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._system_prompt()},
                    {"role": "user", "content": self._user_prompt(question, contexts)},
                ],
                "temperature": 0.0,
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise AnswerGenerationError(f"answer_generation_failed:{response.status_code}")
        return response.json()["choices"][0]["message"]["content"].strip()

    def stream(self, answer: str) -> Iterable[str]:
        for token in answer.split(" "):
            yield token + " "

    def _system_prompt(self) -> str:
        return (
            "당신은 문서 기반 RAG Q&A 도우미입니다. "
            "반드시 제공된 근거 안에서만 답하고, 근거가 부족하면 확인 불가라고 답하세요."
        )

    def _user_prompt(self, question: str, contexts: list[SearchResult]) -> str:
        context_text = "\n\n".join(
            f"[{index}] {result.chunk.document_name} p.{result.chunk.page}\n{result.chunk.content}"
            for index, result in enumerate(contexts, start=1)
        )
        return f"질문:\n{question}\n\n근거:\n{context_text}\n\n답변:"
