# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Structure

This is a full-stack application with a React TypeScript frontend and Python backend:

```
con-ai/
├── frontend/            # React TypeScript frontend (main development area)
├── backend/             # Python backend API (placeholder structure)
├── scripts/             # Utility scripts (e.g., create_issues.py)
└── docs/                # Documentation
```

## Frontend Development Commands

Navigate to `frontend/` directory for all commands:

- **Start dev server**: `npm run dev` (serves on default Vite port)
- **Build**: `npm run build` (TypeScript compile + Vite build)
- **Preview build**: `npm run preview`
- **Lint**: `npm run lint` (ESLint with TypeScript)
- **Test**: `npm run test` (Vitest)
- **Test UI**: `npm run test:ui` (Vitest with UI)

## Frontend Architecture

React 19 + TypeScript application built with Vite, designed as an agent management/dashboard system.

### Tech Stack
- **Framework**: React 19 + TypeScript
- **Build Tool**: Vite
- **Routing**: React Router DOM v7
- **State Management**: Zustand
- **Styling**: Tailwind CSS v4 + PostCSS + Headless UI
- **Charts**: Recharts
- **Icons**: React Icons
- **Testing**: Vitest

### Source Structure
```
frontend/src/
├── components/
│   ├── agents/          # Agent-related UI components
│   ├── charts/          # Data visualization components
│   ├── common/          # Shared components (Layout, ErrorBoundary)
│   ├── dashboard/       # Dashboard-specific components
│   └── onboarding/      # User onboarding flow
├── pages/               # Route-level components
├── hooks/               # Custom React hooks
├── stores/              # Zustand state management
├── types/               # TypeScript definitions
└── utils/               # Helper functions
```

### Key Configuration
- **Vite config**: Path aliases (`@/*` → `./src/*`), proxy setup
- **Backend integration**: `/api` → `http://localhost:8080`, `/ws` → WebSocket proxy
- **Build output**: `build/` directory
- **TypeScript**: Strict mode, separate configs for app/node

### Routing
- `/` → Dashboard (main view)
- `/agents` → Agent management
- `/settings` → Application settings  
- `/help` → Help/documentation

Layout component provides consistent wrapper with ErrorBoundary for error handling.

## Backend Structure

Python backend with organized modules (currently placeholder):
```
backend/
├── agents/              # Agent-related logic
├── api/                 # API endpoints
├── models/              # Data models
├── services/            # Business logic
└── tests/               # Backend tests
```