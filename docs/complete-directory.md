frontend/
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
├── tsconfig.json
├── vite.config.ts
├── public/
│   ├── manifest.json
│   ├── icon-192.png
│   ├── icon-512.png
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── agents/
│   │   │   ├── AgentCard.tsx
│   │   │   ├── AgentConfig.tsx
│   │   │   ├── AgentStatus.tsx
│   │   │   └── AgentList.tsx
│   │   ├── dashboard/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── ProjectOverview.tsx
│   │   │   ├── RFIChart.tsx
│   │   │   └── BudgetChart.tsx
│   │   ├── common/
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── ErrorBoundary.tsx
│   │   ├── charts/
│   │   │   ├── ProjectChart.tsx
│   │   │   ├── ProgressChart.tsx
│   │   │   └── BudgetVarianceChart.tsx
│   │   └── onboarding/
│   │       ├── WelcomeScreen.tsx
│   │       ├── ConfigWizard.tsx
│   │       └── FirstTimeSetup.tsx
│   ├── hooks/
│   │   ├── useWebSocket.ts
│   │   ├── useAgents.ts
│   │   ├── useLocalStorage.ts
│   │   └── useConstructionData.ts
│   ├── stores/
│   │   ├── agentStore.ts
│   │   ├── dataStore.ts
│   │   └── uiStore.ts
│   ├── types/
│   │   ├── agents.ts
│   │   ├── construction.ts
│   │   ├── api.ts
│   │   └── index.ts
│   ├── utils/
│   │   ├── api.ts
│   │   ├── formatters.ts
│   │   ├── constants.ts
│   │   └── validation.ts
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Agents.tsx
│   │   ├── Settings.tsx
│   │   └── Help.tsx
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
└── tests/
    ├── components/
    ├── hooks/
    └── utils/