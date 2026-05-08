from __future__ import annotations

import json
import os

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import GoogleCredential

router = APIRouter()

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


def _make_flow(state: str | None = None) -> Flow:
    client_config = {
        "web": {
            "client_id": os.getenv("GOOGLE_CLIENT_ID", ""),
            "client_secret": os.getenv("GOOGLE_CLIENT_SECRET", ""),
            "redirect_uris": [os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES, state=state)
    flow.redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/auth/google/callback")
    return flow


@router.get("/google")
def google_auth(session_id: str = Query(..., description="클라이언트 세션 ID")):
    """Google OAuth 로그인 시작. session_id를 state로 전달해 콜백에서 식별."""
    if not os.getenv("GOOGLE_CLIENT_ID"):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google OAuth 설정이 누락됐습니다. .env를 확인해주세요.",
        )
    flow = _make_flow()
    auth_url, _ = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        state=session_id,
        prompt="consent",
    )
    return RedirectResponse(auth_url)


@router.get("/google/callback")
def google_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """Google에서 돌아오는 콜백. 토큰을 받아 DB에 저장."""
    session_id = state
    flow = _make_flow(state=session_id)
    try:
        flow.fetch_token(code=code)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google 인증 코드가 올바르지 않습니다.",
        ) from exc

    creds = flow.credentials
    existing = db.query(GoogleCredential).filter_by(session_id=session_id).first()
    if existing:
        existing.token = creds.token
        existing.refresh_token = creds.refresh_token or existing.refresh_token
        existing.token_uri = creds.token_uri
        existing.client_id = creds.client_id
        existing.client_secret = creds.client_secret
        existing.scopes = json.dumps(list(creds.scopes or []))
    else:
        db.add(GoogleCredential(
            session_id=session_id,
            token=creds.token,
            refresh_token=creds.refresh_token,
            token_uri=creds.token_uri,
            client_id=creds.client_id,
            client_secret=creds.client_secret,
            scopes=json.dumps(list(creds.scopes or [])),
        ))
    db.commit()
    return {
        "status": "ok",
        "session_id": session_id,
        "message": "Google Calendar 연동이 완료됐습니다.",
    }


@router.get("/status")
def auth_status(session_id: str = Query(...), db: Session = Depends(get_db)):
    """해당 session_id가 Google Calendar 연동이 됐는지 확인."""
    cred = db.query(GoogleCredential).filter_by(session_id=session_id).first()
    return {"connected": cred is not None}
