import pytest
from app.ingestion.clause_tree import build_clause_tree


def _flatten_clauses(nested):
    """Flatten the nested clause tree into a flat list."""
    clauses = []
    for item in nested:
        if isinstance(item, list):
            clauses.extend(item)
        else:
            clauses.append(item)
    return clauses


@pytest.mark.unit
def test_numbered_clause_detection():
    """F1.3: Numbered clauses are detected."""
    text = "1. First clause text here.\n2. Second clause text here.\n3. Third clause."
    nested, defs = build_clause_tree(text)
    clauses = _flatten_clauses(nested)
    assert len(clauses) >= 2


@pytest.mark.unit
def test_heading_detection():
    """F1.3: Headings are detected."""
    text = "TERMINATION\nThe agreement may be terminated by either party.\n\nRENEWAL\nThe agreement renews automatically."
    nested, defs = build_clause_tree(text)
    clauses = _flatten_clauses(nested)
    assert len(clauses) >= 2


@pytest.mark.unit
def test_stable_ids():
    """F1.4: Clause IDs follow c-NNN pattern."""
    text = "1. First clause.\n2. Second clause."
    nested, defs = build_clause_tree(text)
    clauses = _flatten_clauses(nested)
    for clause in clauses:
        assert clause.id.startswith("c-")


@pytest.mark.unit
def test_fallback_unstructured():
    """F1.3: Unstructured text still produces at least one clause."""
    text = "This is just a paragraph of text without any numbered headings or structure."
    nested, defs = build_clause_tree(text)
    clauses = _flatten_clauses(nested)
    assert len(clauses) >= 1


@pytest.mark.unit
def test_clause_has_span():
    """F1.4: Each clause has a span with valid start/end."""
    text = "1. First clause content.\n2. Second clause content."
    nested, defs = build_clause_tree(text)
    clauses = _flatten_clauses(nested)
    for clause in clauses:
        assert clause.span is not None
        assert clause.span.start >= 0
        assert clause.span.end > clause.span.start
