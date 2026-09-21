import re
import unicodedata
from typing import List, Optional
from rapidfuzz import fuzz

from app.llm.schemas import Citation, Clause, Span

class CitationVerifier:
    def __init__(self, fuzzy_threshold: float = 90.0):
        self.fuzzy_threshold = fuzzy_threshold

    def _normalize(self, text: str) -> str:
        # NFKC, lowercase, unify quotes/dashes, collapse whitespace, strip placeholder brackets
        text = unicodedata.normalize('NFKC', text)
        text = text.lower()
        # unify quotes
        text = re.sub(r'[\u2018\u2019\u201A\u201B\u0027]', "'", text)
        text = re.sub(r'[\u201C\u201D\u201E\u201F\u0022]', '"', text)
        # unify dashes
        text = re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015]', '-', text)
        # strip placeholder brackets e.g. [[AADHAAR_1]] -> AADHAAR_1
        text = re.sub(r'\[\[(.*?)\]\]', r'\1', text)
        # collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def verify(self, citation: Citation, clauses: List[Clause]) -> Citation:
        if not citation.quote or not citation.clause_id:
            citation.verified = False
            return citation

        target_clause = next((c for c in clauses if c.id == citation.clause_id), None)
        if not target_clause:
            citation.verified = False
            return citation

        norm_quote = self._normalize(citation.quote)
        norm_source = self._normalize(target_clause.text)
        
        # Exact match
        if norm_quote in norm_source:
            citation.verified = True
            # approximate span
            start_idx = norm_source.find(norm_quote)
            # mapping back to original is complex, so we just set approximate or None
            citation.span = None
            return citation
            
        # Fuzzy match (partial_ratio > 90)
        # partial_ratio_alignment gives (score, start, end)
        score = fuzz.partial_ratio(norm_quote, norm_source)
        if score >= self.fuzzy_threshold:
            citation.verified = True
            citation.span = None
            return citation
            
        # Search neighbors could be added here
        
        citation.verified = False
        return citation
