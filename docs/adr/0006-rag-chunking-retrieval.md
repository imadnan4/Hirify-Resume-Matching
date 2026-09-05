# ADR-0006: RAG chunking + retrieval (top-k=6 per candidate)

Date: 2026-09-05 · Status: accepted

## Context

Ground every claim in CV/JD spans without blowing the Qwen context window.

## Decision

JD split by requirement bullets (keeps `REQ-<n>`); CV split by section, ~400–600 tokens, 10% overlap. Parser: `pdfplumber` primary, `pypdf` fallback; seed PDFs generated via `reportlab`. Retrieve top-k=6 per candidate filtered by `candidate_id`. PII (email/phone/name) redacted in explanation views only; originals retained.

Seed: 3 JDs (Backend FastAPI, Frontend React+Tailwind, Junior Data) × 5–6 CVs (level spread, 1 KO + 1 near-miss per JD), script-generated + hand-checked.

## Consequences

Small, citable context per scoring call; chunker + parser covered by unit tests.
