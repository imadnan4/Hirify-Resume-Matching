# Hirify

Open-source resume-to-job matching engine. Upload resumes, add job descriptions, and get AI-powered match scores with transparent breakdowns.

- **Frontend**: React + TypeScript + Vite + Tailwind CSS + Optics UI
- **Backend**: FastAPI + SQLAlchemy 2 + Pydantic v2 + FastEmbed
- **Document parsing**: PyMuPDF (PDF) + docx2txt (DOCX)
- **Matching**: Hybrid keyword + semantic embedding scoring

## Quick Start

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
fastapi dev app/main.py

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 — the frontend proxies `/api` to the backend.

## Architecture

### Matching Engine

The matching system uses a **hybrid approach** that combines lexical skill matching with semantic embeddings:

| Component | Weight | Method |
|-----------|--------|--------|
| Skills | 40% | 55% keyword overlap + 45% embedding similarity |
| Experience | 30% | Years comparison + semantic similarity |
| Education | 20% | Degree level matching + semantic similarity |
| Additional | 10% | Certifications, location, summary bonuses |

Each match produces:
- Overall score (0.0–1.0)
- Per-category breakdowns
- Matched and missing skills lists
- Confidence level (high/medium/low)
- Human-readable recommendation
- Detailed explanation with reasons

### Embeddings

**Production**: FastEmbed with ONNX Runtime. Uses `BAAI/bge-small-en-v1.5` (384-dim). No PyTorch required — significantly lighter and faster cold start than sentence-transformers.

**Fallback**: A deterministic hashing provider produces pseudo-embeddings for environments where ML libraries cannot be installed. This is a **degraded mode** — matching quality will be reduced. Always prefer the FastEmbed provider for production.

Set `EMBEDDING_BACKEND=auto` (the default) to auto-detect FastEmbed availability. Set `EMBEDDING_BACKEND=hash` to force the fallback.

### Resume Parsing

PDFs are extracted with PyMuPDF (fast, accurate for digital documents). DOCX files via docx2txt. Extracted text passes through a purpose-built regex pipeline that detects:

- Contact information (name, email, phone, location, URLs)
- Work experience (job titles, companies, date ranges)
- Education (degrees, institutions, graduation years)
- Skills (against a curated vocabulary of 50+ tech skills)
- Certifications and professional summaries

### Database

- **Development**: SQLite (zero-config, stored in `data/hirify.db`)
- **Production**: PostgreSQL with optional `pgvector` extension for native vector operations. Falls back to JSON storage when pgvector is unavailable.

Tables are auto-created on startup via `Base.metadata.create_all()`. Alembic migrations are available for production schema management.

## API Endpoints

### Resumes

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/resumes/upload` | Upload a single resume |
| POST | `/api/v1/resumes/bulk-upload` | Upload multiple resumes |
| GET | `/api/v1/resumes/` | List resumes (paginated, filterable by status) |
| GET | `/api/v1/resumes/{id}` | Get resume metadata |
| GET | `/api/v1/resumes/{id}/status` | Get processing status and progress |
| GET | `/api/v1/resumes/{id}/preview` | Get extracted structured data |
| POST | `/api/v1/resumes/{id}/reprocess` | Re-trigger parsing pipeline |
| PUT | `/api/v1/resumes/{id}` | Update resume metadata |
| DELETE | `/api/v1/resumes/{id}` | Delete resume and file |

### Jobs

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/jobs/` | Create a job description |
| GET | `/api/v1/jobs/` | List jobs (paginated, filterable) |
| GET | `/api/v1/jobs/{id}` | Get job details |
| GET | `/api/v1/jobs/{id}/skills` | Get extracted skills for a job |
| PUT | `/api/v1/jobs/{id}` | Update job description |
| POST | `/api/v1/jobs/{id}/reprocess` | Re-extract skills and re-embed |
| DELETE | `/api/v1/jobs/{id}` | Delete job description |
| GET | `/api/v1/jobs/search/skills` | Find jobs by skill keywords |

### Matching

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/matching/match` | Single resume-to-job match |
| POST | `/api/v1/matching/bulk-match` | Many-to-many bulk matching |
| GET | `/api/v1/matching/` | List matches (paginated, filterable) |
| GET | `/api/v1/matching/{id}` | Get match details |
| GET | `/api/v1/matching/{id}/explanation` | Get match explanation |
| PUT | `/api/v1/matching/{id}` | Update match record |
| DELETE | `/api/v1/matching/{id}` | Delete match record |
| GET | `/api/v1/matching/stats` | Aggregate match statistics |
| GET | `/api/v1/matching/top-matches` | Top N matches by score |
| GET | `/api/v1/matching/job/{job_id}/candidates` | Ranked candidates for a job |

### Candidates

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/candidates/` | List candidates (paginated) |
| GET | `/api/v1/candidates/{id}` | Get candidate details |
| GET | `/api/v1/candidates/{id}/resume` | Get linked resume data |
| PUT | `/api/v1/candidates/{id}` | Update candidate record |
| DELETE | `/api/v1/candidates/{id}` | Delete candidate record |
| GET | `/api/v1/candidates/search/by-skills` | Find candidates by skills |

### API Conventions

All list endpoints return paginated responses:
```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```

Match scores are in `0.0–1.0` range. The frontend multiplies by 100 for display percentages.

## Configuration

Environment variables (with defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///data/hirify.db` | Database connection string |
| `UPLOAD_ROOT` | `data/uploads` | File upload storage path |
| `CORS_ORIGINS` | `http://localhost:3000,...` | Allowed CORS origins |
| `EMBEDDING_BACKEND` | `auto` | `auto`, `fastembed`, or `hash` |
| `EMBEDDING_MODEL_NAME` | `BAAI/bge-small-en-v1.5` | Embedding model identifier |
| `EMBEDDING_DIMENSIONS` | `384` | Embedding vector dimension |
| `SQL_ECHO` | `false` | Log all SQL queries |
| `DEBUG` | `false` | Enable debug mode |
| `MATCH_WEIGHT_SKILLS` | `0.40` | Skills weight in scoring |
| `MATCH_WEIGHT_EXPERIENCE` | `0.30` | Experience weight in scoring |
| `MATCH_WEIGHT_EDUCATION` | `0.20` | Education weight in scoring |
| `MATCH_WEIGHT_ADDITIONAL` | `0.10` | Additional factors weight |

## Project Structure

```text
hirify/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── alembic/
│   │   ├── versions/
│   │   │   └── 0001_frontend_first_contract.py
│   │   ├── env.py
│   │   └── script.py.mako
│   ├── alembic.ini
│   ├── app/
│   │   ├── api/routes/
│   │   │   ├── candidates.py
│   │   │   ├── jobs.py
│   │   │   ├── matching.py
│   │   │   └── resumes.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   └── database.py
│   │   ├── models/
│   │   │   ├── base.py
│   │   │   ├── candidate.py
│   │   │   ├── job.py
│   │   │   ├── match.py
│   │   │   ├── resume.py
│   │   │   └── types.py
│   │   ├── schemas/
│   │   │   ├── candidate.py
│   │   │   ├── common.py
│   │   │   ├── job.py
│   │   │   ├── match.py
│   │   │   └── resume.py
│   │   ├── services/
│   │   │   ├── candidate_service.py
│   │   │   ├── document_extractor.py
│   │   │   ├── embedding_service.py
│   │   │   ├── job_service.py
│   │   │   ├── matching_service.py
│   │   │   ├── resume_parser.py
│   │   │   └── text_processing.py
│   │   └── main.py
│   ├── tests/
│   │   ├── conftest.py
│   │   └── test_contract.py
│   ├── .env.example
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── optics/       # Optics UI design system components
│   │   │   ├── ui/           # Re-exports, toast, charts, confirm-dialog
│   │   │   ├── Analytics.tsx
│   │   │   ├── AppSidebar.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── JobManager.tsx
│   │   │   ├── Layout.tsx
│   │   │   ├── MatchingInterface.tsx
│   │   │   └── ResumeManager.tsx
│   │   ├── hooks/
│   │   │   └── use-mobile.ts
│   │   ├── lib/
│   │   │   └── utils.ts
│   │   ├── services/
│   │   │   └── api.ts        # Frontend-backend contract
│   │   ├── App.tsx
│   │   ├── globals.css
│   │   └── main.tsx
│   ├── .env.example
│   ├── components.json
│   ├── index.html
│   ├── package.json
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── vite.config.ts
├── .env.example
├── .gitignore
├── netlify.toml
└── README.md
```

## Testing

```bash
cd backend
pip install python-docx  # needed for test DOCX generation
python -m pytest tests/ -v
```

The contract test suite validates the full pipeline end-to-end:
- Health endpoint
- PDF and DOCX upload and parsing
- Legacy `.doc` rejection
- Structured data extraction (skills, experience, education, contact info)
- Single and bulk matching
- Match statistics and ranked candidates
- CRUD operations across all resources

## Production Deployment

### Railway + Neon (Backend)

```bash
cd backend
railway init
railway service

# Set production variables
railway variables set \
  DATABASE_URL='postgresql://...' \
  CORS_ORIGINS='["https://your-frontend.netlify.app"]' \
  EMBEDDING_BACKEND='auto'

railway up
```

The Dockerfile in `backend/` uses `fastapi run app/main.py` and includes FastEmbed for production-quality embeddings.

### Netlify (Frontend)

The `netlify.toml` is pre-configured for a Vite SPA. Set `VITE_API_URL` in Netlify environment variables to your backend URL.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| API framework | FastAPI 0.115+ |
| ORM | SQLAlchemy 2.0+ |
| Schema validation | Pydantic v2 |
| Embeddings | FastEmbed (ONNX Runtime) |
| PDF parsing | PyMuPDF |
| DOCX parsing | docx2txt |
| NLP/Text | Custom regex pipeline + keyword matching |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS v4, Optics UI |
| Charts | Recharts |
| HTTP client | Axios (frontend), HTTPX (test) |
| Testing | Pytest |


