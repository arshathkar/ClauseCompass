# ADR-004: Ephemeral Storage

## Status
Accepted

## Context
ClauseCompass processes sensitive legal documents. Users need assurance that their data is not retained. We also want to avoid the complexity and cost of persistent storage.

## Decision
All document data is stored in-memory only, with a 60-minute TTL per session. No database, no filesystem writes, no cache persistence.

- Sessions use random 128-bit+ IDs (not sequential)
- Documents, clause trees, redaction maps, and analysis results live in session memory
- "Delete everything now" button immediately wipes the session
- TTL expiry deletes all session data
- The placeholder-to-original PII map never leaves server memory
- No content is ever written to logs, analytics, or error reports

## Consequences
- Privacy: strong guarantee — nothing persists beyond the session
- Simplicity: no database setup, no migration scripts, no backup concerns
- Cost: no storage infrastructure ($0)
- Trade-off: users lose their analysis on page refresh or session expiry — acceptable for the use case (short interaction, not a document vault)
- Trade-off: no cross-session analytics — acceptable (we log only metadata)
