import json
import os
from typing import AsyncGenerator, Dict, List, Any
from app.analysis.merge import merge_findings
from app.analysis.rules.engine import RuleEngine
from app.analysis.taxonomy import RiskCategory
from app.core.logging import get_logger
from app.llm.base import LLMClient, TaskName
from app.llm.schemas import Clause, ClauseFindingBatch, KeyFactsResult
from app.qa.citation_verifier import CitationVerifier

logger = get_logger(__name__)

class AnalysisOrchestrator:
    def __init__(self, llm_client: LLMClient, rule_engine: RuleEngine, verifier: CitationVerifier):
        self.llm = llm_client
        self.rule_engine = rule_engine
        self.verifier = verifier

    def _batch_clauses(self, clauses: List[Clause], max_chars: int = 25000) -> List[List[Clause]]:
        batches = []
        current_batch = []
        current_len = 0
        
        for c in clauses:
            l = len(c.text)
            if current_len + l > max_chars and current_batch:
                batches.append(current_batch)
                current_batch = []
                current_len = 0
            current_batch.append(c)
            current_len += l
            
        if current_batch:
            batches.append(current_batch)
        return batches

    async def run_analysis(
        self,
        session_id: str,
        clauses: List[Clause],
        doc_type: str,
        user_role: str,
        definitions_map: Dict[str, str],
        full_text: str,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        
        yield {"event": "status", "data": "Running rule engine"}
        
        rule_findings = self.rule_engine.evaluate_all(clauses, doc_type)
        
        yield {"event": "status", "data": "Analyzing key facts"}
        
        system_prompt = self._load_prompt("common@1.3.md").format(
            user_role=user_role,
            counterparty_role="counterparty",
            reading_level="Standard",
            output_language="English",
            schema_name="KeyFactsResult"
        )
        
        key_facts_prompt = self._load_prompt("key-facts@1.0.md").format(
            document_text=full_text[:40000], # truncate to fit context
            definitions=json.dumps(definitions_map),
            user_role=user_role,
            counterparty_role="counterparty"
        )
        
        kf_result = await self.llm.generate_json(
            task=TaskName.KEY_FACTS,
            system=system_prompt,
            user=key_facts_prompt,
            schema=KeyFactsResult,
            tier="analysis",
            session_id=session_id
        )
        
        # Verify citations in key facts
        verified_facts = []
        for f in kf_result.data.facts:
            if f.citation:
                f.citation = self.verifier.verify(f.citation, clauses)
            verified_facts.append(f)
        kf_result.data.facts = verified_facts
        
        verified_obs = []
        for o in kf_result.data.obligations:
            o.citation = self.verifier.verify(o.citation, clauses)
            if o.citation.verified:
                verified_obs.append(o)
        kf_result.data.obligations = verified_obs
        
        yield {"event": "key_facts", "data": kf_result.data.model_dump()}
        
        yield {"event": "status", "data": "Analyzing clauses for risks"}
        
        batches = self._batch_clauses(clauses)
        llm_findings = []
        
        tax_keys = [e.value for e in RiskCategory]
        
        for i, batch in enumerate(batches):
            yield {"event": "status", "data": f"Analyzing clause batch {i+1}/{len(batches)}"}
            
            batch_text = "\n\n".join([f"[{c.id}] {c.text}" for c in batch])
            
            ca_prompt = self._load_prompt("clause-analysis@1.3.md").format(
                document_text=batch_text,
                definitions=json.dumps(definitions_map),
                taxonomy_keys=json.dumps(tax_keys),
                law_pack="[]" # simplified
            )
            
            ca_sys = self._load_prompt("common@1.3.md").format(
                user_role=user_role,
                counterparty_role="counterparty",
                reading_level="Standard",
                output_language="English",
                schema_name="ClauseFindingBatch"
            )
            
            res = await self.llm.generate_json(
                task=TaskName.CLAUSE_ANALYSIS,
                system=ca_sys,
                user=ca_prompt,
                schema=ClauseFindingBatch,
                tier="analysis",
                session_id=session_id
            )
            
            # verify citations
            for f in res.data.findings:
                f.citation = self.verifier.verify(f.citation, clauses)
                if f.citation.verified:
                    llm_findings.append(f)
                    
        # Merge
        final_findings = merge_findings(rule_findings, llm_findings)
        
        for f in final_findings:
            yield {"event": "finding", "data": f.model_dump()}
            
        yield {"event": "status", "data": "Analysis complete"}
        yield {"event": "done", "data": {}}

    def _load_prompt(self, name: str) -> str:
        path = os.path.join("backend", "app", "llm", "prompts", name)
        if not os.path.exists(path):
            path = os.path.join("app", "llm", "prompts", name)
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
