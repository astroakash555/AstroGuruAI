# AstroGuruAI Frontend

Production-quality React dashboard for the AstroGuruAI platform.

## Stack

- React + TypeScript + Vite
- React Router
- TanStack Query
- Axios
- Tailwind CSS + shadcn/ui-style components
- React Hook Form + Zod

## Getting started

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The dev server runs on `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

## Scripts

- `npm run dev` — start Vite dev server
- `npm run build` — typecheck and build production bundle
- `npm run preview` — preview production build
- `npm test` — run Vitest component/unit tests

## Pages

- Login
- Dashboard
- Clients
- Add/Edit Client
- Birth Details Form
- Generate Report
- Report Viewer
- PDF Viewer
- AI Chat
- Settings

## API integration

The frontend uses the existing FastAPI backend without API changes:

- `GET /api/v1/health`
- `/api/v1/clients`
- `/api/v1/dashboard/reports`
- `POST /api/v1/chat`

Configure the API base URL with `VITE_API_BASE_URL`.

## Auth note

Login uses a local demo session token and Bearer header injection so the UI is authentication-ready before backend auth lands.
