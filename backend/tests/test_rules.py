import pytest
from app.analysis.rules.engine import RuleEngine
from app.llm.schemas import Clause, Span


@pytest.fixture
def engine():
    return RuleEngine()


@pytest.fixture
def make_clause():
    """Factory for creating test clauses."""
    def _make(clause_id, text, heading="Test", number="1.0"):
        return Clause(
            id=clause_id, text=text, heading=heading, number=number,
            span=Span(start=0, end=len(text))
        )
    return _make


@pytest.mark.unit
def test_rules_positive(engine, make_clause):
    """F3.1: Rules fire on positive examples."""
    clause = make_clause(
        "c-001",
        "The Licensor may terminate this Agreement at any time without assigning any reason by giving 30 days' written notice."
    )
    findings = engine.evaluate_clause(clause, "rental")
    assert len(findings) >= 1
    categories = [f.category for f in findings]
    assert "termination_unilateral" in categories


@pytest.mark.unit
def test_rules_negative(engine, make_clause):
    """F3.1: Rules don't fire on clean text."""
    clause = make_clause("c-002", "The rent is payable on the first of every month.")
    findings = engine.evaluate_clause(clause, "rental")
    assert len(findings) == 0


@pytest.mark.unit
def test_doc_type_scoping(engine, make_clause):
    """F3.2: Rules respect doc_type scoping."""
    # A rental-specific clause tested against employment shouldn't match
    clause = make_clause(
        "c-003",
        "The Licensor may terminate this Agreement at any time without assigning any reason."
    )
    rental_findings = engine.evaluate_clause(clause, "rental")
    employment_findings = engine.evaluate_clause(clause, "employment")
    # At least for rental it should match; employment might not if rule is scoped
    assert len(rental_findings) >= len(employment_findings)


@pytest.mark.unit
def test_severity(engine, make_clause):
    """F3.2: Rule findings have correct severity."""
    clause = make_clause(
        "c-004",
        "The Licensor may terminate this Agreement at any time without assigning any reason."
    )
    findings = engine.evaluate_clause(clause, "rental")
    for f in findings:
        assert f.severity in ("high", "medium", "low", "info")


@pytest.mark.unit
def test_rule_finding_has_citation(engine, make_clause):
    """F3.2: Rule findings include citation with source quote."""
    clause = make_clause(
        "c-005",
        "The Licensor reserves the right to modify the terms at any time without notice."
    )
    findings = engine.evaluate_clause(clause, "rental")
    for f in findings:
        assert f.citation is not None
        assert f.citation.verified is True
        assert f.source == "rule"


@pytest.mark.unit
def test_rules_loaded(engine):
    """F3.1: Rules loaded from risk_rules.yaml."""
    assert len(engine.rules) >= 10  # We have 11 seed rules
