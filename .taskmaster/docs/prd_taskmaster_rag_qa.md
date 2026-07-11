# 문서 기반 RAG Q&A 앱 - TaskMaster 입력용 축약 PRD

## 목표
PDF, DOCX, HTML 문서를 업로드하면 Upstage Document Parse로 표와 레이아웃을 보존해 파싱하고, Solar Embedding으로 색인한 뒤, Solar Pro 3와 LangGraph 기반 Self-Correcting RAG로 문서 근거 기반 답변을 스트리밍 제공한다. Groundness Check로 환각을 억제하고, 답변에는 문서명과 페이지 출처를 표시한다.

## 핵심 완료 기준
- PDF/DOCX/HTML 업로드부터 파싱, 청크 분할, 임베딩, 색인까지 자동 완료된다.
- 질문 입력 시 문서 근거 기반 답변이 SSE 스트리밍으로 출력된다.
- 답변 하단에 출처(문서명, 페이지 또는 청크 위치)가 표시된다.
- Groundness Check가 동작하고 근거 부족 시 쿼리 재작성, 재검색, 재답변 또는 "확인 불가" 안내를 수행한다.
- 지원하지 않는 형식 또는 20MB 초과 업로드는 사용자 친화적 오류로 차단된다.
- 문서 삭제 시 해당 문서의 벡터 색인도 함께 제거된다.

## 기능 요구사항
1. 문서 업로드 및 파싱
   - FastAPI `POST /api/documents`에서 multipart 파일을 받는다.
   - 지원 포맷은 PDF, DOCX, HTML이다.
   - Upstage Document Parse API로 Markdown을 생성하고 표 구조 보존을 확인한다.
   - 처리 상태는 `processing`, `indexed`, `failed`로 관리한다.

2. 임베딩 및 벡터 색인
   - 파싱된 Markdown을 검색 가능한 청크로 분할한다.
   - Solar Embedding으로 벡터화한다.
   - MVP 기본은 FAISS 또는 Chroma 인메모리 벡터 스토어다.
   - 중복 업로드 정책을 명확히 하고, 삭제 시 orphan 벡터가 남지 않게 한다.

3. LangGraph Self-Correcting RAG
   - State에는 질문, 검색 결과, 답변, 출처, groundness 결과, retryCount를 포함한다.
   - 8개 Node를 구현한다: 질문평가, 질문재작성, 문서검색, 검색결과평가, 검색쿼리재작성, 답변생성, 답변평가, 문제진단.
   - 조건부 라우팅으로 정상 경로와 재시도 경로를 모두 처리한다.
   - `MAX_RETRY_COUNT` 초과 시 확인 불가 응답으로 종료한다.

4. 답변 생성 및 검증
   - Solar Pro 3로 검색 청크 기반 답변을 생성한다.
   - 응답은 SSE 스트리밍으로 반환한다.
   - Upstage Groundness Check로 답변이 검색 근거에 부합하는지 검증한다.
   - 근거가 없으면 답을 지어내지 않고 명확히 안내한다.

5. 백엔드 API
   - `POST /api/documents`: 업로드, 파싱, 색인 트리거. 성공 시 202와 `documentId`, `status` 반환.
   - `GET /api/documents`: 문서 목록과 상태 반환.
   - `DELETE /api/documents/{documentId}`: 문서 메타데이터와 벡터 삭제.
   - `POST /api/chat`: 질문을 받아 RAG 실행 후 `text/event-stream`으로 답변 토큰과 최종 출처 정보를 반환.
   - CORS, 오류 응답, 타임아웃, 입력 검증을 포함한다.

6. 프론트엔드
   - React 18, Vite 5, TailwindCSS 3, Axios를 사용한다.
   - 라우트는 `/`, `/documents`, `/chat`이다.
   - `/documents`: 드래그앤드롭 업로드, 문서 목록, 상태 배지, 삭제 확인, 실패 시 재시도 버튼을 제공한다.
   - `/chat`: 질문 입력, 스트리밍 답변, 출처 칩, Groundness 라벨, 대화 이력 유지, 생성 중 중복 전송 차단을 제공한다.
   - `/`: 업로드/색인완료/처리중/실패 요약 카드 대시보드를 제공한다.

7. 디자인 및 UX
   - 근거 우선, 차분한 신뢰감, 정직한 상태 표시, 빠른 피드백을 따른다.
   - 상태 색상은 성공, 경고, 오류, 정보 의미로만 사용한다.
   - 처리중/완료/실패/근거 불충분 상태를 명확한 라벨로 표시한다.
   - Toast는 3초 자동 소멸, 우하단 위치, 최신 메시지 우선 원칙을 따른다.

8. 데이터 구조
   - Document: `documentId`, `filename`, `fileType`, `status`, `pageCount`, `chunkCount`, `failReason`, `uploadedAt`, `indexedAt`.
   - Chunk: `chunkId`, `documentId`, `documentName`, `page`, `content`, `embedding`.
   - Message: `messageId`, `conversationId`, `role`, `content`, `sources`, `grounded`, `retryCount`, `createdAt`.
   - ID는 UUID v4, 시간은 ISO 8601 UTC를 사용한다.

9. 환경변수 및 보안
   - `UPSTAGE_API_KEY`, `VITE_API_BASE_URL`, `MAX_UPLOAD_MB`, `MAX_RETRY_COUNT`를 사용한다.
   - API 키는 `.env` 또는 배포 환경변수에만 저장하며 프론트 번들에 노출하지 않는다.
   - `.env.example`에는 키 없이 구조만 포함한다.
   - 업로드 파일 형식과 크기는 서버 측에서 재검증한다.

10. 프로젝트 구조
    - `backend/main.py`: FastAPI 앱 진입점.
    - `backend/routers/documents.py`, `backend/routers/chat.py`: API 라우터.
    - `backend/graph/state.py`, `backend/graph/nodes.py`, `backend/graph/graph.py`: LangGraph 상태, 노드, 그래프.
    - `backend/services/parse_service.py`, `embedding_service.py`, `llm_service.py`, `groundness_service.py`: 외부 API 및 벡터 연동.
    - `frontend/src/pages/Dashboard.jsx`, `DocumentsPage.jsx`, `ChatPage.jsx`.
    - `frontend/src/components/DropZone.jsx`, `DocumentTable.jsx`, `StatusBadge.jsx`, `ChatMessageList.jsx`, `SourceChip.jsx`, `GroundnessLabel.jsx`, `ChatInput.jsx`, `Modal.jsx`, `Toast.jsx`.
    - `frontend/src/api/axios.js`.

## 개발 Phase
1. Phase 0: Upstage API, Document Parse 응답, Embedding 차원, LangGraph/langchain-upstage 호환성, Solar Pro 3 스트리밍 사전 검증.
2. Phase 1: 백엔드/프론트 디렉토리, `.gitignore`, `.env.example`, 의존성, 기본 서버와 라우팅 환경 구성.
3. Phase 2: 문서 파싱 및 임베딩 색인 파이프라인 구현.
4. Phase 3: LangGraph RAG 그래프와 Groundness 재시도 루프 구현.
5. Phase 4: FastAPI documents/chat API와 SSE 스트리밍 조립.
6. Phase 5: Vite React Tailwind 라우팅과 Axios 클라이언트 구성.
7. Phase 6: 문서 관리 화면 구현.
8. Phase 7: Q&A 채팅 화면 구현.
9. Phase 8: 통합 E2E 검증과 로컬 실행 문서화.

## E2E 검증
- 표 포함 PDF 업로드 후 상태가 처리중에서 완료로 전환되고 표 구조가 보존된다.
- 문서 내 존재하는 사실 질문에 정답, 출처, 근거 확인 라벨이 표시된다.
- 문서에 없는 내용 질문에는 확인 불가 안내가 표시된다.
- 모호한 질문은 쿼리 재작성과 재검색 흐름을 거친다.
- DOCX와 HTML도 PDF와 동일하게 색인 및 질의 가능하다.
- 삭제된 문서는 더 이상 검색 근거로 사용되지 않는다.
- 20MB 초과 또는 미지원 형식 업로드는 오류 메시지와 함께 차단된다.
- 답변 생성 중 중복 전송은 비활성화로 차단된다.
