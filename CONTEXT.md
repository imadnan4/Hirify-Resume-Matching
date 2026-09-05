# Hirify — CONTEXT.md

Canonical project name: **Hirify**. (Directory is still `Autonomous-Candidate-Screening-Agent`; the older Hirify repo gets wiped. This plan is the source of truth.)

Vision: ingest a job description + CVs, retrieve grounding context via RAG, rank candidates with evidence-backed explanations.

## Ubiquitous language

- **Job**: one hiring role. Has title, description text, requirements list. `jobs` table.
- **Requirement**: one bullet of a Job (e.g. `REQ-3: 2+ yrs FastAPI`). JDs chunk by requirement. ID stable (`REQ-<n>`).
- **Candidate**: one applicant for a Job. Has raw CV file (PDF/TXT) + parsed text. `candidates` table.
- **Chunk**: one retrievable unit. JD chunks carry `requirement_id`; CV chunks carry `section` (experience/projects/education). `chunks` table, `embedding vector(384)`.
- **Score**: overall 0–100 + 5 sub-scores. Every sub-score carries ≥1 verbatim **quote** from the CV linked to a `requirement_id`. `scores` table.
- **Tag**: structured label on a candidate (`missing_work_auth`, `below_min_years`, `missing_required_credential`, skill tags). `tags` table. KO tags cap overall at ≤40, never silent-zero.
- **InterviewStub**: `schedule_interview_stub` output. DB row only, no calendar. `interviews_stub` table.
- **Screening run**: `POST /jobs/{id}/screen` → parse → chunk → embed → retrieve (top-k=6 per candidate) → tool-called scoring → ranking.
- **Held-out eval**: 1 JD + 8–10 CVs + `labels.json` hand-ranks. Metrics: P@3, NDCG@5, Spearman rho, citation faithfulness. Bar: NDCG@5 ≥ 0.75, zero uncited claims.

## Rubric (lives in `config/rubric.yaml`, loaded at runtime)

Skills 35 / Experience 30 / Project-impact 20 / Education-certs 5 / CV-clarity 10. Weights sum to 100. Tune config, not code.

## Flows

Upload (JD text/file + CV bulk) → Screen → Ranking table (score, tags, KO badge) → Candidate detail (sub-scores + quotes → REQ ids) → Eval results.

## Scope cuts (30–40h solo)

In: Q9 spike first, ingest/parse/chunk/store, tools+agent loop, FastAPI API, Vite React+Tailwind UI (4 views), evals+tests+Compose+CI, docs+deploy+video. Freeze rubric + schemas after agent loop.
Out for now: auth (single demo workspace), multi-tenant roles, real calendar, OpenAI embeddings (swappable later via `embed()` seam).

## Runtime config (never commit `.env`)

`XKIRO_API_KEY`, `XKIRO_BASE_URL=https://api.xkiro.com/v1`, `QWEN_MODEL=qwen/qwen3.8-max:free`, `DATABASE_URL` (Neon prod; local Compose uses `pgvector/pg16`). Frontend: `VITE_API_URL`. Placeholders in `.env.example`. Prompts + tool JSON schemas live versioned under `prompts/`, loaded at runtime.
