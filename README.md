# Hirify — AI candidate screening

Upload a job description + CVs (PDF/TXT), get evidence-backed rankings with per-criterion scores.

- **Backend**: FastAPI + SQLAlchemy 2 + Postgres/pgvector (Neon in prod, `pgvector:pg16` in Compose)
- **Agent**: Qwen via xkiro OpenAI-compatible gateway, tools-first scoring with JSON fallback
- **RAG**: JD-by-requirement + CV-by-section chunks, 384-dim embeddings (local MiniLM, hash fallback in CI)
- **Eval**: `evals/run.py` → P@3 / NDCG@5 / Spearman / citation faithfulness

## Backend quickstart

```bash
cp .env.example .env   # fill XKIRO_API_KEY + DATABASE_URL
docker compose up --build        # api :8000, db :5432
# or local: pip install -r backend/requirements.txt && uvicorn app.main:app --app-dir backend
pytest backend/tests/            # EMBEDDING_BACKEND=hash DATABASE_URL="sqlite://"
python evals/run.py              # held-out eval (fixture mode without key)
```

API: `POST /jobs`, `POST /jobs/{id}/candidates:upload`, `POST /jobs/{id}/screen`,
`GET /jobs/{id}/ranking`, `GET /candidates/{id}`, `POST /candidates/{id}/schedule?slot=...`, `GET /eval`.

## Layout

`backend/` API + agent · `frontend/` web UI (owned by frontend agent) ·
`config/rubric.yaml` scoring weights · `prompts/` versioned agent prompt ·
`data/seed` sample JDs/CVs · `data/eval/heldout` labels + harness output in `evals/`.
