# PRD ② 기술 명세 & 화면 명세
## 문서 기반 RAG Q&A 앱

> 본 문서는 전체 PRD를 3부로 분리한 것 중 **2부(기술·화면)** 입니다.
> ① 제품 기획 & 기능 요구사항 · ③ 개발 프로세스 & 일정 문서와 함께 참조하세요.

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
| Response (스트리밍, 200, `text/event-stream`) | SSE `status` → `token` 반복 → `final` 순서로 전송, 오류 시 `error` 이벤트 전송 |
| Token 이벤트 예시 | `event: token`, `data: { "token": "string" }` |
| 최종 이벤트 예시 | `event: final`, `data: { "answer": "string", "sources": [{ "documentName": "string", "page": number }], "grounded": boolean, "groundness": "grounded", "conversationId": "string" }` |
| Response (근거 없음) | `grounded: false` + 안내 문구 반환 (답변을 지어내지 않음) |

> API 명세는 1차 초안이며, FR-1~FR-5 구현 과정에서 세부 필드가 조정될 수 있습니다. 변경 시 본 문서를 갱신합니다.


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
| 에이전트 오케스트레이션 | LangGraph | 1.1.6 |
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
