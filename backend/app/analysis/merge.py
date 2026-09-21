from typing import List, Dict, Tuple
from app.llm.schemas import Finding

def severity_rank(sev: str) -> int:
    ranks = {"high": 4, "medium": 3, "low": 2, "info": 1}
    return ranks.get(sev, 0)

def merge_findings(rule_findings: List[Finding], llm_findings: List[Finding]) -> List[Finding]:
    """
    Merge rule and LLM findings according to the agreement matrix.
    Keys are (clause_id, category).
    """
    rule_map: Dict[Tuple[str, str], Finding] = {}
    llm_map: Dict[Tuple[str, str], Finding] = {}
    
    for f in rule_findings:
        rule_map[(f.clause_id, f.category)] = f
        
    for f in llm_findings:
        llm_map[(f.clause_id, f.category)] = f
        
    merged = []
    
    all_keys = set(rule_map.keys()) | set(llm_map.keys())
    
    for key in all_keys:
        rf = rule_map.get(key)
        lf = llm_map.get(key)
        
        if rf and lf:
            # Agree
            lf.source = "both"
            lf.rule_agreement = "agree"
            
            # Severity = higher of the two
            if severity_rank(rf.severity) > severity_rank(lf.severity):
                lf.severity = rf.severity
                
            # Confidence = max
            lf.confidence = max(rf.confidence, lf.confidence)
            
            # Combine law pack refs
            lf.law_pack_refs = list(set(rf.law_pack_refs + lf.law_pack_refs))
            
            merged.append(lf)
            
        elif rf and not lf:
            # Rule only -> Needs review
            rf.source = "rule"
            rf.rule_agreement = "rule_only"
            rf.needs_review = True
            merged.append(rf)
            
        elif not rf and lf:
            # LLM only
            lf.source = "llm"
            lf.rule_agreement = "llm_only"
            if lf.severity == "high":
                lf.needs_review = True # "AI-only - verify"
            merged.append(lf)
            
    return merged
