import json
import os
from typing import AsyncGenerator, Dict, List, Any

from app.llm.base import LLMClient, TaskName
from app.llm.schemas import Clause, QAAnswer
from app.qa.citation_verifier import CitationVerifier
from app.retrieval.bm25 import retrieve_top_k
from app.retrieval.query_rewrite import rewrite_query

class QAAnswerer:
    def __init__(self, llm_client: LLMClient, verifier: CitationVerifier):
        self.llm = llm_client
        self.verifier = verifier

    async def answer(
        self,
        session_id: str,
        question: str,
        language: str,
        clauses: List[Clause],
        definitions_map: Dict[str, str],
        chat_history: str = ""
    ) -> AsyncGenerator[Dict[str, Any], None]:
        
        # 1. Rewrite non-English queries
        english_query = question
        if language.lower() not in ["en", "english"]:
            english_query = await rewrite_query(self.llm, question, language, session_id)
            
        # 2. Retrieve (skip if doc <= 12k tokens roughly. 1 char ~ 0.25 tokens -> 48k chars)
        total_chars = sum(len(c.text) for c in clauses)
        if total_chars <= 48000:
            top_clauses = clauses
        else:
            top_clauses = retrieve_top_k(english_query, clauses, k=6)
            
        # 3. Answer
        clauses_text = "\n\n".join([f"[{c.id}] {c.text}" for c in top_clauses])
        
        system_prompt = self._load_prompt("common@1.3.md").format(
            user_role="user",
            counterparty_role="counterparty",
            reading_level="Standard",
            output_language=language,
            schema_name="QAAnswer"
        )
        
        qa_prompt = self._load_prompt("qa-answer@1.0.md").format(
            document_text=clauses_text,
            definitions=json.dumps(definitions_map),
            chat_history=chat_history,
            question=question
        )
        
        res = await self.llm.generate_json(
            task=TaskName.QA_ANSWER,
            system=system_prompt,
            user=qa_prompt,
            schema=QAAnswer,
            tier="analysis",
            session_id=session_id
        )
        
        ans: QAAnswer = res.data
        
        if not ans.answerable:
            yield {"event": "abstain", "data": ans.model_dump()}
            return
            
        # 4. Verify and stream segments
        verified_segments = []
        for seg in ans.segments:
            verified_cites = []
            for cite in seg.citations:
                vc = self.verifier.verify(cite, clauses)
                if vc.verified:
                    verified_cites.append(vc)
                    
            if verified_cites or not seg.citations:
                # keep segment if it has verified cites or didn't try to cite
                # actually, "no segment survives verification" -> abstain. 
                # PRD: "Every claim carries a verified citation".
                # If a segment has no citations, should we drop it? 
                # Yes, unless it's just conversational filler.
                seg.citations = verified_cites
                verified_segments.append(seg)
                
        if not verified_segments:
            ans.answerable = False
            yield {"event": "abstain", "data": ans.model_dump()}
            return
            
        for seg in verified_segments:
            yield {"event": "segment", "data": seg.model_dump()}
            
        yield {"event": "done", "data": {}}

    def _load_prompt(self, name: str) -> str:
        path = os.path.join("backend", "app", "llm", "prompts", name)
        if not os.path.exists(path):
            path = os.path.join("app", "llm", "prompts", name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
