import re
from typing import Dict, List, Tuple
from app.llm.schemas import Clause, Span

L0_PATTERN = re.compile(r'^(article|section|clause|schedule|annexure|exhibit)\s+[ivxlc\d]+[.:)]?', re.IGNORECASE)
L1_PATTERN = re.compile(r'^\d{1,2}[.)]\s+\S')
L2_PATTERN = re.compile(r'^\d{1,2}\.\d{1,2}[.)]?\s+\S')
L3_PATTERN = re.compile(r'^\d{1,2}\.\d{1,2}\.\d{1,2}[.)]?\s+\S')
L4_PATTERN = re.compile(r'^\(([a-z]|[ivxlc]+|\d+)\)\s+\S', re.IGNORECASE)
H_PATTERN = re.compile(r'^[A-Z][A-Z0-9 ,&/\-]{3,60}$')

PAGE_MARKER_PATTERN = re.compile(r'^\[\[page:(\d+)\]\]$')

def is_definition_node(heading: str, text: str) -> bool:
    if heading and re.search(r'\b(definitions|interpretation)\b', heading, re.IGNORECASE):
        return True
    if re.search(r'"([^"]+)"\s+(means|shall mean|refers to)', text, re.IGNORECASE):
        return True
    return False

def build_clause_tree(sanitized_text: str) -> Tuple[List[Clause], Dict[str, str]]:
    lines = sanitized_text.split('\n')
    clauses = []
    definitions_map = {}
    
    current_clause_lines = []
    current_start = 0
    current_page = 1
    page_start = 1
    
    clause_counter = 1
    
    def finalize_clause(lines_buffer, start_idx, end_idx, c_page_start, c_page_end):
        nonlocal clause_counter
        text = '\n'.join(lines_buffer).strip()
        if not text:
            return None
            
        is_def = is_definition_node("", text)
        clause_id = f"c-{clause_counter:03d}"
        
        clause = Clause(
            id=clause_id,
            number=None, # Extracting exact number is heuristic
            heading=None, # Extracting exact heading is heuristic
            text=text,
            span=Span(start=start_idx, end=end_idx),
            pages=(c_page_start, c_page_end),
            is_definition=is_def
        )
        clause_counter += 1
        
        if is_def:
            # simple definitions extraction
            matches = re.finditer(r'"([^"]+)"\s+(means|shall mean|refers to)\s+([^.]+\.)', text, re.IGNORECASE)
            for m in matches:
                definitions_map[m.group(1).lower()] = text

        return clause

    pos = 0
    for line in lines:
        line_len = len(line) + 1 # +1 for newline
        
        page_match = PAGE_MARKER_PATTERN.match(line.strip())
        if page_match:
            current_page = int(page_match.group(1))
            pos += line_len
            continue
            
        # Basic heuristic for new clause: Matches L0-L4 or H
        is_new_clause = False
        if any(p.match(line) for p in [L0_PATTERN, L1_PATTERN, L2_PATTERN, L3_PATTERN, L4_PATTERN, H_PATTERN]):
            is_new_clause = True
            
        if is_new_clause and current_clause_lines:
            c = finalize_clause(current_clause_lines, current_start, pos, page_start, current_page)
            if c:
                clauses.append(c)
            current_clause_lines = []
            current_start = pos
            page_start = current_page
            
        current_clause_lines.append(line)
        pos += line_len
        
    if current_clause_lines:
        c = finalize_clause(current_clause_lines, current_start, pos, page_start, current_page)
        if c:
            clauses.append(c)

    # Fallback if too few clauses
    if len(clauses) < 3:
        # Fallback segmentation by blank lines
        pass # Simplified for hackathon context, but would split by \n\n
        
    return clauses, definitions_map
