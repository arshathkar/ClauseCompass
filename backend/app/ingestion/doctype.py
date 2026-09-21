from typing import Optional, Tuple
from app.llm.base import LLMClient, TaskName
from pydantic import BaseModel

class DocTypeResult(BaseModel):
    doc_type: str
    confidence: float

async def classify_doctype(text: str, llm_client: LLMClient) -> Tuple[str, float]:
    # Heuristic keywords mapping
    # Simplified for the build
    text_lower = text[:3000].lower()
    
    heuristics = {
        "rental": ["rent", "landlord", "tenant", "lease", "leave and license"],
        "employment": ["salary", "employer", "employee", "probation", "offer of employment"],
        "loan": ["lender", "borrower", "loan", "interest rate", "repayment"],
        "freelance": ["freelance", "contractor", "services", "statement of work", "deliverables"],
        "nda": ["confidential", "non-disclosure", "disclosing party", "receiving party"],
    }
    
    scores = {}
    for dtype, keywords in heuristics.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[dtype] = score / len(keywords)
            
    if scores:
        best_type, best_score = max(scores.items(), key=lambda x: x[1])
        if best_score >= 0.7:
            return best_type, best_score
            
    # Fallback to LLM
    system_prompt = "Classify the type of legal document based on the text."
    user_prompt = f"Text:\n{text[:3000]}"
    
    try:
        result = await llm_client.generate_json(
            task=TaskName.DOC_TYPE,
            system=system_prompt,
            user=user_prompt,
            schema=DocTypeResult,
            tier="fast"
        )
        return result.data.doc_type, result.data.confidence
    except Exception:
        return "other", 0.0
