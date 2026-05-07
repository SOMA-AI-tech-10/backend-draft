from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, TypedDict

from langgraph.graph import END, START, StateGraph

from app.schemas import AnalyzeScheduleResponse, ScheduleCandidate
from app.services.ai_parser import ParsedSchedule, parse_schedule_text


class ScheduleGraphState(TypedDict, total=False):
    text: str
    timezone: str
    parsed: ParsedSchedule
    schedule: ScheduleCandidate
    message: str


def parse_schedule_node(state: ScheduleGraphState) -> dict[str, Any]:
    parsed = parse_schedule_text(state["text"], state["timezone"])
    return {"parsed": parsed}


def build_schedule_node(state: ScheduleGraphState) -> dict[str, Any]:
    parsed = state["parsed"]
    schedule = ScheduleCandidate(
        title=parsed.title,
        start_at=_parse_datetime(parsed.start_at),
        end_at=_parse_datetime(parsed.end_at),
        location=parsed.location,
        reminder_minutes=parsed.reminder_minutes,
    )

    return {"schedule": schedule, "message": "일정 정보를 확인해주세요."}


def analyze_schedule(text: str, timezone: str) -> AnalyzeScheduleResponse:
    graph = _build_graph()
    result = graph.invoke({"text": text, "timezone": timezone})
    return AnalyzeScheduleResponse(
        original_text=text,
        schedule=result["schedule"],
        message=result["message"],
    )


def _build_graph():
    builder = StateGraph(ScheduleGraphState)
    builder.add_node("parse_schedule", parse_schedule_node)
    builder.add_node("build_schedule", build_schedule_node)
    builder.add_edge(START, "parse_schedule")
    builder.add_edge("parse_schedule", "build_schedule")
    builder.add_edge("build_schedule", END)
    return builder.compile()


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        return None

