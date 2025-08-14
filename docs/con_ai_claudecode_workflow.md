# Con-AI ClaudeCode Development Workflow

## Overview
This workflow is optimized for Con-AI's local desktop PWA architecture using FastAPI backend + React frontend, with ClaudeCode handling both Python and TypeScript development for 10x speed improvements.

## Quick Start (2-Hour Setup)

### 1. ClaudeCode Installation & Con-AI Setup
```bash
# Install ClaudeCode globally
npm install -g @anthropic-ai/claude-code

# Clone and setup Con-AI project
git clone https://github.com/your-org/con-ai.git
cd con-ai

# Initialize ClaudeCode in project root
claude

# Connect your Anthropic account (follow prompts)
```

### 2. Con-AI Specific Workflow Stack
- **Project Management**: GitHub Issues with Con-AI milestones
- **Development**: ClaudeCode for Python FastAPI + React TypeScript
- **Testing**: pytest (backend) + Vitest (frontend)
- **Local Development**: Concurrent FastAPI + Vite dev servers
- **Distribution**: PyInstaller for desktop packaging

## Project Structure

```
con-ai/
├── .claudecode/
│   ├── config.json              # ClaudeCode settings
│   └── instructions.md          # Con-AI specific context
├── .github/
│   └── workflows/
│       ├── ci.yml               # Python + Node.js CI
│       ├── build-desktop.yml    # PyInstaller packaging
│       └── claude-pr.yml        # ClaudeCode PR automation
├── backend/                     # Python FastAPI service
│   ├── main.py                  # FastAPI app entry
│   ├── api/                     # REST endpoints
│   ├── services/                # Business logic
│   ├── agents/                  # AI agent implementations
│   ├── models/                  # SQLAlchemy models
│   ├── tests/                   # pytest tests
│   └── requirements.txt
├── frontend/                    # React PWA
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── public/
│   │   ├── manifest.json        # PWA manifest
│   │   ├── icon-192.png         # PWA icons
│   │   ├── icon-512.png
│   │   └── favicon.ico
│   ├── src/
│   │   ├── components/
│   │   │   ├── agents/          # Agent management UI
│   │   │   │   ├── AgentCard.tsx
│   │   │   │   ├── AgentConfig.tsx
│   │   │   │   ├── AgentStatus.tsx
│   │   │   │   └── AgentList.tsx
│   │   │   ├── dashboard/       # Main dashboard components
│   │   │   │   ├── Dashboard.tsx
│   │   │   │   ├── ProjectOverview.tsx
│   │   │   │   ├── RFIChart.tsx
│   │   │   │   └── BudgetChart.tsx
│   │   │   ├── common/          # Shared UI components
│   │   │   │   ├── Layout.tsx
│   │   │   │   ├── Header.tsx
│   │   │   │   ├── Sidebar.tsx
│   │   │   │   ├── LoadingSpinner.tsx
│   │   │   │   └── ErrorBoundary.tsx
│   │   │   ├── charts/          # Data visualization
│   │   │   │   ├── ProjectChart.tsx
│   │   │   │   ├── ProgressChart.tsx
│   │   │   │   └── BudgetVarianceChart.tsx
│   │   │   └── onboarding/      # First-time user setup
│   │   │       ├── WelcomeScreen.tsx
│   │   │       ├── ConfigWizard.tsx
│   │   │       └── FirstTimeSetup.tsx
│   │   ├── hooks/               # Custom React hooks
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useAgents.ts
│   │   │   ├── useLocalStorage.ts
│   │   │   └── useConstructionData.ts
│   │   ├── stores/              # Zustand state management
│   │   │   ├── agentStore.ts
│   │   │   ├── dataStore.ts
│   │   │   └── uiStore.ts
│   │   ├── types/               # TypeScript type definitions
│   │   │   ├── agents.ts
│   │   │   ├── construction.ts
│   │   │   ├── api.ts
│   │   │   └── index.ts
│   │   ├── utils/               # Utility functions
│   │   │   ├── api.ts
│   │   │   ├── formatters.ts
│   │   │   ├── constants.ts
│   │   │   └── validation.ts
│   │   ├── pages/               # Route-level components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Agents.tsx
│   │   │   ├── Settings.tsx
│   │   │   └── Help.tsx
│   │   ├── App.tsx              # Main App component
│   │   ├── main.tsx             # React app entry point
│   │   └── index.css            # Global styles
│   └── tests/                   # Frontend tests
│       ├── components/
│       ├── hooks/
│       └── utils/
├── docs/                        # Documentation
├── scripts/                     # Build and deployment scripts
├── build/                       # PyInstaller output
└── README.md
```

## Development Workflow

### Daily Development Flow
1. **Start with GitHub Issues**: Create issues aligned with Con-AI milestones
2. **Branch Strategy**: Feature branches from main for each agent/component
3. **Concurrent Development**:
   ```bash
   # Terminal 1: Backend development
   cd backend
   source venv/bin/activate
   claude
   # "Create a new Procore agent that extracts project data via browser automation"
   
   # Terminal 2: Frontend development  
   cd frontend
   claude
   # "Build a real-time dashboard component for displaying agent status"
   ```
4. **Integration Testing**: Test FastAPI ↔ React WebSocket communication
5. **Desktop Build**: Test PyInstaller packaging locally
6. **PR Creation**: Push to GitHub with automated CI/CD

### ClaudeCode Best Practices for Con-AI

#### Project Context Setup
```bash
# Create Con-AI specific instructions
echo "# Con-AI Project Context
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
" > .claudecode/instructions.md
```

#### Effective Claude Prompts for Con-AI

**Backend Development**:
- "Create a Procore agent that logs into Procore via browser automation and extracts project budget data, sending real-time updates via WebSocket"
- "Build a FastAPI endpoint that manages multiple construction software agents and returns their status"
- "Implement SQLAlchemy models for storing project data from Procore, Autodesk, and Primavera"

**Frontend Development**:
- "Create the Dashboard.tsx page component with ProjectOverview, RFIChart, and BudgetChart components, all displaying real-time agent data via WebSocket"
- "Build the agentStore.ts Zustand store for managing agent state and WebSocket connections across the app"
- "Implement TypeScript interfaces in types/agents.ts and types/api.ts for WebSocket message protocols and agent state management"
- "Create AgentCard and AgentStatus components in components/agents/ that show real-time agent activity with Tailwind styling"
- "Build the useWebSocket and useAgents custom hooks for managing WebSocket lifecycle and agent data fetching"

**Integration & Testing**:
- "Write pytest tests for the agent framework including mock browser automation scenarios"
- "Create a WebSocket client service in React that handles connection lifecycle and message routing"
- "Set up PyInstaller configuration to package the FastAPI backend with React build into a single executable"

## GitHub Integration for Con-AI

### GitHub Actions Workflow
```yaml
# .github/workflows/ci.yml
name: Con-AI CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install backend dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run backend tests
        run: |
          cd backend
          pytest tests/ -v
      - name: Test FastAPI startup
        run: |
          cd backend
          python -c "from main import app; print('FastAPI app loads successfully')"

  frontend-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js 20
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci
      - name: Run frontend tests
        run: |
          cd frontend
          npm run test
      - name: Build React PWA
        run: |
          cd frontend
          npm run build
      - name: Test PWA manifest
        run: |
          cd frontend
          test -f dist/manifest.json && echo "PWA manifest generated"

  desktop-build:
    needs: [backend-test, frontend-test]
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Setup Node.js 20
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Build frontend
        run: |
          cd frontend
          npm ci
          npm run build
      - name: Package desktop app
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pyinstaller
          pyinstaller --onefile main.py
      - name: Upload desktop build
        uses: actions/upload-artifact@v3
        with:
          name: con-ai-desktop
          path: backend/dist/
```

### Issue Templates for Con-AI
```markdown
# .github/ISSUE_TEMPLATE/agent-feature.md
---
name: Construction Agent Feature
about: Create a new construction software agent
title: '[AGENT] Add {Platform} integration agent'
labels: agent, enhancement
---

## Construction Platform
- [ ] Procore
- [ ] Autodesk Construction Cloud  
- [ ] Oracle Primavera P6
- [ ] Other: ___________

## Data Extraction Requirements
- [ ] Project information
- [ ] Budget/cost data
- [ ] Schedule data
- [ ] Document management
- [ ] Other: ___________

## ClaudeCode Implementation Tasks
- [ ] Create agent class inheriting from BaseAgent
- [ ] Implement browser automation logic
- [ ] Add WebSocket status updates
- [ ] Create frontend components for agent status
- [ ] Write tests for agent functionality
- [ ] Update documentation

## Acceptance Criteria
- [ ] Agent successfully authenticates with platform
- [ ] Data extraction works reliably
- [ ] Real-time status updates via WebSocket
- [ ] Error handling for network issues
- [ ] Logs activities for audit compliance
```

## Local Development Setup

### Backend Development Environment
```bash
# Setup Python environment
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start FastAPI development server
uvicorn main:app --reload --port 8080

# In another terminal, use ClaudeCode for backend development
claude
# "Create a new agent for Autodesk Construction Cloud that extracts BIM model information"
```

### Frontend Development Environment
```bash
# Setup Node.js environment
cd frontend
npm install

# Start Vite development server
npm run dev  # Runs on localhost:3000

# In another terminal, use ClaudeCode for frontend development
claude
# "Build the Dashboard.tsx page with ProjectOverview, RFIChart, and BudgetChart components integrated with real-time WebSocket data"

# Create specific component structures
claude "Create the complete agents management interface:
1. components/agents/AgentList.tsx - grid layout of all agents
2. components/agents/AgentCard.tsx - individual agent status card
3. components/agents/AgentConfig.tsx - agent configuration modal
4. components/agents/AgentStatus.tsx - detailed agent status view"

# Build data visualization components
claude "Create chart components in components/charts/:
1. ProjectChart.tsx - project timeline visualization
2. ProgressChart.tsx - construction progress tracking
3. BudgetVarianceChart.tsx - budget vs actual spending analysis"
```

### Desktop Testing
```bash
# Test PyInstaller packaging
cd backend
pip install pyinstaller
pyinstaller --onefile main.py

# Test the executable
./dist/main.exe  # Windows
./dist/main      # macOS/Linux
```

## VSCode Enhancement for Con-AI

### Recommended Extensions
```json
// .vscode/extensions.json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode",
    "ms-vscode.vscode-typescript-next",
    "ms-toolsai.jupyter",
    "github.vscode-pull-request-github"
  ]
}
```

### Workspace Settings
```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./backend/venv/bin/python",
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "tailwindCSS.includeLanguages": {
    "typescript": "javascript",
    "typescriptreact": "javascript"
  }
}
```

## Con-AI Specific Agent Development

### Agent Development with ClaudeCode
```bash
# Create a new construction software agent
claude "Create a Procore agent that:
1. Inherits from BaseAgent class
2. Uses browser-use to navigate Procore interface
3. Extracts project budget data
4. Sends real-time updates via WebSocket
5. Handles authentication errors gracefully
6. Logs all activities for compliance"

# Create corresponding frontend components
claude "Build components in frontend/src/components/agents/ that:
1. AgentCard.tsx - displays individual agent status with real-time updates
2. AgentList.tsx - shows all active agents in a responsive grid
3. AgentConfig.tsx - provides agent configuration interface
4. AgentStatus.tsx - detailed status view with activity logs
5. Use agentStore.ts for state management and useWebSocket hook for real-time data"

# Create dashboard components for data visualization
claude "Build dashboard components in frontend/src/components/dashboard/ that:
1. Dashboard.tsx - main dashboard layout with grid of charts
2. ProjectOverview.tsx - project summary cards with key metrics
3. RFIChart.tsx - request for information trends using Recharts
4. BudgetChart.tsx - budget variance tracking with real-time updates"
```

### WebSocket Integration Patterns
```bash
# Backend WebSocket handler
claude "Create FastAPI WebSocket endpoint that:
1. Manages multiple agent connections
2. Broadcasts agent status updates
3. Handles client disconnections gracefully
4. Validates message formats with Pydantic"

# Frontend WebSocket client
claude "Build WebSocket integration in frontend/src/hooks/ that:
1. useWebSocket.ts - manages connection lifecycle and reconnection
2. useAgents.ts - provides agent data fetching and real-time updates
3. Routes messages to appropriate Zustand stores (agentStore.ts, dataStore.ts)
4. Handles connection errors and offline state in uiStore.ts"

# Type definitions for WebSocket messages
claude "Create TypeScript types in frontend/src/types/ that:
1. agents.ts - agent status, configuration, and activity types
2. api.ts - WebSocket message protocols and API response types
3. construction.ts - project data types from Procore/Autodesk/Primavera
4. index.ts - exports all types for easy importing"
```

## Advanced Con-AI Workflows

### Multi-Agent Orchestration
```bash
claude "Create an agent orchestrator that:
1. Manages multiple construction software agents
2. Coordinates data collection schedules
3. Handles agent conflicts and priorities
4. Provides unified status reporting
5. Implements circuit breaker patterns for failed agents"
```

### Desktop Packaging Automation
```bash
# Automated build script
claude "Create a build script that:
1. Builds React frontend with Vite
2. Copies frontend build to FastAPI static directory
3. Packages everything with PyInstaller
4. Creates installer for Windows/macOS
5. Validates the packaged application works"
```

### Data Synchronization
```bash
claude "Implement a data sync system that:
1. Extracts data from Procore, Autodesk, and Primavera
2. Normalizes data formats into unified schema
3. Stores in SQLite with proper relationships
4. Provides real-time updates to React frontend
5. Handles conflicts between different data sources"
```

## Cost Optimization for Con-AI

### Anthropic Plan Recommendations
- **Claude Pro ($20/month)**: Individual developers working on Con-AI
- **Teams Plan**: For multi-developer teams building agents

### Usage Strategy
- Use ClaudeCode for complex agent logic and browser automation
- Leverage for React component development and TypeScript interfaces
- Let Claude handle PyInstaller configuration and build scripts
- Use for WebSocket message protocol design
- Automate test writing for both Python and TypeScript

## Success Metrics for Con-AI

### Before ClaudeCode
- Manual coding for each construction platform integration
- Complex WebSocket setup and debugging
- Time-consuming PyInstaller configuration
- Separate expertise needed for Python and TypeScript

### After ClaudeCode
- **5-10x faster agent development**
- **Seamless full-stack development** (Python + TypeScript)
- **Rapid prototyping** of new construction integrations
- **Automated testing and packaging** workflows

## Con-AI Development Milestones

### Milestone 1: Core Infrastructure (Weeks 1-2)
```bash
claude "Set up FastAPI backend with:
1. WebSocket support for real-time communication
2. SQLAlchemy models for project data
3. Base agent class with browser automation
4. CORS configuration for React development"

claude "Create React PWA with:
1. Vite configuration and PWA manifest
2. Zustand store for global state
3. WebSocket client service
4. Tailwind CSS design system setup"
```

### Milestone 2: First Construction Integration (Weeks 3-4)
```bash
claude "Build Procore agent with:
1. Browser automation for login and navigation
2. Data extraction for projects and budgets
3. Real-time WebSocket status updates
4. Error handling and retry logic"

claude "Create complete Procore dashboard interface:
1. pages/Dashboard.tsx - main dashboard page with layout
2. components/dashboard/ProjectOverview.tsx - project summary cards
3. components/dashboard/RFIChart.tsx - RFI trends visualization
4. components/dashboard/BudgetChart.tsx - budget tracking with variance
5. components/agents/AgentList.tsx - agent management interface
6. stores/agentStore.ts - agent state management
7. hooks/useAgents.ts - agent data fetching and real-time updates"

claude "Implement chart components for data visualization:
1. components/charts/ProjectChart.tsx - project timeline and milestones
2. components/charts/ProgressChart.tsx - construction progress tracking
3. components/charts/BudgetVarianceChart.tsx - budget vs actual analysis
4. All components should use Recharts and display real-time data"
```

### Milestone 3: Multi-Agent Orchestration (Weeks 5-6)
```bash
claude "Implement agent orchestrator that:
1. Manages Procore, Autodesk, and Primavera agents
2. Schedules data collection to avoid conflicts
3. Provides unified project view across platforms
4. Handles authentication refresh across agents"
```

### Milestone 4: Production-Ready Package (Weeks 7-8)
```bash
claude "Create production build system:
1. PyInstaller configuration for single executable
2. Automated installer creation for Windows/macOS
3. Auto-updater for future versions
4. License validation and compliance logging"
```

## Troubleshooting Con-AI Development

### Common Issues
1. **WebSocket Connection Issues**: Use ClaudeCode to debug connection lifecycle
2. **Browser Automation Failures**: Let Claude handle error scenarios and retries
3. **PyInstaller Package Problems**: Use ClaudeCode for build configuration
4. **CORS Issues**: Let Claude fix FastAPI CORS setup for React development

### Performance Tips
- Use ClaudeCode to optimize browser automation scripts
- Let Claude design efficient WebSocket message protocols
- Use ClaudeCode for SQLAlchemy query optimization
- Let Claude implement proper React component memoization

---

*This workflow positions Con-AI for rapid development of a production-ready construction project management tool using ClaudeCode's full-stack capabilities.*