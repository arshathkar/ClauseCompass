import re
from typing import List

MONEY_PATTERN = re.compile(r'((?:rs\.?|₹|inr)\s*[\d,]+(?:[.]\d{1,2})?)', re.IGNORECASE)
PERCENT_PATTERN = re.compile(r'(\d+(?:\.\d+)?\s*%)')
DURATION_PATTERN = re.compile(r'(\d+\s*(?:days?|months?|years?))', re.IGNORECASE)

def extract_numbers(text: str) -> set:
    vals = set()
    for p in [MONEY_PATTERN, PERCENT_PATTERN, DURATION_PATTERN]:
        for match in p.finditer(text):
            vals.add(match.group(1).lower())
    return vals

def compute_numeric_diff(text_a: str, text_b: str) -> List[str]:
    nums_a = extract_numbers(text_a)
    nums_b = extract_numbers(text_b)
    
    changes = []
    
    # Just list them out. A real diff would try to align them contextually.
    removed = nums_a - nums_b
    added = nums_b - nums_a
    
    if removed or added:
        changes.append(f"Removed: {', '.join(removed)} | Added: {', '.join(added)}")
        
    return changes
