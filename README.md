# ClauseCompass

> **Understand what you're signing** — grounded in your document, private by default, accessible to everyone.

ClauseCompass turns a dense legal document into something a non-lawyer can act on. Upload a rental agreement, offer letter, loan agreement, or NDA and get:

- 📋 **Plain-language summary** at a reading level you choose
- 🔴 **Risk Radar** — clauses that deserve attention, with severity and why it matters
- 📊 **Key Facts card** — money, dates, notice periods, obligations per party
- 💬 **Grounded Q&A** — ask questions, get answers with clickable citations to the source text
- 🔄 **Compare mode** — see what changed between two versions or offers
- ✅ **Action Pack** — "before you sign" checklist, questions to ask, lawyer-prep brief

## What Sets It Apart

| Principle | How |
|---|---|
| **Grounded or silent** | Every claim has a verified citation. Unverifiable claims are dropped. Unanswerable questions get "the document doesn't say." |
| **Hybrid detection** | Rules and AI analyse independently, then merge. Disagreements show "Needs review" — never hidden. |
| **Private by default** | Files parsed in your browser. PII masked before any AI call. Nothing persists beyond your session. |
| **Accessible** | WCAG 2.2 AA. Keyboard-first. Screen-reader tested. Plain language. English/Hindi/Tamil. |
| **\$0 infrastructure** | Free-tier AI with graceful fallback. Works with no API key (replay demo). |

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

## With a Live API Key

```bash
# Edit .env:
LLM_MODE=live
LLM_API_KEY=your-gemini-api-key-here    # Get free at https://aistudio.google.com/apikey

make dev
```

## Architecture

```
Browser (React + TypeScript)         Backend (FastAPI + Python)
┌────────────────────────┐          ┌──────────────────────────────┐
│ pdf.js / mammoth       │──text──→ │ Sanitiser → Clause Segmenter │
│ (files never leave     │          │ → PII Masker → Orchestrator  │
│  the browser)          │          │   ├── Rule Engine (det.)     │
│                        │ ←─SSE──  │   ├── LLM Gateway            │
│ React + Radix UI       │          │   │   (limiter, fallback,    │
│ (WCAG 2.2 AA)          │          │   │    cache, replay)        │
│                        │          │   └── Citation Verifier      │
└────────────────────────┘          └──────────────────────────────┘
```

See [docs/architecture.md](docs/architecture.md) for details.

## Make Targets

| Target | Purpose |
|---|---|
| `make dev` | Start backend + frontend (replay mode, no key) |
| `make demo` | Production-like local build (replay mode) |
| `make lint typecheck` | Static analysis |
| `make test` | Unit + integration tests |
| `make e2e` | Playwright end-to-end tests |
| `make a11y` | Accessibility tests (axe + contrast) |
| `make eval` | Golden-set evaluations |
| `make doctor` | Verify configured model IDs are live |
| `make audit` | Security audits (pip-audit, npm audit, bandit, gitleaks) |
| `make size` | Check repo size budget |

## Project Structure

```
clausecompass/
├── backend/           Python backend (FastAPI)
│   ├── app/
│   │   ├── api/       Route handlers (no business logic)
│   │   ├── core/      Settings, errors, logging, security
│   │   ├── ingestion/ Sanitiser, clause tree, doc-type classifier
│   │   ├── privacy/   PII masking, validators, outbound guard
│   │   ├── analysis/  Orchestrator, rules engine, merge
│   │   ├── llm/       Provider adapter (Gemini/Groq/Ollama/replay)
│   │   ├── qa/        Q&A answerer, citation verifier
│   │   ├── compare/   Document comparison engine
│   │   ├── safety/    Advice boundary, urgency, injection guard
│   │   └── export/    Brief generator, calendar export
│   └── tests/
├── frontend/          React frontend (Vite + TypeScript)
│   └── src/
│       ├── components/ Accessible UI components (Radix-based)
│       ├── features/   Screen implementations
│       ├── lib/        API client, SSE hook, document extraction
│       ├── stores/     Zustand state management
│       └── i18n/       English, Hindi, Tamil translations
├── data/              Shared data files
│   ├── risk_rules.yaml          Deterministic risk detection rules
│   ├── pii_patterns.yaml        PII detection patterns
│   ├── glossary.json            Legal jargon definitions
│   ├── resources.yaml           Legal aid resources
│   ├── checklists/              Missing-clause checklists
│   ├── jurisdictions/in/        Indian law pack
│   ├── samples/                 Synthetic sample documents
│   └── fixtures/llm/            Recorded AI responses (demo mode)
├── docs/              Architecture, threat model, accessibility, evals
├── scripts/           CI checks (size, contrast, traceability, doctor)
└── .github/           CI pipeline, PR template
```

## Key Documents

- [Architecture](docs/architecture.md) — System design and data flow
- [Threat Model](docs/threat-model.md) — STRIDE-lite security analysis
- [Accessibility](docs/accessibility.md) — WCAG 2.2 AA mapping
- [Evaluation](docs/evaluation.md) — Quality metrics and gates
- [Model Log](docs/model-log.md) — LLM provider tracking
- [ADRs](docs/adr/) — Key design decisions

## Free-Tier AI Notice

This demo uses free AI services that may use sent content to improve their products. Personal details are automatically masked, but names and addresses can slip through. Use sample documents or documents you're comfortable sharing. For confidential documents, use [Ollama](https://ollama.ai/) (local mode).

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript (strict), Vite, Tailwind CSS, Radix UI |
| Backend | Python 3.12, FastAPI, Pydantic v2, httpx |
| AI | Gemini Flash-Lite (free tier), Groq fallback, Ollama (local) |
| Retrieval | BM25 (rank-bm25) — no PyTorch, no embeddings |
| Matching | rapidfuzz for citation verification and clause alignment |
| Testing | pytest, Vitest, Playwright, axe-core |

## License

MIT — see [LICENSE](LICENSE)
