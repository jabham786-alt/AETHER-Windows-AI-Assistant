# AETHER — Windows AI Assistant

AETHER is a personal Windows AI desktop assistant.

## Phase 2 — Voice AI (فری / لوکل)

Phase 2 paid voice APIs پر منحصر نہیں ہے۔ موجودہ implementation میں:

- **Speech-to-Text:** Local `faster-whisper` — API key نہیں چاہیے
- **Text-to-Speech:** Windows local TTS (`pyttsx3`) — API key نہیں چاہیے
- **Microphone:** Windows/Electron browser media API
- **Wake word:** Phase 2 میں Push-to-Talk رکھا گیا ہے؛ ہمیشہ سننے والا wake-word بعد میں optional module ہوگا
- **Voice API:** `/api/voice/transcribe`, `/api/voice/speak`, `/api/voice/providers`

### Phase 2 Setup

اسی setup command سے voice dependencies بھی install ہوں گی:

    Set-ExecutionPolicy -Scope Process Bypass
    .\\scripts\\setup.ps1

پہلی transcription پر Whisper model مقامی طور پر download ہو سکتا ہے۔ اسے ڈاؤن لوڈ کرنے کے لیے internet درکار ہوگا، لیکن استعمال کے لیے کسی paid API subscription کی ضرورت نہیں۔ پہلے سے چھوٹا `base` model default ہے۔ Windows CPU پر کمزور مشین ہو تو `AETHER_WHISPER_MODEL=tiny` استعمال کیا جا سکتا ہے۔

**اہم:** فری ہونے کا مطلب یہ نہیں کہ کوئی cloud provider ہمیشہ کے لیے مفت قیمت کی ضمانت دیتا ہے؛ AETHER Phase 2 میں بنیادی voice path cloud/API billing سے آزاد رکھا گیا ہے۔

## Phase 3 — Windows Control / Automation

Phase 3 میں محفوظ local Windows automation شامل ہے۔ اس میں paid API کی ضرورت نہیں ہے۔

### موجودہ capabilities

- Allowlisted apps: Notepad, Calculator, Paint, Explorer
- HTTP/HTTPS URL اور web search کھولنا
- موجودہ folders کھولنا
- files/folders search کرنا
- folder یا empty file بنانا
- file rename/copy/move/delete
- action history SQLite میں محفوظ کرنا
- risk-based permission system
- high-risk delete کے لیے explicit confirmation
- arbitrary shell/PowerShell execution **نہیں** ہے

### Security model

AETHER کسی AI-generated string کو براہِ راست shell command کے طور پر execute نہیں کرتا۔ ہر request کو ایک مخصوص allowlisted action، validation اور permission check سے گزرنا ہوتا ہے:

    AI / UI
      ↓
    Allowed Action
      ↓
    Parameter Validation
      ↓
    Risk Check
      ↓
    Confirmation (when required)
      ↓
    Windows Action
      ↓
    Action History

Low-risk actions براہِ راست چل سکتے ہیں۔ File creation/rename/copy/move confirmation مانگتے ہیں، جبکہ delete high-risk ہے اور ہمیشہ explicit confirmation مانگتا ہے۔

### Phase 3 API

- GET `/api/automation/actions`
- POST `/api/automation/execute`
- GET `/api/automation/history`

Phase 3 کا اگلا incremental حصہ Windows volume/mute، screenshots، richer browser automation اور voice-to-action intent planning ہو سکتا ہے؛ انہیں arbitrary command execution کے بغیر permission model کے ساتھ شامل کیا جائے گا۔

## Phase 1 — Foundation

- Electron desktop shell
- React + TypeScript interface
- Secure preload bridge with context isolation and Node disabled in renderer
- FastAPI backend bound to 127.0.0.1
- SQLite + SQLAlchemy persistence
- OpenAI and Gemini provider adapters
- AI Chat
- CPU, memory, disk and OS monitoring
- Environment-based secrets
- Pytest and GitHub Actions CI

## Setup

Requirements: Windows 10/11, Node.js 22+, Python 3.12+, Git, and an OpenAI or Gemini API key.

PowerShell:

    Set-ExecutionPolicy -Scope Process Bypass
    .\scripts\setup.ps1

Configure .env with one provider:

    AETHER_AI_PROVIDER=openai
    AETHER_AI_MODEL=gpt-4.1-mini
    OPENAI_API_KEY=your_key

or:

    AETHER_AI_PROVIDER=gemini
    AETHER_AI_MODEL=gemini-2.5-flash
    GEMINI_API_KEY=your_key

Start:

    .\scripts\dev.ps1

Backend tests:

    .\.venv\Scripts\python.exe -m pytest backend/tests -q

## Security

The renderer has no Node.js access. Electron uses context isolation and sandboxing. FastAPI listens only on localhost. API secrets stay in environment variables and are not committed.

Arbitrary Windows command execution is intentionally excluded from Phase 1. Voice control, Windows automation, memory/RAG, work automation, multi-agent orchestration and plugins are planned for later phases with explicit permission boundaries.

## Roadmap

1. Phase 1 — Foundation
2. Phase 2 — Voice
3. Phase 3 — Windows Control
4. Phase 4 — Memory + RAG
5. Phase 5 — Work Automation
6. Phase 6 — Multi-Agent
7. Phase 7 — Plugins
8. Phase 8 — Production

## License

MIT
