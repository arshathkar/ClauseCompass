import pytest
from app.privacy.guard import OutboundGuard
from app.privacy.redactor import Redactor
from app.core.errors import PrivacyLeakError


@pytest.fixture
def guard():
    return OutboundGuard(redactor=Redactor())


@pytest.mark.unit
def test_outbound_guard_catches_pii(guard):
    """F2.3: Outbound guard catches PII in payload."""
    with pytest.raises(PrivacyLeakError):
        guard.check_payload("Send this to test@example.com please")


@pytest.mark.unit
def test_outbound_guard_catches_phone(guard):
    """F2.3: Outbound guard catches phone numbers."""
    with pytest.raises(PrivacyLeakError):
        guard.check_payload("Call +91 98765 43210 for details")


@pytest.mark.unit
def test_outbound_guard_clean(guard):
    """F2.3: Clean payload passes without error."""
    # Should not raise
    guard.check_payload("The monthly rent is [[AMOUNT_1]] payable by [[DATE_1]].")


@pytest.mark.unit
def test_outbound_guard_with_placeholders(guard):
    """F2.3: Already-masked text passes."""
    guard.check_payload("Contact [[EMAIL_1]] at [[PHONE_1]] regarding [[PAN_1]].")
