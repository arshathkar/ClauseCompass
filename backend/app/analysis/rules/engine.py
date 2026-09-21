import time
from typing import List, Optional
from app.analysis.rules.loader import RuleDef, load_rules
from app.core.logging import get_logger
from app.llm.schemas import Citation, Clause, Finding

logger = get_logger(__name__)

class RuleEngine:
    def __init__(self, rules_path: str | None = None):
        self.rules = load_rules(rules_path)
        
    def evaluate_clause(self, clause: Clause, doc_type: str) -> List[Finding]:
        findings = []
        text = clause.text
        
        # Per-clause budget (e.g. 50ms)
        start_time = time.monotonic()
        
        for rule in self.rules:
            # Check doc type applicability
            if rule.doc_types and doc_type not in rule.doc_types:
                continue
                
            # Check 'any' regexes
            matched_any = False
            match_span = None
            for rx in rule._any_regexes:
                match = rx.search(text)
                if match:
                    matched_any = True
                    match_span = match.span()
                    break
                    
            if not matched_any:
                continue
                
            # Check 'unless' regexes
            matched_unless = False
            for rx in rule._unless_regexes:
                if rx.search(text):
                    matched_unless = True
                    break
                    
            if matched_unless:
                continue
                
            # Create finding
            # For quote, just take the match up to 40 words
            quote_text = text[match_span[0]:match_span[1]]
            words = quote_text.split()
            if len(words) > 40:
                quote_text = " ".join(words[:40]) + "..."
                
            finding = Finding(
                id=f"rule-{clause.id}-{rule.id}",
                clause_id=clause.id,
                category=rule.category,
                severity=rule.severity,
                plain_summary=rule.explain,
                why_it_matters=rule.explain, # fallback
                who_is_affected="unclear", # fallback
                citation=Citation(clause_id=clause.id, quote=quote_text, verified=True),
                confidence=1.0,
                source="rule",
                rule_agreement="n/a",
                law_pack_refs=rule.law_pack_refs or []
            )
            findings.append(finding)
            
            # Enforce budget
            if (time.monotonic() - start_time) > 0.05:
                logger.warning(f"Rule engine time budget exceeded on clause {clause.id}")
                break
                
        return findings

    def evaluate_all(self, clauses: List[Clause], doc_type: str) -> List[Finding]:
        all_findings = []
        for c in clauses:
            all_findings.extend(self.evaluate_clause(c, doc_type))
        return all_findings
