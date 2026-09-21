import pytest
from app.qa.citation_verifier import CitationVerifier
from app.llm.schemas import Citation, Clause, Span


@pytest.fixture
def verifier():
    return CitationVerifier(fuzzy_threshold=90.0)


@pytest.fixture
def sample_clause():
    return Clause(
        id="c-001",
        text="The Licensor may terminate this Agreement at any time without assigning any reason by giving 30 days' written notice to the Licensee.",
        number="4.1",
        heading="Termination",
        span=Span(start=0, end=130),
    )


@pytest.mark.unit
def test_exact_match(verifier, sample_clause):
    """F5.1: Exact substring match is verified."""
    cit = Citation(
        clause_id="c-001",
        quote="terminate this Agreement at any time without assigning any reason",
        verified=False,
    )
    result = verifier.verify(cit, [sample_clause])
    assert result.verified is True


@pytest.mark.unit
def test_fuzzy_match(verifier, sample_clause):
    """F5.2: Fuzzy match >= 0.90 passes."""
    # Slightly altered quote (missing apostrophe, minor typo)
    cit = Citation(
        clause_id="c-001",
        quote="terminate this Agreement at any time without assigning any reason by giving 30 days written notice",
        verified=False,
    )
    result = verifier.verify(cit, [sample_clause])
    assert result.verified is True


@pytest.mark.unit
def test_failed_citation(verifier, sample_clause):
    """F5.1: Completely unrelated quote fails verification."""
    cit = Citation(
        clause_id="c-001",
        quote="The rent shall be paid on the first of every month",
        verified=False,
    )
    result = verifier.verify(cit, [sample_clause])
    assert result.verified is False


@pytest.mark.unit
def test_normalization_dashes(verifier):
    """F5.3: Em-dash normalizes to hyphen for matching."""
    clause = Clause(
        id="c-002",
        text="non-compete clause shall apply for 12 months after termination",
        number="7.1",
        heading="Non-Compete",
        span=Span(start=0, end=60),
    )
    cit = Citation(
        clause_id="c-002",
        quote="non\u2014compete clause shall apply",  # em-dash
        verified=False,
    )
    result = verifier.verify(cit, [clause])
    assert result.verified is True


@pytest.mark.unit
def test_missing_clause_id(verifier, sample_clause):
    """F5.1: Citation with non-existent clause ID fails."""
    cit = Citation(
        clause_id="c-999",
        quote="terminate this Agreement",
        verified=False,
    )
    result = verifier.verify(cit, [sample_clause])
    assert result.verified is False


@pytest.mark.unit
def test_empty_quote(verifier, sample_clause):
    """F5.1: Citation with empty quote fails."""
    cit = Citation(
        clause_id="c-001",
        quote="",
        verified=False,
    )
    result = verifier.verify(cit, [sample_clause])
    assert result.verified is False
