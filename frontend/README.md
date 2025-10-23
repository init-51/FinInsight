# FinInsight Frontend

This is a Vite + React frontend for the FinInsight project.

Quick start

1. Install dependencies

```bash
cd frontend
npm install
```

2. Start dev server

```bash
npm run dev
```

3. Build production

```bash
npm run build
npm run preview
```

Environment

Copy `.env.example` to `.env` and adjust `VITE_API_URL` to point to your API (e.g., http://localhost:8000 for local development)

Docker

Build and run:

```bash
docker build -t fininsight-frontend ./frontend
docker run -p 3000:3000 fininsight-frontend
```

Notes

- The frontend proxies `/api` to the backend during development (see `vite.config.ts`).
- Components:
  - `PortfolioForm` - submit new backtest jobs
  - `JobTracker` - poll job status and display results
  - `ResultsView` - display charts using Chart.js
