# AETHER — Windows AI Assistant

AETHER is a personal Windows AI desktop assistant.

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
