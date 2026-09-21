from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    status_code: int = 500
    type_uri: str = "about:blank"
    title: str = "Internal Server Error"
    detail: str = "An unexpected error occurred."

    def __init__(self, detail: Optional[str] = None, extensions: Optional[Dict[str, Any]] = None):
        if detail:
            self.detail = detail
        self.extensions = extensions or {}
        super().__init__(self.detail)

    def to_problem_json(self, instance: Optional[str] = None) -> Dict[str, Any]:
        payload = {
            "type": self.type_uri,
            "title": self.title,
            "status": self.status_code,
            "detail": self.detail,
        }
        if instance:
            payload["instance"] = instance
        payload.update(self.extensions)
        return payload


class ValidationError(AppError):
    status_code = 422
    type_uri = "https://clausecompass.invalid/errors/validation"
    title = "Validation Error"
    detail = "The input failed validation."


class UnsupportedInputError(AppError):
    status_code = 415
    type_uri = "https://clausecompass.invalid/errors/unsupported-input"
    title = "Unsupported Input"
    detail = "The provided file or input type is not supported."


class PayloadTooLargeError(AppError):
    status_code = 413
    type_uri = "https://clausecompass.invalid/errors/payload-too-large"
    title = "Payload Too Large"
    detail = "The request payload exceeds the configured limit."


class SessionExpiredError(AppError):
    status_code = 401
    type_uri = "https://clausecompass.invalid/errors/session-expired"
    title = "Session Expired"
    detail = "The session has expired or is invalid."


class NotFoundError(AppError):
    status_code = 404
    type_uri = "https://clausecompass.invalid/errors/not-found"
    title = "Not Found"
    detail = "The requested resource was not found."


class RateLimitedError(AppError):
    status_code = 429
    type_uri = "https://clausecompass.invalid/errors/rate-limited"
    title = "Rate Limited"
    detail = "Too many requests. Please try again later."


class BudgetExceededError(AppError):
    status_code = 402
    type_uri = "https://clausecompass.invalid/errors/budget-exceeded"
    title = "Budget Exceeded"
    detail = "The maximum allowed LLM calls or tokens for this session/analysis was exceeded."


class CapacityExhaustedError(AppError):
    status_code = 503
    type_uri = "https://clausecompass.invalid/errors/capacity-exhausted"
    title = "Capacity Exhausted"
    detail = "Free AI capacity is currently unavailable. Please use the replay demo or try later."


class LLMInvalidOutputError(AppError):
    status_code = 502
    type_uri = "https://clausecompass.invalid/errors/llm-invalid-output"
    title = "LLM Invalid Output"
    detail = "The LLM returned an invalid or unparseable response."


class PrivacyLeakError(AppError):
    status_code = 403
    type_uri = "https://clausecompass.invalid/errors/privacy-leak"
    title = "Privacy Leak Blocked"
    detail = "Request was blocked because potential PII was detected before calling the LLM."


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_problem_json(instance=str(request.url)),
        headers={"Content-Type": "application/problem+json"}
    )
