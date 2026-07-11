# Repository Guidelines

## 프로젝트 구조 및 모듈 구성

이 저장소는 RAG 기반 Q&A 애플리케이션의 PRD와 초기 개발 문서를 중심으로 구성되어 있습니다. 요구사항과 API 계약은 `PRD_00_메인.md`, `PRD_01_기획_기능요구사항.md`, `PRD_02_기술_화면명세.md`, `PRD_03_개발프로세스_일정.md`를 기준으로 확인합니다.

구현 시 백엔드는 `backend/`, 프론트엔드는 `frontend/` 아래에 분리합니다. FastAPI 라우터, 서비스, LangGraph 기반 RAG 흐름, 테스트는 `backend/`에 둡니다. React/Vite/Tailwind 화면, 컴포넌트, API 클라이언트는 `frontend/src/`에 둡니다. 업로드 파일과 생성 인덱스는 Git 추적 대상에서 제외합니다.

## 빌드, 테스트, 개발 명령

현재 저장소에는 실행 가능한 애플리케이션 패키지 설정이 아직 없습니다. 앱 스캐폴딩 후 하위 README 또는 패키지 스크립트를 기준으로 문서화합니다. 예상 개발 진입점은 다음과 같습니다.

```bash
# 프론트엔드 Vite 개발 서버 실행
cd frontend && npm run dev

# 백엔드 FastAPI 개발 서버 실행
cd backend && uvicorn app.main:app --reload
```

테스트, 린트, 포맷 명령은 동작 확인 후 문서에 추가합니다.

## 코딩 스타일 및 네이밍 규칙

프로젝트 도구가 추가되면 해당 설정을 우선합니다. Python은 4칸 들여쓰기, 모듈·함수·변수는 `snake_case`를 사용합니다. React 컴포넌트는 `PascalCase`, TypeScript 변수와 함수는 `camelCase`를 사용합니다. 라우트 모듈은 `documents.py`처럼 리소스명으로 작성하고, API 경로는 PRD의 `/api/documents`, `/api/chat` 형식을 유지합니다.

## 테스트 지침

백엔드 테스트는 `backend/tests/`에 배치하고, 프론트엔드 테스트는 컴포넌트 옆 또는 `frontend/src/**/*.test.*` 패턴으로 둡니다. 테스트명은 동작 중심으로 작성합니다. 예: `test_retries_when_groundness_check_fails`. 정상 RAG 응답, 재시도, 근거 부족 응답 경로를 검증합니다. 리뷰 요청 전 관련 단위 테스트와 업로드부터 채팅까지의 핵심 흐름을 확인합니다.

## 커밋 및 Pull Request 지침

현재 Git 이력에는 `Initial commit`만 있어 고정된 커밋 규칙은 없습니다. 커밋 메시지는 명령형의 짧은 제목을 사용합니다. 예: `feat: add document upload route`, `fix: handle empty retrieval results`. Pull Request에는 변경 사항, 관련 요구사항 또는 이슈, 검증한 명령, UI 변경 시 스크린샷을 포함합니다.

## 보안 및 설정

필요할 때만 `.env.example`을 참고해 로컬 `.env`를 만들고, 비밀값·API 키·업로드 문서·벡터 스토어 데이터는 커밋하지 않습니다. 파일 업로드와 외부 API 입력은 검증 로직을 거치도록 설계합니다. 로그에는 인증 정보나 문서 원문이 노출되지 않도록 마스킹을 적용합니다.
