import re
import json
import os

def compile_patterns():
    """Compile regex patterns for different clause formats."""
    return {
        'section': re.compile(r'^\s*§\s*\d'),
        'decimal': re.compile(r'^\s*\d+\.\d'),
        'numeric': re.compile(r'^\s*\d+[\.\)](?!\d)'),
        'roman':   re.compile(r'^\s*(?=[IVXLCDMivxlcdm]+[\.\)])[IVXLCDMivxlcdm]+[\.\)]'),
        'letter':  re.compile(r'^\s*(?:\([A-Za-z]\)|[A-Za-z][\.\)])')
    }

def count_matches(lines, patterns):
    """Count how many lines match each pattern and return a dict of counts."""
    counts = {name: 0 for name in patterns}
    for line in lines:
        for name, pattern in patterns.items():
            if pattern.match(line):
                counts[name] += 1
    return counts

def resolve_roman_letter_conflict(lines, patterns):
    """
    Distinguish between roman and letter format by examining tokens.
    Return either 'roman' or 'letter' based on multi-character tokens.
    """
    roman_chars = set("IVXLCDMivxlcdm")
    has_multi_roman = has_multi_letter = False
    for line in lines:
        if patterns['roman'].match(line) or patterns['letter'].match(line):
            token = line.strip().split()[0]
            token = token.rstrip('.)').lstrip('(')
            if len(token) > 1 and all(ch in roman_chars for ch in token):
                has_multi_roman = True
            elif len(token) > 1 and not all(ch in roman_chars for ch in token):
                has_multi_letter = True
    if has_multi_roman and not has_multi_letter:
        return 'roman'
    if has_multi_letter and not has_multi_roman:
        return 'letter'
    return None

def detect_format(lines):
    """Detect the enumeration format of the clauses by pattern matching."""
    patterns = compile_patterns()
    counts = count_matches(lines, patterns)

    # Order of priority checks
    if counts['section'] > 0:
        return 'section'
    if counts['decimal'] > 0:
        return 'decimal'
    if counts['roman'] > 0 and counts['letter'] > 0:
        conflict_resolution = resolve_roman_letter_conflict(lines, patterns)
        if conflict_resolution:
            return conflict_resolution
        # If still ambiguous, compare counts
        return 'roman' if counts['roman'] >= counts['letter'] else 'letter'
    if counts['roman'] > 0:
        return 'roman'
    if counts['letter'] > 0:
        return 'letter'
    if counts['numeric'] > 0:
        return 'numeric'
    return None

def get_header_pattern(style):
    """Return the compiled regex for the given style."""
    if style == 'numeric':
        return re.compile(r'^\s*(\d+[\.\)])')
    elif style == 'decimal':
        return re.compile(r'^\s*((?:\d+\.\d+(?:\.\d+)*|\d+\.))')
    elif style == 'roman':
        return re.compile(r'^\s*([IVXLCDMivxlcdm]+[\.\)])')
    elif style == 'letter':
        return re.compile(r'^\s*((?:\([A-Za-z]\)|[A-Za-z][\.\)]))')
    elif style == 'section':
        return re.compile(r'^\s*(§\s*\d+(?:\.\d+)*)')
    return None

def build_clause(line, match):
    """Initialize a new clause dict with ID and text from the match."""
    clause_id = match.group(1)
    content_start = match.end()
    # Remainder of the line after header
    clause_text = line[content_start:].lstrip()
    return {'id': clause_id, 'text': clause_text}

def process_line(line, current_clause):
    """Append or merge a line's text to the current_clause."""
    line_text = line.strip()
    if current_clause['text'].endswith('-'):
        # Merge hyphenated word
        current_clause['text'] = current_clause['text'][:-1] + line_text
    else:
        # Insert space for normal line break
        current_clause['text'] += ' ' + line_text

def build_decimal_hierarchy(clauses):
    """Build nested structure for decimal-style clauses."""
    clause_tree = []
    node_index = {}
    for clause in clauses:
        cid = clause['id']
        ctext = clause['text']
        node = {'id': cid, 'text': ctext}
        norm_id = cid[:-1] if cid.endswith('.') else cid
        node_index[norm_id] = node
        parent_id = None
        if '.' in norm_id:
            parent_id = norm_id.rsplit('.', 1)[0]
        if parent_id and parent_id in node_index:
            parent = node_index[parent_id]
            parent.setdefault('subclauses', []).append(node)
        else:
            clause_tree.append(node)
    return clause_tree

def extract(text):
    """
    Extract regulatory clauses from text and return a structured
    list or nested list of clauses, ready to be converted into JSON.
    """
    lines = text.splitlines()
    style = detect_format(lines)
    if not style:
        return []  # No recognizable clause format

    header_pat = get_header_pattern(style)
    clauses = []
    current_clause = None

    for line in lines:
        if not line.strip():
            continue
        match = header_pat.match(line) if header_pat else None
        if match:
            if current_clause:
                current_clause['text'] = current_clause['text'].rstrip()
                clauses.append(current_clause)
            current_clause = build_clause(line, match)
        else:
            if not current_clause:
                # Content before any recognized header is treated as noise
                continue
            process_line(line, current_clause)

    if current_clause:
        current_clause['text'] = current_clause['text'].rstrip()
        clauses.append(current_clause)

    if style == 'decimal':
        return build_decimal_hierarchy(clauses)
    return clauses

def extract_clauses(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    txt_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".txt")]

    for txt_file in txt_files:
        file_path = os.path.join(input_dir, txt_file)
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()

        clauses = extract(text)
        base_name = os.path.splitext(txt_file)[0]
        output_path = os.path.join(output_dir, f"{base_name}_clauses.json")

        with open(output_path, "w", encoding="utf-8") as out_f:
            json.dump(clauses, out_f, indent=2)