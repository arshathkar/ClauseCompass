import re
from typing import Dict, List, Set, Tuple
from pydantic import BaseModel

from app.privacy.patterns import load_patterns, PII_Pattern


class RedactionItem(BaseModel):
    id: str
    type: str
    original_value: str
    placeholder: str
    is_active: bool = True
    start: int
    end: int


class Redactor:
    def __init__(self, patterns_yaml_path: str | None = None):
        self.patterns = load_patterns(patterns_yaml_path)
        
    def detect_and_mask(self, text: str, custom_terms: List[str] = None) -> Tuple[str, List[RedactionItem], Dict[str, str]]:
        if custom_terms is None:
            custom_terms = []
            
        custom_terms = sorted(custom_terms, key=len, reverse=True)
        items: List[RedactionItem] = []
        placeholder_map: Dict[str, str] = {}
        type_counters: Dict[str, int] = {}
        
        def get_placeholder(ptype: str, val: str) -> str:
            val_norm = val.lower().strip()
            # If we already have a placeholder for this exact value, reuse it
            for item in items:
                if item.original_value.lower().strip() == val_norm and item.type == ptype:
                    return item.placeholder
            
            count = type_counters.get(ptype, 0) + 1
            type_counters[ptype] = count
            return f"[[{ptype}_{count}]]"

        # 1. Custom terms
        for term in custom_terms:
            if not term.strip():
                continue
            # simple regex escape and find
            escaped = re.escape(term)
            for match in re.finditer(escaped, text, re.IGNORECASE):
                val = match.group(0)
                placeholder = get_placeholder("CUSTOM", val)
                items.append(RedactionItem(
                    id=f"redact-{len(items)}",
                    type="CUSTOM",
                    original_value=val,
                    placeholder=placeholder,
                    start=match.start(),
                    end=match.end()
                ))
                
        # 2. Pattern-based detection
        for pattern in self.patterns:
            for match in pattern.regex.finditer(text):
                val = match.group(pattern.group)
                start = match.start(pattern.group)
                end = match.end(pattern.group)
                
                # Check validator
                if pattern.validator and not pattern.validator(val):
                    continue
                    
                # Check overlap
                overlap = False
                for item in items:
                    if not (end <= item.start or start >= item.end):
                        # Overlap logic: custom wins, else longer match wins
                        if item.type == "CUSTOM":
                            overlap = True
                            break
                        elif (end - start) <= (item.end - item.start):
                            overlap = True
                            break
                        else:
                            # We are longer, remove the shorter one
                            item.is_active = False # Mark for removal later
                
                if not overlap:
                    placeholder = get_placeholder(pattern.name, val)
                    items.append(RedactionItem(
                        id=f"redact-{len(items)}",
                        type=pattern.name,
                        original_value=val,
                        placeholder=placeholder,
                        start=start,
                        end=end
                    ))

        # Filter out inactive items (overridden by longer matches)
        items = [i for i in items if i.is_active]
        
        # Build masked text (right-to-left to not mess up indices)
        masked_text = text
        sorted_items = sorted(items, key=lambda x: x.start, reverse=True)
        
        for item in sorted_items:
            masked_text = masked_text[:item.start] + item.placeholder + masked_text[item.end:]
            placeholder_map[item.placeholder] = item.original_value
            
        return masked_text, sorted_items, placeholder_map

    def apply_toggles(self, text: str, items: List[RedactionItem]) -> Tuple[str, Dict[str, str]]:
        # This takes the original text and reapplies only active items
        active_items = [i for i in items if i.is_active]
        sorted_items = sorted(active_items, key=lambda x: x.start, reverse=True)
        
        masked_text = text
        placeholder_map = {}
        for item in sorted_items:
            masked_text = masked_text[:item.start] + item.placeholder + masked_text[item.end:]
            placeholder_map[item.placeholder] = item.original_value
            
        return masked_text, placeholder_map
