"""
Tool danh gia trung lap code giua 2 san pham Python.

Yeu cau:
- Nhap vao 2 thu muc chua source code Python.
- Danh gia % trung lap code tong quan.
- Danh gia muc do trung lap cach giai quyet/cach code (dua tren cau truc AST).

Cach dung:
    python bainangcao.py <thu_muc_sp1> <thu_muc_sp2>

Vi du:
    python bainangcao.py D:/sanphamA D:/sanphamB
"""

from __future__ import annotations

import argparse
import ast
import io
import math
import os
import re
import tokenize
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple


@dataclass
class FileProfile:
    path: Path
    rel_path: str
    raw_text: str
    clean_tokens: List[str]
    ast_tokens: List[str]
    feature_counter: Counter


def find_python_files(root: Path) -> List[Path]:
    files = [p for p in root.rglob("*.py") if p.is_file()]
    return sorted(files)


def remove_comments_and_docstrings(source: str) -> str:
    """Loai bo comment va docstring, giu lai code de so sanh textual cong bang hon."""
    out_tokens = []
    try:
        tok_gen = tokenize.generate_tokens(io.StringIO(source).readline)
    except tokenize.TokenError:
        return source

    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0

    for tok_type, tok_string, (sline, scol), (eline, ecol), _ in tok_gen:
        if sline > last_lineno:
            last_col = 0
        if scol > last_col:
            out_tokens.append(" " * (scol - last_col))

        if tok_type == tokenize.COMMENT:
            pass
        elif tok_type == tokenize.STRING and prev_toktype in {
            tokenize.INDENT,
            tokenize.NEWLINE,
            tokenize.DEDENT,
            tokenize.NL,
        }:
            pass
        else:
            out_tokens.append(tok_string)

        prev_toktype = tok_type
        last_col = ecol
        last_lineno = eline

    return "".join(out_tokens)


def simple_tokenize(code: str) -> List[str]:
    """Token hoa don gian de tinh trung lap lexical."""
    return re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+|==|!=|<=|>=|[-+*/%(){}\[\],.:]", code)


class ASTNormalizer(ast.NodeTransformer):
    """Chuan hoa AST de giam anh huong doi ten bien/hang so."""

    def visit_Name(self, node: ast.Name) -> ast.AST:
        return ast.copy_location(ast.Name(id="VAR", ctx=node.ctx), node)

    def visit_arg(self, node: ast.arg) -> ast.AST:
        node.arg = "ARG"
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.AST:
        node.name = "FUNC"
        return self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AST:
        node.name = "FUNC"
        return self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.AST:
        node.name = "CLASS"
        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        if isinstance(node.value, str):
            value = "STR"
        elif isinstance(node.value, (int, float, complex)):
            value = 0
        elif isinstance(node.value, bytes):
            value = b""
        else:
            value = node.value
        return ast.copy_location(ast.Constant(value=value), node)


def ast_signature_and_features(source: str) -> Tuple[List[str], Counter]:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return [], Counter()

    normalizer = ASTNormalizer()
    norm_tree = normalizer.visit(tree)
    ast.fix_missing_locations(norm_tree)

    node_types = [type(n).__name__ for n in ast.walk(norm_tree)]
    features = Counter(node_types)

    try:
        normalized_code = ast.unparse(norm_tree)
    except Exception:
        normalized_code = "\n".join(node_types)

    tokens = simple_tokenize(normalized_code)
    return tokens, features


def build_shingles(tokens: Sequence[str], k: int = 5) -> Set[Tuple[str, ...]]:
    if len(tokens) < k:
        return {tuple(tokens)} if tokens else set()
    return {tuple(tokens[i : i + k]) for i in range(0, len(tokens) - k + 1)}


def jaccard_similarity(set_a: Set[Tuple[str, ...]], set_b: Set[Tuple[str, ...]]) -> float:
    if not set_a and not set_b:
        return 1.0
    if not set_a or not set_b:
        return 0.0
    inter = len(set_a & set_b)
    union = len(set_a | set_b)
    return inter / union if union else 0.0


def cosine_counter(c1: Counter, c2: Counter) -> float:
    if not c1 and not c2:
        return 1.0
    if not c1 or not c2:
        return 0.0

    keys = set(c1) | set(c2)
    dot = sum(c1[k] * c2[k] for k in keys)
    n1 = math.sqrt(sum(v * v for v in c1.values()))
    n2 = math.sqrt(sum(v * v for v in c2.values()))
    if n1 == 0 or n2 == 0:
        return 0.0
    return dot / (n1 * n2)


def profile_file(path: Path, root: Path) -> FileProfile:
    text = path.read_text(encoding="utf-8", errors="ignore")
    clean = remove_comments_and_docstrings(text)
    clean_tokens = simple_tokenize(clean)
    ast_tokens, feature_counter = ast_signature_and_features(clean)

    return FileProfile(
        path=path,
        rel_path=str(path.relative_to(root)).replace(os.sep, "/"),
        raw_text=text,
        clean_tokens=clean_tokens,
        ast_tokens=ast_tokens,
        feature_counter=feature_counter,
    )


def best_match_scores(
    files_a: Sequence[FileProfile],
    files_b: Sequence[FileProfile],
) -> Tuple[float, float, List[Tuple[str, str, float, float]]]:
    """
    Tra ve:
    - lexical_coverage_a_to_b
    - structural_coverage_a_to_b
    - top_matches[(fileA, fileB, lexical, structural)]
    """
    if not files_a:
        return 0.0, 0.0, []
    if not files_b:
        return 0.0, 0.0, []

    shingles_clean_b = [build_shingles(f.clean_tokens, k=5) for f in files_b]
    shingles_ast_b = [build_shingles(f.ast_tokens, k=5) for f in files_b]

    total_weight = sum(max(1, len(f.clean_tokens)) for f in files_a)
    weighted_lex = 0.0
    weighted_ast = 0.0

    match_rows: List[Tuple[str, str, float, float]] = []

    for fa in files_a:
        s_clean_a = build_shingles(fa.clean_tokens, k=5)
        s_ast_a = build_shingles(fa.ast_tokens, k=5)

        best_j_clean = -1.0
        best_j_ast = -1.0
        best_idx = 0

        for idx, fb in enumerate(files_b):
            j_clean = jaccard_similarity(s_clean_a, shingles_clean_b[idx])
            j_ast = jaccard_similarity(s_ast_a, shingles_ast_b[idx])

            # Chon cap file tot nhat theo trung binh lexical + AST
            merged = (j_clean + j_ast) / 2.0
            current_best = (best_j_clean + best_j_ast) / 2.0
            if merged > current_best:
                best_j_clean = j_clean
                best_j_ast = j_ast
                best_idx = idx

        weight = max(1, len(fa.clean_tokens))
        weighted_lex += weight * max(best_j_clean, 0.0)
        weighted_ast += weight * max(best_j_ast, 0.0)

        fb = files_b[best_idx]
        match_rows.append((fa.rel_path, fb.rel_path, max(best_j_clean, 0.0), max(best_j_ast, 0.0)))

    lex_coverage = weighted_lex / total_weight if total_weight else 0.0
    ast_coverage = weighted_ast / total_weight if total_weight else 0.0

    match_rows.sort(key=lambda x: (x[2] + x[3]), reverse=True)
    return lex_coverage, ast_coverage, match_rows[:10]


def aggregate_features(files: Iterable[FileProfile]) -> Counter:
    total = Counter()
    for f in files:
        total.update(f.feature_counter)
    return total


def verdict(lex_pct: float, ast_pct: float, strategy_pct: float) -> str:
    if lex_pct >= 80 and ast_pct >= 80:
        return "Nguy co trung lap rat cao (co kha nang copy truc tiep)."
    if ast_pct >= 75 and lex_pct < 60:
        return "Cau truc giai phap rat giong nhau, co dau hieu doi ten bien/decor lai code."
    if lex_pct >= 55 or ast_pct >= 55:
        return "Co trung lap dang ke, can review thu cong cac cap file top match."
    if strategy_pct >= 65:
        return "Khac text nhung cach giai quyet giong nhau o muc trung binh-cao."
    return "Muc trung lap thap, chua thay dau hieu copy ro rang tren tong the."


def print_report(
    root_a: Path,
    root_b: Path,
    files_a: Sequence[FileProfile],
    files_b: Sequence[FileProfile],
    lexical_pct: float,
    ast_pct: float,
    strategy_pct: float,
    top_a_to_b: List[Tuple[str, str, float, float]],
    top_b_to_a: List[Tuple[str, str, float, float]],
) -> None:
    print("=" * 72)
    print("BAO CAO DANH GIA TRUNG LAP CODE (PYTHON)")
    print("=" * 72)
    print(f"San pham 1: {root_a}")
    print(f"San pham 2: {root_b}")
    print(f"So file .py SP1: {len(files_a)}")
    print(f"So file .py SP2: {len(files_b)}")
    print("-" * 72)
    print(f"1) % trung lap code (lexical): {lexical_pct:.2f}%")
    print(f"2) % trung lap cau truc code (AST): {ast_pct:.2f}%")
    print(f"3) % giong nhau ve cach giai quyet: {strategy_pct:.2f}%")
    print("-" * 72)
    print("Nhan dinh:", verdict(lexical_pct, ast_pct, strategy_pct))

    print("\nTop cap file giong nhau (SP1 -> SP2):")
    if not top_a_to_b:
        print("  Khong co du lieu.")
    else:
        for fa, fb, l, s in top_a_to_b:
            print(f"  - {fa}  <->  {fb} | lexical={l*100:.1f}% | AST={s*100:.1f}%")

    print("\nTop cap file giong nhau (SP2 -> SP1):")
    if not top_b_to_a:
        print("  Khong co du lieu.")
    else:
        for fb, fa, l, s in top_b_to_a:
            print(f"  - {fb}  <->  {fa} | lexical={l*100:.1f}% | AST={s*100:.1f}%")

    print("=" * 72)


def validate_dir(path_str: str) -> Path:
    path = Path(path_str).expanduser().resolve()
    if not path.exists() or not path.is_dir():
        raise argparse.ArgumentTypeError(f"Thu muc khong hop le: {path_str}")
    return path


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "So sanh 2 thu muc Python va danh gia trung lap code theo % "
            "(lexical + cau truc AST + cach giai quyet)."
        )
    )
    parser.add_argument("product_a", type=validate_dir, help="Duong dan thu muc san pham A")
    parser.add_argument("product_b", type=validate_dir, help="Duong dan thu muc san pham B")
    args = parser.parse_args()

    files_path_a = find_python_files(args.product_a)
    files_path_b = find_python_files(args.product_b)

    files_a = [profile_file(p, args.product_a) for p in files_path_a]
    files_b = [profile_file(p, args.product_b) for p in files_path_b]

    if not files_a or not files_b:
        print("Khong du file .py de so sanh (mot trong hai thu muc rong).")
        return

    lex_a2b, ast_a2b, top_a2b = best_match_scores(files_a, files_b)
    lex_b2a, ast_b2a, top_b2a = best_match_scores(files_b, files_a)

    lexical_pct = ((lex_a2b + lex_b2a) / 2.0) * 100.0
    ast_pct = ((ast_a2b + ast_b2a) / 2.0) * 100.0

    # So sanh "cach giai quyet" o muc toan bo san pham bang vector dac trung AST.
    feat_a = aggregate_features(files_a)
    feat_b = aggregate_features(files_b)
    strategy_pct = cosine_counter(feat_a, feat_b) * 100.0

    print_report(
        root_a=args.product_a,
        root_b=args.product_b,
        files_a=files_a,
        files_b=files_b,
        lexical_pct=lexical_pct,
        ast_pct=ast_pct,
        strategy_pct=strategy_pct,
        top_a_to_b=top_a2b,
        top_b_to_a=top_b2a,
    )


if __name__ == "__main__":
    main()
