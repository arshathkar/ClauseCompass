import pytest
from app.ingestion.doctype import classify_doctype


class FakeLLMClient:
    """Minimal fake for doctype tests — heuristics should handle these."""
    async def generate_json(self, **kwargs):
        return None


@pytest.fixture
def fake_llm():
    return FakeLLMClient()


@pytest.mark.asyncio
@pytest.mark.unit
async def test_rental_keyword_scoring(fake_llm):
    """F1.5: Rental document detected by keywords."""
    text = "This Leave and License Agreement is between the Landlord and the Tenant for a monthly rent of Rs. 25,000."
    doc_type, conf = await classify_doctype(text, fake_llm)
    assert doc_type == "rental"
    assert conf > 0


@pytest.mark.asyncio
@pytest.mark.unit
async def test_employment_keyword_scoring(fake_llm):
    """F1.5: Employment document detected by keywords."""
    text = "This offer of employment is made by the Employer. Your salary will be Rs. 50,000 per month. A probation period of 6 months applies."
    doc_type, conf = await classify_doctype(text, fake_llm)
    assert doc_type == "employment"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_loan_keyword_scoring(fake_llm):
    """F1.5: Loan document detected by keywords."""
    text = "This loan agreement is between the Lender and the Borrower. The interest rate is 12% per annum. Repayment shall be monthly."
    doc_type, conf = await classify_doctype(text, fake_llm)
    assert doc_type == "loan"


@pytest.mark.asyncio
@pytest.mark.unit
async def test_unknown_fallback(fake_llm):
    """F1.5: Unclassifiable text returns 'other'."""
    text = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    doc_type, conf = await classify_doctype(text, fake_llm)
    assert doc_type == "other"
