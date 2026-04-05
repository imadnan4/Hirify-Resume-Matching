# Hirify Frontend-to-Backend Contract

This document describes the backend contract the current frontend expects, based on actual frontend code and then cross-checked against the current backend implementation.

It is intentionally not based on the root `README.md` alone, because several parts of that file are stale or do not match the codebase anymore.

## Scope

This document answers four questions:

1. What routes the frontend currently calls.
2. What request shape each route sends.
3. What response shape the frontend expects back.
4. Where the current backend does and does not match that contract.

## Sources Used

Frontend sources:

- `frontend/src/services/api.ts`
- `frontend/src/App.tsx`
- `frontend/src/components/Dashboard.tsx`
- `frontend/src/components/ResumeManager.tsx`
- `frontend/src/components/JobManager.tsx`
- `frontend/src/components/MatchingInterface.tsx`
- `frontend/src/components/Analytics.tsx`
- `frontend/src/components/Layout.tsx`

Backend sources:

- `backend/app/main.py`
- `backend/app/api/v1/endpoints/resumes.py`
- `backend/app/api/v1/endpoints/jobs.py`
- `backend/app/api/v1/endpoints/candidates.py`
- `backend/app/api/v1/endpoints/matching.py`
- `backend/app/api/v1/endpoints/auth.py`
- `backend/app/schemas/resume.py`
- `backend/app/schemas/job_description.py`
- `backend/app/schemas/candidate.py`
- `backend/app/schemas/match.py`
- `backend/app/models/resume.py`
- `backend/app/models/job_description.py`
- `backend/app/models/candidate.py`
- `backend/app/models/match.py`
- `backend/app/core/config.py`

Local docs reviewed but treated as non-authoritative:

- `README.md`
- `backend/SETUP_GUIDE.md`

## High-Level Architecture the Frontend Assumes

The frontend is a Vite + React SPA with four active pages:

- `/` -> dashboard
- `/resumes` -> resume management
- `/jobs` -> job management
- `/matching` -> match creation and match review

All backend calls are centralized in `frontend/src/services/api.ts`.

There are no direct `fetch(...)` calls elsewhere in the frontend. The current UI only talks to the backend through the `apiService` wrapper.

## Base URL, Ports, and Runtime Modes

The frontend axios client is configured as:

- Base URL: `import.meta.env.VITE_API_URL || 'http://localhost:8000'`
- Timeout: `30000` ms
- Default header: `Content-Type: application/json`

What is actually verifiable from the repo:

- `frontend/src/services/api.ts` hardcodes the fallback backend base URL to `http://localhost:8000`.
- `frontend/vite.config.ts` runs Vite dev server on port `3000`.
- `frontend/vite.config.ts` proxies `/api` requests to `http://localhost:8000`.
- `backend/main.py` runs uvicorn on port `8000`.
- `backend/app/main.py` also runs uvicorn on port `8000`.
- `nginx/nginx.conf` assumes an upstream `frontend:3000` and `backend:8000`.
- `scripts/deploy.sh` health-checks `http://localhost:3000` for frontend and `http://localhost:8000/health` for backend.
- There is no checked-in frontend `.env` or backend `.env` in this repo proving a different committed runtime port.

Implications:

- For local dev, the committed code does point to frontend `3000` and backend `8000`.
- For deployed/proxied mode, the browser may talk to the public domain on `80/443`, while nginx forwards to internal `frontend:3000` and `backend:8000`.
- Because there is no committed `frontend/.env` or root `.env` overriding `VITE_API_URL`, we cannot verify a different frontend API host from the repo alone.
- `.env.example` contains `REACT_APP_API_URL=http://localhost:8000`, but that key is stale for this Vite frontend because the frontend code reads `VITE_API_URL`, not `REACT_APP_API_URL`.
- File upload endpoints override the content type to `multipart/form-data`.
- No auth token injection is currently implemented in `frontend/src/services/api.ts`.
- The active UI does not use the auth routes at all.

## What the User Can Actually Do in the Current Frontend

### Dashboard page

The dashboard loads:

- resumes list
- jobs list
- matches list

It computes analytics client-side from those three list endpoints.

### Resumes page

The resumes page allows:

- selecting PDF/DOC/DOCX files
- validating files client-side
- uploading resumes one-by-one
- listing resumes
- deleting resumes
- reprocessing a resume
- previewing extracted structured data

Important note: the UI exposes multi-file upload selection, but when the user clicks upload it calls `uploadResume(file)` once per file. It does not currently call the backend bulk upload route from the UI, even though `api.ts` defines one.

### Jobs page

The jobs page allows:

- listing jobs
- manually creating one job
- deleting one job

The current UI does not expose:

- job update
- job scraping
- job reprocessing
- job skill lookup
- bulk job creation
- job search by skills

### Matching page

The matching page allows:

- listing processed resumes
- listing jobs
- listing matches
- creating a single match
- creating bulk matches
- deleting a match

The current UI does not expose:

- fetch single match detail
- update match
- fetch explanation endpoint
- fetch matching stats endpoint
- fetch top matches endpoint
- ranked candidates for a job

### Analytics component

`frontend/src/components/Analytics.tsx` exists and makes backend calls, but it is not mounted in `frontend/src/App.tsx`.

So it is part of the codebase contract, but not part of the currently reachable UI routes.

## Canonical Frontend Data Shapes

These are the TypeScript shapes the frontend uses as its working contract.

### Resume

```ts
{
  id: number
  filename: string
  file_type: string
  file_size: number
  file_path: string
  upload_date: string
  processed_date?: string
  status: 'pending' | 'processing' | 'completed' | 'failed'
  extracted_text?: string
  structured_data?: any
  processing_errors?: any
  created_at: string
  updated_at: string
}
```

### JobDescription

```ts
{
  id: number
  title: string
  company: string
  description: string
  source: string
  location?: string
  salary_range?: string
  employment_type?: string
  experience_level?: string
  scraped_date?: string
  processed_date?: string
  requirements?: string
  source_url?: string
  structured_data?: any
  extracted_skills?: any
  processing_errors?: any
  status: string
  created_at: string
  updated_at: string
}
```

### Candidate

```ts
{
  id: number
  resume_id: number
  full_name?: string
  email?: string
  phone?: string
  location?: string
  linkedin_url?: string
  portfolio_url?: string
  years_experience?: number
  education_level?: string
  field_of_study?: string
  university?: string
  graduation_year?: number
  current_position?: string
  current_company?: string
  skills?: any
  work_history?: any
  education_history?: any
  certifications?: any
  languages?: any
  projects?: any
  achievements?: any
  summary?: string
  created_at: string
  updated_at: string
}
```

### Match

```ts
{
  id: number
  resume_id: number
  job_id: number
  overall_score: number
  skills_score?: number
  experience_score?: number
  education_score?: number
  additional_score?: number
  matched_skills?: any
  missing_skills?: any
  skill_overlap_count?: number
  total_required_skills?: number
  explanation?: any
  confidence_level?: string
  recommendation?: string
  created_at: string
  updated_at: string
}
```

### PaginatedResponse<T>

```ts
{
  items: T[]
  total: number
  page: number
  size: number
  pages: number
}
```

## Route Inventory

The frontend API service defines the following route set.

Legend:

- `USED`: actively called by mounted UI screens
- `DEFINED_ONLY`: present in `api.ts` but not called by mounted UI
- `BACKEND_OK`: route exists in backend with compatible path/method
- `BACKEND_MISMATCH`: path, method, body shape, or response shape does not match
- `BACKEND_PARTIAL_MATCH`: main route exists, but some documented params or semantics drift
- `BACKEND_RISKY_MATCH`: route exists, but implementation or route ordering makes it unreliable
- `BACKEND_MISSING_AS_PATH`: backend has related functionality, but at a different path
- `BACKEND_MISSING`: frontend expects it, backend does not implement it

### Health

#### `GET /health`

- Frontend status: `DEFINED_ONLY`
- Current UI usage: no mounted screen calls it
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "status": "healthy",
  "message": "API is running"
}
```

Backend currently returns exactly that shape.

## Resume Routes

### `POST /api/v1/resumes/upload`

- Frontend status: `USED`
- Screen: resumes page
- Content type: `multipart/form-data`
- Form fields:
  - `file`: binary file

Client-side validation before sending:

- extension or MIME type must indicate PDF, DOC, or DOCX
- file size must be <= 10 MB

Frontend expects a response like:

```json
{
  "id": 123,
  "filename": "resume.pdf",
  "file_size": 345678,
  "status": "pending",
  "upload_date": "2026-04-05T12:34:56Z",
  "message": "Resume uploaded successfully"
}
```

Backend match:

- Path and method match.
- Body shape matches.
- Response schema matches `ResumeUploadResponse`.

Observed backend processing flow:

1. Save file under `uploads/resumes/<uuid>.<ext>`.
2. Create DB row with `status="pending"`.
3. Since `USE_BACKGROUND_PROCESSING` defaults to `False`, processing runs synchronously in the request.
4. Resume is eventually marked `completed` or `failed`.
5. A candidate row may be auto-created if extracted contact info contains a full name.

Important implementation note:

- The response schema is declared as upload confirmation, but because processing is synchronous by default, the returned `status` may already be `completed` by the time the request returns.

### `POST /api/v1/resumes/bulk-upload`

- Frontend status: `DEFINED_ONLY`
- Current mounted UI usage: not used
- Backend status: `BACKEND_OK`

Request:

- `multipart/form-data`
- repeated field name `files`

Expected response:

```json
{
  "successful": [
    {
      "id": 1,
      "filename": "a.pdf",
      "file_size": 123,
      "status": "completed",
      "upload_date": "..."
    }
  ],
  "failed": [
    {
      "filename": "bad.txt",
      "error": "Invalid file type..."
    }
  ],
  "total_uploaded": 1,
  "total_failed": 1
}
```

Backend matches this shape.

### `GET /api/v1/resumes/`

- Frontend status: `USED`
- Screens: dashboard, resumes page, matching page, analytics component
- Backend status: `BACKEND_OK`

Query params the frontend may send:

- `skip?: number`
- `limit?: number`
- `status?: string`

Expected response:

```json
{
  "items": [/* Resume[] */],
  "total": 50,
  "page": 1,
  "size": 50,
  "pages": 1
}
```

Backend matches this shape.

Frontend usage details:

- resumes page calls with `{ limit: 50 }`
- matching page calls with `{ limit: 100 }`
- dashboard and analytics call with `{ limit: 1000 }`
- matching page further filters client-side to `resume.status === 'completed'`

### `GET /api/v1/resumes/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response: full `Resume` object.

### `GET /api/v1/resumes/{id}/status`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "id": 1,
  "filename": "resume.pdf",
  "status": "processing",
  "processed_date": null,
  "processing_errors": null,
  "progress": 50
}
```

Backend matches this.

Progress mapping currently hardcoded by backend:

- `pending` -> `0`
- `processing` -> `50`
- `completed` -> `100`
- `failed` -> `0`

### `PUT /api/v1/resumes/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected request body: partial `Resume`.

Backend accepts a partial `ResumeUpdate` object:

```json
{
  "filename": "...",
  "status": "completed",
  "processed_date": "...",
  "extracted_text": "...",
  "structured_data": {},
  "processing_errors": {}
}
```

### `DELETE /api/v1/resumes/{id}`

- Frontend status: `USED`
- Screen: resumes page
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "message": "Resume deleted successfully"
}
```

Backend behavior:

- deletes related candidate rows
- deletes related match rows
- deletes file from disk if present
- deletes resume row

### `POST /api/v1/resumes/{id}/reprocess`

- Frontend status: `USED`
- Screen: resumes page
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "message": "Resume reprocessing started"
}
```

Backend notes:

- resets status to `pending`
- clears `processed_date` and `processing_errors`
- runs processing immediately in development mode

### `GET /api/v1/resumes/{id}/preview`

- Frontend status: `USED`
- Screen: resumes page preview modal
- Backend status: `BACKEND_OK`

Frontend expects arbitrary structured JSON, and the preview modal is written against this shape:

```json
{
  "contact_info": {
    "full_name": "Jane Doe",
    "email": "jane@example.com",
    "phone": "...",
    "location": "..."
  },
  "summary": "...",
  "work_experience": [
    {
      "job_title": "...",
      "company": "...",
      "start_date": "...",
      "end_date": "...",
      "description": "..."
    }
  ],
  "education": [
    {
      "degree": "...",
      "field_of_study": "...",
      "institution": "...",
      "graduation_year": 2022
    }
  ],
  "skills": ["React", "TypeScript"],
  "certifications": ["AWS CCP"],
  "processing_metadata": {}
}
```

Important mismatch risk inside this same feature:

- Backend stores `skills` from `parsed_resume.skills`.
- Frontend preview modal assumes `previewData.skills` is an array and calls `.map(...)`.
- If backend parser returns a non-array object for `skills`, the modal will break.

## Job Routes

### `POST /api/v1/jobs/`

- Frontend status: `USED`
- Screen: jobs page
- Backend status: `BACKEND_OK`

Frontend sends:

```json
{
  "title": "Frontend Engineer",
  "company": "Acme",
  "description": "...",
  "requirements": "...",
  "location": "Remote",
  "salary_range": "$60k-$80k",
  "employment_type": "full-time",
  "experience_level": "mid",
  "source": "manual"
}
```

Required fields from frontend/UI perspective:

- `title`
- `company`
- `description`

Backend defaults if omitted:

- `source: "manual"`
- `status: "active"`

Expected response: full `JobDescription`.

Observed backend processing flow:

1. Create job row.
2. Spawn `asyncio.create_task(process_job_background(job_id))`.
3. Background task extracts skills and fills:
   - `extracted_skills`
   - `structured_data`
   - `processed_date`

### `GET /api/v1/jobs/`

- Frontend status: `USED`
- Screens: jobs page, dashboard, matching page, analytics component
- Backend status: `BACKEND_OK`

Possible query params:

- `skip`
- `limit`
- `company`
- `location`
- `employment_type`
- `experience_level`
- `status`

Expected response:

```json
{
  "items": [/* JobDescription[] */],
  "total": 100,
  "page": 1,
  "size": 100,
  "pages": 1
}
```

Backend matches this shape.

### `GET /api/v1/jobs/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response: full `JobDescription`.

### `PUT /api/v1/jobs/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected request body: partial `JobDescription`.

### `DELETE /api/v1/jobs/{id}`

- Frontend status: `USED`
- Screen: jobs page
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "message": "Job description deleted successfully"
}
```

Backend also deletes associated matches before deleting the job.

### `POST /api/v1/jobs/scrape`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISMATCH`

Frontend sends:

```json
{
  "urls": [
    "https://example.com/job/1",
    "https://example.com/job/2"
  ]
}
```

Backend signature expects the request body itself to be a raw JSON array:

```json
[
  "https://example.com/job/1",
  "https://example.com/job/2"
]
```

This means:

- current frontend client shape and current backend shape do not match
- if this client method is called as written, FastAPI will reject it with a validation error unless the backend is changed

Backend response shape if called correctly:

```json
{
  "successful": [/* JobDescription[] */],
  "failed": [
    { "url": "...", "error": "..." }
  ],
  "total_scraped": 1,
  "total_failed": 1
}
```

### `GET /api/v1/jobs/search/skills`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_RISKY_MATCH`

Frontend query params:

- `skills`: comma-separated string
- `min_matches`: number

Frontend expects response:

```json
{
  "jobs": [
    {
      "id": 1,
      "title": "...",
      "company": "...",
      "skill_matches": 3,
      "matched_skills": ["react", "typescript", "css"]
    }
  ],
  "total_matches": 1,
  "searched_skills": ["react", "typescript", "css"]
}
```

Backend does implement this route, but there is a routing risk:

- `@router.get("/{job_id}/skills")` is registered before `@router.get("/search/skills")`
- depending on FastAPI route resolution, `/search/skills` can be shadowed by `/{job_id}/skills` with `job_id="search"` and then fail integer validation

So for a rebuild, treat this endpoint as intended, but currently fragile.

### `GET /api/v1/jobs/{id}/skills`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "job_id": 1,
  "title": "Frontend Engineer",
  "company": "Acme",
  "extracted_skills": {
    "skills": ["react", "typescript"],
    "extraction_date": "...",
    "source_text_length": 1234
  },
  "processed_date": "..."
}
```

### Job routes implemented by backend but not used by frontend

These exist in backend but are not represented in the current mounted UI:

- `POST /api/v1/jobs/bulk`
- `POST /api/v1/jobs/{id}/reprocess`

## Candidate Routes

The mounted UI does not currently call any candidate route, but `frontend/src/services/api.ts` defines them.

### `GET /api/v1/candidates/`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISMATCH`

Frontend expects a paginated wrapper:

```json
{
  "items": [/* Candidate[] */],
  "total": 10,
  "page": 1,
  "size": 10,
  "pages": 1
}
```

Backend actually returns a bare array:

```json
[
  { "id": 1, "resume_id": 12, "full_name": "..." }
]
```

So the frontend client typing for `getCandidates()` is wrong for the current backend.

### `GET /api/v1/candidates/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response: full `Candidate`.

### `GET /api/v1/candidates/{id}/resume`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISMATCH`

Backend returns:

```json
{
  "candidate_id": 1,
  "candidate_name": "???",
  "resume_id": 12,
  "resume_filename": "resume.pdf",
  "resume_status": "completed",
  "processed_date": "...",
  "structured_data": {}
}
```

Important bug:

- backend uses `candidate.name`
- candidate model field is `full_name`
- unless SQLAlchemy model has some other property not shown, this will likely error at runtime

### `PUT /api/v1/candidates/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected request body: partial `Candidate`.

### `DELETE /api/v1/candidates/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "message": "Candidate deleted successfully"
}
```

### `GET /api/v1/candidates/search/by-skills`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_RISKY_MATCH`

Frontend query params:

- `skills`: comma-separated string
- `min_matches`: number

Expected response:

```json
{
  "candidates": [
    {
      "id": 1,
      "resume_id": 12,
      "full_name": "Jane Doe",
      "skill_matches": 3,
      "matched_skills": ["react", "typescript", "css"]
    }
  ],
  "total_matches": 1,
  "searched_skills": ["react", "typescript", "css"]
}
```

Backend does implement this shape, but there is route ordering risk:

- `@router.get("/{candidate_id}")` is registered before `@router.get("/search/by-skills")`
- `/search/by-skills` may be shadowed by the dynamic ID route and fail validation

## Matching Routes

### `POST /api/v1/matching/match`

- Frontend status: `USED`
- Screen: matching page single-match mode
- Backend status: `BACKEND_OK`

Frontend sends:

```json
{
  "resume_id": 1,
  "job_id": 2
}
```

Frontend only relies on success; it does not use the returned body directly.

Backend returns a computation-focused object, not a persisted `Match` row:

```json
{
  "match_id": 99,
  "overall_score": 0.78,
  "scores": {
    "semantic_similarity": 0.8,
    "skills_match": 0.75,
    "experience_match": 0.7,
    "education_match": 0.6
  },
  "matched_skills": ["react", "typescript"],
  "missing_skills": ["graphql"],
  "skills_analysis": {},
  "confidence": 0.82,
  "explanation": "...",
  "recommendation": "Good match - consider for interview"
}
```

Backend creation/update behavior:

- if a match for `(resume_id, job_id)` already exists, it updates it
- otherwise it inserts a new match row

Preconditions enforced by backend:

- resume must exist
- job must exist
- resume status must be `completed`
- resume must have `extracted_text`

### `POST /api/v1/matching/bulk-match`

- Frontend status: `USED`
- Screen: matching page bulk-match mode
- Backend status: `BACKEND_OK`

Frontend sends:

```json
{
  "resume_ids": [1, 2, 3],
  "job_ids": [10, 11],
  "min_score_threshold": 0.5,
  "include_explanations": true
}
```

Backend returns:

```json
{
  "total_matches": 4,
  "matches": [
    {
      "resume_id": 1,
      "job_id": 10,
      "overall_score": 0.81,
      "matched_skills": ["react", "typescript"]
    }
  ],
  "processing_time_seconds": 0.42
}
```

Frontend again only relies on success, then refreshes match list.

### `GET /api/v1/matching/`

- Frontend status: `USED`
- Screens: dashboard, matching page, analytics component
- Backend status: `BACKEND_PARTIAL_MATCH`

Frontend may send:

- `skip`
- `limit`
- `resume_id`
- `job_id`
- `min_score`
- `max_score`

Expected response:

```json
{
  "items": [/* Match[] */],
  "total": 20,
  "page": 1,
  "size": 100,
  "pages": 1
}
```

Backend reality:

- supports `skip`
- supports `limit`
- supports `resume_id`
- supports `job_id`
- supports `min_score`
- does not support `max_score`

So the path is correct, but the frontend client advertises one filter the backend does not implement.

Important score semantics:

- frontend treats scores as `0..1` and multiplies by `100` in UI
- backend schema also declares `0..1`
- that is internally consistent for list/display

### `GET /api/v1/matching/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_OK`

Expected response: full persisted `Match`.

### `PUT /api/v1/matching/{id}`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISSING`

Frontend defines `updateMatch(id, data)` but backend has no `PUT /{match_id}` route.

### `DELETE /api/v1/matching/{id}`

- Frontend status: `USED`
- Screen: matching page
- Backend status: `BACKEND_OK`

Expected response:

```json
{
  "status": "deleted",
  "id": 99
}
```

Backend returns exactly this shape.

### `GET /api/v1/matching/{id}/explanation`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISSING`

Frontend defines the method, backend does not implement it.

### `GET /api/v1/matching/stats`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISSING_AS_PATH`

Frontend expects:

- `GET /api/v1/matching/stats`

Backend actually implements:

- `GET /api/v1/matching/statistics/overview`

So this is a path mismatch.

There is also a deeper semantic mismatch in current backend statistics code:

- match scores are stored as `0..1`
- backend statistics thresholds compare against `80`, `50`, etc
- ranked-candidate helper divides stored scores by `100`

That suggests some of the backend statistics code still assumes an older `0..100` score model.

### `GET /api/v1/matching/top-matches`

- Frontend status: `DEFINED_ONLY`
- Mounted UI usage: not used
- Backend status: `BACKEND_MISSING`

Frontend defines it. Backend does not implement it.

### Backend matching route not represented in frontend API service

This exists in backend but not in `frontend/src/services/api.ts`:

- `GET /api/v1/matching/job/{job_id}/candidates`

Its current response is intended to be ranked candidates for a job.

Important bug in current backend implementation:

- it divides `overall_score`, `skills_score`, and `experience_score` by `100`
- current storage appears to already be `0..1`
- returned values would therefore be too small by 100x

## Auth Routes

The backend exposes a full auth area under `/api/v1/auth`, but the current frontend does not call it at all.

Implemented backend auth routes:

- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `PUT /api/v1/auth/me`
- `POST /api/v1/auth/change-password`
- `POST /api/v1/auth/forgot-password`
- `POST /api/v1/auth/reset-password`
- `POST /api/v1/auth/logout`
- `DELETE /api/v1/auth/delete-account`
- `GET /api/v1/auth/verify-email/{token}`

Current frontend implications:

- no login screen
- no token storage
- no auth header injection
- backend rebuild can ignore auth initially if the goal is only to satisfy current UI behavior

## Screen-to-Endpoint Map

### Dashboard (`/`)

Requests on mount:

- `GET /api/v1/resumes/?limit=1000`
- `GET /api/v1/jobs/?limit=1000`
- `GET /api/v1/matching/?limit=1000`

The dashboard computes locally:

- total resumes from `resumeResponse.total`
- total jobs from `jobResponse.total`
- average match score from `matchResponse.items[*].overall_score`
- time-series charts from `created_at` values

Backend requirement for a rewrite:

- these three list endpoints must return paginated wrappers with `total` and `items`

### Resumes (`/resumes`)

Requests on mount:

- `GET /api/v1/resumes/?limit=50`

Requests on user action:

- upload one file: `POST /api/v1/resumes/upload`
- delete: `DELETE /api/v1/resumes/{id}`
- reprocess: `POST /api/v1/resumes/{id}/reprocess`
- preview: `GET /api/v1/resumes/{id}/preview`
- refresh: `GET /api/v1/resumes/?limit=50`

Behavioral expectations:

- uploaded files show up in the list after refresh
- preview route should return structured JSON safe for direct rendering
- `processing_errors` should be displayable as JSON

### Jobs (`/jobs`)

Requests on mount:

- `GET /api/v1/jobs/?limit=50`

Requests on user action:

- create manual job: `POST /api/v1/jobs/`
- delete job: `DELETE /api/v1/jobs/{id}`
- refresh: `GET /api/v1/jobs/?limit=50`

Behavioral expectations:

- newly created jobs must appear in list
- list items should include enough data for title/company/description snippet/location/salary/experience/status metadata

### Matching (`/matching`)

Requests on mount:

- `GET /api/v1/resumes/?limit=100`
- `GET /api/v1/jobs/?limit=100`
- `GET /api/v1/matching/?limit=100`

Requests on user action:

- single match: `POST /api/v1/matching/match`
- bulk match: `POST /api/v1/matching/bulk-match`
- delete match: `DELETE /api/v1/matching/{id}`
- refresh after each action: same three list calls again

Behavioral expectations:

- only completed resumes are matchable in the UI
- job list is not filtered by status in UI
- match scores are decimal fractions, later multiplied by `100` for display
- match rows should include:
  - `overall_score`
  - optional `skills_score`
  - optional `experience_score`
  - optional `education_score`
  - optional `confidence_level`
  - optional `recommendation`
  - optional `skill_overlap_count`
  - optional `total_required_skills`

### Analytics component (present but not routed)

Requests on mount:

- `GET /api/v1/resumes/?limit=1000`
- `GET /api/v1/jobs/?limit=1000`
- `GET /api/v1/matching/?limit=1000`

Behavioral expectations:

- `job.extracted_skills` should usually be an array-like skill list or include a `.skills` array that can be transformed consistently
- resume `status` values are used to build counts
- jobs are grouped by `company`

Current issue in analytics logic:

- it only counts top skills if `job.extracted_skills` is directly an array
- backend stores `extracted_skills` as an object with a nested `skills` array
- this means analytics top-skill computation likely undercounts or returns empty data unless adapted

## Structured Data Shapes Implied by Backend Processing

For a backend rewrite, these shapes are worth preserving because the current frontend renders against them.

### Resume `structured_data`

Backend currently populates:

```json
{
  "contact_info": {
    "full_name": "...",
    "email": "...",
    "phone": "...",
    "location": "..."
  },
  "work_experience": [
    {
      "job_title": "...",
      "company": "...",
      "start_date": "...",
      "end_date": "...",
      "description": "..."
    }
  ],
  "education": [
    {
      "degree": "...",
      "field_of_study": "...",
      "institution": "...",
      "graduation_year": 2024
    }
  ],
  "skills": [],
  "certifications": [],
  "summary": "...",
  "processing_metadata": {}
}
```

### Job `extracted_skills`

Backend currently populates:

```json
{
  "skills": ["react", "typescript", "css"],
  "extraction_date": "2026-04-05T12:34:56.000000",
  "source_text_length": 1234
}
```

### Job `structured_data`

Backend currently populates:

```json
{
  "title": "...",
  "company": "...",
  "location": "...",
  "employment_type": "...",
  "experience_level": "...",
  "salary_range": "...",
  "skills": ["react", "typescript"],
  "processed_date": "..."
}
```

## Contract Problems and Drift Found

This section is the most important one if the backend is going to be rebuilt from scratch.

### Frontend expects these routes and shapes correctly enough to support the active UI

These should be treated as priority routes for a rebuild:

- `GET /health`
- `POST /api/v1/resumes/upload`
- `GET /api/v1/resumes/`
- `DELETE /api/v1/resumes/{id}`
- `POST /api/v1/resumes/{id}/reprocess`
- `GET /api/v1/resumes/{id}/preview`
- `POST /api/v1/jobs/`
- `GET /api/v1/jobs/`
- `DELETE /api/v1/jobs/{id}`
- `POST /api/v1/matching/match`
- `POST /api/v1/matching/bulk-match`
- `GET /api/v1/matching/`
- `DELETE /api/v1/matching/{id}`

### Frontend defines these routes, but the current UI does not use them

These are secondary for a rebuild:

- `POST /api/v1/resumes/bulk-upload`
- `GET /api/v1/resumes/{id}`
- `GET /api/v1/resumes/{id}/status`
- `PUT /api/v1/resumes/{id}`
- `GET /api/v1/jobs/{id}`
- `PUT /api/v1/jobs/{id}`
- `POST /api/v1/jobs/scrape`
- `GET /api/v1/jobs/search/skills`
- `GET /api/v1/jobs/{id}/skills`
- all candidate routes in `api.ts`
- `GET /api/v1/matching/{id}`
- `PUT /api/v1/matching/{id}`
- `GET /api/v1/matching/{id}/explanation`
- `GET /api/v1/matching/stats`
- `GET /api/v1/matching/top-matches`

### Hard mismatches already present today

1. `POST /api/v1/jobs/scrape`
   - frontend sends `{ urls: string[] }`
   - backend expects raw `string[]`

2. `GET /api/v1/candidates/`
   - frontend expects paginated wrapper
   - backend returns bare array

3. `PUT /api/v1/matching/{id}`
   - frontend defines it
   - backend does not implement it

4. `GET /api/v1/matching/{id}/explanation`
   - frontend defines it
   - backend does not implement it

5. `GET /api/v1/matching/stats`
   - frontend defines it
   - backend implements `/statistics/overview` instead

6. `GET /api/v1/matching/top-matches`
   - frontend defines it
   - backend does not implement it

7. `GET /api/v1/matching/`
   - frontend advertises `max_score`
   - backend ignores it

### Backend logic bugs or likely bugs

1. Score scale drift
   - much of matching storage and UI assume `0..1`
   - some backend statistics/ranking code still compares against `50`, `80` or divides by `100`

2. Candidate resume endpoint references `candidate.name`
   - model field is `full_name`

3. Route ordering risk for static search routes
   - `/api/v1/jobs/search/skills`
   - `/api/v1/candidates/search/by-skills`

4. Analytics top-skills drift
   - frontend analytics expects `job.extracted_skills` array
   - backend stores object containing nested `.skills`

5. README drift
   - references `project.md`, which is not present
   - mentions some route names that no longer match backend code exactly

## Unused Endpoint Audit

This section separates endpoints into three buckets:

1. used by mounted UI routes today
2. defined in frontend client but unused by mounted UI
3. backend routes with no frontend client usage at all

### Used by mounted UI today

These are the endpoints the current routed frontend actually calls:

- `POST /api/v1/resumes/upload`
- `GET /api/v1/resumes/`
- `DELETE /api/v1/resumes/{id}`
- `POST /api/v1/resumes/{id}/reprocess`
- `GET /api/v1/resumes/{id}/preview`
- `POST /api/v1/jobs/`
- `GET /api/v1/jobs/`
- `DELETE /api/v1/jobs/{id}`
- `POST /api/v1/matching/match`
- `POST /api/v1/matching/bulk-match`
- `GET /api/v1/matching/`
- `DELETE /api/v1/matching/{id}`

Supporting note:

- `GET /health` is defined in frontend client but not called by a mounted page.
- `Analytics.tsx` is not routed, so its calls do not count as active UI traffic.

### Defined in frontend client but unused by mounted UI

These exist in `frontend/src/services/api.ts` but are not called by the mounted route tree in `frontend/src/App.tsx`:

- `GET /health`
- `POST /api/v1/resumes/bulk-upload`
- `GET /api/v1/resumes/{id}`
- `GET /api/v1/resumes/{id}/status`
- `PUT /api/v1/resumes/{id}`
- `GET /api/v1/jobs/{id}`
- `PUT /api/v1/jobs/{id}`
- `POST /api/v1/jobs/scrape`
- `GET /api/v1/jobs/search/skills`
- `GET /api/v1/jobs/{id}/skills`
- `GET /api/v1/candidates/`
- `GET /api/v1/candidates/{id}`
- `GET /api/v1/candidates/{id}/resume`
- `PUT /api/v1/candidates/{id}`
- `DELETE /api/v1/candidates/{id}`
- `GET /api/v1/candidates/search/by-skills`
- `GET /api/v1/matching/{id}`
- `PUT /api/v1/matching/{id}`
- `GET /api/v1/matching/{id}/explanation`
- `GET /api/v1/matching/stats`
- `GET /api/v1/matching/top-matches`

If the goal is to shrink the frontend API layer to only what the current routed UI uses, these are removable from `frontend/src/services/api.ts`.

### Referenced only by unrouted frontend code

These endpoints are only used by `frontend/src/components/Analytics.tsx`, which currently is not mounted in `frontend/src/App.tsx`:

- `GET /api/v1/resumes/`
- `GET /api/v1/jobs/`
- `GET /api/v1/matching/`

That means they are still important because the live dashboard and matching page use them too, but Analytics itself does not create any additional unique endpoint requirements.

### Backend routes with no frontend client usage at all

These backend routes are implemented but not referenced anywhere in `frontend/src/services/api.ts` or any mounted frontend component:

- `POST /api/v1/jobs/bulk`
- `POST /api/v1/jobs/{job_id}/reprocess`
- `GET /api/v1/matching/job/{job_id}/candidates`
- all auth routes under `/api/v1/auth/*`

If the immediate goal is a backend rebuilt only for the current UI, these are optional and can be dropped in phase one.

## Recommended Backend Skeleton for a Rewrite

If the next step is rebuilding the backend from scratch to satisfy the current frontend first, the minimum stable contract should be:

### Core routes needed by mounted UI

```http
GET    /health

POST   /api/v1/resumes/upload
GET    /api/v1/resumes/
DELETE /api/v1/resumes/{id}
POST   /api/v1/resumes/{id}/reprocess
GET    /api/v1/resumes/{id}/preview

POST   /api/v1/jobs/
GET    /api/v1/jobs/
DELETE /api/v1/jobs/{id}

POST   /api/v1/matching/match
POST   /api/v1/matching/bulk-match
GET    /api/v1/matching/
DELETE /api/v1/matching/{id}
```

### Strongly recommended response conventions

Use paginated wrappers consistently for list endpoints:

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "size": 50,
  "pages": 0
}
```

Use `0..1` score storage and `0..1` API output consistently for all match scores.

Keep preview output compatible with the resumes modal:

- `contact_info`
- `summary`
- `work_experience[]`
- `education[]`
- `skills[]`
- `certifications[]`

Keep job records compatible with the jobs page and analytics:

- `title`
- `company`
- `description`
- `requirements`
- `location`
- `salary_range`
- `employment_type`
- `experience_level`
- `source`
- `status`
- `created_at`
- `updated_at`
- optional `extracted_skills`

## Short Rebuild Priority Order

If we rebuild backend in phases, the safest order is:

1. health
2. resume upload/list/delete/reprocess/preview
3. jobs create/list/delete
4. matching create/bulk/list/delete
5. optional consistency routes from `api.ts`
6. auth only if/when the frontend starts using it

## Final Summary

The mounted frontend currently depends on a relatively small set of backend behaviors, even though the backend codebase contains much more.

For the current UI to work, the true contract is mostly:

- paginated resume list
- paginated job list
- paginated match list
- resume upload + preview + reprocess + delete
- job create + delete
- match create + bulk create + delete

The biggest documented drift points today are:

- candidate list pagination mismatch
- matching stats path mismatch
- missing `updateMatch`, `getMatchExplanation`, and `top-matches`
- job scrape request body mismatch
- score-scale inconsistency in some backend matching utilities

This file should be treated as the starting backend spec for the rewrite, because it is grounded in what the frontend actually calls and renders today.
