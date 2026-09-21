#!/usr/bin/env python3
"""Verify that all design-token color pairs meet WCAG contrast requirements.

Reads the token pairs from §8.8 of the PRD and checks each pair's contrast
ratio against its requirement (4.5:1 for text, 3:1 for non-text/borders).

Fails CI if any pair is below threshold.
"""

from __future__ import annotations

import sys


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """Convert a hex color string to RGB tuple."""
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def relative_luminance(r: int, g: int, b: int) -> float:
    """Calculate WCAG 2.x relative luminance."""

    def linearize(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    lr, lg, lb = linearize(r), linearize(g), linearize(b)
    return 0.2126 * lr + 0.7152 * lg + 0.0722 * lb


def contrast_ratio(fg: str, bg: str) -> float:
    """Calculate WCAG contrast ratio between two hex colors."""
    l1 = relative_luminance(*hex_to_rgb(fg))
    l2 = relative_luminance(*hex_to_rgb(bg))
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


# Token pairs from §8.8 of the PRD
# Format: (name, foreground, background, minimum_ratio)
PAIRS: list[tuple[str, str, str, float]] = [
    # Light theme
    ("Light · body text", "#111827", "#FFFFFF", 4.5),
    ("Light · muted text", "#4B5563", "#FFFFFF", 4.5),
    ("Light · brand/links/focus", "#1D4ED8", "#FFFFFF", 4.5),
    ("Light · High badge", "#B91C1C", "#FEF2F2", 4.5),
    ("Light · Medium badge", "#92400E", "#FFFBEB", 4.5),
    ("Light · Low badge", "#166534", "#F0FDF4", 4.5),
    ("Light · Info badge", "#374151", "#F3F4F6", 4.5),
    ("Light · control borders", "#6B7280", "#FFFFFF", 3.0),
    # Dark theme
    ("Dark · body text", "#F3F4F6", "#0B1220", 4.5),
    ("Dark · muted text", "#9CA3AF", "#0B1220", 4.5),
    ("Dark · brand/focus", "#93C5FD", "#0B1220", 4.5),
    ("Dark · High badge", "#FCA5A5", "#450A0A", 4.5),
    ("Dark · Medium badge", "#FCD34D", "#422006", 4.5),
    ("Dark · Low badge", "#86EFAC", "#052E16", 4.5),
    ("Dark · Info badge", "#D1D5DB", "#1F2937", 4.5),
    ("Dark · control borders", "#6B7280", "#0B1220", 3.0),
    # High contrast
    ("HC · text on black", "#FFFFFF", "#000000", 7.0),
    ("HC · yellow on black", "#FFFF00", "#000000", 7.0),
    ("HC · cyan on black", "#00FFFF", "#000000", 7.0),
]


def main() -> int:
    """Check all contrast pairs. Returns 1 if any fail."""
    failures: list[str] = []
    print("Checking WCAG contrast ratios...\n")

    for name, fg, bg, min_ratio in PAIRS:
        ratio = contrast_ratio(fg, bg)
        status = "✓" if ratio >= min_ratio else "✗"
        line = f"  {status} {name}: {ratio:.2f}:1 (need {min_ratio}:1) [{fg} on {bg}]"
        print(line)
        if ratio < min_ratio:
            failures.append(name)

    print()
    if failures:
        print(f"FAIL: {len(failures)} pair(s) below threshold:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print(f"OK: All {len(PAIRS)} pairs pass contrast checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
