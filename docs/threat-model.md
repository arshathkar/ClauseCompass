# ClauseCompass — Threat Model (STRIDE-lite)

## Scope

This threat model covers the ClauseCompass web application: a React frontend communicating with a FastAPI backend that processes legal document text and calls free-tier LLM providers.

## Trust Boundaries

1. **Browser ↔ Backend**: HTTPS, CORS-restricted, session-authenticated
2. **Backend ↔ LLM Provider**: HTTPS, API-key-authenticated, PII-masked payloads
3. **User-supplied content ↔ System prompts**: Delimiter-based separation in LLM calls

## Threats and Mitigations

| # | Threat | Category | Vector | Likelihood | Impact | Mitigation | Verification |
|---|---|---|---|---|---|---|---|
| T1 | Hostile file crashes/exploits parser | Tampering | Upload | Medium | High | Parsed only in browser worker; pinned pdf.js with `isEvalSupported: false`; timeouts; server never sees binaries | Malformed fixtures in Vitest; e2e cancel path |
| T2 | Prompt injection in document | Tampering | Document text | High | High | Sanitiser strips hidden chars; untrusted-data delimiters; no tools/network in LLM calls; heuristic notice; schema validation; verified citations | 20-doc injection red-team set |
| T3 | PII leakage to provider/logs | Info Disclosure | Document text, logs | Medium | Critical | Server-side masking; outbound guard (fail closed); content-free logs; provider stance documented | Property tests; log canary scan; captured-request assertions |
| T4 | Free-tier provider trains on data | Info Disclosure | Provider terms | High | High | Consent notice; synthetic-only demos; PII masking; replay mode; Ollama option | e2e consent check; docs |
| T5 | Cross-session access (IDOR) | Elevation | Guessing doc IDs | Low | High | Random 128-bit+ IDs bound to session; authz on every route | Integration tests |
| T6 | XSS via LLM/document output | Tampering | Rendered content | Medium | High | Raw-text extraction; no raw HTML; sanitiser; strict CSP | E2E XSS payload test |
| T7 | API key exposure | Info Disclosure | Repo, frontend, logs | Low | Critical | Server-side keys only; git-ignored .env; gitleaks pre-commit + CI; bundle grep test | CI secret scan; bundle test |
| T8 | Quota exhaustion / DoS | Denial of Service | Rapid requests | Medium | Medium | Rate limits; budgets; size caps; fallback chain; replay state | Load smoke; resilience tests |
| T9 | Misleading output (hallucination) | Tampering | Model error | Medium | High | Grounded-only; citation verifier; Law Pack citations; confidence thresholds; abstention; disclaimers | Golden-set evals |
| T10 | Replay fixtures leak real data | Info Disclosure | Recorder | Low | Medium | Recorder refuses non-synthetic docs; fixtures reviewed in PR | Unit test; repo PII scan |
| T11 | SSRF via URL fetch | Tampering | URL input | N/A (P2) | High | Feature deferred; if built: scheme allow-list + private-IP block | N/A in MVP |
| T12 | Supply-chain compromise | Tampering | Dependencies | Low | High | Lockfiles; Dependabot; audits in CI; minimal deps; licence check | CI |
| T13 | Clickjacking / cross-origin | Tampering | Framing, CORS | Low | Medium | `frame-ancestors 'none'`; strict CORS allow-list | Header tests |
| T14 | Retired model breaks demo | Availability | Provider lifecycle | High | Medium | `make doctor`; env-only model IDs; replay fallback | CI doctor step |

## Security Headers

```
Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; 
  worker-src 'self' blob:; connect-src 'self' https://generativelanguage.googleapis.com 
  https://api.groq.com; frame-ancestors 'none'
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Cache-Control: no-store (on API responses)
```

## Data Classification

| Data Type | Storage | Sent to Provider? | In Logs? |
|---|---|---|---|
| Document text (original) | Session memory, TTL 60 min | Never (masked version only) | Never |
| Masked text | Session memory | Yes, with consent | Never |
| PII placeholder map | Session memory only | Never | Never |
| LLM responses | Session memory | N/A | Never (only metadata) |
| User settings | Browser localStorage | Never | Never |
| Session IDs | Memory + HttpOnly cookie | Never | Yes (IDs only) |
