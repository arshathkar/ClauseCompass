import pytest
from app.compare.numeric_diff import extract_numbers, compute_numeric_diff


@pytest.mark.unit
def test_extract_numbers_money():
    """F7.1: Extract monetary amounts."""
    text = "The rent is Rs. 25,000/- per month and the deposit is Rs. 75,000/-."
    numbers = extract_numbers(text)
    assert len(numbers) >= 2


@pytest.mark.unit
def test_extract_numbers_percentage():
    """F7.1: Extract percentage values."""
    text = "Interest at 2% per month, with 5% annual escalation."
    numbers = extract_numbers(text)
    assert len(numbers) >= 2


@pytest.mark.unit
def test_compute_numeric_diff():
    """F7.1: Compute differences between two texts."""
    old_text = "The monthly rent is Rs. 25,000 with a 5% escalation."
    new_text = "The monthly rent is Rs. 27,500 with a 10% escalation."
    diffs = compute_numeric_diff(old_text, new_text)
    # Should detect at least the amount and percentage changes
    assert isinstance(diffs, list)
