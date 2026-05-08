# Kairos 기획서 플로우 실행 로그

- 실행일: 2026-05-08
- 서버: http://127.0.0.1:8000
- 플로우: 자연어 입력 -> 일정 분석 -> 재질문/확인 -> SQLite 저장 -> 목록 조회

## 0. 서버 상태 확인
```json
{
  "status": "ok"
}
```

## 1. 완성된 자연어 일정 등록 플로우
### 1-1. 사용자 자연어 입력
```json
{
  "analysis_context": null,
  "timezone": "Asia/Seoul",
  "text": "내일 오후 4시에 치과 약속 예약해줘. 30분 전에 알려줘"
}
```
### 1-2. AI 일정 분석 결과
```json
{
  "original_text": "내일 오후 4시에 치과 약속 예약해줘. 30분 전에 알려줘",
  "schedule": {
    "title": "치과 약속",
    "start_at": "2026-05-09T16:00:00+09:00",
    "end_at": null,
    "location": null,
    "reminder_minutes": 30,
    "schedule_type": "appointment"
  },
  "missing_fields": [],
  "needs_confirmation": true,
  "analysis_context": {
    "original_text": "내일 오후 4시에 치과 약속 예약해줘. 30분 전에 알려줘",
    "latest_user_text": "내일 오후 4시에 치과 약속 예약해줘. 30분 전에 알려줘",
    "schedule": {
      "title": "치과 약속",
      "start_at": "2026-05-09T16:00:00+09:00",
      "end_at": null,
      "location": null,
      "reminder_minutes": 30,
      "schedule_type": "appointment"
    },
    "missing_fields": [],
    "timezone": "Asia/Seoul",
    "turn_count": 1
  },
  "message": "일정 정보를 확인해주세요."
}
```
### 1-3. 사용자 확인 후 저장 요청
```json
{
  "end_at": null,
  "reminder_minutes": 30,
  "original_text": "내일 오후 4시에 치과 약속 예약해줘. 30분 전에 알려줘",
  "location": null,
  "schedule_type": "appointment",
  "title": "치과 약속",
  "start_at": "2026-05-09T16:00:00+09:00"
}
```
### 1-4. 저장 완료 응답
```json
{
  "id": 1,
  "title": "치과 약속",
  "start_at": "2026-05-09T16:00:00",
  "end_at": "2026-05-09T17:00:00",
  "location": null,
  "reminder_minutes": 30,
  "schedule_type": "appointment",
  "status": "confirmed"
}
```

## 2. 정보 부족 재질문 멀티턴 플로우
### 2-1. 사용자 자연어 입력
```json
{
  "analysis_context": null,
  "timezone": "Asia/Seoul",
  "text": "내일 병원 가는 거 알림 맞춰줘"
}
```
### 2-2. AI 1차 분석 및 재질문 데이터
```json
{
  "original_text": "내일 병원 가는 거 알림 맞춰줘",
  "schedule": {
    "title": "병원 방문",
    "start_at": null,
    "end_at": null,
    "location": "병원",
    "reminder_minutes": null,
    "schedule_type": "appointment"
  },
  "missing_fields": [
    "start_at"
  ],
  "needs_confirmation": false,
  "analysis_context": {
    "original_text": "내일 병원 가는 거 알림 맞춰줘",
    "latest_user_text": "내일 병원 가는 거 알림 맞춰줘",
    "schedule": {
      "title": "병원 방문",
      "start_at": null,
      "end_at": null,
      "location": "병원",
      "reminder_minutes": null,
      "schedule_type": "appointment"
    },
    "missing_fields": [
      "start_at"
    ],
    "timezone": "Asia/Seoul",
    "turn_count": 1
  },
  "message": "일정을 등록하려면 날짜와 시간이 필요해요. 언제로 등록할까요?"
}
```
### 2-3. 사용자 후속 답변
```json
{
  "analysis_context": {
    "original_text": "내일 병원 가는 거 알림 맞춰줘",
    "latest_user_text": "내일 병원 가는 거 알림 맞춰줘",
    "schedule": {
      "title": "병원 방문",
      "start_at": null,
      "end_at": null,
      "location": "병원",
      "reminder_minutes": null,
      "schedule_type": "appointment"
    },
    "missing_fields": [
      "start_at"
    ],
    "timezone": "Asia/Seoul",
    "turn_count": 1
  },
  "timezone": "Asia/Seoul",
  "text": "오후 3시야"
}
```
### 2-4. AI 병합 분석 결과
```json
{
  "original_text": "내일 병원 가는 거 알림 맞춰줘",
  "schedule": {
    "title": "병원 방문",
    "start_at": "2026-05-09T15:00:00+09:00",
    "end_at": null,
    "location": "병원",
    "reminder_minutes": null,
    "schedule_type": "appointment"
  },
  "missing_fields": [],
  "needs_confirmation": true,
  "analysis_context": {
    "original_text": "내일 병원 가는 거 알림 맞춰줘",
    "latest_user_text": "오후 3시야",
    "schedule": {
      "title": "병원 방문",
      "start_at": "2026-05-09T15:00:00+09:00",
      "end_at": null,
      "location": "병원",
      "reminder_minutes": null,
      "schedule_type": "appointment"
    },
    "missing_fields": [],
    "timezone": "Asia/Seoul",
    "turn_count": 2
  },
  "message": "일정 정보를 확인해주세요."
}
```
### 2-5. 사용자 확인 후 저장 요청
```json
{
  "end_at": null,
  "reminder_minutes": 30,
  "original_text": "내일 병원 가는 거 알림 맞춰줘",
  "location": "병원",
  "schedule_type": "appointment",
  "title": "병원 방문",
  "start_at": "2026-05-09T15:00:00+09:00"
}
```
### 2-6. 저장 완료 응답
```json
{
  "id": 2,
  "title": "병원 방문",
  "start_at": "2026-05-09T15:00:00",
  "end_at": "2026-05-09T16:00:00",
  "location": "병원",
  "reminder_minutes": 30,
  "schedule_type": "appointment",
  "status": "confirmed"
}
```

## 3. 캘린더 목록 조회
```json
[
  {
    "id": 2,
    "title": "병원 방문",
    "start_at": "2026-05-09T15:00:00",
    "end_at": "2026-05-09T16:00:00",
    "location": "병원",
    "reminder_minutes": 30,
    "schedule_type": "appointment",
    "status": "confirmed"
  },
  {
    "id": 1,
    "title": "치과 약속",
    "start_at": "2026-05-09T16:00:00",
    "end_at": "2026-05-09T17:00:00",
    "location": null,
    "reminder_minutes": 30,
    "schedule_type": "appointment",
    "status": "confirmed"
  }
]
```

## 4. 데모 데이터 정리
- 삭제 완료: schedule_id=1, schedule_id=2

## 5. 결과 요약
- 완성 입력 플로우: 성공
- 재질문 멀티턴 플로우: 성공
- 저장/목록 조회/정리: 성공
