# Opportunity Intelligence Platform — Frontend

Vite + React + TypeScript frontend for the AI Opportunity Intelligence Platform.

## Tech Stack

- **Vite** — build tool
- **React 18** — UI framework
- **TypeScript** — type safety
- **Tailwind CSS** — utility-first styling
- **Recharts** — data visualization
- **Axios** — HTTP client
- **React Router** — client-side routing
- **Lucide React** — icon library

---

## Project Structure

```
frontend/
├── src/
│   ├── api/
│   │   └── client.ts              # Axios API client
│   ├── components/
│   │   ├── dashboard/
│   │   │   ├── AnalyzeForm.tsx    # Company name input + trigger
│   │   │   ├── AnalysisResult.tsx # AI result + stats display
│   │   │   ├── CompanyList.tsx    # Sidebar tracked companies
│   │   │   └── SignalsPanel.tsx   # Signal cards for selected company
│   │   └── shared/
│   │       └── SignalCard.tsx     # Individual signal card
│   ├── hooks/
│   │   ├── useAnalyze.ts          # Hook for analysis pipeline
│   │   └── useSignals.ts          # Hook for fetching signals
│   ├── pages/
│   │   └── DashboardPage.tsx      # Main dashboard page
│   ├── types/
│   │   └── index.ts               # Shared TypeScript interfaces
│   ├── utils/
│   │   └── format.ts              # Formatting utilities
│   ├── App.tsx                    # Root component + routing
│   ├── main.tsx                   # React entry point
│   └── index.css                  # Global styles + Tailwind
├── index.html
├── package.json
├── tailwind.config.js
├── vite.config.ts
└── tsconfig.json
```

---

## Setup & Run

### 1. Install dependencies

```bash
cd frontend
npm install
```

### 2. Start development server

```bash
npm run dev
```

Frontend runs at: http://localhost:5173

The Vite dev server proxies `/api/*` requests to `http://localhost:8000`, so the backend must be running.

### 3. Build for production

```bash
npm run build
```
