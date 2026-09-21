from dataclasses import dataclass
from enum import Enum
from typing import Generic, Literal, Protocol, Type, TypeVar

T = TypeVar("T")


class TaskName(str, Enum):
    DOC_TYPE = "doc-type"
    KEY_FACTS = "key-facts"
    CLAUSE_ANALYSIS = "clause-analysis"
    MISSING_CLAUSES = "missing-clauses"
    QUERY_REWRITE = "query-rewrite"
    QA_ANSWER = "qa-answer"
    COMPARE_ADJUDICATE = "compare-adjudicate"
    COMPARE_IMPACT = "compare-impact"
    EMAIL_DRAFT = "email-draft"


@dataclass
class LLMResult(Generic[T]):
    data: T
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    cache_hit: bool
    prompt_version: str


class LLMClient(Protocol):
    async def generate_json(
        self,
        *,
        task: TaskName,
        system: str,
        user: str,
        schema: Type[T],
        tier: Literal["fast", "analysis"],
        max_output_tokens: int = 2048,
        temperature: float = 0.1,
    ) -> LLMResult[T]:
        ...
