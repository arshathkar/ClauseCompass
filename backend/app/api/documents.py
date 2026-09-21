import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_session, get_llm_client
from app.api.sse import sse_response
from app.session.store import SessionData
from app.llm.base import LLMClient
from app.ingestion.sanitize import sanitize_text
from app.ingestion.clause_tree import build_clause_tree
from app.ingestion.doctype import classify_doctype
from app.privacy.redactor import Redactor
from app.privacy.guard import OutboundGuard
from app.analysis.rules.engine import RuleEngine
from app.analysis.orchestrator import AnalysisOrchestrator
from app.qa.citation_verifier import CitationVerifier
from app.qa.answerer import QAAnswerer

router = APIRouter()
redactor = Redactor()
outbound_guard = OutboundGuard(redactor)

class DocumentSubmitRequest(BaseModel):
    text: str

class DocumentSubmitResponse(BaseModel):
    doc_id: str
    doc_type: str
    confidence: float
    redactions: List[dict]

@router.post("/v1/documents", response_model=DocumentSubmitResponse)
async def submit_document(
    req: DocumentSubmitRequest,
    session: SessionData = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client)
):
    clean_text = sanitize_text(req.text)
    
    # Run masking first
    masked_text, redactions, placeholder_map = redactor.detect_and_mask(clean_text)
    
    doc_type, confidence = await classify_doctype(masked_text, llm)
    
    doc_id = str(uuid.uuid4())
    session.data[f"doc_{doc_id}"] = {
        "original_text": clean_text,
        "masked_text": masked_text,
        "doc_type": doc_type,
        "redactions": [r.model_dump() for r in redactions],
        "placeholder_map": placeholder_map
    }
    
    return DocumentSubmitResponse(
        doc_id=doc_id,
        doc_type=doc_type,
        confidence=confidence,
        redactions=[r.model_dump() for r in redactions]
    )

class RedactionsUpdateRequest(BaseModel):
    custom_terms: List[str] = []
    active_ids: List[str] = []

@router.post("/v1/documents/{doc_id}/redactions")
async def update_redactions(
    doc_id: str,
    req: RedactionsUpdateRequest,
    session: SessionData = Depends(get_session)
):
    doc_data = session.data.get(f"doc_{doc_id}")
    if not doc_data:
        return {"error": "not found"}
        
    masked_text, redactions, placeholder_map = redactor.detect_and_mask(
        doc_data["original_text"], req.custom_terms
    )
    
    # Filter active ids
    if req.active_ids:
        for r in redactions:
            r.is_active = r.id in req.active_ids
            
    # Apply toggles
    masked_text, placeholder_map = redactor.apply_toggles(doc_data["original_text"], redactions)
    
    doc_data["masked_text"] = masked_text
    doc_data["redactions"] = [r.model_dump() for r in redactions]
    doc_data["placeholder_map"] = placeholder_map
    
    return {"status": "ok", "redactions": doc_data["redactions"]}


class AnalyzeRequest(BaseModel):
    user_role: str

@router.post("/v1/documents/{doc_id}/analyze")
async def analyze_document(
    doc_id: str,
    req: AnalyzeRequest,
    session: SessionData = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client)
):
    doc_data = session.data.get(f"doc_{doc_id}")
    
    # Guard check
    outbound_guard.check_payload(doc_data["masked_text"])
    
    clauses, definitions = build_clause_tree(doc_data["masked_text"])
    doc_data["clauses"] = clauses
    doc_data["definitions"] = definitions
    
    rule_engine = RuleEngine()
    verifier = CitationVerifier()
    orchestrator = AnalysisOrchestrator(llm, rule_engine, verifier)
    
    return sse_response(
        orchestrator.run_analysis(
            session.id, clauses, doc_data["doc_type"], req.user_role, definitions, doc_data["masked_text"]
        )
    )

class QARequest(BaseModel):
    question: str
    language: str = "en"

@router.post("/v1/documents/{doc_id}/qa")
async def ask_question(
    doc_id: str,
    req: QARequest,
    session: SessionData = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client)
):
    doc_data = session.data.get(f"doc_{doc_id}")
    clauses = doc_data["clauses"]
    definitions = doc_data["definitions"]
    
    verifier = CitationVerifier()
    answerer = QAAnswerer(llm, verifier)
    
    return sse_response(
        answerer.answer(session.id, req.question, req.language, clauses, definitions)
    )

@router.delete("/v1/documents/{doc_id}")
async def delete_document(doc_id: str, session: SessionData = Depends(get_session)):
    key = f"doc_{doc_id}"
    if key in session.data:
        del session.data[key]
    return {"status": "deleted"}
