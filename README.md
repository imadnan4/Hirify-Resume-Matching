# Hirify

Hirify is a resume and job matching app with a React frontend and a clean FastAPI backend.

The backend in this repo has been rebuilt around the actual frontend contract in:

- `frontend/src/services/api.ts`
- `docs/frontend-backend-contract.md`

This README reflects the backend that is implemented now, not the older Celery/Redis/auth architecture that used to be documented here.

## Current Backend Status

- Fresh FastAPI backend under `backend/`
- Frontend-first API contract implemented
- Resume ingestion for `PDF` and `DOCX`
- Legacy `.doc` files are rejected in v1
- Structured resume preview data for the current UI
- Single match and many-to-many bulk match
- Candidate records derived from processed resumes
- Local default database is SQLite for easy development
- Production path is Postgres/Neon, with `pgvector` support when available
- Base install works without heavyweight ML packages
- Optional transformer-based embeddings can be added through `backend/requirements-ml.txt`

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS

### Backend

- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Alembic
- Pydantic v2
- Uvicorn

### Document Processing

- PyMuPDF for PDF parsing
- docx2txt for DOCX parsing

### Matching

- Weighted scoring:
  - Skills: `0.40`
  - Experience: `0.30`
  - Education: `0.20`
  - Additional: `0.10`
- Base install uses deterministic hashing embeddings
- Optional local embedding model support via `sentence-transformers`

### Storage

- Local dev default: SQLite
- Production target: Postgres / Neon
- Uploaded files stored on disk via configurable `UPLOAD_ROOT`

## Backend Features

### Resume Processing

- `POST /api/v1/resumes/upload`
- `POST /api/v1/resumes/bulk-upload`
- `GET /api/v1/resumes/`
- `GET /api/v1/resumes/{id}`
- `GET /api/v1/resumes/{id}/status`
- `GET /api/v1/resumes/{id}/preview`
- `POST /api/v1/resumes/{id}/reprocess`
- `PUT /api/v1/resumes/{id}`
- `DELETE /api/v1/resumes/{id}`

Each processed resume stores:

- extracted text
- structured preview data
- processing status
- optional embedding vector
- candidate-facing normalized fields

### Job Management

- `POST /api/v1/jobs/`
- `GET /api/v1/jobs/`
- `GET /api/v1/jobs/{id}`
- `PUT /api/v1/jobs/{id}`
- `DELETE /api/v1/jobs/{id}`
- `POST /api/v1/jobs/scrape`
- `GET /api/v1/jobs/search/skills`
- `GET /api/v1/jobs/{id}/skills`
- `POST /api/v1/jobs/{id}/reprocess`

### Matching

- `POST /api/v1/matching/match`
- `POST /api/v1/matching/bulk-match`
- `GET /api/v1/matching/`
- `GET /api/v1/matching/{id}`
- `PUT /api/v1/matching/{id}`
- `DELETE /api/v1/matching/{id}`
- `GET /api/v1/matching/{id}/explanation`
- `GET /api/v1/matching/stats`
- `GET /api/v1/matching/top-matches`
- `GET /api/v1/matching/job/{job_id}/candidates`

Bulk matching uses the frontend's current many-to-many shape:

```json
{
  "resume_ids": [1, 2, 3],
  "job_ids": [10, 11],
  "min_score_threshold": 0.5,
  "include_explanations": true
}
```

Only pairs meeting the threshold are persisted during bulk matching.

### Candidates

- `GET /api/v1/candidates/`
- `GET /api/v1/candidates/{id}`
- `PUT /api/v1/candidates/{id}`
- `DELETE /api/v1/candidates/{id}`
- `GET /api/v1/candidates/{id}/resume`
- `GET /api/v1/candidates/search/by-skills`

## API Response Conventions

List endpoints return:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 100,
  "pages": 0
}
```

Match scores are returned in the `0..1` range. The frontend multiplies them by `100` for display.

Resume preview responses are shaped for the current modal:

```json
{
  "contact_info": {},
  "summary": "string",
  "work_experience": [],
  "education": [],
  "skills": [],
  "certifications": [],
  "processing_metadata": {}
}
```

## Project Structure

```text
hirify/
├── backend/
│   ├── alembic/
│   │   └── versions/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   └── services/
│   ├── data/
│   ├── tests/
│   ├── main.py
│   ├── requirements.txt
│   └── requirements-ml.txt
├── docs/
├── frontend/
└── README.md
```

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+

### Backend

```bash
cd backend
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

Optional local embedding model support:

```bash
pip install -r requirements-ml.txt
```

Run migrations if you want Alembic-managed schema setup:

```bash
alembic upgrade head
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Useful URLs:

- API root: `http://localhost:8000/`
- Health: `http://localhost:8000/health`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

Note:

- The app also creates tables on startup through `init_db()`, which makes local boot simpler.
- `.doc` files are intentionally not supported in v1.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend expects the backend at `http://localhost:8000` unless `VITE_API_URL` is set.

## Configuration

The most useful backend environment variables are:

```env
DATABASE_URL=sqlite:///backend/data/hirify.db
UPLOAD_ROOT=backend/data/uploads
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://hirify-frontend.netlify.app
EMBEDDING_BACKEND=auto
EMBEDDING_MODEL_NAME=BAAI/bge-small-en-v1.5
EMBEDDING_DIMENSIONS=384
SQL_ECHO=false
```

`EMBEDDING_BACKEND` behavior:

- `auto`: use `sentence-transformers` if installed, otherwise fall back to hashing embeddings
- `hash`: always use the lightweight hashing backend
- `sentence-transformers`: prefer the local transformer embedding path

## Railway / Neon Notes

This backend is structured so it can move from local SQLite to Railway + Neon cleanly.

Recommended production setup:

- Set `DATABASE_URL` to your Neon Postgres connection string
- Mount persistent storage on Railway and point `UPLOAD_ROOT` to it
- Set `CORS_ORIGINS` to your frontend origin(s), for example `https://hirify-frontend.netlify.app`
- Keep `EMBEDDING_BACKEND=hash` for the lightest deploy, or install `requirements-ml.txt` if you want local transformer embeddings

Example production startup command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
```

When running on Postgres, the backend attempts `CREATE EXTENSION IF NOT EXISTS vector` during startup. If `pgvector` is unavailable, embeddings still fall back to JSON storage.

## Testing

Backend contract tests live in `backend/tests/`.

Run them with:

```bash
python -m pytest backend/tests -q
```

The current contract suite covers:

- health check
- resume upload
- resume preview
- resume reprocess
- DOCX support
- `.doc` rejection
- job creation
- single matching
- many-to-many bulk matching
- stats and ranked candidates
- delete flows

## Important Notes

- This backend is synchronous by design in v1 so it matches the current frontend behavior immediately.
- There is no Celery, Redis, JWT auth, or background worker layer in the current backend.
- The backend contract is driven by the mounted frontend, not the older architecture notes.
- The active migration is `backend/alembic/versions/0001_frontend_first_contract.py`.

## License

This project is licensed under the MIT License. See `LICENSE` if present in the repository.
