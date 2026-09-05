# ADR-0003: Neon Postgres + pgvector as prod combined store

Date: 2026-09-05 · Status: accepted (connection unverified — see flag)

## Context

Need one store for app rows + vectors, with a future path to auth/workspace tables without a second DB. Heroku Postgres pgvector support is plan-dependent.

## Decision

Prod: **Neon Postgres** with `pgvector` extension, holding `jobs`, `candidates`, `chunks`, `scores`, `tags`, `interviews_stub` (+ future users/workspaces). Local: `pgvector/pgvector:pg16` in Compose. `DATABASE_URL` from `.env`. Connection currently fails from this machine (pooler + direct, server closes connection) — verify project status / password / `CREATE EXTENSION vector` in Neon dashboard before building on it.

## Consequences

Single `DATABASE_URL` in every env; Compose stays local truth, Neon is the live URL store.
