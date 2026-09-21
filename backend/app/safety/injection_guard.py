import re
from typing import Tuple

INJECTION_PHRASES = [
    "ignore previous instructions",
    "system prompt",
    "you are now",
    "disregard the above",
    "reveal your instructions",
    "forget all previous",
    "new instructions:"
]

def check_injection(text: str) -> Tuple[bool, str]:
    text_lower = text.lower()
    for phrase in INJECTION_PHRASES:
        if phrase in text_lower:
            return True, "This document contains text that tries to instruct AI. It was ignored."
            
    # Hidden chars checking could also happen here, but sanitize handles stripping them
    return False, ""
