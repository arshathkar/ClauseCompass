# ADR-001: LLM Provider Adapter

## Status
Accepted

## Context
ClauseCompass needs to call LLM providers for analysis, Q&A, and comparison tasks. Free-tier quotas are limited, model IDs get retired frequently (gemini-2.0-flash shut down June 2026), and we need to support multiple providers (Gemini, Groq, Ollama) plus a zero-key demo mode.

## Decision
Use a single OpenAI-compatible HTTP client behind a `LLMClient` protocol. All providers are configured via environment variables (base URL + API key + model ID). The `ResilientClient` decorator adds rate limiting, retries, circuit breaker, fallback chain, and caching.

Four client modes:
- **OpenAICompatClient**: Live calls to any OpenAI-compatible endpoint
- **FakeClient**: Deterministic canned responses for unit tests
- **ReplayClient**: Serves recorded fixtures for zero-key demos
- **RecordingClient**: Captures live responses to create fixtures

## Consequences
- Swapping providers requires only env changes, no code changes
- Model IDs live in env, not in code — `make doctor` catches retired IDs
- Testing is deterministic (fake/replay modes)
- Trade-off: limited to providers with OpenAI-compatible endpoints (covers all our targets)
