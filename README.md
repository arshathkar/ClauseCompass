# ClauseCompass — GenAI-Powered Legal Document Analyzer

> **Understand what you're signing** — grounded in your document, private by default, accessible to everyone.

## Problem Statement

**Millions of people sign legal documents they don't fully understand.** Rental agreements, employment offers, loan contracts, and NDAs are written in dense legal language that creates information asymmetry between parties. People unknowingly agree to unfavorable terms — losing deposits, waiving rights, or accepting penalties they never intended to.

**ClauseCompass solves this** by using Generative AI (Google Gemini) to analyze legal documents in real-time, extract key facts, identify risky clauses, and explain everything in plain language that anyone can understand — in English, Hindi, or Tamil.

## What It Does

Upload a rental agreement, offer letter, loan agreement, or NDA and get:

- 📋 **AI-Powered Plain-Language Summary** — Gemini Flash-Lite generates summaries at a reading level you choose
- 🔴 **Risk Radar** — AI + deterministic rules independently analyze clauses, flagging severity with plain-language explanations of *what it says*, *what it means*, and *why it matters*
- 📊 **Key Facts Extraction** — AI extracts money amounts, dates, notice periods, and obligations per party with verified citations
- 💬 **Grounded Q&A Chat** — Ask questions in English/Hindi/Tamil, get AI-generated answers with clickable citations to exact source text. Uses BM25 retrieval + LLM query rewriting for multilingual support
- 🔄 **Document Comparison** — AI-powered clause alignment and impact analysis between two document versions
- ✅ **Action Pack** — AI-generated "before you sign" checklist, questions to ask a lawyer, exportable prep brief
- 🛡️ **Privacy-First PII Masking** — Aadhaar, PAN, phone numbers, and emails are auto-detected and masked before any AI call

## How GenAI Powers the Solution

| Feature | GenAI Integration |
|---|---|
| **Document Type Classification** | Gemini classifies the document type (rental, employment, loan, NDA, etc.) to apply type-specific analysis rules |
| **Key Facts Extraction** | Gemini extracts structured key facts (amounts, dates, parties) from unstructured legal text |
| **Clause Risk Analysis** | Gemini analyzes each clause batch for risks, generating plain-language explanations with severity ratings |
| **Citation Verification** | Every AI-generated claim is verified against source text using fuzzy matching (rapidfuzz). Unverifiable claims are dropped |
| **Q&A Answering** | Gemini answers user questions grounded strictly in the document, with verified citations. Out-of-scope questions get honest "I don't know" responses |
| **Query Rewriting** | For Hindi/Tamil questions, Gemini rewrites the query to English for BM25 retrieval, then answers in the user's language |
| **Document Comparison** | Gemini adjudicates changes between document versions, identifying risk-increasing modifications |
| **Hybrid Detection** | AI findings are merged with deterministic rule-engine results. Disagreements show "Needs review" — never hidden |

## Architecture: How Data Flows Through AI

```
User uploads document (browser-side parsing, file never leaves browser)
    │
    ▼
Browser extracts text (pdf.js / mammoth.js)
    │
    ▼
Text sent to Backend API ──→ Sanitizer ──→ PII Masker (Aadhaar, PAN, phone, email)
    │                                           │
    │                          Masked text (no PII reaches AI)
    │                                           │
    ▼                                           ▼
Outbound Guard validates ──→ Clause Segmenter ──→ Analysis Orchestrator
                                                       │
                              ┌─────────────────────────┼──────────────────────┐
                              │                         │                      │
                     Rule Engine (det.)      LLM Gateway (Gemini)    Citation Verifier
                     risk_rules.yaml         ├─ Key Facts prompt     fuzzy match ≥90%
                     pattern matching        ├─ Clause Analysis prompt
                                             ├─ Rate limiter (token bucket)
                              │              ├─ Circuit breaker
                              │              ├─ Retry with exponential backoff
                              │              ├─ Response cache (TTL)
                              │              └─ Fallback chain:
                              │                   Gemini → Groq → Replay
                              │                         │
                              └───── Merge ◄────────────┘
                                       │
                                       ▼
                              Verified Findings (SSE stream to browser)
                              ├─ Key Facts with citations
                              ├─ Risk findings with severity
                              ├─ Summary (plain language)
                              └─ Urgency alerts
```

## What Sets It Apart

| Principle | How |
|---|---|
| **Grounded or silent** | Every AI claim has a verified citation (fuzzy match ≥90%). Unverifiable claims are dropped. Unanswerable questions get "the document doesn't say." |
| **Hybrid detection** | Rules and AI analyse independently, then merge. Disagreements show "Needs review" — never hidden. |
| **Private by default** | Files parsed in your browser. PII masked before any AI call. Nothing persists beyond your session. |
| **Accessible** | WCAG 2.2 AA. Keyboard-first. Screen-reader tested. Plain language. English/Hindi/Tamil. |
| **$0 infrastructure** | Free-tier Gemini Flash-Lite with graceful fallback to Groq. Works with no API key (replay demo). |

> ⚠️ **Not legal advice.** ClauseCompass explains documents in plain language. It is not a law firm and does not give legal advice. AI can make mistakes — check anything important with a qualified lawyer.

## Quick Start (No API Key Needed)

```bash
git clone <repo-url> clausecompass
cd clausecompass
cp .env.example .env          # LLM_MODE=replay by default
# Backend
cd backend && pip install -e ".[dev]" && cd ..
# Frontend
cd frontend && npm install && cd ..
# Start both
make dev
```

Open http://localhost:5173 → Click **Try a sample** → Full demo with saved AI results.

## With a Live API Key (Real GenAI)

```bash
# Edit .env:
LLM_MODE=live
LLM_API_KEY=your-gemini-api-key-here    # Get free at https://aistudio.google.com/apikey

make dev
```

Now upload any legal document and get real AI-powered analysis with Gemini Flash-Lite.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript (strict), Vite, Tailwind CSS, Radix UI |
| Backend | Python 3.12, FastAPI, Pydantic v2, httpx |
| GenAI | Google Gemini Flash-Lite (free tier), Groq fallback, Ollama (local) |
| Retrieval | BM25 (rank-bm25) for Q&A context retrieval — no PyTorch, no embeddings |
| Citation Matching | rapidfuzz for citation verification and clause alignment |
| PII Detection | Regex patterns (Aadhaar, PAN, phone, email) with YAML-driven rules |
| Testing | pytest (54 tests), Vitest, Playwright, axe-core |

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/v1/sessions` | Create a new analysis session |
| `POST` | `/v1/documents` | Submit document text for PII detection and classification |
| `POST` | `/v1/documents/{id}/redactions` | Update PII masking preferences |
| `POST` | `/v1/documents/{id}/analyze` | Run full AI analysis (SSE stream) |
| `POST` | `/v1/documents/{id}/qa` | Ask a question about the document (SSE stream) |
| `POST` | `/v1/compare` | Compare two document versions |
| `DELETE` | `/v1/documents/{id}` | Delete document data |
| `DELETE` | `/v1/sessions/current` | Delete session and all data |

## Project Structure

```
clausecompass/
├── backend/           Python backend (FastAPI)
│   ├── app/
│   │   ├── api/       Route handlers — sessions, documents, compare, health
│   │   ├── core/      Settings, errors, logging, security headers
│   │   ├── ingestion/ Text sanitizer, clause tree segmenter, doctype classifier (AI)
│   │   ├── privacy/   PII masking (regex), outbound guard (blocks unmasked PII)
│   │   ├── analysis/  Orchestrator (AI), rule engine (deterministic), merge logic
│   │   ├── llm/       Provider adapter — Gemini/Groq/Ollama/Replay with resilience
│   │   ├── qa/        Q&A answerer (AI), citation verifier (fuzzy match)
│   │   ├── compare/   Document comparison — clause alignment, numeric diff, impact (AI)
│   │   ├── safety/    Advice boundary guard, urgency detector, prompt injection guard
│   │   └── export/    Lawyer prep brief (markdown), calendar export (ICS)
│   └── tests/         54 unit tests covering all modules
├── frontend/          React frontend (Vite + TypeScript)
│   └── src/
│       ├── components/ Accessible UI components (Radix-based, WCAG 2.2 AA)
│       ├── features/   Welcome → Upload → Redaction → Results (with AI analysis)
│       ├── lib/        API client, SSE streaming hook, browser-side document extraction
│       ├── stores/     Zustand state management (session, document, settings)
│       └── i18n/       English, Hindi, Tamil translations
├── data/              Shared data files
│   ├── risk_rules.yaml          Deterministic risk detection rules
│   ├── pii_patterns.yaml        PII detection patterns (Aadhaar, PAN, phone, email)
│   ├── glossary.json            Legal jargon → plain language definitions
│   ├── resources.yaml           Legal aid resources (India)
│   ├── checklists/              Missing-clause checklists per document type
│   ├── jurisdictions/in/        Indian law pack for rule engine
│   ├── samples/                 Synthetic sample documents for demo
│   └── fixtures/llm/            Recorded AI responses (replay/demo mode)
├── docs/              Architecture, threat model, accessibility, evaluations
└── scripts/           CI checks (size, contrast, traceability)
```

## Testing

```bash
# Backend tests (54 tests)
cd backend && python -m pytest -v

# Frontend type checking
cd frontend && npx tsc --noEmit

# Build
cd frontend && npm run build
```

## License

MIT — see [LICENSE](LICENSE)
