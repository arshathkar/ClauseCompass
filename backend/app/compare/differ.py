import difflib
from typing import List, Tuple, Literal

def compute_diff(text_a: str, text_b: str) -> List[Tuple[Literal["eq", "ins", "del"], str]]:
    matcher = difflib.SequenceMatcher(None, text_a, text_b)
    ops = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            ops.append(("eq", text_a[i1:i2]))
        elif tag == 'insert':
            ops.append(("ins", text_b[j1:j2]))
        elif tag == 'delete':
            ops.append(("del", text_a[i1:i2]))
        elif tag == 'replace':
            ops.append(("del", text_a[i1:i2]))
            ops.append(("ins", text_b[j1:j2]))
            
    return ops
