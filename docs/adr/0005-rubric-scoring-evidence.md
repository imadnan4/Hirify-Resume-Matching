# ADR-0005: Weighted rubric with KO tags (cap, never silent-zero)

Date: 2026-09-05 · Status: accepted

## Context

Rankings must be explainable and auditable; knock-outs must stay visible.

## Decision

Overall 0–100 + 5 sub-scores, weights in `config/rubric.yaml`: Skills 35, Experience 30, Project-impact 20, Education-certs 5, CV-clarity 10. Each sub-score needs ≥1 verbatim CV quote → `requirement_id`. KO tags (`missing_work_auth`, `below_min_years`, `missing_required_credential`) cap overall at ≤40, preserve sub-scores + quotes.

## Consequences

Tunable without code change. Rubric + schemas frozen after agent-loop step so evals stay comparable.
