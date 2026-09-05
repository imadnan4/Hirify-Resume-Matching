# ADR-0004: FastAPI + Vite React + Tailwind, 4 views, no auth

Date: 2026-09-05 · Status: accepted

## Context

Biggest time sink; need demo speed without cutting the evidence views that carry the brief.

## Decision

Backend `backend/` (FastAPI): `POST /jobs`, `POST /jobs/{id}/candidates:upload`, `POST /jobs/{id}/screen`, `GET /jobs/{id}/ranking`, `GET /candidates/{id}`, `GET /eval`. Frontend `frontend/` (Vite React + Tailwind, `VITE_API_URL`): Upload → Ranking → Candidate detail/evidence → Eval. Single demo workspace, no auth. Polish Ranking + Evidence; keep Upload/Eval functional-minimal. Tools: `score_candidate`, `tag_candidate`, `schedule_interview_stub` (DB-only).

## Consequences

Clear API/UI contract for tests and deploy (API → Heroku, web → Netlify, DB → Neon; Compose for local).
