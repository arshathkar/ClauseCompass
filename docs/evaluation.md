# ClauseCompass — Evaluation Results

> **Status**: Template — populate with real results after running `make eval`.

## Test Environment

| Field | Value |
|---|---|
| Date | TBD |
| Mode | replay / live |
| Primary model | gemini-3.5-flash-lite |
| Fallback model | openai/gpt-oss-120b (Groq) |
| Golden set | rental_v1, offer_letter, loan_agreement |
| Prompt versions | common@1.3, key-facts@1.0, clause-analysis@1.3, qa-answer@1.0 |

## Detection Quality

| Metric | Gate | Result | Status |
|---|---|---|---|
| Risk recall (High+Medium) | ≥ 0.85 | — | — |
| Risk precision | ≥ 0.75 | — | — |
| Severity agreement (±1 level) | ≥ 0.90 | — | — |

## Citation Quality

| Metric | Gate | Result | Status |
|---|---|---|---|
| Raw citation validity | ≥ 0.90 | — | — |
| Citation faithfulness (shown) | ≥ 0.98 | — | — |

## Q&A Quality

| Metric | Gate | Result | Status |
|---|---|---|---|
| Correct abstention | ≥ 0.90 | — | — |
| False abstention rate | ≤ 0.15 | — | — |
| Multilingual retrieval parity (HI/TA) | ≥ 0.80 | — | — |

## Readability

| Metric | Gate | Result | Status |
|---|---|---|---|
| Simple-mode FK ≤ Grade 8 | ≥ 90% of cards | — | — |

## Safety

| Metric | Gate | Result | Status |
|---|---|---|---|
| Advice-boundary pass (30 prompts) | ≥ 95% | — | — |
| Injection resistance (20 docs) | 20/20 | — | — |

## Privacy

| Metric | Gate | Result | Status |
|---|---|---|---|
| Seeded PII in provider requests | 0 | — | — |
| Canaries in logs | 0 | — | — |

## Efficiency

| Metric | Gate | Result | Status |
|---|---|---|---|
| Calls per 20-page analysis | ≤ 8 | — | — |
| p95 Key Facts latency | ≤ 12s | — | — |
| p95 full analysis | ≤ 45s | — | — |
| p95 Q&A first segment | ≤ 6s | — | — |
| p95 Q&A full answer | ≤ 10s | — | — |

## Engineering

| Metric | Gate | Result | Status |
|---|---|---|---|
| Backend coverage (overall) | ≥ 80% | — | — |
| Backend coverage (critical modules) | ≥ 90% | — | — |
| Frontend coverage | ≥ 70% | — | — |
| High/critical dep vulnerabilities | 0 | — | — |
| axe serious+critical violations | 0 | — | — |
| Lighthouse accessibility score | ≥ 95 | — | — |
| Repo size | ≤ 5 MB | — | — |

## Zero-Key Demo

| Test | Gate | Result | Status |
|---|---|---|---|
| Fresh clone → make demo → J1 complete | ≤ 5 min | — | — |

## Notes

Record observations, model quirks, and quality notes here after each eval run.
