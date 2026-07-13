# PRD (Product Requirements Document)
## 문서 기반 RAG Q&A 앱

---

### 문서 정보

| 항목 | 내용 |
|---|---|
| 문서명 | 문서 기반 RAG Q&A 앱 — PRD |
| 상위 문서 | 프로그램 개요서 v0.1 |
| 작성 목적 | 기능 요구사항·완료 기준·화면/API 명세 정의 |
| 개발 방식 | Codex CLI 기반 바이브 코딩 (1일 스프린트) |
| 개발 기간 | 1일 단기 스프린트 (총 10.0h, 13장 타임라인 참조) |
| 배포 목표 | 로컬 개발 환경 우선, 이후 Vercel(프론트) + 서버 배포 검토 |
| 버전 | v0.3 (Draft) |

---

## 0. 이 PRD를 읽기 전에 — 바이브 코딩 3대 원칙

이 프로젝트는 Codex CLI에게 자연어로 작업을 지시하며 빠르게 만들어가는 **바이브 코딩** 방식으로 진행됩니다. 속도가 빠른 만큼 방향을 잃기 쉽기 때문에, 아래 3가지 원칙을 모든 기능 개발에 공통으로 적용합니다.

| 원칙 | 의미 | 이 PRD에서의 적용 |
|---|---|---|
| **① 완료 기준 선언** | "뭘 만들면 끝인지"를 코딩 시작 전에 문서로 못박는다 | 모든 기능에 **DoD(Definition of Done) 체크리스트** 명시 (3장) |
| **② 조사 먼저, 구현 나중** | 새 기술/API를 붙이기 전 5분 조사로 1시간 디버깅을 막는다 | 모든 기능에 **사전 조사(Pre-flight Check) 항목** 명시 (3장) |
| **③ 분석 먼저, 수정 나중** | 버그 발생 시 "고쳐"가 아니라 "원인부터 알려줘"로 접근한다 | 공통 **디버깅 프로토콜** 및 Codex 프롬프트 가이드 (6장) |

> Codex CLI에게 작업을 지시할 때는 이 3원칙을 프롬프트에 포함시키는 것을 권장합니다. 예: *"~~기능을 구현하기 전에 먼저 [라이브러리]의 공식 문서를 확인하고 어떤 방식으로 연동할지 요약해줘. 그 다음 구현해줘."*

### 전체 스프린트 완료 체크리스트 (Master Checklist)

**Must Have — 이것만 되면 데모 가능**
- [ ] PDF/DOCX/HTML 업로드 → Document Parse → 임베딩 → 색인까지 자동 완료
- [ ] 질문 입력 시 문서 근거 기반 답변이 스트리밍으로 출력됨
- [ ] 답변에 출처(문서명·페이지) 표시
- [ ] Groundness Check가 동작하고, 근거 부족 시 재시도 또는 "확인 불가" 안내
- [ ] 지원하지 않는 형식/용량 초과 업로드 시 오류 메시지 표시

**Should Have — 완성도를 높이는 기능**
- [ ] 문서 삭제 시 벡터 색인도 함께 제거
- [ ] 대화 이력 화면 내 유지
- [ ] 파싱 실패 문서 재시도 버튼
- [ ] 메인 대시보드 요약 카드(업로드/색인완료/처리중 건수)

---

## 1. 제품 개요 (Product Summary)

PDF·Word·HTML 문서를 업로드하면, AI가 문서 구조(표·레이아웃)를 보존한 채 내용을 파싱·색인하고, 사용자의 자연어 질문에 문서 근거와 출처를 함께 제시하며 답변하는 RAG(Retrieval-Augmented Generation) 기반 웹 애플리케이션.

**핵심 파이프라인**: `Document Parse → Solar Embedding → Solar Pro 3 (답변 생성) → Groundness Check (근거 검증)`

### 1.1 문제 정의 (Problem Statement)

| 문제 | 설명 |
|------|------|
| 정보 탐색 비효율 | 긴 문서에서 필요한 정보를 찾기 위해 처음부터 끝까지 읽거나 Ctrl+F로 반복 검색해야 함 |
| 표·문맥 검색의 한계 | 표 안의 숫자나 문맥이 필요한 내용은 단순 키워드 검색으로 찾기 어려움 |
| AI 답변 신뢰 부족 | 일반 챗봇은 근거 없이 지어낸 답변(환각)을 제시해 업무 문서 검토에 신뢰하기 어려움 |
| 파이프라인 구축 부담 | 파싱 → 임베딩 → 생성 → 검증 전체 RAG 파이프라인을 처음부터 설계하기 부담스러움 |

### 1.2 솔루션 (Solution)

문서(PDF·DOCX·HTML)를 업로드 하면 **Upstage Document Parse**가 표·레이아웃 구조를 보존해 파싱하고, **Solar Embedding**으로 색인한 뒤, 사용자의 자연어 질문에 대해 **Solar Pro 3**가 문서 근거와 출처를 함께 제시하며 답변한다. 나아가 **Groundness Check**로 답변의 근거를 자동 검증하여 환각을 억제하는 Self-Correcting RAG 웹 애플리케이션을 제공한다.

### 1.3 목표 지표 (Success Metrics)

| 지표 | 목표값 |
|---|---|
| 문서 파싱 성공률 | 표 포함 PDF·DOCX·HTML 기준 90% 이상 (레이아웃 구조 보존 포함) |
| 질문 → 첫 토큰 응답 시간 | 3초 이내 (스트리밍 시작 기준) |
| 근거 검증(Groundness) 통과율 | 색인 문서 내 답이 존재하는 질문 기준 85% 이상 |
| 환각(Hallucination) 억제 | 근거 없는 질문에 "확인 불가" 응답률 100% (지어낸 답변 0건) |
| E2E 흐름 동작 (업로드 → 질문 → 근거 표시) | 1일 스프린트 내 완료 |

---

## 2. 사용자 시나리오 (User Scenarios)

### 2.1 타겟 사용자 (User Personas)

**Persona A — 문서 검토가 많은 실무자**
- **특성**: 보고서·계약서·회의록 등 업무 문서를 자주 검토하는 30~40대 직장인
- **목표**: 문서를 처음부터 끝까지 읽지 않고 필요한 정보만 빠르게 확인
- **Pain Point**: Ctrl+F로는 표 안의 숫자나 문맥이 필요한 내용을 찾기 어려움

**Persona B — RAG 학습 개발자**
- **특성**: LangGraph + Upstage API로 Self-Correcting RAG를 실습하려는 개발자
- **목표**: Codex CLI 바이브 코딩으로 동작하는 RAG 앱을 하루 만에 완성, 포트폴리오 구성
- **Pain Point**: 파싱 → 임베딩 → 생성 → 검증 전체 파이프라인을 처음부터 설계하기 부담스러움

### 2.2 사용자 시나리오

| # | 시나리오 |
|---|---|
| US-1 | 사용자가 PDF 보고서를 업로드하면, 표가 깨지지 않은 상태로 파싱되어 색인 목록에 나타난다 |
| US-2 | 사용자가 "이 문서의 3분기 매출은?"이라고 질문하면, 관련 문서 조각을 찾아 답변과 출처(문서명·페이지)를 함께 보여준다 |
| US-3 | AI가 문서에 없는 내용을 답변하려 할 경우, Groundness Check가 이를 감지하고 재시도하거나 "근거를 찾을 수 없음"을 알린다 |
| US-4 | 사용자가 더 이상 필요 없는 문서를 삭제하면, 해당 문서의 색인도 함께 제거된다 |

---

## 3. 기능 요구사항 (Functional Requirements) & DoD

### 3.0 기능 우선순위 (Feature Priority)

| ID | 기능 | 우선순위 |
|----|------|---------|
| M-01 | 문서 업로드 및 파싱 (FR-1) | Must Have |
| M-02 | 임베딩 및 색인 (FR-2) | Must Have |
| M-03 | RAG 답변 생성 + 스트리밍 (FR-3) | Must Have |
| M-04 | 답변 근거 검증 Groundness Check (FR-4) | Must Have |
| M-05 | LangGraph Self-Correcting 그래프 (FR-5) | Must Have |
| M-06 | Q&A 채팅 화면 (FR-7) | Must Have |
| S-01 | 문서 관리 화면 — 목록·삭제 (FR-6) | Should Have |
| S-02 | 파싱 실패 문서 재시도 | Should Have |
| S-03 | 메인 대시보드 요약 카드 | Should Have |
| S-04 | 출처 칩 클릭 시 원문 페이지 미리보기 | Could Have |

> 각 기능은 **① 사전 조사 → ② 구현 → ③ DoD 체크** 순서로 진행합니다. "사전 조사" 항목은 구현 시작 전에 Codex CLI에게 먼저 확인을 지시해야 하는 사항입니다.

### FR-1. 문서 업로드 및 파싱 (Document Parse)

**설명**: PDF·Word·HTML 문서를 업로드하면 Upstage Document Parse API를 통해 표·레이아웃 구조를 보존한 Markdown으로 변환한다.

**🔍 사전 조사 (구현 전 필수 확인)**
- [x] Upstage Document Parse API의 요청/응답 스키마 확인 (지원 포맷, 파일 용량 제한)
- [x] 비동기 처리 여부 확인 (동기 응답 vs. 작업 큐 + 폴링 방식)
- [x] 표/레이아웃이 Markdown으로 어떤 구조로 변환되는지 샘플 응답 확인

**✅ DoD (Definition of Done)**
- [x] PDF, Word(.docx), HTML 3개 포맷 모두 업로드 성공
- [x] 표가 포함된 문서를 업로드했을 때 표 구조가 깨지지 않고 Markdown으로 변환됨
- [x] 파싱 실패 시(손상 파일, 지원하지 않는 포맷 등) 사용자에게 명확한 에러 메시지 표시
- [x] 파싱 진행 상태(대기/처리중/완료/실패)가 화면에 실시간 반영됨

---

### FR-2. 임베딩 및 색인 (Solar Embedding)

**설명**: 파싱된 문서 청크를 Solar Embedding으로 벡터화하여 인메모리 벡터 스토어에 색인한다.

**🔍 사전 조사**
- [x] Solar Embedding API의 입력 토큰 제한 및 청크 분할 권장 사이즈 확인
- [x] 한국어 특화 임베딩의 차원(dimension) 수 확인 → 벡터 스토어 설정과 일치 여부 검증
- [x] 인메모리 벡터 스토어(예: FAISS, Chroma 등) 선택 시 LangGraph와의 연동 방식 확인

**✅ DoD**
- [x] 파싱 완료된 문서가 자동으로 청크 분할 → 임베딩 → 색인까지 이어짐 (수동 트리거 불필요)
- [x] 동일 문서를 중복 업로드 시 중복 색인되지 않거나, 명확히 구분되어 관리됨
- [x] 문서 삭제 시 해당 문서의 벡터도 함께 제거됨 (orphan 벡터 없음)

---

### FR-3. RAG 답변 생성 (Solar Pro 3)

**설명**: 사용자 질문과 검색된 유사 청크를 결합한 프롬프트로 Solar Pro 3가 문서 근거 기반 답변을 생성한다.

**🔍 사전 조사**
- [ ] Solar Pro 3의 OpenAI 호환 엔드포인트 스펙(요청 포맷, 스트리밍 지원 여부) 확인
- [ ] 컨텍스트 윈도우 제한 확인 → 검색 결과(top-k) 개수 결정에 반영
- [ ] 스트리밍 응답을 프론트엔드에서 어떻게 받을지(SSE/WebSocket) 사전 결정

**✅ DoD**
- [ ] 질문 입력 시 답변이 스트리밍 형태로 출력됨
- [ ] 답변에 참조한 문서명·페이지(또는 청크 위치)가 함께 표시됨
- [ ] 관련 문서가 색인되어 있지 않은 질문에는 "근거를 찾을 수 없음"을 명확히 안내 (없는 답을 지어내지 않음)

---

### FR-4. 답변 근거 검증 (Groundness Check)

**설명**: 생성된 답변이 실제 검색된 문서 내용에 근거하는지 자동 판정하고, 근거가 부족하면 LangGraph가 자동 재시도한다.

**🔍 사전 조사**
- [ ] Groundness Check API/모델의 판정 기준(grounded/notGrounded/notSure 등) 및 응답 포맷 확인
- [ ] 재시도 시 무한 루프에 빠지지 않도록 최대 재시도 횟수 정책 확인

**✅ DoD**
- [ ] 답변 생성 후 Groundness Check가 자동으로 실행됨
- [ ] 근거 부족 판정 시 검색 쿼리 재작성 → 재검색 → 재답변 흐름이 자동으로 동작
- [ ] 최대 재시도 횟수(예: 2~3회) 초과 시 "확실한 답변을 찾지 못했습니다" 등으로 정직하게 안내
- [ ] Self-Correcting RAG 그래프(질문평가 → 검색 → 평가 → 재작성 → 재검색 → 답변 → 평가)가 LangGraph 상에서 정상 동작

---

### FR-5. LangGraph 기반 RAG 오케스트레이션

**설명**: State, Node, Edge로 구성된 LangGraph를 사용하여 위 FR-1~FR-4를 하나의 자기 교정형(Self-Correcting) 그래프로 연결한다.

**🔍 사전 조사**
- [ ] LangGraph의 State 정의 방식(TypedDict 등) 및 조건부 엣지(Conditional Edge) 작성 패턴 확인
- [ ] 각 Node(질문평가, 질문재작성, 문서검색, 검색결과평가, 검색쿼리재작성, 답변생성, 답변평가, 문제진단)의 입출력 State 설계 확정

**✅ DoD**
- [ ] State 정의 완료 (질문, 검색결과, 답변, 평가결과 등 필요한 필드 포함)
- [ ] 8개 Node 함수 모두 구현되고 단위 동작 확인됨
- [ ] Routing 함수가 각 평가 결과에 따라 올바른 다음 Node로 분기함
- [ ] 전체 그래프 실행 시 정상 케이스(1회 통과) / 재시도 케이스(평가 실패 후 재시도) 두 경로 모두 테스트 통과

---

### FR-6. 문서 관리 화면 (`/documents`)

**🔍 사전 조사**
- [ ] 파일 업로드 UX 라이브러리(react-dropzone 등) 선택 및 멀티파일 업로드 지원 여부 확인

**✅ DoD**
- [ ] 드래그앤드롭으로 PDF·Word·HTML 업로드 가능
- [ ] 업로드 중 진행 상태(파싱 중/완료/실패)가 항목별로 표시됨
- [ ] 색인 완료된 문서 목록이 표시되고, 각 문서 삭제 가능
- [ ] 삭제 시 확인(confirm) 절차 존재

---

### FR-7. Q&A 채팅 화면 (`/chat`)

**🔍 사전 조사**
- [ ] 스트리밍 답변을 받기 위한 프론트엔드 처리 방식(EventSource 등) 확인

**✅ DoD**
- [ ] 질문 입력 → 답변이 타이핑되듯 스트리밍으로 표시됨
- [ ] 답변 하단에 출처(문서명·페이지) 표시
- [ ] 대화 이력이 화면 내에 누적되어 표시됨 (새로고침 전까지 유지)
- [ ] 답변 생성 중 로딩 상태가 명확히 표시됨

---

## 4. REST API 명세

### 4.1 문서 관련

**`POST /api/documents`** — 문서 업로드

| 항목 | 내용 |
|---|---|
| 설명 | 문서 업로드 → Document Parse → 벡터 색인까지 트리거 |
| Request | `multipart/form-data` — `file` (PDF/DOCX/HTML) |
| Response (성공, 202) | `{ "documentId": "string", "status": "processing" }` |
| Response (실패, 400) | `{ "error": "unsupported_format" \| "file_too_large" \| "parse_failed" }` |

**`GET /api/documents`** — 색인 문서 목록 조회

| 항목 | 내용 |
|---|---|
| Response (200) | `[{ "documentId": "string", "filename": "string", "status": "processing"\|"indexed"\|"failed", "pageCount": number, "uploadedAt": "ISO8601" }]` |

**`DELETE /api/documents/{documentId}`** — 문서·청크 삭제

| 항목 | 내용 |
|---|---|
| Response (성공, 204) | No Content |
| Response (실패, 404) | `{ "error": "document_not_found" }` |

### 4.2 질의응답 관련

**`POST /api/chat`** — 질문 전송 → RAG 실행 → 답변 반환

| 항목 | 내용 |
|---|---|
| Request | `{ "question": "string", "conversationId": "string (optional)" }` |
| Response (스트리밍, 200, `text/event-stream`) | 토큰 단위 답변 스트림 + 최종 이벤트로 출처 정보 전달 |
| 최종 이벤트 예시 | `{ "answer": "string", "sources": [{ "documentName": "string", "page": number }], "grounded": boolean }` |
| Response (근거 없음) | `grounded: false` + 안내 문구 반환 (답변을 지어내지 않음) |

> API 명세는 1차 초안이며, FR-1~FR-5 구현 과정에서 세부 필드가 조정될 수 있습니다. 변경 시 본 문서를 갱신합니다.

---

## 5. 화면 명세 (Screen Spec)

### 5.1 화면 디자인 & 스타일 가이드 (Design & Style Guide)

#### 5.1.1 디자인 원칙

본 제품은 "AI가 지어낸 답이 아니라 문서에 근거한 답"을 신뢰하고 사용하는 도구입니다. 디자인도 이 신뢰를 뒷받침해야 하므로 아래 3가지 원칙을 따릅니다.

| 원칙 | 의미 |
|---|---|
| **근거 우선 (Evidence-first)** | 출처·페이지·근거 검증 결과는 항상 시각적으로 눈에 띄게 배치한다. 답변 텍스트보다 작거나 흐린 글씨로 숨기지 않는다 |
| **차분한 신뢰감 (Calm confidence)** | 채팅형 AI 제품 특유의 화려한 그라데이션·과한 모션을 피하고, 업무 문서를 다루는 도구다운 차분한 톤을 유지한다 |
| **정직한 상태 표시 (Honest status)** | 처리중 / 완료 / 실패 / 근거 불충분 등의 상태를 추측하게 두지 않고 항상 명시적인 라벨과 색으로 구분한다 |
| **빠른 피드백 (Responsiveness)** | 업로드·질문 전송·삭제 등 모든 동작에 즉각적인 시각적 피드백(스트리밍 커서, 상태 배지 전환, Toast)을 제공한다 |

#### 5.1.2 컬러 팔레트

| 구분 | 색상명 | HEX | 용도 |
|---|---|---|---|
| **Primary** | Indigo 600 | `#4F46E5` | 주요 액션 버튼, 활성 탭, 링크, 포커스 링 |
| **Primary** | Indigo 50 | `#EEF2FF` | Primary 버튼 hover 배경, 선택된 항목 배경 |
| **Neutral** | Ink 900 | `#111827` | 본문 텍스트, 헤딩 |
| **Neutral** | Gray 500 | `#6B7280` | 보조 텍스트, 캡션, 비활성 라벨 |
| **Neutral** | Gray 200 | `#E5E7EB` | 구분선(divider), 테이블 보더 |
| **Neutral** | Gray 50 | `#F9FAFB` | 페이지 배경, 카드 배경 |
| **Neutral** | White | `#FFFFFF` | 카드/패널 표면(surface) |
| **Semantic** | Success Green | `#16A34A` | 색인 완료, 근거 검증 통과(Grounded) |
| **Semantic** | Warning Amber | `#D97706` | 처리중, 근거 불확실(notSure) |
| **Semantic** | Error Red | `#DC2626` | 파싱 실패, 업로드 오류, 근거 없음(notGrounded) |
| **Semantic** | Info Sky | `#0284C7` | 안내 메시지, 빈 상태(empty state) 아이콘 |

> 의미 색상(Semantic)은 상태 배지(Badge), 토스트, 인라인 알림에만 사용하고 장식 목적으로 남용하지 않습니다.

#### 5.1.3 타이포그래피

| 역할 | 폰트 패밀리 | 용도 |
|---|---|---|
| 본문/UI (Body) | **Pretendard** (한글) / **Inter** (영문·숫자) | 본문, 버튼, 입력창, 테이블 — 가독성 최우선의 UI 표준 폰트 |
| 코드/데이터 (Mono) | **JetBrains Mono** | 페이지 번호, 문서 ID, JSON 미리보기 등 데이터성 텍스트 |

**텍스트 스케일**

| 토큰 | 크기 / 줄간격 | 굵기 | 용도 |
|---|---|---|---|
| `text-h1` | 28px / 36px | 700 | 페이지 타이틀 (예: "문서 관리") |
| `text-h2` | 20px / 28px | 600 | 섹션 제목, 카드 헤더 |
| `text-body` | 15px / 24px | 400 | 본문, 채팅 메시지 |
| `text-body-strong` | 15px / 24px | 600 | 강조 텍스트, 답변 내 핵심 문장 |
| `text-caption` | 13px / 18px | 400 | 타임스탬프, 보조 설명 |
| `text-label` | 12px / 16px | 600, uppercase, letter-spacing 0.02em | 상태 배지, 폼 라벨 |

#### 5.1.4 간격 및 크기 시스템 (Spacing)

4px 베이스 스케일을 사용합니다.

| 토큰 | 값 | 용도 |
|---|---|---|
| `space-1` | 4px | 아이콘-텍스트 간격 |
| `space-2` | 8px | 인풋 내부 패딩(수직) |
| `space-3` | 12px | 칩/배지 내부 패딩 |
| `space-4` | 16px | 카드 내부 패딩, 컴포넌트 간 기본 간격 |
| `space-6` | 24px | 섹션 간 간격 |
| `space-8` | 32px | 페이지 상단 여백 |
| `space-12` | 48px | 빈 상태(empty state) 상하 여백 |

**컴포넌트 크기**

| 요소 | 규격 |
|---|---|
| 버튼 높이 | 기본 40px / 작게(small) 32px |
| 인풋·텍스트필드 높이 | 40px |
| 보더 반경(Radius) | 카드 12px / 버튼·인풋 8px / 배지·칩 999px(pill) |
| 그림자(Shadow) | 카드: `0 1px 2px rgba(0,0,0,0.05)` — 입체감보다 평평한 표면 우선 |

#### 5.1.5 레이아웃 & 그리드

**전체 레이아웃 구조**

```
┌─────────────────────────────────────────────┐
│  Top Nav (높이 56px)                          │
│  좌: 로고/제품명   우: (확장 영역, 1차 버전 비움)  │
├───────────┬───────────────────────────────────┤
│           │                                   │
│ Side Nav  │           Main Content            │
│ (폭 220px) │     (max-width 960px, 중앙 정렬)    │
│           │                                   │
│ - 문서관리 │                                   │
│ - Q&A 채팅 │                                   │
│           │                                   │
└───────────┴───────────────────────────────────┘
```

| 항목 | 규격 |
|---|---|
| 그리드 | 12 컬럼, 콘텐츠 영역 max-width 960px (채팅 화면은 720px로 더 좁게 — 가독성 우선) |
| 브레이크포인트 | Desktop ≥1024px / Tablet 768~1023px / Mobile <768px |
| 반응형 규칙 | Tablet 이하에서는 Side Nav가 하단 탭 바 또는 햄버거 메뉴로 전환 |

---

### 5.2 화면별 레이아웃 와이어프레임

#### 5.2.1 메인 대시보드 (`/`) — 첫 진입 화면

```
┌──────────────────────────────────────────────────────────┐
│ [≡ 로고] 문서 기반 RAG Q&A 앱                                │
├───────────┬────────────────────────────────────────────────┤
│ ▣ 문서관리  │  안녕하세요 👋                                  │
│ ▢ Q&A채팅  │  업로드한 문서: 3건  ·  색인 완료: 2건  ·  처리중: 1건  │
│           │                                                │
│           │  ┌──────────────────────────────────────────┐ │
│           │  │  📄  최근 업로드 문서                        │ │
│           │  │  - 2025_사업계획서.pdf      [완료]           │ │
│           │  │  - 계약서_초안.docx        [처리중...]       │ │
│           │  │  - 회의록_0625.html       [완료]           │ │
│           │  └──────────────────────────────────────────┘ │
│           │                                                │
│           │  [+ 문서 업로드하기]      [💬 바로 질문하기]      │
└───────────┴────────────────────────────────────────────────┘
```

| 요소 | 설명 |
|---|---|
| 요약 카드 | 업로드/색인완료/처리중 문서 수를 한눈에 표시 (정직한 상태 표시 원칙) |
| 최근 문서 리스트 | 최대 3~5건, 상태 배지(Success/Warning/Error 색상) 포함 |
| CTA 2종 | 문서가 없으면 "업로드하기"를 Primary로, 문서가 있으면 "질문하기"를 Primary로 전환 |

#### 5.2.2 파일 업로드 페이지 (`/documents`)

```
┌──────────────────────────────────────────────────────────┐
│ [≡ 로고] 문서 기반 RAG Q&A 앱                                │
├───────────┬────────────────────────────────────────────────┤
│ ▢ 문서관리  │  문서 관리                                      │
│ ▢ Q&A채팅  │                                                │
│           │  ┌──────────────────────────────────────────┐ │
│           │  │                                            │ │
│           │  │      📤  파일을 끌어다 놓거나 클릭해 업로드      │ │
│           │  │      PDF · DOCX · HTML  (최대 20MB)         │ │
│           │  │                                            │ │
│           │  └──────────────────────────────────────────┘ │
│           │                                                │
│           │  파일명             상태       업로드일    동작    │
│           │  ──────────────────────────────────────────── │
│           │  사업계획서.pdf    🟢 완료     06.28      [삭제]  │
│           │  계약서.docx      🟡 처리중··   06.29      [-]   │
│           │  회의록.html      🔴 실패      06.29      [재시도][삭제]│
└───────────┴────────────────────────────────────────────────┘
```

| 상태 | 배지 색상 | 동작 가능 여부 |
|---|---|---|
| 처리중 | Warning Amber + 스피너 | 삭제 비활성화(파싱 중에는 취소만 가능) |
| 완료 | Success Green | 삭제 가능, 채팅에서 즉시 검색 대상 포함 |
| 실패 | Error Red | "재시도" / "삭제" 버튼 노출, 실패 사유 tooltip 제공 |

#### 5.2.3 Q&A 채팅 화면 (`/chat`)

```
┌──────────────────────────────────────────────────────────┐
│ [≡ 로고] 문서 기반 RAG Q&A 앱                                │
├───────────┬────────────────────────────────────────────────┤
│ ▢ 문서관리  │  Q&A 채팅                                       │
│ ▣ Q&A채팅  │  ┌──────────────────────────────────────────┐ │
│           │  │                              나: 3분기 매출은?│ │
│           │  │                                            │ │
│           │  │ AI: 3분기 매출은 42억원입니다.                 │ │
│           │  │     [📄 2025_사업계획서.pdf · p.12]            │ │
│           │  │     ✅ 근거 확인됨                             │ │
│           │  │                                            │ │
│           │  │ 나: 4분기 예상은?                              │ │
│           │  │                                            │ │
│           │  │ AI: 죄송하지만 업로드된 문서에서 4분기 예상 매출에   │ │
│           │  │     대한 근거를 찾지 못했습니다.                 │ │
│           │  │     ⚠️ 근거 불충분                             │ │
│           │  └──────────────────────────────────────────┘ │
│           │  ┌──────────────────────────────────────────┐ │
│           │  │ 질문을 입력하세요...              [전송 ▶]    │ │
│           │  └──────────────────────────────────────────┘ │
└───────────┴────────────────────────────────────────────────┘
```

| 요소 | 설명 |
|---|---|
| 출처 칩 | 문서명·페이지를 Mono 폰트로 표시, 클릭 시 해당 페이지 미리보기(선택 기능) |
| 근거 검증 라벨 | "✅ 근거 확인됨"(Success) / "⚠️ 근거 불충분"(Warning) / 근거 없음 시 "확인 불가" 문구(Error 톤 텍스트, 배지 없이 안내형) |
| 빈 상태 (색인 문서 0건) | 채팅창 비활성화 + "문서관리에서 먼저 문서를 업로드하세요" 안내 + 바로가기 버튼 |
| 입력창 비활성 조건 | 답변 생성/검증 중에는 전송 버튼 비활성화 및 로딩 인디케이터 표시 |

---

### 5.3 페이지 목록 및 컴포넌트 명세 (UI Specification)

#### 5.3.1 페이지 목록

| 페이지 | 경로 | 핵심 컴포넌트 |
|--------|------|--------------|
| 메인 대시보드 | `/` | SummaryCard, RecentDocList, QuickActions |
| 문서 관리 | `/documents` | DropZone, DocumentTable, StatusBadge |
| Q&A 채팅 | `/chat` | ChatMessageList, SourceChip, GroundnessLabel, ChatInput |

#### 5.3.2 주요 컴포넌트 명세

**DropZone**
- 드래그 앤 드롭 및 클릭 업로드 지원 (react-dropzone 기반)
- 지원 형식 안내 텍스트 표시 (PDF, DOCX, HTML / 최대 20MB)
- 파일 선택 즉시 `POST /api/documents` 호출

**DocumentTable**
- 컬럼: 파일명 / 상태 배지 / 업로드일 / 동작(삭제·재시도)
- 처리중 항목은 폴링(`GET /api/documents`)으로 상태 자동 갱신

**ChatMessageList**
- 사용자 질문(우측) / AI 답변(좌측) 말풍선
- AI 답변은 토큰 단위 스트리밍 렌더링
- 답변 하단에 SourceChip + GroundnessLabel 부착

**SourceChip**
- `📄 문서명 · p.N` 형식, Mono 폰트
- 클릭 시 원문 페이지 미리보기 (Could Have)

**GroundnessLabel**
- grounded → "✅ 근거 확인됨" (Success)
- notSure → "⚠️ 근거 불충분" (Warning)
- notGrounded → "확인 불가" 안내형 텍스트 (Error 톤)

**ChatInput**
- 멀티라인 지원, Enter 전송 / Shift+Enter 줄바꿈
- 답변 생성 중 비활성화 + 로딩 인디케이터

#### 5.3.3 공통 컴포넌트

| 컴포넌트 | 역할 |
|----------|------|
| StatusBadge | 문서 상태 배지 (처리중·완료·실패, Semantic 색상) |
| Modal | 문서 삭제 확인 다이얼로그 |
| Toast | 업로드/삭제/오류 알림 (3초 자동 소멸) |
| Spinner | 파싱·답변 생성 진행 표시 |
| EmptyState | 문서/대화 없음 안내 + CTA 버튼 |

---

### 5.4 컴포넌트 스타일 명세 (Tailwind)

#### 버튼 (Button)

| 종류 | Tailwind 클래스 | 용도 |
|------|----------------|------|
| Primary | `bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors` | 업로드, 전송 CTA |
| Secondary | `bg-white hover:bg-gray-50 text-gray-700 font-semibold py-2 px-4 rounded-lg border border-gray-300 transition-colors` | 취소, 초기화 |
| Danger | `bg-red-600 hover:bg-red-700 text-white font-semibold py-2 px-4 rounded-lg transition-colors` | 문서 삭제 확인 |
| Ghost | `text-indigo-600 hover:text-indigo-700 font-medium underline` | 텍스트 링크형 버튼 |

#### 카드 (Card)

```
bg-white rounded-xl border border-gray-200
shadow-sm p-4
```

#### 입력 필드 (Input / ChatInput)

```
w-full px-3 py-2
border border-gray-300 rounded-lg
text-sm text-gray-900 placeholder-gray-400
focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent
transition
```

#### DropZone

```
border-2 border-dashed border-gray-300 hover:border-indigo-400
rounded-xl p-12 text-center
bg-gray-50 hover:bg-indigo-50
transition-colors duration-200 cursor-pointer
```

- 드래그 오버 시: `border-indigo-500 bg-indigo-50`
- 업로드 완료 시: `border-green-400 bg-green-50`

#### 상태 배지 (StatusBadge) / 출처 칩 (SourceChip)

```
inline-flex items-center px-2.5 py-0.5
rounded-full text-xs font-medium
```

- 완료: `bg-green-100 text-green-700` / 처리중: `bg-amber-100 text-amber-700` / 실패: `bg-red-100 text-red-700`
- SourceChip: `bg-gray-100 text-gray-700 font-mono hover:bg-indigo-50 cursor-pointer`

#### Toast

```
fixed bottom-4 right-4
flex items-center gap-2 px-4 py-3
rounded-lg shadow-lg text-sm font-medium text-white
animate-slide-up z-50
```

- Success: `bg-green-600` / Error: `bg-red-600` / Info: `bg-sky-600`
- 자동 소멸 3초, 중복 발생 시 최신 메시지만 표시

#### Modal (삭제 확인)

```
/* 오버레이 */ fixed inset-0 bg-black/50 z-40 flex items-center justify-center
/* 패널 */ bg-white rounded-2xl shadow-xl p-6 w-full max-w-sm mx-4 animate-scale-in
```

---

### 5.5 인터랙션 & 애니메이션

| 요소 | 동작 | Tailwind / CSS |
|------|------|---------------|
| 답변 스트리밍 | 토큰 단위 텍스트 추가 + 커서 깜빡임 | `after:content-['▍'] after:animate-pulse` (생성 중에만) |
| 버튼 hover | 색상 어둡게 | `transition-colors duration-150` |
| Toast 등장 | 아래에서 위로 슬라이드 | `animate-[slide-up_0.3s_ease-out]` |
| Modal 등장 | 중앙에서 스케일 인 | `animate-[scale-in_0.2s_ease-out]` |
| DropZone drag | 테두리·배경색 변경 | `border-indigo-500 bg-indigo-50` |
| 상태 배지 갱신 | 처리중 → 완료 전환 시 페이드 | `transition-colors duration-300` |

**커스텀 애니메이션 (tailwind.config.js)**:

```js
module.exports = {
  theme: {
    extend: {
      keyframes: {
        'slide-up': {
          '0%': { transform: 'translateY(16px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        'scale-in': {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
}
```

> 과한 모션은 "차분한 신뢰감" 원칙에 위배되므로 위 목록 외 장식성 애니메이션은 추가하지 않습니다.

---

### 5.6 상태별 UI 명세

#### 로딩 상태

| 상황 | UI |
|------|-----|
| 문서 파싱 중 | DocumentTable 해당 행에 Warning 배지 + 스피너, 삭제 버튼 비활성화 |
| 답변 생성 중 | 말풍선에 스트리밍 커서, ChatInput `disabled` + `opacity-50 cursor-not-allowed` |
| 근거 검증/재시도 중 | "근거를 확인하고 있습니다..." 캡션 표시 (Gray 500) |

#### 빈 상태 (Empty State)

```
┌──────────────────────────────────────┐
│       [문서 아이콘 (회색)]             │
│                                      │
│    아직 색인된 문서가 없습니다          │
│    문서를 업로드하고 질문해 보세요      │
│                                      │
│        [+ 첫 문서 업로드하기]          │
└──────────────────────────────────────┘
```

#### 오류 상태 (파싱 실패)

- 빨간 배너: `bg-red-50 border border-red-200 text-red-700 rounded-lg p-4`
- 메시지: "문서 파싱에 실패했습니다. 파일을 확인하고 다시 시도해 주세요."
- [다시 시도] 버튼 제공, hover 시 실패 사유 tooltip

#### 근거 불충분 상태 (답변)

- 답변 말풍선 하단: `⚠️ 근거 불충분` Warning 라벨
- 재시도 초과 시: "업로드된 문서에서 확실한 근거를 찾지 못했습니다" 안내 문구 (추측 답변 표시 금지)

---

## 6. 디버깅 프로토콜 (버그 대응 공통 규칙)

바이브 코딩 중 버그가 발생했을 때, Codex CLI에게 곧바로 "고쳐줘"라고 지시하지 않고 아래 순서를 따릅니다.

| 단계 | 행동 | Codex 프롬프트 예시 |
|---|---|---|
| 1. 원인 분석 요청 | 증상과 로그를 제공하고 **원인 후보를 먼저 설명**하도록 요청 | *"이 에러가 발생하는 원인이 무엇일 수 있는지 먼저 분석해서 설명해줘. 코드는 아직 고치지 마."* |
| 2. 원인 확정 | 제시된 원인 후보 중 실제 원인을 사람이 확인/선택 | — |
| 3. 수정 요청 | 확정된 원인에 대해서만 최소 범위로 수정 지시 | *"방금 분석한 원인 중 [A]가 맞아. 이 부분만 수정해줘."* |
| 4. 회귀 확인 | 수정 후 관련 DoD 체크리스트 재확인 | — |

> **금지 패턴**: "에러 나니까 알아서 고쳐줘" 식의 즉시 수정 지시. 원인 파악 없는 수정은 같은 버그의 재발 또는 다른 기능의 회귀(regression)로 이어지기 쉽습니다.

### 6.1 예상 버그 유형별 분석 체크리스트

| 버그 유형 | 분석 시 확인할 것 |
|-----------|-----------------|
| Document Parse 실패 (500) | API Key 유효성 / 파일 인코딩·손상 여부 / API 응답 원문(raw) 로그 |
| 임베딩 차원 불일치 오류 | Solar Embedding 차원 수와 벡터 스토어 초기 설정 일치 여부 |
| 검색 결과 0건 | 색인이 실제로 완료됐는지 / 청크 분할이 과도하게 크거나 작지 않은지 |
| LangGraph 무한 루프 | Routing 함수 분기 조건 / 최대 재시도 카운터 State 반영 여부 |
| Groundness Check 항상 실패 | 검증 입력에 답변·근거 청크가 올바른 순서/포맷으로 전달되는지 |
| 스트리밍 응답 끊김 | SSE 연결 유지 여부 / 프록시(CORS·버퍼링) 설정 / 프론트 EventSource 에러 핸들러 |
| CORS 오류 | FastAPI `allow_origins` 설정 / 프론트 API Base URL 일치 여부 |
| 삭제 후 유령(orphan) 벡터 | 문서 삭제 시 벡터 스토어 삭제 로직 호출 여부 / documentId 매핑 정확성 |

### 6.2 디버깅 5단계 워크플로우

| 단계 | 행동 | 설명 |
|------|------|------|
| 1. 증상 기록 | 재현 조건 문서화 | 어떤 문서/질문에서 어떤 오류가 발생했는지 정확히 기록 |
| 2. 로그 확인 | 로그 3곳 순서대로 | 백엔드 서버 로그 → 브라우저 콘솔 → 네트워크 탭 |
| 3. 범위 특정 | 레이어 구분 | 프론트 / API / LangGraph 노드 / 외부 API(Upstage) 중 어디인지 분리 |
| 4. 가설 수립 | 원인 가설 먼저 | 수정 전 원인 가설을 Codex CLI에 먼저 설명 요청 |
| 5. 수정 후 검증 | DoD 재확인 | 해당 FR의 DoD 체크리스트를 다시 통과하는지 확인 |

---

## 7. 비기능 요구사항 (Non-Functional Requirements)

### 7.1 성능

| 항목 | 기준 |
|---|---|
| 응답 지연 | 질문 전송 후 첫 토큰 출력까지 3초 이내 (스트리밍 시작 기준) |
| 문서 파싱 처리 시간 | 20페이지 이내 문서 기준 30초 이내 색인 완료 |
| 목록 조회 응답 시간 | 1초 이내 |
| 동시 사용자 | 1인 기준 (학습/PoC 프로젝트) |
| 안정성 | 동일 질문 반복 시 일관된 근거 기반 답변 (랜덤하게 다른 문서를 근거로 들지 않음) |
| 정직성(Honesty) | 근거가 부족한 경우 추측 답변 대신 "확인 불가" 응답 우선 |

### 7.2 보안

| 항목 | 요구사항 |
|---|---|
| API Key 관리 | `.env` 파일 또는 배포 환경변수에만 저장, 소스코드·프론트 번들 노출 금지 |
| 파일 업로드 검증 | 파일 형식(MIME) 및 크기(20MB) 서버 측 재검증 필수 |
| 인증 | 1차 범위 제외 (로컬/비공개 URL 운영으로 대체) |
| 업로드 문서 취급 | 업로드 원본은 서버 임시 경로에만 저장, 외부 전송은 Upstage API 호출로 한정 |

### 7.3 가용성 및 데이터 영속성

| 방안 | 설명 | 난이도 | 권장 |
|------|------|--------|------|
| 인메모리 벡터 스토어 (FAISS/Chroma in-memory) | 서버 재시작 시 색인 소실, 재업로드 필요 | ⭐ 쉬움 | MVP 1순위 (본 PRD 기본) |
| Chroma persist 디렉토리 | 로컬 디스크에 색인 영속화 | ⭐⭐ 보통 | 로컬 상시 사용 시 |
| 외부 벡터 DB (Qdrant, pgvector 등) | 서버 독립 영속 저장 | ⭐⭐⭐ 어려움 | 장기 운영 시 |

> **MVP 기본 채택**: 인메모리 스토어. 서버 재시작 시 색인이 사라진다는 한계를 사용자에게 UI로 안내한다.

### 7.4 공통 오류 처리 기준

> Codex CLI가 컴포넌트마다 일관된 방식으로 오류를 처리하도록 전체 공통 기준을 정의한다.

| 오류 유형 | 처리 방식 | UI 표현 |
|----------|----------|--------|
| 네트워크 단절 | 요청 중단 + 재시도 버튼 제공 | 빨간 Toast + 재시도 버튼 |
| API 4xx 오류 | 사용자 친화적 메시지 표시 | 노란 Toast |
| API 5xx 오류 (파싱/LLM 실패 포함) | 재시도 안내 메시지 표시 | 빨간 Toast + 재시도 버튼 |
| 스트리밍 중단 | 부분 답변 유지 + "응답이 중단되었습니다" 안내 | 인라인 경고 텍스트 |
| 로딩 중 중복 요청 | 버튼 비활성화로 중복 방지 | `disabled` + `opacity-50 cursor-not-allowed` |
| 파일 형식/크기 오류 | 업로드 즉시 차단 + 안내 메시지 | 빨간 인라인 메시지 |

**Toast 공통 규칙**: 자동 소멸 3초 / 위치 `fixed bottom-4 right-4` / 중복 발생 시 최신 메시지만 표시

### 7.5 유지보수성

- 백엔드와 프론트엔드를 독립 디렉토리(`backend/`, `frontend/`)로 분리
- 환경변수는 `.env` 파일로 중앙 관리 (`.env.example` 동봉)
- LangGraph 노드·외부 API 연동 로직은 `services/` 레이어로 분리하여 교체 용이하게 구성
- 그래프 정의(State/Node/Edge)는 단일 모듈(`graph.py`)에 응집

---

## 8. 범위 외 항목 (Out of Scope) — 프로그램 개요서 동일

- 스캔본 등 이미지 전용 문서의 고급 OCR
- 다중 사용자 권한 관리 / 조직 단위 협업
- 영구 데이터베이스 기반 영속 저장
- 다국어 지원 확장
- 모바일 앱

---

## 9. 데이터 구조 (Data Schema)

### 9.1 문서 메타데이터 스키마

```json
{
  "documentId": "uuid-v4-string",
  "filename": "2025_사업계획서.pdf",
  "fileType": "pdf",
  "status": "processing | indexed | failed",
  "pageCount": 24,
  "chunkCount": 87,
  "failReason": "string or null",
  "uploadedAt": "2026-07-06T10:30:00Z",
  "indexedAt": "2026-07-06T10:30:45Z"
}
```

### 9.2 청크(Chunk) 스키마 — 벡터 스토어 메타데이터

```json
{
  "chunkId": "uuid-v4-string",
  "documentId": "uuid-v4-string",
  "documentName": "2025_사업계획서.pdf",
  "page": 12,
  "content": "3분기 매출은 42억원으로 전년 대비 18% 증가...",
  "embedding": "[float 배열 — Solar Embedding 차원 수와 일치]"
}
```

### 9.3 채팅 메시지 스키마

```json
{
  "messageId": "uuid-v4-string",
  "conversationId": "uuid-v4-string",
  "role": "user | assistant",
  "content": "3분기 매출은 42억원입니다.",
  "sources": [
    { "documentName": "2025_사업계획서.pdf", "page": 12 }
  ],
  "grounded": true,
  "retryCount": 0,
  "createdAt": "2026-07-06T10:35:00Z"
}
```

### 9.4 저장 구조

- **벡터 스토어**: 인메모리 (FAISS 또는 Chroma in-memory) — 서버 재시작 시 소실
- **문서 메타데이터**: 백엔드 인메모리 dict (documentId 키)
- **대화 이력**: 프론트엔드 상태(React state)로만 유지, 새로고침 시 초기화
- **ID 생성**: UUID v4 (서버 측), **타임스탬프**: ISO 8601 (UTC)

---

## 10. 기술 스택 및 의존성 (Tech Stack)

| 구분 | 기술 | 버전 |
|------|------|------|
| 백엔드 | Python FastAPI | v0.111+ |
| 에이전트 오케스트레이션 | LangGraph | v0.2+ |
| LLM 연동 | langchain-upstage | 최신 (Phase 0에서 확정) |
| 문서 파싱 | Upstage Document Parse | API |
| 임베딩 | Solar Embedding (한국어 특화) | API |
| 답변 생성 | Solar Pro 3 | API |
| 근거 검증 | Upstage Groundness Check | API |
| 벡터 스토어 | FAISS (in-memory) | Phase 0에서 확정 |
| 프론트엔드 | ReactJS | v18+ |
| 빌드 도구 | Vite | v5+ |
| 스타일링 | TailwindCSS | v3+ |
| HTTP 클라이언트 | Axios | v1+ |
| 버전 관리 | GitHub | main 브랜치 |

> 정확한 버전 조합은 Phase 0 사전 기술 검증에서 확정하고 `backend/requirements.txt` / `package.json`에 고정(pin)한다 — "조사 먼저, 구현 나중" 원칙.

---

## 11. 환경변수 명세

| 변수명 | 설명 | 적용 위치 |
|--------|------|----------|
| `UPSTAGE_API_KEY` | Upstage API 인증 키 (Parse/Embedding/Solar/Groundness 공용) | 백엔드 `.env` |
| `VITE_API_BASE_URL` | 백엔드 API 기본 URL (로컬: `http://localhost:8000`) | 프론트 `.env` (빌드 시 주입) |
| `MAX_UPLOAD_MB` | 업로드 최대 용량 (기본 20) | 백엔드 `.env` |
| `MAX_RETRY_COUNT` | Groundness 실패 시 최대 재시도 횟수 (기본 2) | 백엔드 `.env` |

> `.env`는 `.gitignore`에 반드시 포함하고, 키 없이 구조만 담은 `.env.example`을 레포에 동봉한다.
> 로컬 FastAPI 앱은 `backend/main.py` 시작 시 프로젝트 루트 `.env`를 라우터 import 전에 로드한다. 기본 문서 파이프라인이 import 시점에 생성되므로 `UPSTAGE_API_KEY`가 먼저 주입되어야 한다.

---

## 12. 프로젝트 디렉토리 구조

```
rag-qa-app/
├── frontend/
│     ├── src/
│     │     ├── pages/
│     │     │     ├── Dashboard.jsx        # 메인 대시보드 (/)
│     │     │     ├── DocumentsPage.jsx    # 문서 관리 (/documents)
│     │     │     └── ChatPage.jsx         # Q&A 채팅 (/chat)
│     │     ├── components/
│     │     │     ├── DropZone.jsx
│     │     │     ├── DocumentTable.jsx
│     │     │     ├── StatusBadge.jsx
│     │     │     ├── ChatMessageList.jsx
│     │     │     ├── SourceChip.jsx
│     │     │     ├── GroundnessLabel.jsx
│     │     │     ├── ChatInput.jsx
│     │     │     ├── Modal.jsx
│     │     │     └── Toast.jsx
│     │     └── api/
│     │           └── axios.js             # Axios 인스턴스 및 API 함수
│     ├── package.json
│     └── vite.config.js
├── backend/
│     ├── main.py                          # FastAPI 앱 진입점 (CORS, 라우터 등록)
│     ├── routers/
│     │     ├── documents.py               # POST/GET/DELETE /api/documents
│     │     └── chat.py                    # POST /api/chat (SSE 스트리밍)
│     ├── graph/
│     │     ├── state.py                   # LangGraph State 정의
│     │     ├── nodes.py                   # 8개 Node 함수
│     │     └── graph.py                   # Edge/Routing 및 그래프 조립
│     ├── services/
│     │     ├── parse_service.py           # Upstage Document Parse 연동
│     │     ├── embedding_service.py       # Solar Embedding + 벡터 스토어
│     │     ├── llm_service.py             # Solar Pro 3 호출
│     │     └── groundness_service.py      # Groundness Check 연동
│     ├── .env.example
│     └── requirements.txt
└── README.md
```

---

## 13. 개발 일정 및 완료 기준 (1일 스프린트)

> Phase 완료 시 해당 Phase의 완료 체크뿐 아니라, 연결된 FR이 있는 경우 `PRD_01_기획_기능요구사항.md`의 **3. 기능 요구사항 (Functional Requirements) & DoD** 항목도 함께 체크한다.

> **전체 개발 타임라인**
>
> ```
> [Phase 0] 사전 기술 검증           ── 0.5h
> [Phase 1] 환경 설정                ── 0.5h
> [Phase 2] 파싱·색인 파이프라인      ── 1.5h
> [Phase 3] LangGraph RAG 그래프    ── 2.5h
> [Phase 4] 백엔드 API 조립          ── 1.0h
> [Phase 5] 프론트 환경 설정         ── 0.5h
> [Phase 6] 문서 관리 화면           ── 1.0h
> [Phase 7] Q&A 채팅 화면           ── 1.5h
> [Phase 8] 통합 E2E 검증           ── 1.0h
>                                   ────────
>                                   총 10.0h
> ```

### Phase 0 — 사전 기술 검증 (0.5h)

> **원칙 ②: 새로운 기술을 붙이기 전 5분 조사로 1시간 디버깅을 방지한다.**

| # | 검증 항목 | 확인 방법 | 완료 기준 |
|---|----------|----------|---------|
| 0-1 | Upstage API Key 유효성 | `curl`로 단순 호출 테스트 | 200 응답 확인 |
| 0-2 | Document Parse 응답 구조 | 표 포함 샘플 PDF 1건 파싱 | Markdown 내 표 구조 확인 |
| 0-3 | Solar Embedding 차원 수 | 샘플 텍스트 임베딩 호출 | 차원 수 기록 → 벡터 스토어 설정 반영 |
| 0-4 | LangGraph + langchain-upstage 버전 호환성 | 의존성 설치 후 임포트 테스트 | 임포트 오류 없음 |
| 0-5 | Solar Pro 3 스트리밍 | 스트리밍 옵션 테스트 호출 | 토큰 단위 수신 확인 |

**완료 기준**
- [ ] 4개 Upstage API(Parse/Embedding/Solar/Groundness) 모두 테스트 호출 성공
- [x] 확정 버전 조합을 `backend/requirements.txt`에 고정

**Phase 0 처리 기록 (2026-07-13)**
- [x] `UPSTAGE_API_KEY` 환경변수 존재 확인 (`.env` 값은 출력하지 않음)
- [x] Python 3.12.7 기준 핵심 패키지 임포트 가능 확인: FastAPI, LangGraph, langchain-upstage, FAISS, requests
- [x] 벡터 스토어는 Phase 0 기준 FAISS in-memory로 확정
- [x] 검증 스크립트 추가: `python scripts/phase0_upstage_check.py`
- [x] Upstage Document Parse 실호출 성공: 샘플 PDF 표 텍스트 감지
- [x] Solar Embedding 실호출 성공: `solar-embedding-1-large-query`, 4096차원
- [x] Solar Pro3 스트리밍 실호출 성공: 토큰 이벤트 수신
- [ ] Groundness Check 실호출 미완료: `/groundedness-check` 경로가 404를 반환해 최신 API 경로 확인 필요

### Phase 1 — 환경 설정 (0.5h)

- GitHub 레포 생성, `.gitignore`(.env 포함), 디렉토리 구조 생성, 가상환경 + 패키지 설치
- **완료 기준**: `uvicorn backend.main:app --reload` 기동, `/docs` Swagger 접근 가능

**Phase 1 처리 기록 (2026-07-13)**
- [x] `.gitignore`에 `.env`, Python 캐시, Node 의존성 제외 규칙 확인
- [x] `requirements.txt` 기준 백엔드 의존성 고정 확인
- [x] PRD 구조에 맞춰 `backend/`, `backend/routers/`, `backend/graph/`, `backend/services/`, `backend/tests/` 생성
- [x] FastAPI 진입점 추가: `backend/main.py`
- [x] `uvicorn backend.main:app --reload` 기동 및 `/docs` Swagger 접근 확인 (`DOCS_STATUS=200`)

### Phase 2 — 파싱·색인 파이프라인 (1.5h) — FR-1, FR-2

- parse_service / embedding_service 구현, 업로드 → 파싱 → 청크 → 색인 자동 연결
- **완료 기준**: FR-1, FR-2의 DoD 전부 체크

**Phase 2 처리 기록 (2026-07-13)**
- [x] `backend/services/parse_service.py` 구현: PDF/DOCX/HTML 확장자 검증, Upstage Document Parse 연동, Markdown 추출
- [x] `backend/services/embedding_service.py` 구현: Markdown 청크 분할, Solar Embedding 연동, FAISS in-memory 색인
- [x] `backend/services/pipeline.py` 구현: 업로드 → 파싱 → 청크 → 임베딩 → 색인 자동 연결
- [x] `backend/routers/documents.py` 구현: `POST/GET/DELETE /api/documents`
- [x] 동일 파일명 중복 업로드는 UUID 기반 서로 다른 문서로 관리
- [x] 문서 삭제 시 메타데이터와 FAISS 벡터를 함께 제거
- [x] `PRD_01_기획_기능요구사항.md`의 FR-1, FR-2 사전 조사 및 DoD 체크 완료
- [x] `python -m pytest backend/tests` 통과 (`7 passed`)

### Phase 3 — LangGraph RAG 그래프 (2.5h) — FR-3, FR-4, FR-5

- State/8개 Node/Routing 구현, Groundness 재시도 루프 포함
- **완료 기준**: FR-3~FR-5의 DoD 전부 체크 (정상 경로 + 재시도 경로 테스트)

### Phase 4 — 백엔드 API 조립 (1.0h)

- documents/chat 라우터 구현, SSE 스트리밍 연결
- **완료 기준**: 4개 엔드포인트 `curl`/Postman 정상 응답, 4장 API 명세와 일치

### Phase 5 — 프론트 환경 설정 (0.5h)

- Vite + React + Tailwind + Router(3개 경로) + Axios 인스턴스 + Pretendard 폰트
- **완료 기준**: `npm run dev` 기동, Tailwind 클래스 적용, 3개 경로 라우팅

**Phase 5 처리 기록 (2026-07-13)**
- [x] `frontend/package.json`에 Vite, React 18, React Router, Axios, TailwindCSS 의존성 및 `dev`/`build`/`preview` 스크립트 정의 완료
- [x] `frontend/src/main.jsx`에 React 진입점과 `BrowserRouter` 연결 완료
- [x] `frontend/src/App.jsx`에 `/`, `/documents`, `/chat` 3개 경로 라우팅 구성 완료
- [x] `frontend/src/styles.css`, `frontend/tailwind.config.js`, `frontend/postcss.config.js`에 TailwindCSS 및 Pretendard 폰트 설정 완료
- [x] `frontend/src/api/axios.js`에 `VITE_API_BASE_URL` 기반 Axios 인스턴스 구성 완료
- [ ] `npm run dev` 실제 기동 검증은 `frontend/node_modules` 미설치 상태라 의존성 설치 후 확인 필요

### Phase 6 — 문서 관리 화면 (1.0h) — FR-6

- **완료 기준**: FR-6 DoD 전부 체크
- [x] PDF 업로드 시 `missing_upstage_api_key`가 발생하지 않도록 FastAPI 시작 시 프로젝트 루트 `.env` 선로딩 처리

### Phase 7 — Q&A 채팅 화면 (1.5h) — FR-7

- **완료 기준**: FR-7 DoD 전부 체크 (스트리밍·출처·Groundness 라벨 표시)

### Phase 8 — 통합 E2E 검증 (1.0h)

#### 8-1. 배포 설정 (선택 — 로컬 검증 후 진행)

> 본 PRD는 로컬 개발 환경을 우선하되, 프론트엔드는 Vercel, 백엔드는 별도 서버(Railway/Render 등) 배포를 검토한다. 인메모리 벡터 스토어 특성상 서버리스 환경에서는 색인이 소실되므로, 백엔드는 상태를 유지하는 일반 서버 배포를 권장한다.

| # | 작업 | 내용 | 상태 |
|---|------|------|------|
| 8-1-1 | 프론트 빌드 배포 | Vercel에 `frontend/` 정적 빌드 연결 | ⬜ 수동 |
| 8-1-2 | 백엔드 서버 배포 | Railway/Render 등 상태 유지 서버에 FastAPI 배포 | ⬜ 수동 |
| 8-1-3 | GitHub 레포 연동 | Vercel 프로젝트 생성 → GitHub Import | ⬜ 수동 |
| 8-1-4 | 환경변수 등록 | 각 배포 환경 대시보드에 키 등록 | ⬜ 수동 |
| 8-1-5 | 첫 배포 실행 | `git push origin main` → 자동 빌드 트리거 | ⬜ 수동 |

##### 배포 등록 필수 환경변수

| 키 | 값 | 적용 위치 | 비고 |
|----|-----|----------|------|
| `UPSTAGE_API_KEY` | `up_xxx...` | 백엔드 | Upstage 콘솔에서 복사 (Parse/Embedding/Solar/Groundness 공용) |
| `MAX_UPLOAD_MB` | `20` | 백엔드 | 업로드 최대 용량 |
| `MAX_RETRY_COUNT` | `2` | 백엔드 | Groundness 실패 시 최대 재시도 횟수 |
| `VITE_API_BASE_URL` | 배포된 백엔드 URL | 프론트 빌드 시 주입 | 로컬은 `http://localhost:8000` |

> ⚠️ 인메모리 색인은 서버 재시작 시 소실되므로(7.3절), 서버리스가 아닌 상태 유지 서버 배포를 사용하거나 Chroma persist / 외부 벡터 DB로 전환한다.

#### 8-2. E2E 시나리오 검증 체크리스트

| # | 시나리오 | 기대 결과 | 우선도 |
|---|----------|----------|--------|
| E2E-01 | 표 포함 PDF 업로드 → 색인 | 상태가 처리중 → 완료로 전환, 표 구조 보존 확인 | Must |
| E2E-02 | 문서 내 존재하는 사실 질문 | 정답 + 출처(문서명·페이지) + ✅ 근거 확인됨 | Must |
| E2E-03 | 문서에 없는 내용 질문 | 지어내지 않고 "확인 불가" 안내 | Must |
| E2E-04 | 모호한 질문 (재시도 유도) | 쿼리 재작성 → 재검색 흐름 후 답변 또는 확인 불가 | Must |
| E2E-05 | DOCX / HTML 업로드 | PDF와 동일하게 색인·질의 가능 | Should |
| E2E-06 | 문서 삭제 후 동일 질문 | 삭제 문서를 근거로 답변하지 않음 (orphan 벡터 없음) | Should |
| E2E-07 | 20MB 초과 / 미지원 형식 업로드 | 오류 메시지 표시, 업로드 차단 | Must |
| E2E-08 | 답변 생성 중 중복 전송 시도 | 입력창 비활성화로 중복 요청 차단 | Should |

**완료 기준**
- [ ] Must 시나리오(E2E-01~04, 07) 전부 통과
- [ ] 브라우저 콘솔에 CORS/미처리 오류 없음
- [ ] Master Checklist(0장) Must Have 전 항목 체크

---

## 14. 리스크 및 대응 방안

| 리스크 | 영향 | 대응 방안 |
|--------|------|----------|
| 인메모리 색인 소실 (서버 재시작) | 재업로드 필요 | UI에 한계 안내, 필요 시 Chroma persist로 전환 (7.3절) |
| Upstage API 응답 지연/초과 | 파싱·답변 실패 | 타임아웃 설정(파싱 60초/생성 30초), 재시도 안내 표시 |
| Groundness 재시도 무한 루프 | 응답 불가 | `MAX_RETRY_COUNT` 환경변수로 상한 강제, 초과 시 "확인 불가" 응답 |
| 임베딩 차원/버전 비호환 | 색인·검색 전면 실패 | Phase 0 사전 검증으로 선제 차단, 버전 고정 |
| 대용량 문서 파싱 시간 초과 | 사용자 이탈 | 페이지 수 상한 안내, 진행 상태 실시간 표시 |
| 1일 스프린트 일정 초과 | 기능 미완성 | Should/Could Have 후순위 처리, Must Have 우선 완료 (3.0절 우선순위 준수) |

---

## 15. 용어 정의

| 용어 | 설명 |
|------|------|
| RAG | Retrieval-Augmented Generation, 검색 결과를 근거로 답변을 생성하는 기법 |
| LangGraph | State/Node/Edge로 LLM 워크플로우를 그래프로 구성하는 오케스트레이션 프레임워크 |
| Self-Correcting RAG | 검색·답변 품질을 자체 평가하고 실패 시 쿼리 재작성 후 재시도하는 RAG 구조 |
| Groundness Check | 생성된 답변이 근거 문서에 실제로 부합하는지 판정하는 검증 단계 |
| 청크(Chunk) | 임베딩·검색 단위로 분할된 문서 조각 |
| 임베딩(Embedding) | 텍스트를 의미 기반 벡터로 변환하는 과정 |
| SSE | Server-Sent Events, 서버→클라이언트 단방향 스트리밍 프로토콜 |
| Hallucination | LLM이 근거 없이 사실처럼 지어낸 답변 |
| DoD | Definition of Done, 기능의 완료 판정 기준 체크리스트 |
| MVP | Minimum Viable Product, 최소 기능 제품 |

---

## 16. 다음 단계

- [ ] FR별 Codex CLI 프롬프트 초안 작성 (사전 조사 단계 포함)
- [ ] LangGraph State/Node 스키마 상세 설계
- [ ] API 명세 확정 후 프론트엔드 Mock 데이터 기준 화면 개발 착수

---

*본 문서는 초안(Draft)이며, 구현 과정에서 사전 조사 결과에 따라 세부 사항이 갱신될 수 있습니다.*
*v0.1: 최초 작성 (FR·DoD·API·화면 명세) | v0.2: 목표 지표, 페르소나, 기능 우선순위, 데이터 구조, 기술 스택·환경변수·디렉토리 구조, Phase별 일정(Phase 0 포함), E2E 체크리스트, 리스크, 용어 정의, 공통 오류 처리 기준, 컴포넌트 스타일 명세 추가 | v0.3: 개발 기간 명시, 문제 정의·솔루션 섹션(1.1~1.2), 디자인 원칙 '빠른 피드백'·'모바일 우선' 추가, Phase 8 Vercel/서버 배포 설정 및 환경변수 등록 표 추가*
