# Kairos Schedule Agent Backend

자연어로 입력한 일정을 AI가 JSON 형태로 정리하고, 사용자가 확인한 일정을 로컬 SQLite에 저장하는 FastAPI 백엔드 초안입니다.

현재 목표는 프론트엔드에서 확인 카드/폼과 달력 화면을 붙일 수 있는 최소 API를 제공하는 것입니다.

## 구현된 범위

- FastAPI 서버 기본 구성
- Upstage `solar-pro3` API를 이용한 자연어 일정 분석
- LangGraph를 이용한 아주 얇은 분석 흐름 구성
- 분석 결과를 프론트 폼에서 쓰기 쉬운 JSON으로 반환
- 사용자가 승인한 일정 SQLite 저장
- 저장된 일정 목록 조회
- Swagger 문서 제공

## 아직 제외한 범위

- 로그인/회원 관리
- Google Calendar, Apple Calendar 실제 연동
- 모바일 푸시 알림
- 일정 수정/삭제
- 반복 일정
- 그룹 가용시간 그리드
- WebSocket 실시간 동기화
- 복수 알람
- 이벤트 타입별 스마트 알림 기본값

## 폴더 구조

```text
backend/
  app/
    main.py                  # FastAPI 앱 진입점
    db.py                    # SQLite 연결
    models.py                # DB 모델
    schemas.py               # 요청/응답 스키마
    routes/
      schedules.py           # 일정 API 라우터
    services/
      ai_parser.py           # Upstage API 호출
      schedule_graph.py      # LangGraph 분석 흐름
      schedule_service.py    # 일정 저장/조회 로직
  requirements.txt
  .env.example
```

## 실행 방법

```bash
cd backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
```

`.env`에 Upstage API 키를 넣습니다.

```env
UPSTAGE_API_KEY=여기에_키_입력
UPSTAGE_BASE_URL=https://api.upstage.ai/v1
UPSTAGE_MODEL=solar-pro3
UPSTAGE_REASONING_EFFORT=high
DATABASE_URL=sqlite:///./schedules.db
DEFAULT_TIMEZONE=Asia/Seoul
```

서버 실행:

```bash
.venv/bin/uvicorn app.main:app --reload
```

실행 후 Swagger 문서는 아래에서 확인할 수 있습니다.

```text
http://127.0.0.1:8000/docs
```

## API 요약

### `GET /health`

서버 상태 확인용 API입니다.

응답 예시:

```json
{
  "status": "ok"
}
```

### `POST /api/schedules/analyze`

자연어 입력을 AI가 일정 JSON으로 변환합니다. 정보가 없으면 해당 필드는 `null`로 내려오고, 프론트에서 빈칸 폼으로 보여주면 됩니다.

요청 예시:

```json
{
  "text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘",
  "timezone": "Asia/Seoul"
}
```

응답 예시:

```json
{
  "original_text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘",
  "schedule": {
    "title": "치과 예약",
    "start_at": "2026-05-08T15:00:00+09:00",
    "end_at": null,
    "location": "치과",
    "reminder_minutes": 30
  },
  "message": "일정 정보를 확인해주세요."
}
```

### `POST /api/schedules`

프론트에서 사용자가 확인/수정한 일정을 SQLite에 저장합니다.

요청 예시:

```json
{
  "title": "치과 예약",
  "start_at": "2026-05-08T15:00:00+09:00",
  "end_at": null,
  "location": "치과",
  "reminder_minutes": 30,
  "original_text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘"
}
```

응답 예시:

```json
{
  "id": 1,
  "title": "치과 예약",
  "start_at": "2026-05-08T15:00:00",
  "end_at": "2026-05-08T16:00:00",
  "location": "치과",
  "reminder_minutes": 30,
  "status": "confirmed"
}
```

`end_at`이 `null`이면 백엔드에서 기본 1시간 일정으로 저장합니다.

### `GET /api/schedules`

저장된 일정을 시작 시간 오름차순으로 조회합니다.

응답 예시:

```json
[
  {
    "id": 1,
    "title": "치과 예약",
    "start_at": "2026-05-08T15:00:00",
    "end_at": "2026-05-08T16:00:00",
    "location": "치과",
    "reminder_minutes": 30,
    "status": "confirmed"
  }
]
```

## 프론트엔드 연동 흐름

```text
1. 사용자가 자연어 입력
2. POST /api/schedules/analyze 호출
3. 응답의 schedule 객체로 확인 카드/폼 표시
4. null 필드는 프론트에서 빈칸으로 표시
5. 사용자가 확인 또는 수정 후 등록 클릭
6. POST /api/schedules 호출
7. GET /api/schedules로 달력에 일정 표시
```

## 참고

- 현재 DB는 로컬 `schedules.db` 파일입니다.
- `.env`와 `schedules.db`는 Git에 올리지 않습니다.
- 현재 서버 루트(`/`)는 별도 화면이 없어서 404가 정상입니다.
