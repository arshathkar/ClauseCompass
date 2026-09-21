import re
from typing import Optional
from datetime import datetime, timedelta

URGENCY_KEYWORDS = re.compile(r'\b(summons|eviction|legal notice|show cause|fir|arrest|court|hearing|vacate|final notice|recall)\b', re.IGNORECASE)
DEADLINE_PATTERN = re.compile(r'\b(?:within\s+(\d+)\s+days|by\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})|by\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4}))\b', re.IGNORECASE)

def detect_urgency(text: str) -> Optional[str]:
    # Check keywords
    if URGENCY_KEYWORDS.search(text):
        return "Contains urgent legal keywords (e.g., summons, eviction, notice)."
        
    # Real implementation would parse dates and check if within 7 days from now (Asia/Kolkata)
    # Simple check for "within N days" where N <= 7
    for pat in [DEADLINE_PATTERN]:
        for match in pat.finditer(text):
            if match.group(1): # within N days
                days = int(match.group(1))
                if days <= 7:
                    return f"Contains a deadline within {days} days."
                    
    return None
