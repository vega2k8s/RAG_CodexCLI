"""Phase 0 사전 기술 검증 스크립트.

실행 전 `.env`에 `UPSTAGE_API_KEY`가 있어야 합니다.
외부 Upstage API를 실제 호출하므로 비용과 네트워크 정책을 확인한 뒤 실행하세요.
"""

from __future__ import annotations

import importlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv


API_BASE_URL = os.getenv("UPSTAGE_API_BASE_URL", "https://api.upstage.ai/v1")
CHAT_MODEL = os.getenv("UPSTAGE_CHAT_MODEL", "solar-pro3")
EMBEDDING_MODEL = os.getenv("UPSTAGE_EMBEDDING_MODEL", "solar-embedding-1-large-query")
GROUNDNESS_PATH = os.getenv("UPSTAGE_GROUNDNESS_PATH")


def require_import(module_name: str) -> None:
    importlib.import_module(module_name)
    print(f"OK import {module_name}")


def headers(api_key: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {api_key}"}


def raise_for_api_error(response: requests.Response) -> None:
    if response.status_code >= 400:
        body = response.text[:1000]
        raise RuntimeError(f"{response.request.method} {response.url} -> {response.status_code}\n{body}")


def make_sample_pdf() -> Path:
    # 표 구조 파싱 확인용 최소 PDF를 런타임 임시 파일로 생성합니다.
    content = b"""BT /F1 12 Tf 72 740 Td (Phase 0 Sample Table) Tj ET
72 710 m 420 710 l 420 650 l 72 650 l 72 710 l S
72 690 m 420 690 l S
190 710 m 190 650 l S
300 710 m 300 650 l S
BT /F1 10 Tf 82 695 Td (Quarter) Tj ET
BT /F1 10 Tf 202 695 Td (Revenue) Tj ET
BT /F1 10 Tf 312 695 Td (Growth) Tj ET
BT /F1 10 Tf 82 670 Td (Q1) Tj ET
BT /F1 10 Tf 202 670 Td (10M) Tj ET
BT /F1 10 Tf 312 670 Td (5%) Tj ET
"""
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"endstream",
    ]
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{index} 0 obj\n".encode())
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_offset = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode())
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode())
    pdf.extend(
        f"trailer << /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_offset}\n%%EOF\n".encode()
    )

    path = Path(tempfile.gettempdir()) / "phase0_upstage_sample_table.pdf"
    path.write_bytes(pdf)
    return path


def check_embedding(api_key: str) -> int:
    response = requests.post(
        f"{API_BASE_URL}/embeddings",
        headers={**headers(api_key), "Content-Type": "application/json"},
        json={"model": EMBEDDING_MODEL, "input": "Phase 0 embedding dimension check"},
        timeout=30,
    )
    raise_for_api_error(response)
    data = response.json()
    vector = data["data"][0]["embedding"]
    dimension = len(vector)
    print(f"OK embedding dimension={dimension} model={EMBEDDING_MODEL}")
    return dimension


def check_chat_stream(api_key: str) -> None:
    response = requests.post(
        f"{API_BASE_URL}/chat/completions",
        headers={**headers(api_key), "Content-Type": "application/json"},
        json={
            "model": CHAT_MODEL,
            "messages": [{"role": "user", "content": "Reply with one short Korean sentence."}],
            "stream": True,
        },
        stream=True,
        timeout=30,
    )
    raise_for_api_error(response)
    token_events = 0
    for line in response.iter_lines(decode_unicode=True):
        if not line or not line.startswith("data: "):
            continue
        payload = line.removeprefix("data: ").strip()
        if payload == "[DONE]":
            break
        token_events += 1
        if token_events >= 1:
            break
    if token_events == 0:
        raise RuntimeError("스트리밍 토큰 이벤트를 수신하지 못했습니다.")
    print(f"OK chat streaming model={CHAT_MODEL}")


def check_document_parse(api_key: str) -> None:
    pdf_path = make_sample_pdf()
    with pdf_path.open("rb") as file:
        response = requests.post(
            f"{API_BASE_URL}/document-ai/document-parse",
            headers=headers(api_key),
            files={"document": (pdf_path.name, file, "application/pdf")},
            data={"output_format": "markdown"},
            timeout=60,
        )
    raise_for_api_error(response)
    text = response.text
    parsed: Any
    try:
        parsed = response.json()
        text = json.dumps(parsed, ensure_ascii=False)
    except ValueError:
        pass
    if "Quarter" not in text and "Q1" not in text:
        raise RuntimeError("Document Parse 응답에서 샘플 표 텍스트를 찾지 못했습니다.")
    print("OK document parse sample table text detected")


def check_groundedness(api_key: str) -> None:
    if not GROUNDNESS_PATH:
        raise RuntimeError(
            "UPSTAGE_GROUNDNESS_PATH가 없습니다. "
            "Upstage 콘솔의 Groundness Check 최신 API 경로를 확인한 뒤 설정하세요."
        )
    response = requests.post(
        f"{API_BASE_URL}{GROUNDNESS_PATH}",
        headers={**headers(api_key), "Content-Type": "application/json"},
        json={
            "context": "RAG는 검색된 문서 근거를 바탕으로 답변을 생성하는 방식입니다.",
            "answer": "RAG는 검색된 문서 근거를 사용해 답변합니다.",
        },
        timeout=30,
    )
    raise_for_api_error(response)
    print("OK groundedness check")


def main() -> None:
    load_dotenv()
    api_key = os.getenv("UPSTAGE_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY가 없습니다. `.env`에 키를 설정하세요.")

    for module_name in ("fastapi", "langgraph", "langchain_upstage", "faiss", "requests"):
        require_import(module_name)

    check_document_parse(api_key)
    dimension = check_embedding(api_key)
    check_chat_stream(api_key)
    check_groundedness(api_key)
    print(f"PHASE0_OK embedding_dimension={dimension}")


if __name__ == "__main__":
    main()
