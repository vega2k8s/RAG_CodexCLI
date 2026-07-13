"""Upstage Groundness Check 연동 서비스."""

from __future__ import annotations

import os
from typing import Literal, Protocol

import requests

from backend.services.models import SearchResult


GroundnessDecision = Literal["grounded", "notGrounded", "notSure"]


class GroundnessError(RuntimeError):
    """근거 검증 실패."""


class GroundnessChecker(Protocol):
    """답변 근거 검증기 인터페이스."""

    def check(self, question: str, answer: str, contexts: list[SearchResult]) -> GroundnessDecision:
        """답변이 검색 근거에 기반하는지 판정합니다."""


class UpstageGroundnessChecker:
    """Upstage Groundness Check API 검증기."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base_url: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        self.api_base_url = api_base_url or os.getenv("UPSTAGE_API_BASE_URL", "https://api.upstage.ai/v1")
        self.timeout = timeout

    def check(self, question: str, answer: str, contexts: list[SearchResult]) -> GroundnessDecision:
        if not self.api_key:
            raise GroundnessError("missing_upstage_api_key")
        response = requests.post(
            f"{self.api_base_url}/groundness-check",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            json={
                "question": question,
                "answer": answer,
                "context": "\n\n".join(result.chunk.content for result in contexts),
            },
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise GroundnessError(f"groundness_check_failed:{response.status_code}")
        payload = response.json()
        raw_decision = payload.get("decision") or payload.get("result") or payload.get("groundedness")
        return _normalize_decision(str(raw_decision))


def _normalize_decision(value: str) -> GroundnessDecision:
    normalized = value.replace("_", "").replace("-", "").lower()
    if normalized in {"grounded", "true", "yes"}:
        return "grounded"
    if normalized in {"notgrounded", "false", "no"}:
        return "notGrounded"
    return "notSure"
