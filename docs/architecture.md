# ClauseCompass — Architecture

## Overview

ClauseCompass is a document-grounded legal information assistant. It analyses legal documents (rental agreements, offer letters, loan agreements, etc.) and provides plain-language explanations, risk flags, key facts extraction, grounded Q&A, version comparison, and actionable outputs — all with verified citations.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│  Browser (React + TypeScript)                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ │
│  │ pdf.js   │ │ mammoth  │ │ Zustand  │ │ useSSE   │ │ Radix UI │ │
│  │ (worker) │ │ (lazy)   │ │ stores   │ │ (fetch)  │ │ (a11y)   │ │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘ │
│  Files parsed here — only text sent to backend                      │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ HTTPS (text only)
┌──────────────────────────▼──────────────────────────────────────────┐
│  FastAPI Backend                                                     │
│  ┌────────┐ ┌────────────┐ ┌───────────┐ ┌──────────┐ ┌─────────┐ │
│  │ API    │→│ Sanitiser  │→│ Clause    │→│ PII      │→│ Orch-   │ │
│  │ routes │ │ (NFC, etc) │ │ Segmenter │ │ Masker   │ │ estrator│ │
│  └────────┘ └────────────┘ └───────────┘ └──────────┘ └────┬────┘ │
│                                                              │      │
│  ┌────────────────────────────────────────────────────────────┤      │
│  │                                                            │      │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────────┐   │      │
│  │  │ Rule       │  │ LLM        │  │ Citation           │   │      │
│  │  │ Engine     │  │ Gateway    │  │ Verifier           │   │      │
│  │  │(determinis-│  │(rate limit,│  │(exact + fuzzy      │   │      │
│  │  │ tic)       │  │ fallback,  │  │ match)             │   │      │
│  │  │            │  │ cache)     │  │                    │   │      │
│  │  └────────────┘  └─────┬──────┘  └────────────────────┘   │      │
│  │                        │                                   │      │
│  │              ┌─────────▼────────────┐                     │      │
│  │              │ Provider Adapter     │                     │      │
│  │              │ (OpenAI-compatible)  │                     │      │
│  │              ├──────────────────────┤                     │      │
│  │              │ Gemini │ Groq │ Ollama│ Replay │ Fake     │      │
│  │              └────────┴──────┴──────┴────────┴──────────┘│      │
│  └────────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────────┐  │
│  │ BM25       │  │ Compare    │  │ Safety     │  │ Session      │  │
│  │ Retrieval  │  │ Engine     │  │ Controls   │  │ Store (mem)  │  │
│  └────────────┘  └────────────┘  └────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

## Key Design Decisions

| Decision | Choice | Why |
|---|---|---|
| Browser-side parsing | pdf.js + mammoth in browser | Server never sees binary files (security) |
| LLM adapter | One OpenAI-compatible client | Swap providers via env, no code changes |
| Hybrid detection | Rules + LLM independently, then merge | Deterministic floor + LLM recall + visible disagreement |
| Citations | Verified before display | Grounded or silent principle |
| Retrieval | BM25 (no embeddings) | No PyTorch, low RAM, works for Hindi/Tamil with query rewrite |
| Storage | In-memory, TTL 60 min | Privacy: nothing persists |
| Streaming | Verified-segment SSE | Correctness over raw token streaming |

## Layer Rules

```
api/          → Route handlers (no business logic)
  ↓
analysis/     → Orchestration, rules, merge
qa/           → Answering, verification
compare/      → Alignment, diff, impact
  ↓
llm/          → Adapter layer (only place that talks to providers)
privacy/      → PII masking (must run before any LLM call)
retrieval/    → BM25 index
safety/       → Boundary checks, urgency, injection guard
  ↓
core/         → Settings, errors, logging, security
session/      → In-memory session store
ingestion/    → Sanitiser, clause tree, doc-type classifier
```

## Data Flow

1. **User uploads** a PDF/DOCX/text in the browser
2. **Browser extracts** text (pdf.js/mammoth) — file never leaves the browser
3. **Text sent** to backend via HTTPS
4. **Sanitiser** cleans text (NFC, hidden chars, length cap)
5. **Clause segmenter** builds a clause tree with stable IDs
6. **PII masker** replaces personal data with placeholders
7. **User confirms** redaction preview
8. **Orchestrator** runs analysis:
   - Rule engine scans clauses deterministically
   - LLM analyses clause batches (independently of rules)
   - Merger compares and labels disagreements
   - Citation verifier validates all quotes
9. **Results stream** via SSE to the UI
10. **Session expires** after 60 min; all data deleted

## Security Boundaries

- Binary files: browser sandbox only
- Document text: PII-masked before any LLM call
- Outbound guard: re-scans every payload, fails closed
- Logs: content-free (IDs, timings, token counts only)
- Sessions: random 128-bit IDs, short TTL, bound to session
- LLM output: treated as untrusted, schema-validated, citations verified
