# ADR-003: Browser-Side Parsing

## Status
Accepted

## Context
Users upload legal documents (PDF, DOCX) that may contain sensitive personal information. Server-side parsing of binary files creates security risks (zip bombs, malformed PDFs, parser exploits) and privacy risks (binary files on the server).

## Decision
Parse all document files in the browser using pdf.js (in a Web Worker) and mammoth (raw text mode). The server only receives extracted plain text — never binary files.

- pdf.js: pinned to a patched version with `isEvalSupported: false` (CVE-2024-4367 mitigation)
- mammoth: `extractRawText` only — the HTML converter is never used
- Both libraries are dynamically imported (lazy-loaded) to keep the initial bundle small
- Extraction is cancellable and reports progress per page

## Consequences
- Security: zip-bomb and malformed-file risks stay in the browser sandbox
- Privacy: raw binary files never reach the server
- Performance: extraction happens on the user's device; may be slower on low-end phones (mitigated by progress UI, page/size caps, and paste alternative)
- Trade-off: scanned PDFs produce empty text — guidance message shown (OCR is P2)
