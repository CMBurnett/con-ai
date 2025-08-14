# Con-AI: Construction Intelligence Platform

A local desktop PWA for construction project management using AI agents to automate interactions with major construction software platforms.

## Overview

Con-AI is a desktop application that uses AI agents to automate data collection and analysis across construction management platforms like Procore, Autodesk Construction Cloud, and Oracle Primavera P6. Built with a local-first approach, it keeps all your project data on your machine while providing intelligent automation and insights.

## Features

- **AI-Powered Automation**: Browser-based agents that interact with construction software
- **Real-time Dashboard**: Live project metrics, RFI tracking, and budget variance analysis
- **Multi-Platform Support**: Procore, Autodesk Construction Cloud, Oracle Primavera P6
- **Local-First**: No cloud storage - all data stays on your machine
- **WebSocket Communication**: Real-time updates between frontend and backend
- **PWA Capabilities**: Installable desktop application with offline functionality

## Architecture

```
┌─────────────────┐    WebSocket    ┌──────────────────┐
│  React Frontend │ ◄──────────────► │ FastAPI Backend  │
│   (TypeScript)  │                 │    (Python)      │
└─────────────────┘                 └──────────────────┘
         │                                   │
         │                                   │
    ┌────▼────┐                         ┌────▼────┐
    │ Zustand │                         │ SQLite  │
    │  Store  │                         │Database │
    └─────────┘                         └─────────┘
                                             │
                                        ┌────▼────┐
                                        │Browser  │
                                        │Automation│
                                        │(Playwright)│
                                        └─────────┘
```

### Tech Stack

**Frontend**
- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS v4
- Zustand (state management)
- Recharts (data visualization)
- React Router DOM v7

**Backend**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (local database)
- browser-use (AI browser automation)
- Playwright (browser control)
- OpenAI/Anthropic APIs

**Distribution**
- PyInstaller (single executable)
- PWA capabilities

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/con-ai.git
   cd con-ai
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

### Development

1. **Start Backend Server**
   ```bash
   cd backend
   python main.py
   ```

2. **Start Frontend Development Server**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Open Application**
   - Navigate to `http://localhost:5173`
   - The frontend will proxy API calls to `http://localhost:8080`

### Building for Production

1. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Create Executable**
   ```bash
   cd backend
   pyinstaller --onefile main.py
   ```

## Project Structure

```
con-ai/
├── frontend/                 # React TypeScript frontend
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── agents/       # Agent management UI
│   │   │   ├── charts/       # Data visualization
│   │   │   ├── common/       # Shared components
│   │   │   ├── dashboard/    # Dashboard components
│   │   │   └── onboarding/   # Setup wizard
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Route components
│   │   ├── stores/           # Zustand state stores
│   │   ├── types/            # TypeScript definitions
│   │   └── utils/            # Helper functions
│   ├── public/               # Static assets
│   └── tests/                # Frontend tests
├── backend/                  # Python FastAPI backend
│   ├── agents/               # AI agent implementations
│   ├── api/                  # REST API endpoints
│   ├── models/               # Database models
│   ├── services/             # Business logic
│   └── tests/                # Backend tests
├── scripts/                  # Utility scripts
└── docs/                     # Documentation
```

## AI Agents

Con-AI includes specialized agents for different construction platforms:

### Procore Agent
- Project data synchronization
- RFI management
- Budget tracking
- Document management

### Autodesk Construction Cloud Agent
- BIM model data extraction
- Issue tracking
- Drawing management
- Collaboration metrics

### Primavera P6 Agent
- Schedule analysis
- Critical path monitoring
- Resource allocation tracking
- Progress reporting

## Security & Privacy

- **Local-First Architecture**: All data stored locally on your machine
- **No Credential Storage**: Uses existing browser sessions, never stores passwords
- **Audit Logging**: Complete audit trail of all agent actions
- **Browser Isolation**: Agents run in isolated browser contexts
- **API Key Management**: Secure local storage of AI service API keys

## Testing

### Frontend Tests
```bash
cd frontend
npm run test          # Run tests
npm run test:ui       # Run tests with UI
```

### Backend Tests
```bash
cd backend
pytest                # Run Python tests
```

## Development Commands

### Frontend
```bash
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
npm run test         # Run tests
```

### Backend
```bash
python main.py       # Start FastAPI server
black .              # Format Python code
pytest               # Run tests
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions, issues, or feature requests:

1. Check the [Issues](https://github.com/yourusername/con-ai/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

## Roadmap

- [ ] Enhanced AI agent capabilities
- [ ] Additional construction software integrations
- [ ] Advanced analytics and reporting
- [ ] Multi-project management
- [ ] Team collaboration features
- [ ] Mobile companion app

---

**Made with ❤️ for the construction industry**