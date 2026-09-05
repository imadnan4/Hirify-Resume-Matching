# ADR-0002: Local embeddings (MiniLM 384) behind `embed()` seam

Date: 2026-09-05 · Status: accepted

## Context

LLM lives on xkiro; `text-embedding-3-small` would need a second (paid) OpenAI key and 1536 dims.

## Decision

Default to `sentence-transformers all-MiniLM-L6-v2` (384-dim, free, offline) behind an `embed()` interface. `chunks.embedding vector(384)` fixed in schema. OpenAI embeddings remain a config swap.

## Consequences

No second key, evals run offline. Slight quality trade vs. larger models; acceptable for seed scale, measurable in eval harness.
