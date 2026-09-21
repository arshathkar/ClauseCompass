from typing import Optional
from app.core.errors import BudgetExceededError
from app.core.settings import settings


class BudgetTracker:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.calls_this_analysis = 0
        self.total_session_calls = 0
        self.total_session_tokens = 0

    def start_analysis(self) -> None:
        self.calls_this_analysis = 0

    def add_call(self, input_tokens: int, output_tokens: int) -> None:
        self.calls_this_analysis += 1
        self.total_session_calls += 1
        self.total_session_tokens += (input_tokens + output_tokens)

        if self.calls_this_analysis > settings.calls_per_analysis_max:
            raise BudgetExceededError(f"Exceeded max LLM calls per analysis ({settings.calls_per_analysis_max})")

        if self.total_session_calls > settings.calls_per_session_max:
            raise BudgetExceededError(f"Exceeded max LLM calls per session ({settings.calls_per_session_max})")

        if self.total_session_tokens > settings.tokens_per_session_max:
            raise BudgetExceededError(f"Exceeded max LLM tokens per session ({settings.tokens_per_session_max})")


# In-memory store for session budgets
_budgets = {}

def get_budget_tracker(session_id: str) -> BudgetTracker:
    if session_id not in _budgets:
        _budgets[session_id] = BudgetTracker(session_id)
    return _budgets[session_id]

def delete_budget_tracker(session_id: str) -> None:
    if session_id in _budgets:
        del _budgets[session_id]
