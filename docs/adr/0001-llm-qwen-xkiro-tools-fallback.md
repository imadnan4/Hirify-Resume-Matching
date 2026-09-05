# ADR-0001: Qwen3.8-Max via xkiro, tools-first with fallback

Date: 2026-09-05 · Status: accepted

## Context

No OpenAI key budget. `qwen/qwen3.8-max:free` reachable over an OpenAI-compatible gateway at `https://api.xkiro.com/v1`. Uncertain strict `tools` / `json_schema` support.

## Decision

Thin custom Python agent loop calling the OpenAI-compatible `chat.completions` endpoint with `QWEN_MODEL`. Attempt `tools` (`score_candidate`, `tag_candidate`, `schedule_interview_stub`) first; on parse failure retry once with `response_format: json_object` + schema reminder, then repair-parse. Run a <1h validation spike before the full loop and log raw transcripts for fixtures.

## Consequences

Cheap and reproducible; gateway outages fall back to recorded fixtures in CI. Prompts + tool schemas versioned under `prompts/`, never inline.
