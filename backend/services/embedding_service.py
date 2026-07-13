"""Solar Embedding 및 FAISS 인메모리 색인 서비스."""

from __future__ import annotations

import os
import uuid
from typing import Protocol

import faiss
import numpy as np
import requests

from backend.services.models import DocumentChunk, SearchResult


EMBEDDING_DIMENSION = 4096


class EmbeddingError(RuntimeError):
    """임베딩 생성 실패."""


class EmbeddingClient(Protocol):
    """임베딩 클라이언트 인터페이스."""

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """여러 텍스트를 벡터로 변환합니다."""


class UpstageEmbeddingClient:
    """Solar Embedding API 클라이언트."""

    def __init__(
        self,
        api_key: str | None = None,
        api_base_url: str | None = None,
        model: str | None = None,
        timeout: int = 30,
    ) -> None:
        self.api_key = api_key or os.getenv("UPSTAGE_API_KEY")
        self.api_base_url = api_base_url or os.getenv("UPSTAGE_API_BASE_URL", "https://api.upstage.ai/v1")
        self.model = model or os.getenv("UPSTAGE_EMBEDDING_MODEL", "solar-embedding-1-large-query")
        self.timeout = timeout

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not self.api_key:
            raise EmbeddingError("missing_upstage_api_key")
        vectors: list[list[float]] = []
        for text in texts:
            response = requests.post(
                f"{self.api_base_url}/embeddings",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json={"model": self.model, "input": text},
                timeout=self.timeout,
            )
            if response.status_code >= 400:
                raise EmbeddingError(f"embedding_failed:{response.status_code}")
            vector = response.json()["data"][0]["embedding"]
            vectors.append(vector)
        return vectors


def split_markdown(markdown: str, max_chars: int = 1200, overlap: int = 120) -> list[str]:
    """Markdown을 검색용 청크로 분할합니다."""

    paragraphs = [part.strip() for part in markdown.split("\n\n") if part.strip()]
    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = f"{current}\n\n{paragraph}".strip() if current else paragraph
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        while len(paragraph) > max_chars:
            chunks.append(paragraph[:max_chars])
            paragraph = paragraph[max_chars - overlap :]
        current = paragraph
    if current:
        chunks.append(current)
    return chunks or [markdown.strip()]


def make_chunks(document_id: str, document_name: str, markdown: str) -> list[DocumentChunk]:
    """파싱 결과를 문서 청크 목록으로 변환합니다."""

    return [
        DocumentChunk(
            chunk_id=str(uuid.uuid4()),
            document_id=document_id,
            document_name=document_name,
            page=index + 1,
            content=content,
        )
        for index, content in enumerate(split_markdown(markdown))
    ]


class FaissVectorStore:
    """문서별 삭제를 지원하는 FAISS 인메모리 벡터 스토어."""

    def __init__(self, dimension: int = EMBEDDING_DIMENSION) -> None:
        self.dimension = dimension
        self._chunks: list[DocumentChunk] = []
        self._vectors: list[list[float]] = []
        self._index = faiss.IndexFlatIP(dimension)

    @property
    def chunk_count(self) -> int:
        """현재 색인된 청크 수."""

        return len(self._chunks)

    def add(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        """청크와 임베딩을 색인합니다."""

        if len(chunks) != len(embeddings):
            raise EmbeddingError("chunk_embedding_count_mismatch")
        matrix = self._to_matrix(embeddings)
        self._index.add(matrix)
        self._chunks.extend(chunks)
        self._vectors.extend(embeddings)

    def delete_document(self, document_id: str) -> int:
        """문서 ID에 해당하는 청크와 벡터를 제거합니다."""

        before = len(self._chunks)
        retained = [
            (chunk, vector)
            for chunk, vector in zip(self._chunks, self._vectors)
            if chunk.document_id != document_id
        ]
        self._chunks = [item[0] for item in retained]
        self._vectors = [item[1] for item in retained]
        self._rebuild_index()
        return before - len(self._chunks)

    def chunks_for_document(self, document_id: str) -> list[DocumentChunk]:
        """문서 ID에 해당하는 청크 목록을 반환합니다."""

        return [chunk for chunk in self._chunks if chunk.document_id == document_id]

    def search(self, query_embedding: list[float], top_k: int = 4, min_score: float = 0.0) -> list[SearchResult]:
        """질의 임베딩과 가장 유사한 문서 청크를 반환합니다."""

        if not self._chunks:
            return []
        top_k = max(1, min(top_k, len(self._chunks)))
        query_matrix = self._to_matrix([query_embedding])
        scores, indices = self._index.search(query_matrix, top_k)
        results: list[SearchResult] = []
        for score, index in zip(scores[0], indices[0]):
            if index < 0 or float(score) < min_score:
                continue
            results.append(SearchResult(chunk=self._chunks[int(index)], score=float(score)))
        return results

    def _rebuild_index(self) -> None:
        self._index = faiss.IndexFlatIP(self.dimension)
        if self._vectors:
            self._index.add(self._to_matrix(self._vectors))

    def _to_matrix(self, embeddings: list[list[float]]) -> np.ndarray:
        matrix = np.array(embeddings, dtype="float32")
        if matrix.ndim != 2 or matrix.shape[1] != self.dimension:
            raise EmbeddingError(f"embedding_dimension_mismatch:{matrix.shape}")
        faiss.normalize_L2(matrix)
        return matrix
