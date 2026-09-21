# ADR-002: Hybrid Detection (Rules + LLM)

## Status
Accepted

## Context
We need to detect risky clauses in legal documents. Pure LLM detection has high recall but can hallucinate. Pure rule-based detection is precise but limited in coverage. We need both reliability and breadth.

## Decision
Run deterministic rules and LLM analysis **independently** on the same clauses, then merge results. Rules never see LLM output and vice versa — so disagreement is informative.

Agreement matrix:
| Rule Hit | LLM Finding | Outcome |
|---|---|---|
| Yes | Yes (same category) | Agree — highest severity, max confidence |
| Yes | No | Show rule finding; badge "Needs review" |
| No | Yes | Show LLM finding; if High severity, badge "AI-only — verify" |
| Yes | Yes (different category) | Show both, linked as "related" |

## Consequences
- Deterministic floor: rules always catch known patterns regardless of model quality
- Visible disagreement: users see "Needs review" instead of hidden conflicts
- Testable: rules have unit tests with positive/negative cases; LLM is evaluated separately
- Trade-off: more complex merge logic; some findings may appear as duplicates
