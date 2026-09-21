import re
import unicodedata
from app.core.errors import PayloadTooLargeError
from app.core.settings import settings


def sanitize_text(text: str) -> str:
    if len(text) > settings.max_text_chars:
        raise PayloadTooLargeError(
            f"Document exceeds maximum length of {settings.max_text_chars} characters."
        )

    # NFC normalize
    text = unicodedata.normalize("NFC", text)

    # Remove zero-width characters and bidi controls
    # Zero-width: U+200B-U+200D, U+2060, U+FEFF
    # Bidi: U+202A-U+202E, U+2066-U+2069
    text = re.sub(r'[\u200B-\u200D\u2060\uFEFF\u202A-\u202E\u2066-\u2069]', '', text)

    # Remove other control characters except \n and \t
    # Control characters are typically \x00-\x1F and \x7F-\x9F
    text = re.sub(r'[\x00-\x08\x0B-\x1F\x7F-\x9F]', '', text)

    # Collapse >= 3 blank lines into 2 blank lines
    text = re.sub(r'\n{4,}', '\n\n\n', text)

    return text
