# ClauseCompass — Accessibility Statement

## Commitment

ClauseCompass targets **WCAG 2.2 Level AA** conformance. Accessibility is built in from the start — not retrofitted.

## Standards & Testing

| Method | Tool | Frequency |
|---|---|---|
| Automated scan | @axe-core/playwright | Every CI run |
| Contrast verification | scripts/check_contrast.py | Every CI run |
| Keyboard-only e2e | Playwright | Every CI run |
| Zoom/reflow tests | Playwright at 200% and 320px | Every CI run |
| Screen-reader manual | NVDA + Chrome | Per milestone |

## WCAG 2.2 AA Mapping

| Criterion | Implementation | Verified By |
|---|---|---|
| 1.1.1 Non-text content | Icons paired with text; diffs have text labels | axe, review |
| 1.3.1 Info & relationships | Landmarks, heading order, real tables/lists, labelled inputs | axe, jest-axe |
| 1.4.1 Use of colour | Icon + label + pattern + colour for severity | SeverityBadge unit test |
| 1.4.3/1.4.11 Contrast | Verified design tokens (§8.8) | check_contrast.py in CI |
| 1.4.4 Resize text | rem units, no fixed-height text boxes | e2e at 200% |
| 1.4.10 Reflow | Responsive layout, scroll containers | e2e at 320px |
| 1.4.12 Text spacing | WCAG spacing overrides don't clip | e2e injects spacing CSS |
| 2.1.1/2.1.2 Keyboard | Radix primitives, managed focus, no traps | keyboard-only e2e |
| 2.1.4 Character-key shortcuts | None implemented | lint rule + review |
| 2.4.1 Bypass blocks | Skip link is first focusable element | e2e |
| 2.4.3/2.4.7 Focus order & visible | Defined focus order; 3px ring, 2px offset | e2e + visual |
| 2.4.11 Focus not obscured | scroll-padding, non-overlapping sticky bars | e2e + manual |
| 2.5.7 Dragging | Upload has a button alternative | e2e |
| 2.5.8 Target size | ≥ 24×24 CSS px | e2e bounding-box check |
| 3.1.1/3.1.2 Language | lang on page and on hi/ta segments | unit + axe |
| 3.2.6 Consistent help | "Help & limits" in same footer position | e2e |
| 3.3.1/3.3.3 Error identification | Inline text + aria-describedby, next step | e2e |
| 3.3.7 Redundant entry | Role/type/language remembered | e2e |
| 4.1.2 Name, role, value | Native elements / Radix | axe |
| 4.1.3 Status messages | Single StatusRegion | e2e + manual |

## Screen-Reader Announcements

| Event | Region | Politeness | Pattern |
|---|---|---|---|
| Extraction finished | status | polite | "Read 18 pages." |
| Redaction preview ready | status | polite | "Found 6 personal details. Review before continuing." |
| Analysis stage change | status | polite, ≥5s apart | "Analysing clauses, 40 percent." |
| Analysis complete | status | polite | "Done. 2 high, 3 medium, 2 low findings." |
| Urgent notice | alert | assertive, once | "Important: deadline on 27 September." |
| Answer ready | status | polite | "Answer ready with 3 citations." |
| Abstention | status | polite | "The document does not say. See suggestions." |
| Error | alert | assertive | Message + next step |
| Quota busy | status | polite | "Free AI capacity low. Retrying in 30 seconds." |

## Visual Design

- **Severity**: filled square (High), triangle (Medium), circle (Low), outlined circle (Info) — all with visible text labels
- **Themes**: system, light, dark, high contrast — all contrast-verified
- **Typography**: system UI stack + optional Atkinson Hyperlegible; Noto Sans Devanagari/Tamil
- **Controls**: minimum 24×24 CSS px target size

## Keyboard Navigation

- **Skip link**: First focusable element → jumps to main content
- **Tab order**: Header → urgency banner → tabs → active panel → footer
- **Dialogs**: Focus trapped; Esc closes; focus returns to trigger
- **Tabs/Accordion**: Arrow-key navigation (Radix pattern)
- **No single-character shortcuts** (WCAG 2.1.4)

## Multilingual Support

- Output in English, Hindi, Tamil
- `lang` attribute set on each translated segment
- Legal terms kept in English in brackets
- Machine-translation notice on all translated output
- Read-aloud with appropriate language voices

## Known Limitations

- Screen-reader testing is manual; automated coverage is via axe + role assertions
- Hindi/Tamil voices depend on OS/browser voice availability; graceful fallback provided
- Scanned PDFs (P2) cannot be processed — guidance message shown
