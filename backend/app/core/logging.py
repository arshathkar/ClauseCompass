import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict

from app.core.settings import settings


class JSONFormatter(logging.Formatter):
    """
    Structured JSON formatter.
    Strictly forbids logging any actual document content or full prompts.
    Only logs IDs, sizes, timings, and statuses.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        if hasattr(record, "session_id"):
            log_obj["session_id"] = record.session_id  # type: ignore

        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = record.duration_ms  # type: ignore
            
        if hasattr(record, "token_count"):
            log_obj["token_count"] = record.token_count  # type: ignore

        if hasattr(record, "status"):
            log_obj["status"] = record.status  # type: ignore

        if record.exc_info:
            log_obj["error"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logging() -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.log_level)

    # Remove default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    # Silence third-party logs
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
