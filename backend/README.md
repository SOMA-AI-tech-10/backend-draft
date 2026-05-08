# Kairos Schedule Agent Backend

자연어로 입력한 일정을 AI가 JSON 형태로 정리하고, 사용자가 확인한 일정을 로컬 SQLite에 저장하는 FastAPI 백엔드 초안입니다.

현재 목표는 프론트엔드에서 확인 카드/폼과 달력 화면을 붙일 수 있는 최소 API를 제공하는 것입니다.

## 구현된 범위

- FastAPI 서버 기본 구성
- Upstage `solar-pro3` API를 이용한 자연어 일정 분석
- LangGraph를 이용한 아주 얇은 분석 흐름 구성
- 분석 결과를 프론트 폼에서 쓰기 쉬운 JSON으로 반환
- 부족한 정보 재질문을 위한 분석 컨텍스트 반환 (2026-05-08 수정)
- 사용자가 승인한 일정 SQLite 저장
- 저장된 일정 수정/삭제 (2026-05-08 수정)
- 저장된 일정 목록 조회
- Swagger 문서 제공

## 아직 제외한 범위

- 로그인/회원 관리
- Google Calendar, Apple Calendar 실제 연동
- 모바일 푸시 알림
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

2026-05-08 수정: 재질문 멀티턴을 위해 `analysis_context`를 요청/응답에 추가했습니다. 첫 요청에서는 `analysis_context`를 생략하거나 `null`로 보내고, 후속 답변에서는 직전 응답의 `analysis_context`를 그대로 다시 보내면 됩니다.

요청 예시:

```json
{
  "text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘",
  "timezone": "Asia/Seoul",
  "analysis_context": null
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
    "reminder_minutes": 30,
    "schedule_type": "appointment"
  },
  "missing_fields": [],
  "needs_confirmation": true,
  "analysis_context": {
    "original_text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘",
    "latest_user_text": "내일 오후 3시에 치과 예약, 30분 전에 알려줘",
    "schedule": {
      "title": "치과 예약",
      "start_at": "2026-05-08T15:00:00+09:00",
      "end_at": null,
      "location": "치과",
      "reminder_minutes": 30,
      "schedule_type": "appointment"
    },
    "missing_fields": [],
    "timezone": "Asia/Seoul",
    "turn_count": 1
  },
  "message": "아래 일정으로 등록할까요?"
}
```

`missing_fields`에 `title` 또는 `start_at`이 포함되면 프론트에서 추가 질문을 보여주고, 모든 필수 정보가 있으면 `needs_confirmation`이 `true`로 내려옵니다.

후속 답변 예시:

```json
{
  "text": "오후 3시야",
  "timezone": "Asia/Seoul",
  "analysis_context": {
    "original_text": "내일 병원 알림 맞춰줘",
    "latest_user_text": "내일 병원 알림 맞춰줘",
    "schedule": {
      "title": "병원 방문",
      "start_at": null,
      "end_at": null,
      "location": null,
      "reminder_minutes": null,
      "schedule_type": "appointment"
    },
    "missing_fields": ["start_at"],
    "timezone": "Asia/Seoul",
    "turn_count": 1
  }
}
```

이 경우 백엔드는 기존 후보 일정에 `"오후 3시야"`를 병합해서 `start_at`을 채운 새 `schedule`과 갱신된 `analysis_context`를 반환합니다.

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
  "schedule_type": "appointment",
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
  "schedule_type": "appointment",
  "status": "confirmed"
}
```

`end_at`이 `null`이면 백엔드에서 기본 1시간 일정으로 저장합니다.

저장 시 다음 예외를 검증합니다.

- 제목이 비어 있으면 저장하지 않습니다.
- 종료 시간이 시작 시간보다 빠르거나 같으면 저장하지 않습니다.
- 이미 지난 일정은 저장하지 않습니다.
- 알림 시간이 이미 지난 경우 저장하지 않습니다.

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
    "schedule_type": "appointment",
    "status": "confirmed"
  }
]
```

### `PATCH /api/schedules/{schedule_id}`

2026-05-08 수정: 일정 수정 API를 추가했습니다.

저장된 일정을 부분 수정합니다. 수정 가능한 필드는 `title`, `start_at`, `end_at`, `location`, `reminder_minutes`, `schedule_type`, `original_text`, `status`입니다.

요청 예시:

```json
{
  "title": "치과 정기검진",
  "reminder_minutes": 60
}
```

### `DELETE /api/schedules/{schedule_id}`

2026-05-08 수정: 일정 삭제 API를 추가했습니다.

저장된 일정을 삭제합니다. 성공 시 응답 본문 없이 `204 No Content`를 반환합니다.

## 변경 이력

- 2026-05-08: 분석 응답에 `missing_fields`, `needs_confirmation`, `schedule_type` 추가
- 2026-05-08: 재질문 멀티턴용 `analysis_context` 추가
- 2026-05-08: 일정 수정/삭제 API 추가
- 2026-05-08: 일정 저장/수정 예외 검증 추가
- 2026-05-08: 분석 완료 후 확인 메시지를 `아래 일정으로 등록할까요?`로 변경

## 현재 처리하지 못하는 것

1.
사용자: 내일 오후 4시 치과 약속 예약해줘.
AI: 처리 완료
사용자: 방금 추가한 일정을 다음주 다다음주에도 추가해줘.

의 시퀀스는 아직 제대로 처리 불가.

2. get을 하니까 일정이 이미 있는 시간에도 일정이 들어가는 버그
- 충돌 여부를 확인해주는 로직도 고도화한다면 필요

## 프론트엔드 연동 흐름

```text
1. 사용자가 자연어 입력
2. POST /api/schedules/analyze 호출
3. 응답의 schedule 객체로 확인 카드/폼 표시
4. missing_fields가 있으면 추가 질문 표시
5. null 필드는 프론트에서 빈칸으로 표시
6. 사용자가 확인 또는 수정 후 등록 클릭
7. POST /api/schedules 호출
8. GET /api/schedules로 달력에 일정 표시
9. 필요하면 PATCH 또는 DELETE로 일정 수정/삭제
```

## 참고

- 현재 DB는 로컬 `schedules.db` 파일입니다.
- `.env`와 `schedules.db`는 Git에 올리지 않습니다.
- 현재 서버 루트(`/`)는 별도 화면이 없어서 404가 정상입니다.
