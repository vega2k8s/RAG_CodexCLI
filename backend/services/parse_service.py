"""Upstage Document Parse 연동 서비스."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Protocol

import requests

from backend.services.models import ParsedDocument


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".html", ".htm"}


class DocumentParseError(RuntimeError):
    """문서 파싱 실패."""


class DocumentParser(Protocol):
    """문서 파서 인터페이스."""

    def parse(self, content: bytes, filename: str, content_type: str | None = None) -> ParsedDocument:
        """파일 바이트를 Markdown 문서로 변환합니다."""


def validate_supported_file(filename: str) -> str:
    """지원하는 파일 확장자를 검증하고 파일 타입을 반환합니다."""

    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise DocumentParseError("unsupported_format")
    return suffix.removeprefix(".")


class UpstageDocumentParser:
    """Upstage Document Parse API 클라이언트."""

    def __init__(self, api_key: str | None = None, api_base_url: str | None = None, timeout: int = 60) -> None:
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        self.api_base_url = api_base_url or os.getenv("UPSTAGE_API_BASE_URL", "https://api.upstage.ai/v1")
        self.timeout = timeout

    def parse(self, content: bytes, filename: str, content_type: str | None = None) -> ParsedDocument:
        validate_supported_file(filename)
        if not self.api_key:
            raise DocumentParseError("missing_upstage_api_key")

        response = requests.post(
            f"{self.api_base_url}/document-ai/document-parse",
            headers={"Authorization": f"Bearer {self.api_key}"},
            files={"document": (filename, content, content_type or "application/octet-stream")},
            data={"output_format": "markdown"},
            timeout=self.timeout,
        )
        if response.status_code >= 400:
            raise DocumentParseError(f"parse_failed:{response.status_code}")

        markdown = self._extract_markdown(response)
        if not markdown.strip():
            raise DocumentParseError("parse_failed:empty_markdown")
        return ParsedDocument(markdown=markdown, page_count=self._estimate_page_count(response))

    def _extract_markdown(self, response: requests.Response) -> str:
        try:
            payload: Any = response.json()
        except ValueError:
            return response.text

        candidates = [
            payload.get("markdown"),
            payload.get("content", {}).get("markdown") if isinstance(payload.get("content"), dict) else None,
            payload.get("result", {}).get("markdown") if isinstance(payload.get("result"), dict) else None,
            payload.get("text"),
        ]
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.strip():
                return candidate
        return json.dumps(payload, ensure_ascii=False)

    def _estimate_page_count(self, response: requests.Response) -> int:
        try:
            payload: Any = response.json()
        except ValueError:
            return 1
        pages = payload.get("pages") if isinstance(payload, dict) else None
        if isinstance(pages, list) and pages:
            return len(pages)
        page_count = payload.get("page_count") if isinstance(payload, dict) else None
        return page_count if isinstance(page_count, int) and page_count > 0 else 1
