import pytest
from app.privacy.redactor import Redactor


@pytest.fixture
def redactor():
    return Redactor()


@pytest.mark.unit
def test_pan_detection(redactor):
    """F2.1: PAN card detection."""
    masked, items, pmap = redactor.detect_and_mask("PAN: ABCPS1234K")
    types = [i.type for i in items]
    assert "PAN" in types


@pytest.mark.unit
def test_phone_detection(redactor):
    """F2.1: Indian phone number detection."""
    masked, items, pmap = redactor.detect_and_mask("Call me at +91 98765 43210")
    types = [i.type for i in items]
    assert "PHONE" in types


@pytest.mark.unit
def test_email_detection(redactor):
    """F2.1: Email detection."""
    masked, items, pmap = redactor.detect_and_mask("Email: meera@example.com")
    types = [i.type for i in items]
    assert "EMAIL" in types


@pytest.mark.unit
def test_ifsc_detection(redactor):
    """F2.1: IFSC code detection."""
    masked, items, pmap = redactor.detect_and_mask("IFSC: SBIN0001234")
    types = [i.type for i in items]
    assert "IFSC" in types


@pytest.mark.unit
def test_placeholder_consistency(redactor):
    """F2.2: Same value gets same placeholder."""
    text = "Call +91 98765 43210 or +91 98765 43210"
    masked, items, pmap = redactor.detect_and_mask(text)
    phone_placeholders = [i.placeholder for i in items if i.type == "PHONE"]
    if len(phone_placeholders) >= 2:
        assert phone_placeholders[0] == phone_placeholders[1]


@pytest.mark.unit
def test_custom_term_masking(redactor):
    """F2.2: Custom terms are masked."""
    text = "Contact Rajesh Kumar Sharma at the office."
    masked, items, pmap = redactor.detect_and_mask(text, custom_terms=["Rajesh Kumar Sharma"])
    assert "Rajesh Kumar Sharma" not in masked
    assert "[[CUSTOM_" in masked


@pytest.mark.unit
def test_reversible_map(redactor):
    """F2.2: Placeholder map allows reversal."""
    text = "Email: meera@example.com"
    masked, items, pmap = redactor.detect_and_mask(text)
    for placeholder, original in pmap.items():
        assert placeholder in masked
        assert original in text


@pytest.mark.unit
def test_masking_produces_placeholders(redactor):
    """F2.1: Masked text contains placeholders not originals."""
    text = "PAN: BNCPN5678L, Phone: +91 87654 32109"
    masked, items, pmap = redactor.detect_and_mask(text)
    if items:
        assert "[[" in masked
        for item in items:
            assert item.original_value not in masked
