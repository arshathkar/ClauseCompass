import difflib
from typing import List, Tuple
from rapidfuzz import fuzz, process

from app.llm.schemas import Clause, ComparePair


def align_clauses(doc_a: List[Clause], doc_b: List[Clause]) -> List[ComparePair]:
    pairs = []
    
    # Track used clauses to prevent multiple assignments
    used_a = set()
    used_b = set()
    
    # 1. Exact number + exact/fuzzy heading match
    for a in doc_a:
        for b in doc_b:
            if b.id in used_b:
                continue
                
            if a.number and a.number == b.number:
                if a.heading and b.heading:
                    if fuzz.ratio(a.heading.lower(), b.heading.lower()) >= 85:
                        pairs.append(ComparePair(
                            status="changed" if a.text != b.text else "unchanged",
                            a_clause_id=a.id,
                            b_clause_id=b.id
                        ))
                        used_a.add(a.id)
                        used_b.add(b.id)
                        break

    # 2. Text similarity greedy one-to-one
    remaining_a = [a for a in doc_a if a.id not in used_a]
    remaining_b = [b for b in doc_b if b.id not in used_b]
    
    for a in remaining_a:
        if not remaining_b:
            break
            
        b_texts = {b.id: b.text for b in remaining_b}
        
        # Using rapidfuzz extractOne
        best_match = process.extractOne(
            a.text, 
            b_texts,
            scorer=fuzz.token_set_ratio
        )
        
        if best_match:
            text, score, b_id = best_match
            if score >= 60:
                pairs.append(ComparePair(
                    status="changed" if a.text != text else "unchanged",
                    a_clause_id=a.id,
                    b_clause_id=b_id
                ))
                used_a.add(a.id)
                used_b.add(b_id)
                remaining_b = [b for b in remaining_b if b.id != b_id]
                
    # 3. Adjudicate ambiguous pairs 40-60 goes to LLM (simplified here, in reality we'd batch to LLM)
    # We will just treat anything below 60 as added/removed for now to save complexity
    
    # 4. Added / Removed
    for a in doc_a:
        if a.id not in used_a:
            pairs.append(ComparePair(
                status="removed",
                a_clause_id=a.id,
                b_clause_id=None
            ))
            
    for b in doc_b:
        if b.id not in used_b:
            pairs.append(ComparePair(
                status="added",
                a_clause_id=None,
                b_clause_id=b.id
            ))
            
    return pairs
