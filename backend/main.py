"""FastAPI 애플리케이션 진입점."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routers.documents import router as documents_router


app = FastAPI(
    title="RAG Q&A API",
    description="문서 기반 RAG Q&A 애플리케이션 백엔드 API",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health_check() -> dict[str, str]:
    """서비스 상태를 확인합니다."""
    return {"status": "ok"}


app.include_router(documents_router)
