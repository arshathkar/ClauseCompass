from typing import List
from rank_bm25 import BM25Okapi
from app.llm.schemas import Clause

def retrieve_top_k(query: str, clauses: List[Clause], k: int = 6) -> List[Clause]:
    if not clauses:
        return []
        
    tokenized_corpus = [c.text.lower().split() for c in clauses]
    bm25 = BM25Okapi(tokenized_corpus)
    
    tokenized_query = query.lower().split()
    top_n = bm25.get_top_n(tokenized_query, clauses, n=k)
    return top_n
