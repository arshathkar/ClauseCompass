import pytest
from app.ingestion.sanitize import sanitize_text
from app.core.errors import PayloadTooLargeError


@pytest.mark.unit
def test_nfc_normalization():
    """F1.1: Text is NFC-normalized."""
    # Combining character form → precomposed
    text = "caf\u0065\u0301"  # e + combining acute = café
    result = sanitize_text(text)
    assert "\u00e9" in result  # precomposed é


@pytest.mark.unit
def test_zero_width_stripping():
    """F1.1: Zero-width characters are stripped."""
    text = "Hello\u200bWorld"  # zero-width space
    result = sanitize_text(text)
    assert "\u200b" not in result


@pytest.mark.unit
def test_control_char_removal():
    """F1.1: Control chars removed except newline and tab."""
    text = "Hello\x00World\tOK\n"
    result = sanitize_text(text)
    assert "\x00" not in result
    assert "\t" in result
    assert "\n" in result


@pytest.mark.unit
def test_normal_text():
    """F1.1: Normal text passes through unchanged."""
    text = "This is a normal legal clause."
    result = sanitize_text(text)
    assert result == text


@pytest.mark.unit
def test_char_cap_enforcement():
    """F1.2: Text exceeding 400k chars raises PayloadTooLargeError."""
    long_text = "a" * 500000
    with pytest.raises(PayloadTooLargeError):
        sanitize_text(long_text)


@pytest.mark.unit
def test_within_cap():
    """F1.2: Text within limit passes."""
    text = "a" * 1000
    result = sanitize_text(text)
    assert len(result) == 1000
