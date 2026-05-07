from __future__ import annotations

import os
import json
from datetime import datetime
from typing import Optional

from openai import OpenAI
from pydantic import BaseModel


class ParsedSchedule(BaseModel):
    title: Optional[str]
    start_at: Optional[str]
    end_at: Optional[str]
    location: Optional[str]
    reminder_minutes: Optional[int]


def parse_schedule_text(text: str, timezone: str) -> ParsedSchedule:
    api_key = os.getenv("UPSTAGE_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("UPSTAGE_API_KEY is not set")

    model = os.getenv("UPSTAGE_MODEL") or os.getenv("OPENAI_MODEL", "solar-pro3")
    base_url = os.getenv("UPSTAGE_BASE_URL", "https://api.upstage.ai/v1")
    reasoning_effort = os.getenv("UPSTAGE_REASONING_EFFORT", "high")
    now = datetime.now().astimezone().isoformat()
    client = OpenAI(api_key=api_key, base_url=base_url)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You extract one calendar event from Korean natural language. "
                    "Return only valid JSON with these exact keys: "
                    "title, start_at, end_at, location, reminder_minutes. "
                    "Use ISO 8601 datetimes with timezone offsets. "
                    "Do not invent missing information. "
                    "If a field is missing, set it to null. "
                    "If title is unclear, create a short Korean noun phrase. "
                    "If reminder is missing, set reminder_minutes to null. "
                    "If end time is missing, set end_at to null."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Current datetime: {now}\n"
                    f"User timezone: {timezone}\n"
                    f"Text: {text}"
                ),
            },
        ],
        reasoning_effort=reasoning_effort,
        stream=False,
    )

    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("AI returned no schedule content")
    return ParsedSchedule.model_validate(_load_json(content))


def _load_json(content: str) -> dict:
    cleaned = content.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").strip()
        if cleaned.startswith("json"):
            cleaned = cleaned[4:].strip()
    return json.loads(cleaned)
