# ADR-005: Verified-Segment Streaming

## Status
Accepted

## Context
Q&A answers contain citations (quotes from the source document). Raw token streaming would show text before its citations are verified, potentially displaying hallucinated quotes. Screen-reader users would also receive excessive per-token announcements.

## Decision
Use **verified-segment streaming** instead of raw token streaming. The LLM returns structured JSON (QAAnswer with segments and citations). Each segment is verified against the source text before being sent to the client via SSE.

Flow:
1. LLM generates complete JSON answer
2. Citation verifier checks each quote (exact match → fuzzy match ≥ 0.90 → fail)
3. Verified segments are streamed to the client one at a time
4. Failed segments are dropped (not shown)
5. If all segments fail → abstention card

## Consequences
- Correctness: no unverified text is ever rendered
- Accessibility: screen readers announce "Answer ready" once, not per-token
- Grounding: citation faithfulness is 100% by construction (for shown claims)
- Trade-off: slightly higher perceived latency (full LLM response before first segment) — mitigated by fast model and progress indicator
- Trade-off: raw citation validity becomes a prompt-quality signal, not a user-facing issue
