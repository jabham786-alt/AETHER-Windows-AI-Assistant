# AETHER — Windows AI Assistant

AETHER is a personal Windows AI desktop assistant.

## Optional cloud integrations

AETHER supports OpenAI, Gemini, or Groq for AI chat; local Faster-Whisper by default or optional Deepgram Nova-3 for speech-to-text; Tavily web search; and Google Calendar, read-only Contacts, read-only Gmail metadata/snippets, and Gmail sending after explicit confirmation. Windows local SAPI/pyttsx3 remains the default text-to-speech engine.

Provider pricing and free tiers can change. Cloud speech and hosted AI/search services send the relevant request, audio, or query to that provider and may have usage limits or charges. Local Whisper remains available without a cloud key.

### Configure providers

Copy .env.example to .env in the project root and fill only the keys you use. Never paste real keys into chat, frontend code, source control, logs, or screenshots.

Groq:
    AETHER_AI_PROVIDER=groq
    AETHER_AI_MODEL=llama-3.3-70b-versatile
    GROQ_API_KEY=your_key

Gemini:
    AETHER_AI_PROVIDER=gemini
    AETHER_AI_MODEL=gemini-2.5-flash
    GEMINI_API_KEY=your_key

Deepgram transcription (optional; cloud audio processing):
    AETHER_STT_PROVIDER=deepgram
    DEEPGRAM_API_KEY=your_key

Keep transcription local:
    AETHER_STT_PROVIDER=local-whisper

Tavily web search:
    TAVILY_API_KEY=your_key

Restart AETHER after changing .env.

### Google Calendar, Contacts and Gmail setup

1. In Google Cloud Console, create/select a project and enable Google Calendar API, People API, and Gmail API.
2. Configure the OAuth consent screen and create an OAuth client. Add this exact authorized redirect URI: http://127.0.0.1:8765/api/integrations/google/callback.
3. Save the downloaded OAuth client JSON as backend/data/google_oauth_client.json. This file is ignored by Git.
4. Install dependencies with .\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt, then start AETHER.
5. Open http://127.0.0.1:8765/api/integrations/google/auth-url, copy the returned authorization_url into your browser, and approve the requested Google permissions.
6. The OAuth token is saved locally to backend/data/google_token.json and ignored by Git.

The OAuth redirect URI must match exactly. Google may require a test user to be added to the consent screen while the app is in testing mode.

### Integration API

- GET /api/integrations/status — provider configuration status (never returns API keys)
- POST /api/integrations/search — Tavily web search
- GET /api/integrations/google/auth-url and GET /api/integrations/google/callback — Google OAuth
- GET /api/integrations/google/calendar — upcoming events
- POST /api/integrations/google/calendar — create event; first request returns a confirmation preview, then repeat with the returned confirmation_token
- GET /api/integrations/google/contacts — contact names, emails and phone numbers
- GET /api/integrations/google/gmail — message metadata and snippets, not full email bodies
- POST /api/integrations/google/gmail/send — first request returns a preview; repeat with the returned confirmation_token only after reviewing it

Google scopes are limited to Calendar event access, read-only contacts, read-only Gmail and Gmail send. Disconnect by deleting backend/data/google_token.json and revoking AETHER in your Google Account security settings.

## Phase 2 — Voice AI

- Speech-to-Text: Local faster-whisper by default; optional Deepgram.
- Text-to-Speech: Windows local TTS (pyttsx3), no API key required.
- Microphone: Windows/Electron browser media API.
- Wake word: Push-to-Talk; no always-listening microphone.
- Voice API: /api/voice/transcribe, /api/voice/speak, /api/voice/providers.

PowerShell setup:

    Set-ExecutionPolicy -Scope Process Bypass
    .\scripts\setup.ps1

The first local Whisper transcription may download a model; internet is needed for that download but not for subsequent local inference. Set AETHER_WHISPER_MODEL=tiny on lower-powered Windows PCs.

## Phase 4 — Memory + RAG

- SQLite local memories, categories and source metadata.
- Create, list, search, edit and delete memories.
- Local keyword retrieval injects relevant memories into AI Chat.
- No hosted vector database or embedding API required.

API: GET /api/memories, POST /api/memories, PATCH /api/memories/{memory_id}, DELETE /api/memories/{memory_id}, GET /api/memories/search?q=....

## Phase 3 — Windows Control / Automation

- Allowlisted apps: Notepad, Calculator, Paint, Explorer.
- Open HTTP/HTTPS URLs and existing folders; search files; create, rename, copy, move and delete files.
- SQLite action history, risk-based permissions and explicit confirmation for risky actions.
- Arbitrary shell/PowerShell execution is intentionally excluded.

The existing Policy Engine and Windows action allowlist remain authoritative. Cloud integrations do not execute web-search results as commands. Sending email and creating calendar events require a second request with the short-lived confirmation_token returned in the preview; inspect the preview first. Tokens are single-use, expire after five minutes, and are bound to the exact action data.

## Foundation and setup

- Electron desktop shell; React + TypeScript UI.
- Secure preload bridge, context isolation and disabled Node integration in renderer.
- FastAPI bound to 127.0.0.1; SQLite/SQLAlchemy.
- Environment-based secrets and pytest/GitHub Actions CI.

Requirements: Windows 10/11, Node.js 22+, Python 3.12+, Git.

    Set-ExecutionPolicy -Scope Process Bypass
    .\scripts\setup.ps1
    .\scripts\dev.ps1

Backend tests:

    .\.venv\Scripts\python.exe -m pytest backend/tests -q

## Security

API keys and Google OAuth tokens stay on the backend/local machine and must never be committed. Google OAuth client and token files are excluded by .gitignore. Cloud providers receive data required for the feature being used. FastAPI is intended to listen only on localhost. No integration grants the model arbitrary shell or PowerShell access.

## License

MIT
