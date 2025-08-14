# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Con-AI is a construction intelligence platform that uses AI agents to automate interactions with construction software platforms (Procore, Autodesk Construction Cloud, Oracle Primavera P6). It's a local-first desktop PWA with a React frontend and Python FastAPI backend.

## Development Commands

### Frontend Commands (run from `/frontend` directory)
- **Start dev server**: `npm run dev` (serves on port 3000, proxies to backend on 8080)
- **Build**: `npm run build` (TypeScript compile + Vite build)
- **Lint**: `npm run lint` (ESLint with TypeScript, max 0 warnings)
- **Test**: `npm run test` (Vitest)
- **Test with UI**: `npm run test:ui` (Vitest with UI)
- **Preview**: `npm run preview` (preview production build)

### Backend Commands (run from `/backend` directory)
- **Start server**: `python main.py` (FastAPI server on port 8080)
- **Install dependencies**: `pip install -r requirements.txt`
- **Format code**: `black .`
- **Run tests**: `pytest`

**Note**: Backend structure exists but is currently empty - Python files need to be created for a functional backend.

### Production Build
1. Frontend: `cd frontend && npm run build`
2. Backend: `cd backend && pyinstaller --onefile main.py`

## Architecture

### Frontend (React 19 + TypeScript)
- **Build tool**: Vite with path aliases (`@/*` → `./src/*`)
- **State management**: Zustand stores (`stores/`)
- **Styling**: Tailwind CSS v4 + Headless UI
- **Charts**: Recharts for data visualization
- **Routing**: React Router DOM v7
- **Testing**: Vitest

### Backend (Python FastAPI)
- **Framework**: FastAPI with WebSocket support
- **Database**: SQLite with SQLAlchemy ORM
- **Browser automation**: Playwright + browser-use
- **AI APIs**: OpenAI/Anthropic integration

### Key Integrations
- Frontend proxies `/api` → `http://localhost:8080`
- WebSocket proxy `/ws` → `ws://localhost:8080`
- Real-time updates between frontend and backend
- Direct WebSocket connection hardcoded to `ws://localhost:8080/ws` in useWebSocket hook

## Code Architecture

### Agent System
Core concept: AI agents that interact with construction software platforms.

**Agent Types** (`frontend/src/types/agents.ts`):
- `procore`: Procore platform integration
- `autodesk`: Autodesk Construction Cloud
- `primavera`: Oracle Primavera P6
- `demo`: Demo/testing agent

**Agent States**: `idle`, `running`, `error`, `completed`

### Frontend Structure
```
frontend/src/
├── components/
│   ├── agents/      # Agent management UI (AgentCard, AgentList, etc.)
│   ├── dashboard/   # Main dashboard views
│   ├── charts/      # Data visualization components
│   ├── common/      # Shared components (Layout, ErrorBoundary)
│   └── onboarding/  # Setup wizard components
├── hooks/           # Custom React hooks (useWebSocket, useAgents)
├── stores/          # Zustand state management
├── types/           # TypeScript definitions
├── utils/           # Helper functions
└── pages/           # Route components
```

### State Management
- **Agent Store**: Agent configuration and status
- **Data Store**: Construction project data
- **UI Store**: UI state and preferences

### Frontend Routing Structure
- `/` → Dashboard (main project overview)
- `/agents` → Agent management interface
- `/settings` → Application configuration
- `/help` → Documentation and help

## Development Patterns

### Component Architecture
- All components use TypeScript with strict typing
- Shared components in `components/common/`
- Domain-specific components organized by feature
- Error boundaries wrap route components

### WebSocket Communication Pattern
- `useWebSocket` hook manages connection state and message handling
- Agent updates are parsed as JSON and stored with timestamps
- Updates are limited to last 100 messages to prevent memory issues
- Commands can be sent to backend via `sendCommand` function

### Data Flow
- **Construction Data Types**: Project, RFI, BudgetItem interfaces define the data model
- **Agent Updates**: Real-time status, progress, and data updates via WebSocket
- **Platform Integration**: Agents connect to Procore, Autodesk, and Primavera platforms

### Testing Approach
- Vitest for unit/integration tests
- Test files organized by feature area
- UI testing available via `npm run test:ui`

### Build Configuration
- TypeScript strict mode with `noUnusedLocals` and `noUnusedParameters`
- Path aliases: `@/*` → `./src/*`
- ESLint config uses flat config format with TypeScript ESLint
- Build output to `frontend/build/` directory
- Source maps enabled for debugging

## API Endpoints (Planned)

Based on project requirements, the following API endpoints will be needed:

### Core Backend API
- `GET /agents` - List all agents and their status
- `POST /agents/start` - Start an agent
- `POST /agents/stop` - Stop an agent
- `GET /agents/status` - Get agent status
- `WebSocket /ws` - Real-time agent communication

### Platform-Specific Agent APIs
**Procore Integration:**
- `POST /agents/procore/configure` - Configure Procore agent
- `GET /procore/projects` - Get Procore project data
- `GET /procore/rfis` - Get RFI data

**Autodesk Construction Cloud:**
- `POST /agents/autodesk/configure` - Configure Autodesk agent
- `GET /autodesk/projects` - Get project data
- `GET /autodesk/models` - Get BIM model data

**Primavera P6:**
- `POST /agents/primavera/configure` - Configure Primavera agent
- `GET /primavera/schedules` - Get schedule data
- `GET /primavera/resources` - Get resource allocation

### Onboarding & Setup
- `GET /onboarding/progress` - Get setup progress
- `POST /onboarding/complete` - Complete onboarding
- `GET /templates/agent` - Get agent configuration templates