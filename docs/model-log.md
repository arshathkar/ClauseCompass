# ClauseCompass — Model Log

Track all model ID changes, observed limits, and quality notes here.

## Active Models

| Role | Provider | Model ID | Added | Status |
|---|---|---|---|---|
| Primary (fast + analysis) | Google AI Studio | gemini-3.5-flash-lite | 2026-09-20 | Active |
| Secondary | Google AI Studio | gemini-3.1-flash-lite | 2026-09-20 | Active |
| Fallback | Groq | openai/gpt-oss-120b | 2026-09-20 | Active |

## Observed Limits (verify on first use)

| Model | RPM | RPD | TPM | Notes |
|---|---|---|---|---|
| gemini-3.5-flash-lite | ~15 | ~500 | ~250K | Free tier; data used to improve products |
| gemini-3.1-flash-lite | ~15 | ~500 | ~250K | Same-provider fallback; separate quota |
| openai/gpt-oss-120b (Groq) | ~30 | ~1,000 | varies | Test Hindi/Tamil quality before enabling |

## Retired Models (DO NOT USE)

| Model ID | Shutdown Date | Notes |
|---|---|---|
| gemini-2.0-flash | 2026-06-01 | Retired |
| gemini-2.5-flash | 2026-10-16 (scheduled) | Do not use |
| gemini-2.5-flash-lite | 2026-10-16 (scheduled) | Do not use |

## Change Log

| Date | Change | Reason |
|---|---|---|
| 2026-09-20 | Initial setup with 3.x models | Avoid 2.x retirement risk |
