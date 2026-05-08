# Backend Draft

자연어 일정 관리 앱의 FastAPI 백엔드 초안입니다.

현재 구현은 `backend/` 폴더 안에 있습니다.

## 현재 구현된 것

- Upstage `solar-pro3` 기반 자연어 일정 분석
- LangGraph를 이용한 간단한 분석 흐름
- 분석 결과를 프론트 폼에서 쓰기 쉬운 JSON으로 반환
- 부족한 정보 재질문을 위한 분석 컨텍스트 반환 (2026-05-08 수정)
- 사용자가 확인한 일정 SQLite 저장
- 저장된 일정 수정/삭제 (2026-05-08 수정)
- 저장된 일정 목록 조회
- Swagger API 문서 제공

## 실행

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

`.env`에 Upstage API 키를 넣은 뒤 실행합니다.

```bash
.venv/bin/uvicorn app.main:app --reload
```

Swagger 문서:

```text
http://127.0.0.1:8000/docs
```

## 주요 API

- `GET /health`
- `POST /api/schedules/analyze`
- `POST /api/schedules`
- `GET /api/schedules`
- `PATCH /api/schedules/{schedule_id}`
- `DELETE /api/schedules/{schedule_id}`

## 변경 이력

- 2026-05-08: 분석 컨텍스트, 구조화 메타 필드, 일정 수정/삭제, 예외 검증 추가
- 2026-05-08: 분석 완료 후 확인 메시지를 `아래 일정으로 등록할까요?`로 변경

자세한 API 예시와 폴더 구조는 [backend/README.md](backend/README.md)를 확인하세요.
