from typing import List
from app.llm.schemas import Finding, KeyFact

def generate_markdown_brief(facts: List[KeyFact], findings: List[Finding]) -> str:
    lines = ["# Lawyer Prep Brief", ""]
    
    lines.append("## Key Facts")
    for f in facts:
        val = f.value if f.value else "Not stated"
        lines.append(f"- **{f.label}**: {val}")
        
    lines.append("")
    lines.append("## Flagged Clauses")
    
    # Sort by severity
    sev_order = {"high": 1, "medium": 2, "low": 3, "info": 4}
    sorted_findings = sorted(findings, key=lambda x: sev_order.get(x.severity, 5))
    
    for f in sorted_findings:
        lines.append(f"### {f.severity.upper()}: {f.plain_summary}")
        lines.append(f"**Why it matters:** {f.why_it_matters}")
        if f.suggested_question:
            lines.append(f"**Ask:** {f.suggested_question}")
        lines.append(f"> {f.citation.quote}")
        lines.append("")
        
    return "\n".join(lines)
