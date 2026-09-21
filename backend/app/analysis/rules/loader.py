import re
from typing import List, Optional
import yaml
from pydantic import BaseModel


class RuleDef(BaseModel):
    id: str
    category: str
    doc_types: Optional[List[str]] = None
    severity: str
    any: List[str]
    unless: Optional[List[str]] = None
    explain: str
    law_pack_refs: Optional[List[str]] = None
    
    # Compiled regexes (will be set after loading)
    _any_regexes: List[re.Pattern] = []
    _unless_regexes: List[re.Pattern] = []


def load_rules(yaml_path: str | None = None) -> List[RuleDef]:
    if yaml_path is None:
        from app.core.settings import settings
        yaml_path = str(settings.data_dir / "risk_rules.yaml")
    with open(yaml_path, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
        
    rules = []
    for r in data.get('rules', []):
        rule = RuleDef(**r)
        
        any_rx = []
        for pat in rule.any:
            if pat.startswith('(?is)'):
                any_rx.append(re.compile(pat[5:], re.IGNORECASE | re.DOTALL))
            else:
                any_rx.append(re.compile(pat))
        rule._any_regexes = any_rx
        
        unless_rx = []
        if rule.unless:
            for pat in rule.unless:
                if pat.startswith('(?is)'):
                    unless_rx.append(re.compile(pat[5:], re.IGNORECASE | re.DOTALL))
                else:
                    unless_rx.append(re.compile(pat))
        rule._unless_regexes = unless_rx
        
        rules.append(rule)
        
    return rules
