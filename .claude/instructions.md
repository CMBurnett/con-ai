# Con-AI Project Context
This is a local desktop PWA for construction project management using AI agents.

## Architecture
- **Backend**: Python FastAPI with WebSocket support
- **Frontend**: React 18 + TypeScript + Vite PWA
- **AI Agents**: browser-use library for construction software automation
- **Database**: SQLite (local) with SQLAlchemy ORM
- **Distribution**: PyInstaller single executable

## Key Technologies
- **Backend**: FastAPI, SQLAlchemy, browser-use, OpenAI/Anthropic APIs
- **Frontend**: React, TypeScript, Tailwind CSS, Zustand, Recharts
- **Automation**: Playwright via browser-use for Procore/Autodesk/Primavera
- **Real-time**: WebSocket communication between frontend/backend

## Construction Software Targets
- Procore (project management)
- Autodesk Construction Cloud (BIM)
- Oracle Primavera P6 (scheduling)

## Coding Standards
- Python: Black formatting, type hints, async/await patterns
- TypeScript: Strict mode, proper typing for WebSocket messages
- FastAPI: Pydantic models for request/response validation
- React: Functional components with hooks, Zustand for state
- WebSocket: Event-driven architecture for agent status updates

## Security Model
- Local-first: No cloud storage, all data on user's machine
- Browser sessions: Use existing auth, never store credentials
- Audit logging: Local compliance logs

## Agent Architecture
- Base Agent class with common browser automation
- Specific agents for each construction platform
- WebSocket events for real-time status updates
- Error handling and retry logic for network issues