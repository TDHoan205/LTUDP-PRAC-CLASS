"""
Multi-Language Code Duplication Checker
=======================================
Tool danh gia trung lap code giua 2 san pham, ho tro da ngon ngu.

Ho tro: Python, Java, JavaScript, TypeScript, C, C++, C#, Go, Ruby, PHP, Swift, Kotlin, Rust

Cach dung:
    python bainangcao.py "thu_muc_sp1" "thu_muc_sp2"
    python bainangcao.py "thu_muc_sp1" "thu_muc_sp2" --html report.html
    python bainangcao.py "thu_muc_sp1" "thu_muc_sp2" --verbose
    python bainangcao.py "thu_muc_sp1" "thu_muc_sp2" --lang python java
"""

from __future__ import annotations

import argparse
import ast
import io
import math
import os
import re
import sys
import tokenize
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Set, Tuple

# ============================================================================
# ANSI Colors (auto-detect Windows support)
# ============================================================================

def _supports_color() -> bool:
    if os.name == 'nt':
        try:
            import ctypes
            kernel32 = ctypes.windll.kernel32
            kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
            return True
        except Exception:
            return os.environ.get('TERM') == 'xterm' or 'WT_SESSION' in os.environ
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()

_COLOR = _supports_color()

class C:
    """ANSI color codes."""
    BOLD = '\033[1m' if _COLOR else ''
    DIM = '\033[2m' if _COLOR else ''
    RED = '\033[91m' if _COLOR else ''
    GREEN = '\033[92m' if _COLOR else ''
    YELLOW = '\033[93m' if _COLOR else ''
    BLUE = '\033[94m' if _COLOR else ''
    MAGENTA = '\033[95m' if _COLOR else ''
    CYAN = '\033[96m' if _COLOR else ''
    WHITE = '\033[97m' if _COLOR else ''
    RESET = '\033[0m' if _COLOR else ''
    BG_RED = '\033[41m' if _COLOR else ''
    BG_GREEN = '\033[42m' if _COLOR else ''
    BG_YELLOW = '\033[43m' if _COLOR else ''
    BG_BLUE = '\033[44m' if _COLOR else ''

# ============================================================================
# Language Detection
# ============================================================================

LANG_EXTENSIONS: Dict[str, List[str]] = {
    'python':     ['.py', '.pyw'],
    'java':       ['.java'],
    'javascript': ['.js', '.jsx', '.mjs'],
    'typescript': ['.ts', '.tsx'],
    'c':          ['.c', '.h'],
    'cpp':        ['.cpp', '.hpp', '.cc', '.cxx', '.hxx', '.hh'],
    'csharp':     ['.cs'],
    'go':         ['.go'],
    'ruby':       ['.rb'],
    'php':        ['.php'],
    'swift':      ['.swift'],
    'kotlin':     ['.kt', '.kts'],
    'rust':       ['.rs'],
}

# Reverse map: extension -> language
EXT_TO_LANG: Dict[str, str] = {}
for lang, exts in LANG_EXTENSIONS.items():
    for ext in exts:
        EXT_TO_LANG[ext] = lang

ALL_EXTENSIONS: Set[str] = set(EXT_TO_LANG.keys())

# Comment styles per language family
C_STYLE_LANGS = {'java', 'javascript', 'typescript', 'c', 'cpp', 'csharp', 'go', 'swift', 'kotlin', 'rust'}
HASH_STYLE_LANGS = {'python', 'ruby', 'php'}

# Language keywords for structural analysis
LANG_KEYWORDS: Dict[str, Set[str]] = {
    'python': {'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'try', 'except', 'finally',
               'with', 'import', 'from', 'return', 'yield', 'lambda', 'async', 'await'},
    'java': {'class', 'interface', 'enum', 'public', 'private', 'protected', 'static', 'void',
             'if', 'else', 'for', 'while', 'switch', 'case', 'try', 'catch', 'finally',
             'import', 'return', 'new', 'extends', 'implements', 'abstract', 'synchronized'},
    'javascript': {'function', 'class', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                   'switch', 'case', 'try', 'catch', 'finally', 'import', 'export', 'return',
                   'new', 'async', 'await', 'yield', 'this', 'super', 'extends'},
    'typescript': {'function', 'class', 'const', 'let', 'var', 'if', 'else', 'for', 'while',
                   'switch', 'case', 'try', 'catch', 'finally', 'import', 'export', 'return',
                   'new', 'async', 'await', 'interface', 'type', 'enum', 'extends', 'implements'},
    'c': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'return', 'struct', 'typedef',
          'enum', 'union', 'static', 'extern', 'include', 'define', 'sizeof', 'malloc', 'free'},
    'cpp': {'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'return', 'class', 'struct',
            'template', 'namespace', 'virtual', 'override', 'new', 'delete', 'try', 'catch',
            'public', 'private', 'protected', 'include', 'using'},
    'csharp': {'class', 'interface', 'struct', 'enum', 'public', 'private', 'protected', 'static',
               'void', 'if', 'else', 'for', 'foreach', 'while', 'switch', 'case', 'try', 'catch',
               'finally', 'using', 'namespace', 'return', 'new', 'async', 'await', 'override'},
    'go': {'func', 'type', 'struct', 'interface', 'if', 'else', 'for', 'switch', 'case', 'select',
           'return', 'import', 'package', 'go', 'defer', 'chan', 'map', 'range', 'make', 'new'},
    'ruby': {'def', 'class', 'module', 'if', 'elsif', 'else', 'unless', 'for', 'while', 'until',
             'do', 'begin', 'rescue', 'ensure', 'end', 'require', 'return', 'yield', 'block_given'},
    'php': {'function', 'class', 'interface', 'trait', 'if', 'elseif', 'else', 'for', 'foreach',
            'while', 'switch', 'case', 'try', 'catch', 'finally', 'use', 'namespace', 'return',
            'new', 'public', 'private', 'protected', 'static', 'require', 'include'},
    'swift': {'func', 'class', 'struct', 'enum', 'protocol', 'if', 'else', 'for', 'while',
              'switch', 'case', 'guard', 'do', 'try', 'catch', 'import', 'return', 'let', 'var'},
    'kotlin': {'fun', 'class', 'interface', 'object', 'if', 'else', 'for', 'while', 'when',
               'try', 'catch', 'finally', 'import', 'return', 'val', 'var', 'data', 'sealed'},
    'rust': {'fn', 'struct', 'enum', 'trait', 'impl', 'if', 'else', 'for', 'while', 'loop',
             'match', 'use', 'mod', 'pub', 'return', 'let', 'mut', 'async', 'await', 'unsafe'},
}

# ============================================================================
# Comment Stripping
# ============================================================================

def strip_c_style_comments(source: str) -> str:
    """Remove // and /* */ comments from C-style languages."""
    result = []
    i, n = 0, len(source)
    in_string = None
    while i < n:
        ch = source[i]
        if in_string:
            result.append(ch)
            if ch == '\\' and i + 1 < n:
                i += 1
                result.append(source[i])
            elif ch == in_string:
                in_string = None
        elif ch in ('"', "'", '`'):
            in_string = ch
            result.append(ch)
        elif ch == '/' and i + 1 < n:
            if source[i + 1] == '/':
                while i < n and source[i] != '\n':
                    i += 1
                continue
            elif source[i + 1] == '*':
                i += 2
                while i + 1 < n and not (source[i] == '*' and source[i + 1] == '/'):
                    i += 1
                i += 2
                continue
            else:
                result.append(ch)
        else:
            result.append(ch)
        i += 1
    return ''.join(result)


def strip_python_comments(source: str) -> str:
    """Remove comments and docstrings from Python source."""
    out = []
    try:
        tok_gen = tokenize.generate_tokens(io.StringIO(source).readline)
        prev_toktype = tokenize.INDENT
        last_lineno, last_col = -1, 0
        for tok_type, tok_string, (sline, scol), (eline, ecol), _ in tok_gen:
            if sline > last_lineno:
                last_col = 0
            if scol > last_col:
                out.append(' ' * (scol - last_col))
            if tok_type == tokenize.COMMENT:
                pass
            elif tok_type == tokenize.STRING and prev_toktype in {
                tokenize.INDENT, tokenize.NEWLINE, tokenize.DEDENT, tokenize.NL}:
                pass
            else:
                out.append(tok_string)
            prev_toktype = tok_type
            last_col = ecol
            last_lineno = eline
        return ''.join(out)
    except Exception:
        # Fallback to simple regex for comment stripping if tokenize fails
        return re.sub(r'#.*', '', source)


def strip_ruby_comments(source: str) -> str:
    """Remove # comments and =begin...=end blocks from Ruby."""
    lines = source.split('\n')
    result, in_block = [], False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('=begin'):
            in_block = True
            continue
        if stripped.startswith('=end'):
            in_block = False
            continue
        if in_block:
            continue
        idx = line.find('#')
        if idx >= 0:
            in_str = False
            str_char = None
            clean_idx = len(line)
            for j, c in enumerate(line):
                if in_str:
                    if c == '\\':
                        continue
                    if c == str_char:
                        in_str = False
                elif c in ('"', "'"):
                    in_str = True
                    str_char = c
                elif c == '#':
                    clean_idx = j
                    break
            result.append(line[:clean_idx])
        else:
            result.append(line)
    return '\n'.join(result)


def strip_comments(source: str, lang: str) -> str:
    """Strip comments based on language."""
    if lang == 'python':
        return strip_python_comments(source)
    if lang == 'ruby':
        return strip_ruby_comments(source)
    if lang in C_STYLE_LANGS:
        return strip_c_style_comments(source)
    if lang == 'php':
        source = strip_c_style_comments(source)
        lines = []
        for line in source.split('\n'):
            idx = line.find('#')
            if idx >= 0:
                lines.append(line[:idx])
            else:
                lines.append(line)
        return '\n'.join(lines)
    return source

# ============================================================================
# Tokenization
# ============================================================================

def simple_tokenize(code: str) -> List[str]:
    """Universal tokenizer for all languages."""
    return re.findall(r'[A-Za-z_]\w*|\d+(?:\.\d+)?|==|!=|<=|>=|=>|->|&&|\|\||<<|>>|[-+*/%(){}[\],.:;!&|^~<>?@#]', code)

# ============================================================================
# Structure Analysis (Pattern-based, works for all languages)
# ============================================================================

# Regex patterns to detect structural elements
STRUCT_PATTERNS: Dict[str, List[Tuple[str, str]]] = {
    'python': [
        ('FUNC_DEF', r'\bdef\s+\w+\s*\('),
        ('CLASS_DEF', r'\bclass\s+\w+'),
        ('IF', r'\bif\s+'), ('ELIF', r'\belif\s+'), ('ELSE', r'\belse\s*:'),
        ('FOR', r'\bfor\s+'), ('WHILE', r'\bwhile\s+'),
        ('TRY', r'\btry\s*:'), ('EXCEPT', r'\bexcept\b'),
        ('WITH', r'\bwith\s+'), ('IMPORT', r'\b(?:import|from)\s+'),
        ('RETURN', r'\breturn\b'), ('YIELD', r'\byield\b'),
        ('LAMBDA', r'\blambda\b'), ('LIST_COMP', r'\[.*\bfor\b.*\bin\b'),
        ('DECORATOR', r'@\w+'),
    ],
    '_c_family': [
        ('FUNC_DEF', r'\b\w+\s+\w+\s*\([^)]*\)\s*\{'),
        ('CLASS_DEF', r'\bclass\s+\w+'),
        ('IF', r'\bif\s*\('), ('ELSE', r'\belse\b'),
        ('FOR', r'\bfor\s*\('), ('WHILE', r'\bwhile\s*\('),
        ('SWITCH', r'\bswitch\s*\('), ('CASE', r'\bcase\s+'),
        ('TRY', r'\btry\s*\{'), ('CATCH', r'\bcatch\s*\('),
        ('RETURN', r'\breturn\b'), ('NEW', r'\bnew\s+\w+'),
        ('IMPORT', r'\b(?:import|include|using|require)\b'),
        ('INTERFACE', r'\binterface\s+\w+'),
    ],
    'go': [
        ('FUNC_DEF', r'\bfunc\s+'), ('STRUCT_DEF', r'\btype\s+\w+\s+struct\b'),
        ('INTERFACE_DEF', r'\btype\s+\w+\s+interface\b'),
        ('IF', r'\bif\s+'), ('ELSE', r'\belse\b'),
        ('FOR', r'\bfor\s+'), ('SWITCH', r'\bswitch\b'),
        ('SELECT', r'\bselect\b'), ('GOROUTINE', r'\bgo\s+\w+'),
        ('DEFER', r'\bdefer\s+'), ('RETURN', r'\breturn\b'),
        ('IMPORT', r'\bimport\b'), ('CHANNEL', r'\bchan\b'),
    ],
    'ruby': [
        ('FUNC_DEF', r'\bdef\s+\w+'), ('CLASS_DEF', r'\bclass\s+\w+'),
        ('MODULE_DEF', r'\bmodule\s+\w+'),
        ('IF', r'\bif\b'), ('UNLESS', r'\bunless\b'), ('ELSE', r'\belse\b'),
        ('FOR', r'\bfor\b'), ('WHILE', r'\bwhile\b'),
        ('BEGIN', r'\bbegin\b'), ('RESCUE', r'\brescue\b'),
        ('RETURN', r'\breturn\b'), ('YIELD', r'\byield\b'),
        ('REQUIRE', r'\brequire\b'), ('BLOCK', r'\bdo\s*\|'),
    ],
    'rust': [
        ('FUNC_DEF', r'\bfn\s+\w+'), ('STRUCT_DEF', r'\bstruct\s+\w+'),
        ('ENUM_DEF', r'\benum\s+\w+'), ('TRAIT_DEF', r'\btrait\s+\w+'),
        ('IMPL', r'\bimpl\b'), ('IF', r'\bif\b'), ('ELSE', r'\belse\b'),
        ('FOR', r'\bfor\b'), ('WHILE', r'\bwhile\b'), ('LOOP', r'\bloop\b'),
        ('MATCH', r'\bmatch\b'), ('RETURN', r'\breturn\b'),
        ('USE', r'\buse\s+'), ('UNSAFE', r'\bunsafe\b'),
    ],
}

def _get_patterns(lang: str) -> List[Tuple[str, str]]:
    if lang in STRUCT_PATTERNS:
        return STRUCT_PATTERNS[lang]
    if lang in C_STYLE_LANGS:
        return STRUCT_PATTERNS['_c_family']
    if lang == 'ruby':
        return STRUCT_PATTERNS['ruby']
    return STRUCT_PATTERNS['_c_family']


def extract_structural_features(source: str, lang: str) -> Counter:
    """Extract structural feature counts from source code."""
    features = Counter()
    patterns = _get_patterns(lang)
    for feat_name, pattern in patterns:
        matches = re.findall(pattern, source)
        if matches:
            features[feat_name] = len(matches)
    keywords = LANG_KEYWORDS.get(lang, set())
    tokens = simple_tokenize(source)
    for t in tokens:
        if t in keywords:
            features[f'KW_{t}'] += 1
    features['TOTAL_LINES'] = source.count('\n') + 1
    features['TOTAL_TOKENS'] = len(tokens)
    return features

# ============================================================================
# Python AST Analysis (enhanced, kept for Python files)
# ============================================================================

class ASTNormalizer(ast.NodeTransformer):
    def visit_Name(self, node): return ast.copy_location(ast.Name(id='VAR', ctx=node.ctx), node)
    def visit_arg(self, node): node.arg = 'ARG'; return self.generic_visit(node)
    def visit_FunctionDef(self, node): node.name = 'FUNC'; return self.generic_visit(node)
    def visit_AsyncFunctionDef(self, node): node.name = 'FUNC'; return self.generic_visit(node)
    def visit_ClassDef(self, node): node.name = 'CLASS'; return self.generic_visit(node)
    def visit_Constant(self, node):
        v = 'STR' if isinstance(node.value, str) else 0 if isinstance(node.value, (int,float,complex)) else b'' if isinstance(node.value, bytes) else node.value
        return ast.copy_location(ast.Constant(value=v), node)


def python_ast_tokens(source: str) -> Tuple[List[str], Counter]:
    try:
        tree = ast.parse(source)
        norm = ASTNormalizer().visit(tree)
        ast.fix_missing_locations(norm)
        types = [type(n).__name__ for n in ast.walk(norm)]
        try:
            code = ast.unparse(norm)
        except Exception:
            code = '\n'.join(types)
        return simple_tokenize(code), Counter(types)
    except Exception:
        return [], Counter()


def generic_normalize(source: str, lang: str) -> List[str]:
    """Normalize identifiers and literals for non-Python languages."""
    tokens = simple_tokenize(source)
    keywords = LANG_KEYWORDS.get(lang, set())
    result = []
    for t in tokens:
        if t in keywords:
            result.append(t)
        elif re.match(r'^[A-Za-z_]\w*$', t):
            result.append('ID')
        elif re.match(r'^\d', t):
            result.append('NUM')
        else:
            result.append(t)
    return result

# ============================================================================
# File Profile
# ============================================================================

@dataclass
class FileProfile:
    path: Path
    rel_path: str
    lang: str
    raw_text: str
    clean_tokens: List[str]
    norm_tokens: List[str]
    features: Counter


def profile_file(path: Path, root: Path, lang: str) -> FileProfile:
    text = path.read_text(encoding='utf-8', errors='ignore')
    clean = strip_comments(text, lang)
    clean_tokens = simple_tokenize(clean)

    if lang == 'python':
        norm_tokens, feat = python_ast_tokens(clean)
        feat.update(extract_structural_features(clean, lang))
    else:
        norm_tokens = generic_normalize(clean, lang)
        feat = extract_structural_features(clean, lang)

    return FileProfile(
        path=path, rel_path=str(path.relative_to(root)).replace(os.sep, '/'),
        lang=lang, raw_text=text, clean_tokens=clean_tokens,
        norm_tokens=norm_tokens, features=feat,
    )

# ============================================================================
# Similarity Engine
# ============================================================================

def build_shingles(tokens: Sequence[str], k: int = 5) -> Set[Tuple[str, ...]]:
    if len(tokens) < k:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i:i+k]) for i in range(len(tokens) - k + 1)}


def jaccard(a: Set, b: Set) -> float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)


def cosine_counter(c1: Counter, c2: Counter) -> float:
    if not c1 and not c2: return 1.0
    if not c1 or not c2: return 0.0
    keys = set(c1) | set(c2)
    dot = sum(c1[k] * c2[k] for k in keys)
    n1 = math.sqrt(sum(v*v for v in c1.values()))
    n2 = math.sqrt(sum(v*v for v in c2.values()))
    return dot / (n1 * n2) if n1 and n2 else 0.0


def best_match_scores(files_a: Sequence[FileProfile], files_b: Sequence[FileProfile]) -> Tuple[float, float, List[Tuple[str, str, str, float, float]]]:
    if not files_a or not files_b:
        return 0.0, 0.0, []

    # Map shingles to list of file indices in B
    clean_indices_b: Dict[Tuple[str, ...], List[int]] = {}
    norm_indices_b: Dict[Tuple[str, ...], List[int]] = {}

    sh_clean_b = [build_shingles(f.clean_tokens) for f in files_b]
    sh_norm_b = [build_shingles(f.norm_tokens) for f in files_b]

    for idx, sh_set in enumerate(sh_clean_b):
        for s in sh_set:
            clean_indices_b.setdefault(s, []).append(idx)
    for idx, sh_set in enumerate(sh_norm_b):
        for s in sh_set:
            norm_indices_b.setdefault(s, []).append(idx)

    total_w = sum(max(1, len(f.clean_tokens)) for f in files_a)
    w_lex = w_struct = 0.0
    rows = []

    for fa in files_a:
        sa_clean = build_shingles(fa.clean_tokens)
        sa_norm = build_shingles(fa.norm_tokens)

        # Candidate selection: only check files that share at least one shingle
        candidates = set()
        for s in sa_clean:
            if s in clean_indices_b:
                candidates.update(clean_indices_b[s])
        for s in sa_norm:
            if s in norm_indices_b:
                candidates.update(norm_indices_b[s])

        # If no candidates share any shingles, similarity is 0
        if not candidates:
            # Still pick the first file as a dummy placeholder if needed, 
            # but usually we want a real match. Let's find index 0.
            best_l = best_s = 0.0
            best_idx = 0
        else:
            best_l = best_s = -1.0
            best_idx = 0
            # Only compare against candidates
            for idx in candidates:
                fb = files_b[idx]
                # Optional: Skip if languages are totally different and not compatible
                # But for now, we follow the user's "check plagiarism" which might be cross-project
                jl = jaccard(sa_clean, sh_clean_b[idx])
                js = jaccard(sa_norm, sh_norm_b[idx])
                if (jl + js) / 2 > (best_l + best_s) / 2:
                    best_l, best_s, best_idx = jl, js, idx

        w = max(1, len(fa.clean_tokens))
        w_lex += w * max(best_l, 0)
        w_struct += w * max(best_s, 0)
        fb = files_b[best_idx]
        rows.append((fa.rel_path, fb.rel_path, fa.lang, max(best_l, 0), max(best_s, 0)))

    rows.sort(key=lambda x: x[3] + x[4], reverse=True)
    return w_lex / total_w, w_struct / total_w, rows[:15]

# ============================================================================
# Report Generator
# ============================================================================

def progress_bar(pct: float, width: int = 25) -> str:
    filled = int(pct / 100 * width)
    bar = '█' * filled + '░' * (width - filled)
    if pct >= 75:
        color = C.RED
    elif pct >= 40:
        color = C.YELLOW
    else:
        color = C.GREEN
    return f'{color}{bar}{C.RESET} {pct:.1f}%'


def severity_color(pct: float) -> str:
    if pct >= 75: return C.RED
    if pct >= 40: return C.YELLOW
    return C.GREEN


def verdict(lex: float, struct: float, strategy: float) -> str:
    if lex >= 80 and struct >= 80:
        return f'{C.RED}⚠ NGUY CO CAO: Co kha nang copy truc tiep code!{C.RESET}'
    if struct >= 75 and lex < 60:
        return f'{C.RED}⚠ Cau truc rat giong: Co dau hieu doi ten bien/refactor lai code.{C.RESET}'
    if lex >= 55 or struct >= 55:
        return f'{C.YELLOW}⚡ Trung lap dang ke: Can review thu cong cac cap file.{C.RESET}'
    if strategy >= 65:
        return f'{C.YELLOW}⚡ Cach giai quyet tuong tu o muc trung binh-cao.{C.RESET}'
    return f'{C.GREEN}✓ Muc trung lap thap, khong co dau hieu copy ro rang.{C.RESET}'


def print_box(title: str, content_lines: List[str]) -> None:
    max_w = max(len(re.sub(r'\033\[[0-9;]*m', '', l)) for l in [title] + content_lines) + 4
    max_w = max(max_w, 60)
    print(f'\n{C.CYAN}╔{"═" * max_w}╗{C.RESET}')
    pad = max_w - len(re.sub(r'\033\[[0-9;]*m', '', title))
    print(f'{C.CYAN}║{C.RESET} {C.BOLD}{title}{C.RESET}{" " * (pad - 1)}{C.CYAN}║{C.RESET}')
    print(f'{C.CYAN}╠{"═" * max_w}╣{C.RESET}')
    for line in content_lines:
        vis_len = len(re.sub(r'\033\[[0-9;]*m', '', line))
        pad = max_w - vis_len - 1
        print(f'{C.CYAN}║{C.RESET} {line}{" " * max(pad, 0)}{C.CYAN}║{C.RESET}')
    print(f'{C.CYAN}╚{"═" * max_w}╝{C.RESET}')


def print_report(root_a, root_b, files_a, files_b, lex_pct, struct_pct, strategy_pct,
                 top_a2b, top_b2a, lang_stats, verbose=False):
    print(f'\n{C.BOLD}{C.CYAN}{"=" * 72}{C.RESET}')
    print(f'{C.BOLD}{C.WHITE}  🔍 MULTI-LANGUAGE CODE DUPLICATION CHECKER{C.RESET}')
    print(f'{C.BOLD}{C.CYAN}{"=" * 72}{C.RESET}')

    info = [
        f'{C.BOLD}San pham 1:{C.RESET} {C.WHITE}{root_a}{C.RESET}',
        f'{C.BOLD}San pham 2:{C.RESET} {C.WHITE}{root_b}{C.RESET}',
        f'{C.BOLD}Tong file SP1:{C.RESET} {len(files_a)}    {C.BOLD}Tong file SP2:{C.RESET} {len(files_b)}',
        '',
        f'{C.BOLD}Ngon ngu phat hien:{C.RESET}',
    ]
    for lang, (c1, c2) in sorted(lang_stats.items()):
        icon = '🐍' if lang == 'python' else '☕' if lang == 'java' else '📜' if lang in ('javascript','typescript') else '⚙'
        info.append(f'  {icon} {lang:12s}: SP1={c1} files, SP2={c2} files')
    print_box('THONG TIN CHUNG', info)

    results = [
        f'{C.BOLD}1) Trung lap code (lexical):{C.RESET}     {progress_bar(lex_pct)}',
        f'{C.BOLD}2) Trung lap cau truc (structural):{C.RESET} {progress_bar(struct_pct)}',
        f'{C.BOLD}3) Giong cach giai quyet (strategy):{C.RESET} {progress_bar(strategy_pct)}',
        '',
        verdict(lex_pct, struct_pct, strategy_pct),
    ]
    print_box('KET QUA DANH GIA', results)

    if top_a2b:
        rows = []
        for fa, fb, lang, l, s in top_a2b[:10]:
            sc = severity_color(max(l, s) * 100)
            rows.append(f'  {sc}{fa}{C.RESET}  ↔  {sc}{fb}{C.RESET}  [{lang}]')
            rows.append(f'    Lexical={l*100:.1f}%  Structural={s*100:.1f}%')
        print_box('TOP CAP FILE GIONG NHAU (SP1 → SP2)', rows)

    if verbose and top_b2a:
        rows = []
        for fb, fa, lang, l, s in top_b2a[:10]:
            sc = severity_color(max(l, s) * 100)
            rows.append(f'  {sc}{fb}{C.RESET}  ↔  {sc}{fa}{C.RESET}  [{lang}]')
            rows.append(f'    Lexical={l*100:.1f}%  Structural={s*100:.1f}%')
        print_box('TOP CAP FILE GIONG NHAU (SP2 → SP1)', rows)

    print(f'\n{C.BOLD}{C.CYAN}{"=" * 72}{C.RESET}\n')

# ============================================================================
# HTML Report
# ============================================================================

def generate_html(root_a, root_b, files_a, files_b, lex_pct, struct_pct, strategy_pct,
                  top_a2b, top_b2a, lang_stats, output_path):
    def bar_html(pct):
        color = '#ef4444' if pct >= 75 else '#eab308' if pct >= 40 else '#22c55e'
        return f'<div style="background:#1e293b;border-radius:8px;overflow:hidden;height:28px;position:relative"><div style="background:{color};height:100%;width:{pct:.1f}%;border-radius:8px"></div><span style="position:absolute;right:10px;top:4px;color:#fff;font-weight:600">{pct:.1f}%</span></div>'

    rows_html = ''
    for fa, fb, lang, l, s in top_a2b[:15]:
        avg = (l + s) / 2 * 100
        color = '#ef4444' if avg >= 60 else '#eab308' if avg >= 30 else '#22c55e'
        rows_html += f'<tr><td>{fa}</td><td>{fb}</td><td><span style="background:#1e293b;padding:2px 8px;border-radius:4px;color:#94a3b8">{lang}</span></td><td style="color:{color};font-weight:600">{l*100:.1f}%</td><td style="color:{color};font-weight:600">{s*100:.1f}%</td></tr>'

    lang_rows = ''
    for lang, (c1, c2) in sorted(lang_stats.items()):
        lang_rows += f'<tr><td style="text-transform:capitalize">{lang}</td><td>{c1}</td><td>{c2}</td></tr>'

    html = f'''<!DOCTYPE html><html lang="vi"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Code Duplication Report</title>
<style>*{{margin:0;padding:0;box-sizing:border-box}}body{{font-family:'Segoe UI',system-ui,sans-serif;background:#0f172a;color:#e2e8f0;padding:40px 20px}}
.container{{max-width:960px;margin:0 auto}}.card{{background:#1e293b;border-radius:12px;padding:24px;margin-bottom:24px;border:1px solid #334155}}
h1{{font-size:28px;text-align:center;margin-bottom:8px;color:#38bdf8}}h2{{font-size:18px;color:#94a3b8;margin-bottom:16px;border-bottom:1px solid #334155;padding-bottom:8px}}
.subtitle{{text-align:center;color:#64748b;margin-bottom:32px}}
table{{width:100%;border-collapse:collapse}}th,td{{padding:10px 12px;text-align:left;border-bottom:1px solid #334155}}th{{color:#94a3b8;font-size:13px;text-transform:uppercase}}
.metric{{margin-bottom:16px}}.metric-label{{font-weight:600;margin-bottom:6px;color:#cbd5e1}}
.verdict{{padding:16px;border-radius:8px;font-weight:600;text-align:center;margin-top:16px}}
.info-grid{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}.info-item{{background:#0f172a;padding:12px;border-radius:8px}}.info-label{{color:#64748b;font-size:13px}}.info-value{{font-size:16px;font-weight:600;color:#f1f5f9}}</style></head>
<body><div class="container">
<h1>🔍 Code Duplication Report</h1><p class="subtitle">Multi-Language Code Duplication Analysis</p>
<div class="card"><h2>Thong Tin Chung</h2><div class="info-grid">
<div class="info-item"><div class="info-label">San pham 1</div><div class="info-value">{root_a}</div></div>
<div class="info-item"><div class="info-label">San pham 2</div><div class="info-value">{root_b}</div></div>
<div class="info-item"><div class="info-label">So file SP1</div><div class="info-value">{len(files_a)}</div></div>
<div class="info-item"><div class="info-label">So file SP2</div><div class="info-value">{len(files_b)}</div></div>
</div><h2 style="margin-top:16px">Ngon Ngu</h2><table>{lang_rows}</table></div>
<div class="card"><h2>Ket Qua Danh Gia</h2>
<div class="metric"><div class="metric-label">Trung lap code (Lexical)</div>{bar_html(lex_pct)}</div>
<div class="metric"><div class="metric-label">Trung lap cau truc (Structural)</div>{bar_html(struct_pct)}</div>
<div class="metric"><div class="metric-label">Giong cach giai quyet (Strategy)</div>{bar_html(strategy_pct)}</div>
</div>
<div class="card"><h2>Top Cap File Giong Nhau</h2><table><thead><tr><th>File SP1</th><th>File SP2</th><th>Lang</th><th>Lexical</th><th>Structural</th></tr></thead><tbody>{rows_html}</tbody></table></div>
</div></body></html>'''
    Path(output_path).write_text(html, encoding='utf-8')
    print(f'{C.GREEN}✓ Da xuat bao cao HTML: {output_path}{C.RESET}')

# ============================================================================
# Main
# ============================================================================

def find_code_files(root: Path, lang_filter: Optional[List[str]] = None) -> List[Tuple[Path, str]]:
    exclude_dirs = {'.venv', 'venv', 'node_modules', '__pycache__', '.git', '.vscode', 'dist', 'build', 'env'}
    exts = set()
    if lang_filter:
        for lang in lang_filter:
            lang = lang.lower()
            if lang in LANG_EXTENSIONS:
                exts.update(LANG_EXTENSIONS[lang])
    else:
        exts = ALL_EXTENSIONS

    result = []
    # Use os.walk for better control over excluding directories
    for dirpath, dirnames, filenames in os.walk(root):
        # Filter directories in-place to skip recursion
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

        current_path = Path(dirpath)
        for f in filenames:
            ext = os.path.splitext(f)[1].lower()
            if ext in exts:
                lang = EXT_TO_LANG.get(ext, 'unknown')
                result.append((current_path / f, lang))

    return sorted(result)


def validate_dir(s: str) -> Path:
    p = Path(s).expanduser().resolve()
    if not p.exists() or not p.is_dir():
        raise argparse.ArgumentTypeError(f'Thu muc khong hop le: {s}')
    return p


def main() -> None:
    parser = argparse.ArgumentParser(
        description='🔍 Multi-Language Code Duplication Checker - So sanh trung lap code toan dien',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Vi du:
  python bainangcao.py ./project_a ./project_b
  python bainangcao.py ./sp1 ./sp2 --html report.html
  python bainangcao.py ./sp1 ./sp2 --lang python java --verbose

Ho tro: Python, Java, JavaScript, TypeScript, C, C++, C#, Go, Ruby, PHP, Swift, Kotlin, Rust''',
    )
    parser.add_argument('product_a', type=validate_dir, help='Duong dan thu muc san pham A')
    parser.add_argument('product_b', type=validate_dir, help='Duong dan thu muc san pham B')
    parser.add_argument('--lang', nargs='+', metavar='LANG', help='Loc theo ngon ngu (vd: python java)')
    parser.add_argument('--html', metavar='FILE', help='Xuat bao cao HTML ra file')
    parser.add_argument('--verbose', '-v', action='store_true', help='Hien thi chi tiet')
    args = parser.parse_args()

    print(f'\n{C.DIM}Dang quet file...{C.RESET}')
    fp_a = find_code_files(args.product_a, args.lang)
    fp_b = find_code_files(args.product_b, args.lang)

    if not fp_a or not fp_b:
        print(f'{C.RED}Khong du file code de so sanh (mot trong hai thu muc rong hoac khong co file phu hop).{C.RESET}')
        return

    lang_stats: Dict[str, List[int]] = {}
    for _, lang in fp_a:
        lang_stats.setdefault(lang, [0, 0])
        lang_stats[lang][0] += 1
    for _, lang in fp_b:
        lang_stats.setdefault(lang, [0, 0])
        lang_stats[lang][1] += 1
    lang_stats_tuples = {k: tuple(v) for k, v in lang_stats.items()}

    print(f'{C.DIM}Dang phan tich {len(fp_a)} + {len(fp_b)} files...{C.RESET}')
    files_a = [profile_file(p, args.product_a, lang) for p, lang in fp_a]
    files_b = [profile_file(p, args.product_b, lang) for p, lang in fp_b]

    lex_a2b, struct_a2b, top_a2b = best_match_scores(files_a, files_b)
    lex_b2a, struct_b2a, top_b2a = best_match_scores(files_b, files_a)

    lex_pct = ((lex_a2b + lex_b2a) / 2) * 100
    struct_pct = ((struct_a2b + struct_b2a) / 2) * 100

    feat_a, feat_b = Counter(), Counter()
    for f in files_a: feat_a.update(f.features)
    for f in files_b: feat_b.update(f.features)
    strategy_pct = cosine_counter(feat_a, feat_b) * 100

    print_report(args.product_a, args.product_b, files_a, files_b,
                 lex_pct, struct_pct, strategy_pct, top_a2b, top_b2a,
                 lang_stats_tuples, args.verbose)

    if args.html:
        generate_html(args.product_a, args.product_b, files_a, files_b,
                      lex_pct, struct_pct, strategy_pct, top_a2b, top_b2a,
                      lang_stats_tuples, args.html)


if __name__ == '__main__':
    main()
