from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.db import get_db
from app.schemas import (
    AnalyzeScheduleRequest,
    AnalyzeScheduleResponse,
    ScheduleCreate,
    ScheduleRead,
)
from app.services.schedule_graph import analyze_schedule
from app.services.schedule_service import create_schedule, list_schedules

router = APIRouter()


@router.post("/analyze", response_model=AnalyzeScheduleResponse)
def analyze_schedule_route(payload: AnalyzeScheduleRequest) -> AnalyzeScheduleResponse:
    try:
        return analyze_schedule(payload.text, payload.timezone)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="일정 분석 중 문제가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from exc


@router.post("", response_model=ScheduleRead, status_code=status.HTTP_201_CREATED)
def create_schedule_route(payload: ScheduleCreate, db: Session = Depends(get_db)):
    try:
        return create_schedule(db, payload)
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="일정을 저장하지 못했습니다.",
        ) from exc


@router.get("", response_model=list[ScheduleRead])
def list_schedules_route(db: Session = Depends(get_db)):
    return list_schedules(db)
