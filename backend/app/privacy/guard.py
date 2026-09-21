import json
from typing import Any
from app.core.errors import PrivacyLeakError
from app.privacy.redactor import Redactor


class OutboundGuard:
    def __init__(self, redactor: Redactor):
        self.redactor = redactor
        
    def check_payload(self, payload: str) -> None:
        """
        Re-scan the payload before sending to LLM.
        Any hit raises PrivacyLeakError.
        """
        _, items, _ = self.redactor.detect_and_mask(payload)
        
        # We only care about pattern matches, ignoring custom terms since custom terms 
        # would already be replaced by placeholders if active. But wait, if they weren't masked
        # because the user toggled them off, they shouldn't trigger the guard either.
        # Wait, the spec says "re-scan the payload with the same detectors; any hit raises PrivacyLeakError".
        # This implies we scan for patterns. If a pattern matches, it means PII is leaking.
        
        # We only throw error if a pattern is detected.
        # If the user toggled off masking for an AADHAAR, the guard will block it!
        # This enforces "fail closed" / privacy by default.
        # Actually, if the user toggled it off, they consented. But the PRD says:
        # "outbound guard: before every provider call, re-scan the payload with the same detectors; any hit raises PrivacyLeakError and the call is not made (fail closed)."
        # We will follow the PRD strictly.
        
        if items:
            raise PrivacyLeakError(detail=f"Privacy guard blocked outbound call: detected {items[0].type}")
