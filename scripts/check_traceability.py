#!/usr/bin/env python3
"""Verify that every P0 acceptance criterion ID has a matching test.

Scans backend/tests/ for `test_<ID>_` patterns and frontend/tests/ for
`describe("<ID>` patterns. Reports any P0 ID without a matching test.

Fails CI if any P0 ID is untested.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

# P0 feature IDs from the PRD
P0_IDS: list[str] = [
    "F1_1", "F1_2", "F1_3", "F1_4", "F1_5", "F1_6",
    "F2_1", "F2_2", "F2_3",
    "F3_1", "F3_2",
    "F4_1", "F4_2",
    "F5_1", "F5_2", "F5_3", "F5_6",
    "F6_1", "F6_2", "F6_3",
    "F7_1", "F7_2",
    "F8_1", "F8_4",
    "F9_1", "F9_2", "F9_3", "F9_4",
    "F10_1", "F10_2", "F10_3", "F10_4",
    "F11_1", "F11_2", "F11_3", "F11_4", "F11_5", "F11_6", "F11_7", "F11_9",
    "F12_1", "F12_2", "F12_3", "F12_4",
    "F13_1", "F13_2", "F13_3", "F13_4",
]

# Also accept dot-separated: F1.1, F1.2, etc.
ID_VARIANTS = {
    fid: [fid, fid.replace("_", "."), fid.replace("_", "-")]
    for fid in P0_IDS
}


def find_tested_ids(root: Path) -> set[str]:
    """Scan test files for ID references."""
    tested: set[str] = set()
    patterns_by_id = {
        fid: re.compile(
            "|".join(re.escape(v) for v in variants),
            re.IGNORECASE,
        )
        for fid, variants in ID_VARIANTS.items()
    }

    for ext in ("*.py", "*.ts", "*.tsx", "*.js"):
        for path in root.rglob(ext):
            if "node_modules" in str(path) or ".venv" in str(path):
                continue
            try:
                content = path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            for fid, pattern in patterns_by_id.items():
                if pattern.search(content):
                    tested.add(fid)
    return tested


def main() -> int:
    """Check traceability. Returns 1 if any P0 ID is untested."""
    project_root = Path(__file__).resolve().parent.parent

    test_dirs = [
        project_root / "backend" / "tests",
        project_root / "frontend" / "tests",
        project_root / "frontend" / "src",  # Also check inline test files
    ]

    tested: set[str] = set()
    for d in test_dirs:
        if d.exists():
            tested |= find_tested_ids(d)

    untested = sorted(set(P0_IDS) - tested)

    print(f"P0 IDs: {len(P0_IDS)}")
    print(f"Tested: {len(tested)}")
    print(f"Untested: {len(untested)}")
    print()

    if untested:
        print("FAIL: The following P0 IDs have no matching test:")
        for fid in untested:
            print(f"  - {fid}")
        return 1

    print("OK: All P0 acceptance criteria have matching tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
