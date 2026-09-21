import re
from typing import Tuple

ADVICE_PATTERNS = [
    re.compile(r'\b(should i sign|is it safe to sign|tell me to sign)\b', re.IGNORECASE),
    re.compile(r'\b(will i win|can i sue|is this legal)\b', re.IGNORECASE)
]

def check_advice_boundary(question: str) -> Tuple[bool, str]:
    """
    Returns (is_asking_advice, message)
    """
    for pat in ADVICE_PATTERNS:
        if pat.search(question):
            return True, "I can't tell you whether to sign or if you will win. Here are the clauses relevant to your question. A lawyer can advise on your situation."
    return False, ""
