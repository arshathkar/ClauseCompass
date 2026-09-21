from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_session, get_llm_client
from app.api.sse import sse_response
from app.session.store import SessionData
from app.llm.base import LLMClient
from app.compare.aligner import align_clauses
from app.compare.numeric_diff import compute_numeric_diff

router = APIRouter()

class CompareRequest(BaseModel):
    doc_a_id: str
    doc_b_id: str
    user_role: str

@router.post("/v1/compare")
async def compare_documents(
    req: CompareRequest,
    session: SessionData = Depends(get_session),
    llm: LLMClient = Depends(get_llm_client)
):
    doc_a = session.data.get(f"doc_{req.doc_a_id}")
    doc_b = session.data.get(f"doc_{req.doc_b_id}")
    
    async def compare_gen():
        yield {"event": "status", "data": "Aligning clauses"}
        
        pairs = align_clauses(doc_a["clauses"], doc_b["clauses"])
        
        for p in pairs:
            if p.status == "changed" and p.a_clause_id and p.b_clause_id:
                # Add numeric diffs
                ca = next(c for c in doc_a["clauses"] if c.id == p.a_clause_id)
                cb = next(c for c in doc_b["clauses"] if c.id == p.b_clause_id)
                p.numeric_changes = compute_numeric_diff(ca.text, cb.text)
                
            yield {"event": "pair", "data": p.model_dump()}
            
        yield {"event": "done", "data": {}}
        
    return sse_response(compare_gen())
