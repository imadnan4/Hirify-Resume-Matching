# ADR-0007: Held-out eval harness + CI smoke on fixtures

Date: 2026-09-05 · Status: accepted

## Context

Brief grades screening quality on a held-out set plus prompt/tool validation rigor.

## Decision

`evals/run.py` reads `data/eval/heldout/` (1 JD + 8–10 CVs + `labels.json` hand-ranks), writes `results.json` + `results.md`: P@3, NDCG@5, Spearman rho, citation faithfulness (% claims with quote, quote-exists check). Bar: NDCG@5 ≥ 0.75, zero uncited claims. Full eval runs locally with key; CI runs eval-smoke on 2–3 CVs with recorded Qwen transcripts (no secrets). Tests: `pytest` backend + minimal frontend smoke; CI: Ruff → pytest → `tsc --noEmit` → eval-smoke → docker build.

## Consequences

Comparable runs after rubric freeze; forks pass CI without keys.
