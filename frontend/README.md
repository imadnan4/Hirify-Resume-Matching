# Hirify — Autonomous Candidate Screening Agent Frontend

A high-fidelity web application built with **React 19**, **TypeScript**, and **Vite**, adhering strictly to the **Olive Familjen Theme** (`Familjen Grotesk` display typography, `Inter` UI, OKLCH olive color tokens, and comprehensive light/dark mode support).

Hirify enables recruiters and hiring managers to ingest job requisitions and candidate resumes, running an autonomous AI agent loop with RAG semantic retrieval, 100% verbatim resume citations, and auditable knock-out guardrails.

---

## 🚀 Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Run Development Server
```bash
npm run dev
```
Open `http://localhost:5173` in your browser.

### 3. Typecheck & Build
```bash
npm run typecheck
npm run build
```

### 4. Preview Production Build
```bash
npm run preview
```

---

## 📁 Component Architecture

```
frontend/
├── index.html                   # React 19 Single Page Application entry point
├── test.html                    # Hero Dashboard comparison & verification sandbox
├── vite.config.ts               # Clean multi-page rollup for SPA and test sandbox
├── src/
│   ├── components/
│   │   ├── common/              # Shared navigation, footer, and theme toggles
│   │   │   ├── Navbar.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── ThemeToggle.tsx
│   │   ├── dashboard/           # Core 4-column screening agent dashboard
│   │   │   └── HeroDashboard.tsx
│   │   └── landing/             # Modular landing page sections
│   │       ├── HeroSection.tsx
│   │       ├── FeaturesSection.tsx
│   │       ├── HowItWorks.tsx
│   │       ├── MetricsSection.tsx
│   │       ├── FaqSection.tsx
│   │       └── CallToAction.tsx
│   ├── pages/                   # Top-level view controllers
│   │   ├── Home.tsx             # Composed landing page with embedded HeroDashboard
│   │   ├── UploadView.tsx       # Step 1: Requisition definition & batch CV ingest
│   │   ├── RankingView.tsx      # Step 2: Filterable candidate leaderboard & KO tags
│   │   ├── CandidateDetailView.tsx # Step 3: Evidence dossier & verbatim quotes
│   │   ├── EvalView.tsx         # Step 4: Heldout benchmark evaluation harness
│   │   ├── Test.tsx             # React sandbox for dashboard verification
│   │   ├── Pricing.tsx
│   │   └── About.tsx
│   ├── services/
│   │   └── api.ts               # Typed client connecting to FastAPI backend
│   ├── styles/
│   │   ├── oatmeal.css          # Olive Familjen OKLCH theme variables & fonts
│   │   └── test.css             # Hero dashboard pixel-level layout rules
│   ├── types/
│   │   ├── hirify.ts            # Domain types matching backend schemas
│   │   └── custom-elements.d.ts # Custom web component declarations
│   ├── App.tsx                  # Client router & theme state manager
│   └── main.tsx                 # React DOM mount point
└── public/
    └── assets/                  # Logos, screenshots, and static brand assets
```

---

## 🔗 Backend Contract Integration

The frontend seamlessly connects to the FastAPI backend defined in `docs/BACKEND_API.md`:

| Endpoint | Purpose | Method |
| :--- | :--- | :--- |
| `POST /jobs` | Create role specification & parse REQ criteria | `HirifyAPI.createJob` |
| `POST /jobs/{id}/candidates:upload` | Multipart batch resume upload (PDF/TXT) | `HirifyAPI.uploadCandidates` |
| `POST /jobs/{id}/screen` | Trigger autonomous Qwen screening loop | `HirifyAPI.triggerScreening` |
| `GET /jobs/{id}/ranking` | Retrieve ranked candidates with scores & KO tags | `HirifyAPI.getCandidates` |
| `GET /candidates/{id}` | Inspect detailed evidence dossier & citations | `HirifyAPI.getCandidate` |
| `POST /candidates/{id}/schedule?slot=...` | Schedule database interview stub (no email) | `HirifyAPI.scheduleInterviewStub` |
| `GET /eval` | Fetch latest evaluation benchmark metrics | `HirifyAPI.getEvalResults` |

*Note: All API calls include typed graceful fallbacks with pre-seeded test data for standalone demo mode.*

---

## 🎨 Design System: Olive Familjen Theme

- **Headings**: `Familjen Grotesk` (weights 400..700)
- **UI & Body**: `Inter` (weights 100..900)
- **Palette**: Olive OKLCH scale (`--color-olive-50` through `--color-olive-950`)
- **Theme Persistence**: Automatic system theme detection with manual light/dark toggle persisted in `localStorage`.
