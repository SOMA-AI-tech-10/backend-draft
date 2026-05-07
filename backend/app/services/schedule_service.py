from __future__ import annotations

from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Schedule
from app.schemas import ScheduleCreate


def create_schedule(db: Session, data: ScheduleCreate) -> Schedule:
    end_at = data.end_at or data.start_at + timedelta(hours=1)
    schedule = Schedule(
        title=data.title,
        start_at=data.start_at,
        end_at=end_at,
        location=data.location,
        reminder_minutes=data.reminder_minutes,
        original_text=data.original_text,
        status="confirmed",
    )
    db.add(schedule)
    db.commit()
    db.refresh(schedule)
    return schedule


def list_schedules(db: Session) -> list[Schedule]:
    stmt = select(Schedule).order_by(Schedule.start_at.asc())
    return list(db.scalars(stmt).all())
