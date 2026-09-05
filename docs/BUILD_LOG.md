# Build Log

Build order: Q9 spike → ingest/parse/chunk/store → tools/agent loop → API → UI → eval/tests/Compose/CI → docs/deploy/video. Rubric + schemas frozen after agent loop.

| Date | Step | What ran | Result |
| ---- | ---- | -------- | ------ |
| 2026-09-05 | plan | grilling rounds Q1–Q19 locked; Neon prod change; `.env` + skills installed; Neon connection failing (verify in dashboard) | — |
| | | | |

## AI Usage Report

Record per run: model (`QWEN_MODEL`), prompt version (`prompts/` hash), tool schema version, rubric weights, retrieval top-k, eval numbers (P@3 / NDCG@5 / Spearman / faithfulness), raw transcript path, cost/latency notes, what changed and why.

| Date | Task | Model | Prompts/tools tried | Eval delta | Notes |
| ---- | ---- | ----- | ------------------- | ---------- | ----- |
| | | | | | |
