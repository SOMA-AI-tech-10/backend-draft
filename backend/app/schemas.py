from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AnalyzeScheduleRequest(BaseModel):
    text: str = Field(..., min_length=1)
    timezone: str = "Asia/Seoul"


class ScheduleCandidate(BaseModel):
    title: Optional[str] = None
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: Optional[int] = None


class AnalyzeScheduleResponse(BaseModel):
    original_text: str
    schedule: ScheduleCandidate
    message: str = "일정 정보를 확인해주세요."


class ScheduleCreate(BaseModel):
    title: str = Field(..., min_length=1)
    start_at: datetime
    end_at: Optional[datetime] = None
    location: Optional[str] = None
    reminder_minutes: int = Field(default=30, ge=0)
    original_text: Optional[str] = None


class ScheduleRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    start_at: datetime
    end_at: Optional[datetime]
    location: Optional[str]
    reminder_minutes: int
    status: str
