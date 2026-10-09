import base64
import os
from datetime import datetime, timedelta, timezone
from email.mime.text import MIMEText
from pathlib import Path
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, EmailStr, Field

from backend.app.config import get_settings

router = APIRouter(prefix="/integrations", tags=["integrations"])
_GOOGLE_SCOPES = [
    "https://www.googleapis.com/auth/calendar.events",
    "https://www.googleapis.com/auth/contacts.readonly",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
]
_oauth_state: str | None = None


class SearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=500)
    max_results: int = Field(default=5, ge=1, le=10)


class CalendarEventRequest(BaseModel):
    summary: str = Field(min_length=1, max_length=200)
    start: datetime
    end: datetime
    description: str = Field(default="", max_length=4000)
    confirmed: bool = False


class SendEmailRequest(BaseModel):
    to: EmailStr
    subject: str = Field(min_length=1, max_length=200)
    body: str = Field(min_length=1, max_length=10000)
    confirmed: bool = False


def _google_credentials():
    settings = get_settings()
    token_path = Path(settings.google_token_file)
    if not token_path.is_file():
        raise HTTPException(status_code=401, detail="Google account is not connected. Start OAuth from /google/auth-url.")
    try:
        from google.oauth2.credentials import Credentials
        from google.auth.transport.requests import Request as GoogleRequest
        credentials = Credentials.from_authorized_user_file(str(token_path), _GOOGLE_SCOPES)
        if credentials.expired and credentials.refresh_token:
            credentials.refresh(GoogleRequest())
            token_path.parent.mkdir(parents=True, exist_ok=True)
            token_path.write_text(credentials.to_json(), encoding="utf-8")
        if not credentials.valid:
            raise HTTPException(status_code=401, detail="Google authorization expired. Reconnect the account.")
        return credentials
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not load Google OAuth credentials.") from exc


def _google_service(name: str, version: str):
    try:
        from googleapiclient.discovery import build
        return build(name, version, credentials=_google_credentials(), cache_discovery=False)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Google API service could not be initialized.") from exc


@router.get("/status")
def integration_status():
    s = get_settings()
    token_exists = Path(s.google_token_file).is_file()
    return {
        "ai": {
            "provider": s.ai_provider,
            "openai": bool(s.openai_api_key),
            "gemini": bool(s.gemini_api_key),
            "groq": bool(s.groq_api_key),
        },
        "speech": {
            "active_stt": s.stt_provider,
            "deepgram_configured": bool(s.deepgram_api_key),
            "local_whisper_available": True,
        },
        "search": {"tavily_configured": bool(s.tavily_api_key)},
        "google": {"connected": token_exists, "oauth_client_configured": Path(s.google_oauth_client_file).is_file()},
    }


@router.post("/search")
async def search_web(payload: SearchRequest):
    key = get_settings().tavily_api_key
    if not key:
        raise HTTPException(status_code=503, detail="TAVILY_API_KEY is not configured.")
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.tavily.com/search",
                json={"api_key": key, "query": payload.query, "max_results": payload.max_results, "search_depth": "basic", "include_answer": True},
            )
        if response.status_code >= 400:
            raise HTTPException(status_code=502, detail=f"Tavily returned HTTP {response.status_code}.")
        data = response.json()
        return {
            "answer": data.get("answer", ""),
            "results": [
                {"title": item.get("title", ""), "url": item.get("url", ""), "content": item.get("content", "")[:2000]}
                for item in data.get("results", [])
            ],
        }
    except HTTPException:
        raise
    except (httpx.HTTPError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=502, detail="Tavily search failed.") from exc


@router.get("/google/auth-url")
def google_auth_url():
    global _oauth_state
    settings = get_settings()
    client_file = Path(settings.google_oauth_client_file)
    if not client_file.is_file():
        raise HTTPException(status_code=503, detail=f"Google OAuth client JSON not found at {client_file}.")
    try:
        from google_auth_oauthlib.flow import Flow
        redirect_uri = f"http://{settings.host}:{settings.port}/api/integrations/google/callback"
        flow = Flow.from_client_secrets_file(str(client_file), scopes=_GOOGLE_SCOPES, redirect_uri=redirect_uri)
        authorization_url, _oauth_state = flow.authorization_url(access_type="offline", include_granted_scopes="true", prompt="consent")
        return {"authorization_url": authorization_url, "redirect_uri": redirect_uri, "scopes": _GOOGLE_SCOPES}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Could not create Google OAuth authorization URL.") from exc


@router.get("/google/callback")
def google_oauth_callback(request: Request, state: str = Query(min_length=1), code: str = Query(min_length=1)):
    global _oauth_state
    if not _oauth_state or state != _oauth_state:
        raise HTTPException(status_code=400, detail="OAuth state mismatch. Restart Google account connection.")
    settings = get_settings()
    try:
        from google_auth_oauthlib.flow import Flow
        redirect_uri = f"http://{settings.host}:{settings.port}/api/integrations/google/callback"
        flow = Flow.from_client_secrets_file(str(settings.google_oauth_client_file), scopes=_GOOGLE_SCOPES, state=state, redirect_uri=redirect_uri)
        flow.fetch_token(authorization_response=str(request.url))
        token_path = Path(settings.google_token_file)
        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(flow.credentials.to_json(), encoding="utf-8")
        try:
            os.chmod(token_path, 0o600)
        except OSError:
            pass
        _oauth_state = None
        return {"status": "connected", "message": "Google account connected. You may close this page and return to AETHER."}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Google OAuth callback failed. Check the OAuth redirect URI and consent settings.") from exc


@router.get("/google/calendar")
def calendar_events(max_results: int = Query(default=10, ge=1, le=50)):
    service = _google_service("calendar", "v3")
    now = datetime.now(timezone.utc).isoformat()
    try:
        data = service.events().list(calendarId="primary", timeMin=now, maxResults=max_results, singleEvents=True, orderBy="startTime").execute()
        return [{"id": x.get("id"), "summary": x.get("summary", "(No title)"), "start": x.get("start", {}), "end": x.get("end", {}), "htmlLink": x.get("htmlLink", "")} for x in data.get("items", [])]
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Could not read Google Calendar events.") from exc


@router.post("/google/calendar")
def create_calendar_event(payload: CalendarEventRequest):
    if payload.end <= payload.start:
        raise HTTPException(status_code=400, detail="Event end must be later than its start.")
    preview = {"summary": payload.summary, "start": payload.start.isoformat(), "end": payload.end.isoformat(), "description": payload.description}
    if not payload.confirmed:
        return {"status": "confirmation_required", "action": "create_calendar_event", "preview": preview}
    service = _google_service("calendar", "v3")
    event = {
        "summary": payload.summary,
        "description": payload.description,
        "start": {"dateTime": payload.start.isoformat()},
        "end": {"dateTime": payload.end.isoformat()},
    }
    try:
        result = service.events().insert(calendarId="primary", body=event).execute()
        return {"status": "created", "id": result.get("id"), "htmlLink": result.get("htmlLink", "")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Google Calendar event creation failed.") from exc


@router.get("/google/contacts")
def google_contacts(limit: int = Query(default=50, ge=1, le=100)):
    service = _google_service("people", "v1")
    try:
        data = service.people().connections().list(resourceName="people/me", personFields="names,emailAddresses,phoneNumbers", pageSize=limit).execute()
        result = []
        for person in data.get("connections", []):
            names = person.get("names", [])
            result.append({
                "name": names[0].get("displayName", "") if names else "",
                "emails": [x.get("value", "") for x in person.get("emailAddresses", [])],
                "phones": [x.get("value", "") for x in person.get("phoneNumbers", [])],
            })
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Could not read Google Contacts.") from exc


@router.get("/google/gmail")
def gmail_messages(limit: int = Query(default=10, ge=1, le=25), q: str = Query(default="", max_length=200)):
    service = _google_service("gmail", "v1")
    try:
        listing = service.users().messages().list(userId="me", maxResults=limit, q=q or None).execute()
        result = []
        for item in listing.get("messages", []):
            message = service.users().messages().get(userId="me", id=item["id"], format="metadata", metadataHeaders=["From", "To", "Subject", "Date"]).execute()
            headers = {h.get("name", "").lower(): h.get("value", "") for h in message.get("payload", {}).get("headers", [])}
            result.append({"id": item["id"], "threadId": message.get("threadId"), "from": headers.get("from", ""), "to": headers.get("to", ""), "subject": headers.get("subject", ""), "date": headers.get("date", ""), "snippet": message.get("snippet", "")})
        return result
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Could not read Gmail messages.") from exc


@router.post("/google/gmail/send")
def send_gmail(payload: SendEmailRequest):
    if not payload.confirmed:
        return {"status": "confirmation_required", "action": "send_email", "preview": {"to": str(payload.to), "subject": payload.subject, "body": payload.body}}
    service = _google_service("gmail", "v1")
    message = MIMEText(payload.body, "plain", "utf-8")
    message["to"] = str(payload.to)
    message["subject"] = payload.subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode("ascii")
    try:
        sent = service.users().messages().send(userId="me", body={"raw": raw}).execute()
        return {"status": "sent", "id": sent.get("id")}
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Gmail send failed.") from exc
