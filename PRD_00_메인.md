# PRD (Product Requirements Document)
## 문서 기반 RAG Q&A 앱

> 본 문서는 **메인(허브) 문서**입니다. 전체 개요와 각 세부 문서로의 진입점을 제공합니다.
> 상세 내용은 아래 3개의 분리된 문서를 참조하세요.

---

### 문서 정보

| 항목 | 내용 |
|---|---|
| 문서명 | 문서 기반 RAG Q&A 앱 — PRD |
| 상위 문서 | 프로그램 개요서 v0.1 |
| 작성 목적 | 기능 요구사항·완료 기준·화면/API 명세 정의 |
| 개발 방식 | Codex CLI 기반 바이브 코딩 (1일 스프린트) |
| 개발 기간 | 1일 단기 스프린트 (총 10.0h, ③ 개발프로세스 타임라인 참조) |
| 배포 목표 | 로컬 개발 환경 우선, 이후 Vercel(프론트) + 서버 배포 검토 |
| 버전 | v0.3 (Draft) |

---

## 문서 구성 (Document Map)

이 PRD는 독자와 참조 시점에 따라 3개 문서로 분리되어 있습니다.

| # | 문서 | 담은 내용 | 주 독자 / 사용 시점 |
|---|------|----------|-------------------|
| ① | [PRD_01 기획 & 기능요구사항](./PRD_01_기획_기능요구사항.md) | 제품 개요·문제·솔루션·지표, 사용자 시나리오, 기능 요구사항(FR+DoD), 비기능 요구사항, 범위 외, 용어 정의 | 기획 합의 · 무엇을 만들지 정의 |
| ② | [PRD_02 기술 & 화면명세](./PRD_02_기술_화면명세.md) | REST API 명세, 화면 명세(디자인·와이어프레임·컴포넌트), 데이터 스키마, 기술 스택, 환경변수, 디렉토리 구조 | 구현 · 프론트엔드 개발 시 참조 |
| ③ | [PRD_03 개발프로세스 & 일정](./PRD_03_개발프로세스_일정.md) | 바이브 코딩 3원칙·마스터 체크리스트, 디버깅 프로토콜, Phase별 일정·E2E 검증, 리스크, 다음 단계 | 스프린트 실행 · 관리 |

---

## 1. 제품 한눈에 보기 (At a Glance)

PDF·Word·HTML 문서를 업로드하면, AI가 문서 구조(표·레이아웃)를 보존한 채 내용을 파싱·색인하고, 사용자의 자연어 질문에 문서 근거와 출처를 함께 제시하며 답변하는 RAG(Retrieval-Augmented Generation) 기반 웹 애플리케이션.

**핵심 파이프라인**: `Document Parse → Solar Embedding → Solar Pro3 (답변 생성) → Groundness Check (근거 검증)`

> 문제 정의·솔루션·목표 지표 상세는 → [① 기획 & 기능요구사항](./PRD_01_기획_기능요구사항.md#1-제품-개요-product-summary)

---

## 2. 핵심 기능 요약 (Feature Overview)

| ID | 기능 | 우선순위 | 상세 |
|----|------|---------|------|
| M-01 | 문서 업로드 및 파싱 (FR-1) | Must Have | [① FR-1](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| M-02 | 임베딩 및 색인 (FR-2) | Must Have | [① FR-2](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| M-03 | RAG 답변 생성 + 스트리밍 (FR-3) | Must Have | [① FR-3](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| M-04 | 답변 근거 검증 Groundness Check (FR-4) | Must Have | [① FR-4](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| M-05 | LangGraph Self-Correcting 그래프 (FR-5) | Must Have | [① FR-5](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| M-06 | Q&A 채팅 화면 (FR-7) | Must Have | [① FR-7](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |
| S-01 | 문서 관리 화면 — 목록·삭제 (FR-6) | Should Have | [① FR-6](./PRD_01_기획_기능요구사항.md#3-기능-요구사항-functional-requirements--dod) |

> 전체 기능 목록·DoD 체크리스트는 → [① 기획 & 기능요구사항](./PRD_01_기획_기능요구사항.md)

---

## 3. 기술 스택 요약 (Tech Stack)

| 구분 | 기술 |
|------|------|
| 백엔드 | Python FastAPI + LangGraph |
| 문서 파싱 | Upstage Document Parse |
| 임베딩 / 생성 / 검증 | Solar Embedding · Solar Pro3 · Upstage Groundness Check |
| 벡터 스토어 | FAISS 또는 Chroma (in-memory) |
| 프론트엔드 | ReactJS + Vite + TailwindCSS + Axios |

> API 명세·데이터 스키마·환경변수·디렉토리 구조 상세는 → [② 기술 & 화면명세](./PRD_02_기술_화면명세.md)

---

## 4. 개발 타임라인 요약 (1일 스프린트)

```
[Phase 0] 사전 기술 검증           ── 0.5h
[Phase 1] 환경 설정                ── 0.5h
[Phase 2] 파싱·색인 파이프라인      ── 1.5h
[Phase 3] LangGraph RAG 그래프    ── 2.5h
[Phase 4] 백엔드 API 조립          ── 1.0h
[Phase 5] 프론트 환경 설정         ── 0.5h
[Phase 6] 문서 관리 화면           ── 1.0h
[Phase 7] Q&A 채팅 화면           ── 1.5h
[Phase 8] 통합 E2E 검증           ── 1.0h
                                  ────────
                                  총 10.0h
```

> Phase별 상세 완료 기준·E2E 체크리스트·바이브 코딩 원칙·리스크는 → [③ 개발프로세스 & 일정](./PRD_03_개발프로세스_일정.md)

---

## 5. 목표 지표 (Success Metrics)

| 지표 | 목표값 |
|---|---|
| 문서 파싱 성공률 | 표 포함 PDF·DOCX·HTML 기준 90% 이상 |
| 질문 → 첫 토큰 응답 시간 | 3초 이내 (스트리밍 시작 기준) |
| 근거 검증(Groundness) 통과율 | 색인 문서 내 답이 존재하는 질문 기준 85% 이상 |
| 환각 억제 | 근거 없는 질문에 "확인 불가" 응답률 100% |
| E2E 흐름 동작 | 1일 스프린트 내 완료 |

---

*본 문서는 초안(Draft)이며, 구현 과정에서 사전 조사 결과에 따라 세부 사항이 갱신될 수 있습니다.*
*메인 문서는 요약·진입점 역할만 하며, 상세 정의는 각 세부 문서(①②③)를 정본(正本)으로 합니다.*
