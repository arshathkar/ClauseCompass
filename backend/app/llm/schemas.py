from typing import List, Literal, Optional, Tuple
from pydantic import BaseModel, Field

Severity = Literal["high", "medium", "low", "info"]


class Span(BaseModel):
    start: int
    end: int


class Citation(BaseModel):
    clause_id: str
    quote: str = Field(max_length=400)
    verified: bool = False
    span: Optional[Span] = None


class Clause(BaseModel):
    id: str  # e.g., "c-001"
    number: Optional[str]
    heading: Optional[str]
    text: str
    span: Span
    pages: Optional[Tuple[int, int]] = None
    parent_id: Optional[str] = None
    is_definition: bool = False


class Finding(BaseModel):
    id: str
    clause_id: str
    category: str  # taxonomy key, e.g. "termination_unilateral"
    severity: Severity
    plain_summary: str
    why_it_matters: str
    who_is_affected: Literal["user", "counterparty", "both", "unclear"]
    suggested_question: Optional[str] = None
    citation: Citation
    confidence: float = Field(ge=0, le=1)
    source: Literal["rule", "llm", "both"]
    rule_agreement: Literal["agree", "rule_only", "llm_only", "n/a"]
    needs_review: bool = False
    law_pack_refs: List[str] = []
    prompt_version: Optional[str] = None


class ClauseFindingBatch(BaseModel):
    findings: List[Finding]


class KeyFact(BaseModel):
    label: str  # "Monthly rent"
    value: Optional[str]  # None -> shown as "Not stated"
    citation: Optional[Citation]


class Obligation(BaseModel):
    party: Literal["user", "counterparty"]
    text: str
    citation: Citation


class KeyFactsResult(BaseModel):
    facts: List[KeyFact]
    obligations: List[Obligation]
    summary_simple: str
    summary_standard: str
    summary_detailed: str
    summary_citations: List[Citation]


class QASegment(BaseModel):
    text: str
    citations: List[Citation]


class QAAnswer(BaseModel):
    answerable: bool
    segments: List[QASegment]
    follow_ups: List[str] = []
    confidence: float = Field(ge=0, le=1)


class ComparePair(BaseModel):
    status: Literal["added", "removed", "changed", "unchanged"]
    a_clause_id: Optional[str]
    b_clause_id: Optional[str]
    diff_ops: List[Tuple[Literal["eq", "ins", "del"], str]] = []
    numeric_changes: List[str] = []
    change_summary: Optional[str] = None
    favors: Optional[Literal["user", "counterparty", "neutral", "unclear"]] = None
    risk_delta: Optional[Literal["up", "down", "neutral", "unclear"]] = None
    citations: List[Citation] = []
