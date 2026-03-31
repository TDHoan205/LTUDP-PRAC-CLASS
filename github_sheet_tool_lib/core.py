from __future__ import annotations

import argparse
import ast
import base64
import csv
import difflib
import hashlib
import io
import json
import keyword
import os
import re
import sys
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
import tokenize
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen


GITHUB_REPO_PATTERN = re.compile(r"https?://github\.com/[^\s,;]+", re.IGNORECASE)
DEFAULT_TIMEOUT = 20
MAX_WORKERS = min(16, max(4, (os.cpu_count() or 4) * 2))


@dataclass
class Submission:
    row_number: int
    repo_url: str
    repo_full_name: str
    group: str = ""
    student_name: str = ""
    student_id: str = ""
    accessible: bool = False
    status_code: int = 0
    error: str = ""


@dataclass
class RequirementSpec:
    section: str = ""
    required_files: List[str] = None
    assignment_text: str = ""
    enabled: bool = False


@dataclass
class FileCheck:
    required_name: str
    exists: bool
    path: str = ""
    syntax_ok: bool = False
    score: float = 0.0
    verdict: str = "MISSING"
    notes: List[str] = None
    similarity_hash: str = ""


def normalize_google_sheet_to_csv_url(sheet_url: str) -> str:
    parsed = urlparse(sheet_url)
    if "docs.google.com" not in parsed.netloc or "/spreadsheets/" not in parsed.path:
        return sheet_url

    parts = [p for p in parsed.path.split("/") if p]
    try:
        d_index = parts.index("d")
        sheet_id = parts[d_index + 1]
    except (ValueError, IndexError):
        return sheet_url

    gid = "0"
    if parsed.fragment.startswith("gid="):
        gid = parsed.fragment.split("=", 1)[1] or "0"
    else:
        query = parse_qs(parsed.query)
        gid = query.get("gid", ["0"])[0]

    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?{urlencode({'format': 'csv', 'gid': gid})}"


def fetch_csv_rows(csv_url: str, timeout: int = DEFAULT_TIMEOUT) -> List[Dict[str, str]]:
    req = Request(csv_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as resp:
        content = resp.read().decode("utf-8-sig", errors="replace")

    reader = csv.DictReader(content.splitlines())
    return [dict(row) for row in reader]


def sanitize_github_url(url: str) -> str:
    return url.strip().rstrip(").,;\"' ")


def normalize_text_key(value: str) -> str:
    lowered = value.lower()
    lowered = lowered.replace("đ", "d")
    return re.sub(r"[^a-z0-9]+", "", lowered)


def detect_group_column(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return ""

    headers = list(rows[0].keys())
    for h in headers:
        key = normalize_text_key(h)
        if key in {"nhom", "group"}:
            return h

    for h in headers:
        key = normalize_text_key(h)
        if "nhom" in key or "group" in key:
            return h

    return ""


def detect_name_column(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    preferred = ["hovaten", "hoten", "fullname", "name", "ten"]
    for h in headers:
        key = normalize_text_key(h)
        if key in preferred:
            return h
    for h in headers:
        key = normalize_text_key(h)
        if "hovaten" in key or "hoten" in key or "name" in key:
            return h
    return ""


def detect_student_id_column(rows: List[Dict[str, str]]) -> str:
    if not rows:
        return ""
    headers = list(rows[0].keys())
    preferred = ["mssv", "studentid", "masosinhvien", "id"]
    for h in headers:
        key = normalize_text_key(h)
        if key in preferred:
            return h
    for h in headers:
        key = normalize_text_key(h)
        if "mssv" in key or "studentid" in key or "sinhvien" in key:
            return h
    return ""


def parse_repo_full_name(url: str) -> Optional[str]:
    parsed = urlparse(sanitize_github_url(url))
    if "github.com" not in parsed.netloc.lower():
        return None

    path_parts = [p for p in parsed.path.split("/") if p]
    if len(path_parts) < 2:
        return None

    owner = path_parts[0]
    repo = path_parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        return None

    return f"{owner}/{repo}"


def find_repo_urls_in_row(row: Dict[str, str]) -> List[str]:
    urls: Set[str] = set()
    for value in row.values():
        if not value:
            continue
        matches = GITHUB_REPO_PATTERN.findall(value)
        for raw in matches:
            clean = sanitize_github_url(raw)
            if clean:
                urls.add(clean)
    return sorted(urls)


def collect_submissions(rows: List[Dict[str, str]]) -> List[Submission]:
    submissions: List[Submission] = []
    group_col = detect_group_column(rows)
    name_col = detect_name_column(rows)
    id_col = detect_student_id_column(rows)
    for idx, row in enumerate(rows, start=2):
        group_value = ""
        student_name = ""
        student_id = ""
        if group_col:
            group_value = str(row.get(group_col, "")).strip()
        if name_col:
            student_name = str(row.get(name_col, "")).strip()
        if id_col:
            student_id = str(row.get(id_col, "")).strip()

        urls = find_repo_urls_in_row(row)
        for url in urls:
            full_name = parse_repo_full_name(url)
            if not full_name:
                continue
            submissions.append(
                Submission(
                    row_number=idx,
                    repo_url=url,
                    repo_full_name=full_name,
                    group=group_value,
                    student_name=student_name,
                    student_id=student_id,
                )
            )
    return submissions


class GithubClient:
    def __init__(self, token: Optional[str], timeout: int = DEFAULT_TIMEOUT, retries: int = 2):
        self.token = token
        self.timeout = timeout
        self.retries = retries

    def _request_json(self, path: str) -> Tuple[Optional[object], int, str]:
        url = f"https://api.github.com{path}"
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "github-sheet-tool",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        for attempt in range(self.retries + 1):
            req = Request(url, headers=headers)
            try:
                with urlopen(req, timeout=self.timeout) as resp:
                    data = json.loads(resp.read().decode("utf-8"))
                    return data, resp.status, ""
            except HTTPError as e:
                try:
                    body = e.read().decode("utf-8", errors="replace")
                except Exception:
                    body = str(e)

                lower_body = body.lower()
                is_rate_limit = e.code == 403 and "rate limit" in lower_body
                if is_rate_limit and attempt < self.retries:
                    time.sleep(1.5 * (attempt + 1))
                    continue
                return None, e.code, body
            except URLError as e:
                if attempt < self.retries:
                    time.sleep(0.8 * (attempt + 1))
                    continue
                return None, 0, str(e)

        return None, 0, "unknown error"

    def check_repo_access(self, repo_full_name: str) -> Tuple[bool, int, str]:
        data, status, error = self._request_json(f"/repos/{repo_full_name}")
        if data is not None and 200 <= status < 300:
            return True, status, ""
        return False, status, error

    def fetch_all_contributors(self, repo_full_name: str) -> Tuple[List[Dict[str, object]], str]:
        contributors: List[Dict[str, object]] = []
        page = 1

        while True:
            data, status, error = self._request_json(
                f"/repos/{repo_full_name}/contributors?per_page=100&page={page}"
            )
            if data is None:
                return contributors, f"[{repo_full_name}] API error {status}: {error[:200]}"

            if not isinstance(data, list):
                return contributors, f"[{repo_full_name}] Unexpected contributors format"

            if not data:
                break

            contributors.extend(data)
            if len(data) < 100:
                break
            page += 1

        return contributors, ""

    def fetch_repo_tree(self, repo_full_name: str) -> Tuple[List[str], str, str]:
        data, status, error = self._request_json(f"/repos/{repo_full_name}")
        if data is None or not isinstance(data, dict):
            return [], "", f"[{repo_full_name}] Cannot read repo info: {status} {error[:160]}"

        default_branch = str(data.get("default_branch", ""))
        if not default_branch:
            return [], "", f"[{repo_full_name}] Missing default_branch"

        tree_data, tree_status, tree_error = self._request_json(
            f"/repos/{repo_full_name}/git/trees/{default_branch}?recursive=1"
        )
        if tree_data is None or not isinstance(tree_data, dict):
            return [], default_branch, f"[{repo_full_name}] Cannot read tree: {tree_status} {tree_error[:160]}"

        items = tree_data.get("tree", [])
        if not isinstance(items, list):
            return [], default_branch, f"[{repo_full_name}] Invalid tree response"

        paths = [str(item.get("path", "")) for item in items if str(item.get("path", ""))]
        return paths, default_branch, ""

    def fetch_file_content(self, repo_full_name: str, file_path: str, ref: str) -> Tuple[Optional[str], str]:
        safe_path = file_path.replace(" ", "%20")
        data, status, error = self._request_json(f"/repos/{repo_full_name}/contents/{safe_path}?ref={ref}")
        if data is None or not isinstance(data, dict):
            return None, f"[{repo_full_name}] Cannot read file {file_path}: {status} {error[:120]}"

        content_b64 = str(data.get("content", ""))
        encoding = str(data.get("encoding", ""))
        if encoding != "base64" or not content_b64:
            return None, f"[{repo_full_name}] Unsupported encoding at {file_path}"

        try:
            raw = base64.b64decode(content_b64, validate=False)
            text = raw.decode("utf-8", errors="replace")
            return text, ""
        except Exception as e:
            return None, f"[{repo_full_name}] Decode error at {file_path}: {e}"


def parse_required_files(required_files_arg: str, bai_range_arg: str) -> List[str]:
    required: Set[str] = set()

    if required_files_arg.strip():
        for item in required_files_arg.split(","):
            name = item.strip()
            if not name:
                continue
            required.add(name)

    if bai_range_arg.strip():
        m = re.fullmatch(r"(\d+)\s*-\s*(\d+)", bai_range_arg.strip())
        if m:
            start = int(m.group(1))
            end = int(m.group(2))
            if start <= end:
                for i in range(start, end + 1):
                    required.add(f"bai{i}.py")

    return sorted(required)


def normalize_path_for_match(path: str) -> str:
    return path.replace("\\", "/").strip("/").lower()


def section_exists_in_tree(paths: Sequence[str], section: str) -> bool:
    if not section:
        return True

    s = normalize_path_for_match(section)
    for p in paths:
        np = normalize_path_for_match(p)
        if np == s or np.startswith(s + "/") or ("/" + s + "/") in ("/" + np + "/"):
            return True
    return False


def choose_path_for_required(paths: Sequence[str], required_name: str, section: str) -> str:
    target = normalize_path_for_match(required_name)
    candidates = [p for p in paths if normalize_path_for_match(p).endswith("/" + target) or normalize_path_for_match(p) == target]
    if not candidates:
        return ""

    if not section:
        return sorted(candidates, key=lambda x: len(x))[0]

    section_n = normalize_path_for_match(section)
    in_section = []
    for p in candidates:
        np = normalize_path_for_match(p)
        if np.startswith(section_n + "/") or ("/" + section_n + "/") in ("/" + np + "/"):
            in_section.append(p)

    if in_section:
        return sorted(in_section, key=lambda x: len(x))[0]

    return ""


def extract_keywords(text: str) -> List[str]:
    lowered = text.lower()
    tokens = re.findall(r"[a-zA-Z0-9_\.]{3,}", lowered)
    stop = {
        "cho", "trong", "nhap", "viet", "chuong", "phan", "bai", "kiem", "tra", "hoac",
        "theo", "yeu", "cau", "mot", "so", "va", "co", "la", "khong", "duoc", "nguoi",
        "dung", "code", "python", "file"
    }
    out = []
    seen = set()
    for t in tokens:
        if t in stop:
            continue
        if t in seen:
            continue
        seen.add(t)
        out.append(t)
    return out


def detect_required_signals(assignment_text: str) -> Dict[str, bool]:
    t = assignment_text.lower()
    return {
        "need_modulo": ("chia het" in t) or ("chia hết" in t) or ("%" in t),
        "need_sqrt": ("sqrt" in t) or ("can bac" in t) or ("căn bậc" in t) or ("phuong trinh bac 2" in t),
        "need_triangle": ("tam giac" in t) or ("tam giác" in t),
        "need_age": ("nam sinh" in t) or ("tuoi" in t) or ("tuổi" in t),
    }


def is_section_23(section: str) -> bool:
    s = normalize_path_for_match(section)
    return s == "2.3" or s.endswith("/2.3") or "/2.3/" in ("/" + s + "/")


def normalize_code_for_similarity(code: str) -> str:
    tokens: List[str] = []
    try:
        stream = io.StringIO(code)
        for tok in tokenize.generate_tokens(stream.readline):
            if tok.type in {
                tokenize.ENCODING,
                tokenize.NEWLINE,
                tokenize.NL,
                tokenize.INDENT,
                tokenize.DEDENT,
                tokenize.ENDMARKER,
                tokenize.COMMENT,
            }:
                continue

            if tok.type == tokenize.STRING:
                tokens.append("STR")
                continue

            if tok.type == tokenize.NUMBER:
                tokens.append("NUM")
                continue

            if tok.type == tokenize.NAME:
                if keyword.iskeyword(tok.string):
                    tokens.append(tok.string)
                else:
                    tokens.append("ID")
                continue

            tokens.append(tok.string)
    except Exception:
        return re.sub(r"\s+", " ", code).strip().lower()

    return " ".join(tokens)


def hash_normalized_code(normalized_code: str) -> str:
    return hashlib.sha256(normalized_code.encode("utf-8", errors="replace")).hexdigest()


def score_with_section_rules(
    required_name: str,
    section: str,
    code: str,
) -> Tuple[Optional[float], List[str]]:
    if not is_section_23(section):
        return None, []

    name = required_name.lower()
    if name not in {"bai1.py", "bai2.py", "bai3.py", "bai4.py", "bai5.py"}:
        return None, []

    notes: List[str] = []
    code_l = code.lower()

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return 0.0, [f"SyntaxError: line {e.lineno}"]

    has_input = "input(" in code_l
    has_print = "print(" in code_l
    has_if = any(isinstance(node, ast.If) for node in ast.walk(tree))
    has_elif = any(isinstance(node, ast.If) and node.orelse for node in ast.walk(tree))
    has_loop = any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
    has_sqrt = "sqrt(" in code_l or "math.sqrt" in code_l
    has_time = "time" in code_l or "datetime" in code_l or ".year" in code_l
    compare_count = len(re.findall(r">|<|==|!=|>=|<=", code))
    plus_count = code.count("+")

    def add_rule(ok: bool, points: float, ok_note: str, fail_note: str) -> float:
        if ok:
            notes.append(f"OK: {ok_note}")
            return points
        notes.append(f"THIEU: {fail_note}")
        return 0.0

    score = 0.0
    score += add_rule(has_input, 12, "Co input()", "Can nhap du lieu tu ban phim")
    score += add_rule(has_print, 10, "Co print()", "Can in ket qua")
    score += add_rule(has_if, 8, "Co cau truc re nhanh", "Can dung if/elif/else")

    if name == "bai1.py":
        score += add_rule(re.search(r"%\s*2", code) is not None, 30, "Kiem tra chan/le bang %2", "Can dung %2 de phan biet chan/le")
        score += add_rule(has_elif or "else" in code_l, 10, "Co xu ly du 2 truong hop chan/le", "Nen co 2 nhanh chan va le")
        score += add_rule("chan" in code_l or "le" in code_l, 10, "Thong bao ket qua ro rang", "Nen thong bao chan/le ro rang")
        score += add_rule(not has_loop, 5, "Code ngan gon dung muc bai 1", "Bai 1 khong can lap, nen gian don")

    elif name == "bai2.py":
        score += add_rule(code_l.count("input(") >= 3, 12, "Nhap 3 canh", "Can nhap du 3 canh a,b,c")
        tri_rule = compare_count >= 3 and plus_count >= 2 and "and" in code_l
        score += add_rule(tri_rule, 30, "Dung dinh ly bat dang thuc tam giac", "Can kiem tra tong 2 canh > canh con lai")
        score += add_rule("tam giac" in code_l or "tam giác" in code_l, 10, "Co thong bao ve tam giac", "Nen in thong bao co/khong phai tam giac")
        score += add_rule(has_if, 10, "Co xu ly dung/sai", "Can co nhanh xu ly dung/sai")

    elif name == "bai3.py":
        score += add_rule(has_time, 28, "Co lay nam hien tai", "Nen lay nam hien tai bang time/datetime")
        score += add_rule("-" in code, 18, "Co cong thuc tuoi = nam_hien_tai - nam_sinh", "Can tru nam sinh de ra tuoi")
        score += add_rule("tuoi" in code_l or "tuổi" in code_l, 10, "In duoc tuoi", "Nen in ket qua tuoi")
        score += add_rule(code_l.count("input(") >= 1, 4, "Co nhap nam sinh", "Can nhap nam sinh")

    elif name == "bai4.py":
        has_mod2 = re.search(r"%\s*2", code) is not None
        has_mod3 = re.search(r"%\s*3", code) is not None
        score += add_rule(has_mod2, 12, "Kiem tra chia het cho 2", "Can kiem tra dieu kien chia het cho 2")
        score += add_rule(has_mod3, 12, "Kiem tra chia het cho 3", "Can kiem tra dieu kien chia het cho 3")
        score += add_rule((" and " in code_l) or (" or " in code_l), 18, "Ket hop dieu kien logic", "Nen ket hop dieu kien bang and/or")
        score += add_rule(has_if and has_elif, 18, "Xu ly du cac truong hop", "Nen xu ly ca 4 truong hop (2, 3, ca hai, khong)")
        score += add_rule("chia het" in code_l or "chia hết" in code_l, 10, "Thong bao dung ngu canh de bai", "Nen in thong bao chia het/khong chia het")

    elif name == "bai5.py":
        score += add_rule(has_sqrt, 15, "Su dung sqrt de tinh nghiem", "Can dung math.sqrt")
        has_delta = "delta" in code_l or "b * b - 4" in code_l or "b**2" in code_l
        score += add_rule(has_delta, 20, "Co tinh delta", "Can tinh delta = b^2 - 4ac")
        score += add_rule(compare_count >= 2, 15, "Co phan nhanh theo delta", "Can xet cac truong hop delta <0, =0, >0")
        score += add_rule(("2 * a" in code_l) or ("/ (2*a)" in code_l) or ("/ (2 * a)" in code_l), 12, "Dung cong thuc nghiem bac 2", "Can dung mau so 2*a")
        score += add_rule("a == 0" in code_l or "if a==0" in code_l or "if a == 0" in code_l, 8, "Co xu ly truong hop a=0", "Nen xu ly truong hop suy bien a=0")
        score += add_rule("nghiem" in code_l or "nghiệm" in code_l, 5, "Co thong bao nghiem", "Nen in thong bao nghiem")

    # Thuong nho cho code clean.
    if has_loop:
        score += 2

    score = min(100.0, round(score, 2))
    if score >= 80:
        notes.append("Dat yeu cau bai theo rule 2.3")
    elif score >= 60:
        notes.append("Dat mot phan yeu cau bai theo rule 2.3")
    else:
        notes.append("Chua dat yeu cau bai theo rule 2.3")
    return score, notes


def analyze_python_file(code: str, assignment_text: str) -> Tuple[bool, float, List[str]]:
    notes: List[str] = []
    syntax_ok = True
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        syntax_ok = False
        notes.append(f"SyntaxError: line {e.lineno}")
        return syntax_ok, 0.0, notes

    code_l = code.lower()
    signals = detect_required_signals(assignment_text)
    keywords = extract_keywords(assignment_text)

    has_input = "input(" in code_l
    has_print = "print(" in code_l
    has_if = any(isinstance(node, ast.If) for node in ast.walk(tree))
    has_loop = any(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
    has_modulo = "%" in code
    has_sqrt = "sqrt(" in code_l or "math.sqrt" in code_l

    score = 35.0
    if has_input:
        score += 10
    else:
        notes.append("Khong thay input()")

    if has_print:
        score += 10
    else:
        notes.append("Khong thay print()")

    if has_if:
        score += 10
    else:
        notes.append("Khong thay cau truc if")

    if has_loop:
        score += 5

    if signals["need_modulo"]:
        if has_modulo and has_if:
            score += 15
        else:
            notes.append("De bai can logic chia het (%), file chua the hien ro")

    if signals["need_sqrt"]:
        if has_sqrt:
            score += 15
        else:
            notes.append("De bai can sqrt/math.sqrt")

    if signals["need_triangle"]:
        if ">" in code and "+" in code:
            score += 15
        else:
            notes.append("De bai tam giac can so sanh tong canh")

    if signals["need_age"]:
        if ("time" in code_l) or ("datetime" in code_l) or ("nam_hien_tai" in code_l):
            score += 15
        else:
            notes.append("De bai tuoi/nam sinh can nam hien tai")

    if keywords:
        matched = sum(1 for k in keywords if k in code_l)
        keyword_score = 10.0 * matched / max(1, len(keywords))
        score += keyword_score

    score = min(100.0, round(score, 2))

    if score >= 80:
        notes.append("Muc do khop de bai cao")
    elif score >= 60:
        notes.append("Muc do khop de bai trung binh")
    else:
        notes.append("Muc do khop de bai thap")

    return syntax_ok, score, notes


def evaluate_repo_exercises(
    client: GithubClient,
    repo: str,
    spec: RequirementSpec,
    preloaded_tree: Optional[Tuple[List[str], str, str]] = None,
) -> Tuple[Dict[str, object], List[str]]:
    warnings: List[str] = []
    if preloaded_tree is None:
        paths, default_branch, tree_err = client.fetch_repo_tree(repo)
    else:
        paths, default_branch, tree_err = preloaded_tree
    if tree_err:
        return {
            "repo": repo,
            "section_exists": False,
            "default_branch": default_branch,
            "required_files_total": len(spec.required_files),
            "required_files_found": 0,
            "missing_files": spec.required_files,
            "files": [],
            "repo_status": "FAIL",
            "score": 0.0,
            "reason": "Khong doc duoc cay thu muc repo",
        }, [tree_err]

    section_ok = section_exists_in_tree(paths, spec.section)
    file_checks: List[FileCheck] = []
    similarity_sources: List[Dict[str, str]] = []

    for required_name in spec.required_files:
        matched_path = choose_path_for_required(paths, required_name, spec.section)
        if not matched_path:
            file_checks.append(
                FileCheck(
                    required_name=required_name,
                    exists=False,
                    verdict="MISSING",
                    notes=["Khong tim thay file theo yeu cau"],
                )
            )
            continue

        content, err = client.fetch_file_content(repo, matched_path, default_branch)
        if err or content is None:
            file_checks.append(
                FileCheck(
                    required_name=required_name,
                    exists=True,
                    path=matched_path,
                    verdict="ERROR",
                    notes=[err or "Khong doc duoc noi dung file"],
                )
            )
            continue

        syntax_ok, score, notes = analyze_python_file(content, spec.assignment_text)
        special_score, special_notes = score_with_section_rules(required_name, spec.section, content)
        if special_score is not None:
            score = special_score
            notes = special_notes

        normalized_code = normalize_code_for_similarity(content)
        similarity_hash = hash_normalized_code(normalized_code)
        similarity_sources.append(
            {
                "required_name": required_name,
                "path": matched_path,
                "similarity_hash": similarity_hash,
                "normalized_code": normalized_code,
            }
        )
        verdict = "PASS" if syntax_ok and score >= 60 else "FAIL"
        file_checks.append(
            FileCheck(
                required_name=required_name,
                exists=True,
                path=matched_path,
                syntax_ok=syntax_ok,
                score=score,
                verdict=verdict,
                notes=notes,
                similarity_hash=similarity_hash,
            )
        )

    found = sum(1 for f in file_checks if f.exists)
    passed = sum(1 for f in file_checks if f.verdict == "PASS")
    avg_score = round(sum(f.score for f in file_checks if f.exists) / max(1, found), 2)
    missing = [f.required_name for f in file_checks if not f.exists]

    repo_status = "PASS"
    if not section_ok or missing:
        repo_status = "FAIL"
    elif passed < len(spec.required_files):
        repo_status = "WARN"

    reason = ""
    if not section_ok:
        reason = f"Khong co thu muc/phan {spec.section}"

    return {
        "repo": repo,
        "section_exists": section_ok,
        "default_branch": default_branch,
        "required_files_total": len(spec.required_files),
        "required_files_found": found,
        "required_files_passed": passed,
        "missing_files": missing,
        "files": [asdict(f) for f in file_checks],
        "repo_status": repo_status,
        "score": avg_score,
        "reason": reason,
        "_similarity_sources": similarity_sources,
    }, warnings


def summarize_repo_contents(paths: Sequence[str], section: str) -> Dict[str, object]:
    root_items: Set[str] = set()
    py_files: List[str] = []
    for p in paths:
        normalized = p.replace("\\", "/").strip("/")
        if not normalized:
            continue
        first = normalized.split("/", 1)[0]
        if first:
            root_items.add(first)
        if normalized.lower().endswith(".py"):
            py_files.append(normalized)

    section_found = section_exists_in_tree(paths, section) if section else False
    section_py_count = 0
    section_norm = normalize_path_for_match(section)
    if section_norm:
        for p in py_files:
            np = normalize_path_for_match(p)
            if np.startswith(section_norm + "/") or ("/" + section_norm + "/") in ("/" + np + "/"):
                section_py_count += 1

    return {
        "root_items_preview": sorted(root_items)[:12],
        "root_items_total": len(root_items),
        "python_files_total": len(py_files),
        "section_found": section_found,
        "section_python_files": section_py_count,
        "python_files_preview": sorted(py_files)[:12],
    }


def parallel_map_repos(
    repos: Iterable[str],
    worker,
    max_workers: int,
) -> Tuple[Dict[str, object], List[str]]:
    results: Dict[str, object] = {}
    warnings: List[str] = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, repo): repo for repo in repos}
        for future in as_completed(futures):
            repo = futures[future]
            try:
                payload, warn = future.result()
                results[repo] = payload
                warnings.extend(warn)
            except Exception as e:
                warnings.append(f"[{repo}] unexpected error: {e}")
    return results, warnings


def build_similarity_report(repo_rows: List[Dict[str, object]], threshold: float) -> Dict[str, object]:
    by_required: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for row in repo_rows:
        repo = str(row.get("repo", ""))
        for src in row.get("_similarity_sources", []):
            item = dict(src)
            item["repo"] = repo
            by_required[str(item.get("required_name", ""))].append(item)

    suspicious_pairs: List[Dict[str, object]] = []
    exact_duplicates: List[Dict[str, object]] = []

    for required_name, items in by_required.items():
        # Group exact duplicates by normalized hash.
        groups: Dict[str, List[str]] = defaultdict(list)
        for it in items:
            h = str(it.get("similarity_hash", ""))
            if not h:
                continue
            groups[h].append(str(it.get("repo", "")))

        for h, repos in groups.items():
            unique_repos = sorted(set(r for r in repos if r))
            if len(unique_repos) >= 2:
                exact_duplicates.append(
                    {
                        "required_name": required_name,
                        "hash": h,
                        "repos": unique_repos,
                        "repo_count": len(unique_repos),
                    }
                )

        # Pairwise near-duplicate check using normalized token stream.
        n = len(items)
        for i in range(n):
            for j in range(i + 1, n):
                a = items[i]
                b = items[j]
                repo_a = str(a.get("repo", ""))
                repo_b = str(b.get("repo", ""))
                if not repo_a or not repo_b or repo_a == repo_b:
                    continue

                code_a = str(a.get("normalized_code", ""))
                code_b = str(b.get("normalized_code", ""))
                if not code_a or not code_b:
                    continue

                ratio = difflib.SequenceMatcher(None, code_a, code_b).ratio()
                if ratio >= threshold:
                    suspicious_pairs.append(
                        {
                            "required_name": required_name,
                            "repo_a": repo_a,
                            "repo_b": repo_b,
                            "similarity": round(ratio, 4),
                            "path_a": str(a.get("path", "")),
                            "path_b": str(b.get("path", "")),
                        }
                    )

    suspicious_pairs.sort(key=lambda x: x["similarity"], reverse=True)
    exact_duplicates.sort(key=lambda x: x["repo_count"], reverse=True)
    return {
        "enabled": True,
        "threshold": threshold,
        "exact_duplicate_groups": exact_duplicates,
        "near_duplicate_pairs": suspicious_pairs,
        "near_duplicate_count": len(suspicious_pairs),
    }


def build_group_ranking(repo_rows: List[Dict[str, object]]) -> Dict[str, object]:
    grouped: Dict[str, List[Dict[str, object]]] = defaultdict(list)
    for row in repo_rows:
        group = str(row.get("group", "")).strip() or "NO_GROUP"
        grouped[group].append(row)

    ranking_rows: List[Dict[str, object]] = []
    for group, rows in grouped.items():
        scores = [float(r.get("score_10", 0.0)) for r in rows]
        avg_score = round(sum(scores) / max(1, len(scores)), 2)
        pass_count = sum(1 for r in rows if str(r.get("repo_status", "")) == "PASS")
        warn_count = sum(1 for r in rows if str(r.get("repo_status", "")) == "WARN")
        fail_count = sum(1 for r in rows if str(r.get("repo_status", "")) == "FAIL")

        ranking_rows.append(
            {
                "group": group,
                "repo_count": len(rows),
                "avg_score_10": avg_score,
                "pass_count": pass_count,
                "warn_count": warn_count,
                "fail_count": fail_count,
            }
        )

    ranking_rows.sort(
        key=lambda x: (x["avg_score_10"], x["pass_count"], -x["fail_count"]),
        reverse=True,
    )

    current_rank = 0
    prev_key = None
    for idx, row in enumerate(ranking_rows, start=1):
        key = (row["avg_score_10"], row["pass_count"], row["fail_count"])
        if key != prev_key:
            current_rank = idx
            prev_key = key
        row["rank"] = current_rank

    return {
        "enabled": True,
        "groups": ranking_rows,
    }


def build_plagiarism_repo_flags(similarity_check: Dict[str, object], high_threshold: float = 0.97) -> Dict[str, Dict[str, object]]:
    flags: Dict[str, Dict[str, object]] = {}

    def ensure(repo: str) -> Dict[str, object]:
        if repo not in flags:
            flags[repo] = {
                "high_risk": False,
                "max_similarity": 0.0,
                "related_repos": set(),
                "reasons": set(),
            }
        return flags[repo]

    for grp in similarity_check.get("exact_duplicate_groups", []):
        repos = grp.get("repos", [])
        for r in repos:
            entry = ensure(str(r))
            entry["high_risk"] = True
            entry["max_similarity"] = max(float(entry["max_similarity"]), 1.0)
            entry["reasons"].add("exact_duplicate")
            for other in repos:
                if other != r:
                    entry["related_repos"].add(str(other))

    for pair in similarity_check.get("near_duplicate_pairs", []):
        repo_a = str(pair.get("repo_a", ""))
        repo_b = str(pair.get("repo_b", ""))
        sim = float(pair.get("similarity", 0.0))
        if not repo_a or not repo_b:
            continue

        for me, other in ((repo_a, repo_b), (repo_b, repo_a)):
            entry = ensure(me)
            entry["max_similarity"] = max(float(entry["max_similarity"]), sim)
            entry["related_repos"].add(other)
            if sim >= high_threshold:
                entry["high_risk"] = True
                entry["reasons"].add("near_duplicate_high")

    for repo, entry in flags.items():
        entry["max_similarity"] = round(float(entry["max_similarity"]), 4)
        entry["related_repos"] = sorted(entry["related_repos"])
        entry["reasons"] = sorted(entry["reasons"])

    return flags


def write_exercise_summary_csv(report: Dict[str, object], csv_output_path: str) -> None:
    exercise = report.get("exercise_check", {})
    if not exercise.get("enabled"):
        return

    repo_rows = exercise.get("repo_results", [])
    required_files = exercise.get("required_files", [])
    plagiarism_flags = report.get("plagiarism_flags", {})

    headers = [
        "repo",
        "group",
        "rank_overall",
        "repo_status",
        "score",
        "score_10",
        "section_exists",
        "required_files_total",
        "required_files_found",
        "required_files_passed",
        "plagiarism_high_risk",
        "plagiarism_max_similarity",
        "plagiarism_related_repos",
        "plagiarism_reasons",
        "missing_files",
        "reason",
    ]

    for rf in required_files:
        headers.append(f"{rf}_verdict")
        headers.append(f"{rf}_score")
        headers.append(f"{rf}_path")

    os.makedirs(os.path.dirname(csv_output_path) or ".", exist_ok=True)
    with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

        for row in repo_rows:
            repo_name = str(row.get("repo", ""))
            pflag = plagiarism_flags.get(repo_name, {})
            out = {
                "repo": repo_name,
                "group": row.get("group", ""),
                "rank_overall": row.get("rank_overall", 0),
                "repo_status": row.get("repo_status", ""),
                "score": row.get("score", 0),
                "score_10": row.get("score_10", 0),
                "section_exists": row.get("section_exists", False),
                "required_files_total": row.get("required_files_total", 0),
                "required_files_found": row.get("required_files_found", 0),
                "required_files_passed": row.get("required_files_passed", 0),
                "plagiarism_high_risk": bool(pflag.get("high_risk", row.get("plagiarism_high_risk", False))),
                "plagiarism_max_similarity": pflag.get("max_similarity", row.get("plagiarism_max_similarity", 0.0)),
                "plagiarism_related_repos": "|".join(pflag.get("related_repos", row.get("plagiarism_related_repos", []))),
                "plagiarism_reasons": "|".join(pflag.get("reasons", row.get("plagiarism_reasons", []))),
                "missing_files": "|".join(row.get("missing_files", [])),
                "reason": row.get("reason", ""),
            }

            file_map = {f.get("required_name", ""): f for f in row.get("files", [])}
            for rf in required_files:
                fobj = file_map.get(rf, {})
                out[f"{rf}_verdict"] = fobj.get("verdict", "MISSING")
                out[f"{rf}_score"] = fobj.get("score", 0)
                out[f"{rf}_path"] = fobj.get("path", "")

            writer.writerow(out)


def build_report(
    sheet_url: str,
    token: Optional[str],
    spec: RequirementSpec,
    max_workers: int,
    similarity_threshold: float,
) -> Dict[str, object]:
    csv_url = normalize_google_sheet_to_csv_url(sheet_url)
    rows = fetch_csv_rows(csv_url)
    submissions = collect_submissions(rows)
    repo_group_map: Dict[str, str] = {}
    repo_student_map: Dict[str, Dict[str, str]] = {}
    for s in submissions:
        if s.repo_full_name not in repo_group_map and s.group:
            repo_group_map[s.repo_full_name] = s.group
        if s.repo_full_name not in repo_student_map:
            repo_student_map[s.repo_full_name] = {
                "student_name": s.student_name,
                "student_id": s.student_id,
                "group": s.group,
            }

    client = GithubClient(token=token)
    unique_repos = sorted({s.repo_full_name for s in submissions})

    def _access_worker(repo: str):
        ok, status, err = client.check_repo_access(repo)
        warns: List[str] = []
        err_l = err.lower()
        if (status in {403, 429}) and ("rate limit" in err_l or "abuse" in err_l):
            warns.append(f"[{repo}] GitHub API rate limited ({status})")
        return {"ok": ok, "status": status, "err": err}, warns

    access_results, access_warnings = parallel_map_repos(unique_repos, _access_worker, max_workers)

    for item in submissions:
        payload = access_results.get(item.repo_full_name, {"ok": False, "status": 0, "err": "unknown"})
        item.accessible = bool(payload["ok"])
        item.status_code = int(payload["status"])
        item.error = str(payload["err"])[:200]

    total_submitted_links = len(submissions)
    accessible_links = sum(1 for s in submissions if s.accessible)
    unique_accessible_repos = sorted({s.repo_full_name for s in submissions if s.accessible})

    contribution_counts: Dict[str, int] = defaultdict(int)

    # Fetch repo trees once and reuse for both submission overview and exercise checks.
    def _tree_worker(repo: str):
        paths, default_branch, err = client.fetch_repo_tree(repo)
        payload = {
            "paths": paths,
            "default_branch": default_branch,
            "error": err,
        }
        warns = [err] if err else []
        return payload, warns

    tree_results, tree_warnings = parallel_map_repos(unique_accessible_repos, _tree_worker, max_workers)

    def _contrib_worker(repo: str):
        contributors, warn = client.fetch_all_contributors(repo)
        payload = {"contributors": contributors}
        warnings = [warn] if warn else []
        return payload, warnings

    contrib_results, contrib_warnings = parallel_map_repos(unique_accessible_repos, _contrib_worker, max_workers)
    for repo in unique_accessible_repos:
        contributors = contrib_results.get(repo, {}).get("contributors", [])
        for c in contributors:
            login = str(c.get("login", "unknown"))
            commits = int(c.get("contributions", 0))
            contribution_counts[login] += commits

    total_commits = sum(contribution_counts.values())
    contribution_percent = []
    for login, commits in sorted(contribution_counts.items(), key=lambda x: x[1], reverse=True):
        percent = (commits / total_commits * 100.0) if total_commits else 0.0
        contribution_percent.append({"member": login, "commits": commits, "percent": round(percent, 2)})

    exercise_report = {}
    similarity_report = {"enabled": False}
    group_ranking_report = {"enabled": False}
    plagiarism_flags: Dict[str, Dict[str, object]] = {}
    exercise_warnings: List[str] = []

    submission_overview: List[Dict[str, object]] = []
    for s in submissions:
        base = {
            "row_number": s.row_number,
            "student_name": s.student_name,
            "student_id": s.student_id,
            "group": s.group,
            "repo_url": s.repo_url,
            "repo_full_name": s.repo_full_name,
            "accessible": s.accessible,
            "status_code": s.status_code,
            "error": s.error,
            "repo_contents": {},
        }
        if s.accessible:
            tree_payload = tree_results.get(s.repo_full_name, {})
            paths = tree_payload.get("paths", [])
            if isinstance(paths, list) and paths:
                base["repo_contents"] = summarize_repo_contents(paths, spec.section)
            else:
                base["repo_contents"] = {
                    "root_items_preview": [],
                    "root_items_total": 0,
                    "python_files_total": 0,
                    "section_found": False,
                    "section_python_files": 0,
                    "python_files_preview": [],
                }
        submission_overview.append(base)

    if spec.enabled and spec.required_files:
        def _exercise_worker(repo: str):
            t = tree_results.get(repo, {})
            preloaded = (
                t.get("paths", []) if isinstance(t.get("paths", []), list) else [],
                str(t.get("default_branch", "")),
                str(t.get("error", "")),
            )
            return evaluate_repo_exercises(client, repo, spec, preloaded_tree=preloaded)

        exercise_results, exercise_warnings = parallel_map_repos(unique_accessible_repos, _exercise_worker, max_workers)
        repo_rows = [exercise_results[r] for r in unique_accessible_repos if r in exercise_results]

        for row in repo_rows:
            repo_name = str(row.get("repo", ""))
            row["group"] = repo_group_map.get(repo_name, "")
            row["score_10"] = round(float(row.get("score", 0.0)) / 10.0, 2)

        repo_rows.sort(key=lambda x: (float(x.get("score_10", 0.0)), float(x.get("score", 0.0))), reverse=True)
        for idx, row in enumerate(repo_rows, start=1):
            row["rank_overall"] = idx

        similarity_report = build_similarity_report(repo_rows, similarity_threshold)
        plagiarism_flags = build_plagiarism_repo_flags(similarity_report, high_threshold=max(0.95, similarity_threshold))
        group_ranking_report = build_group_ranking(repo_rows)

        for row in repo_rows:
            p = plagiarism_flags.get(str(row.get("repo", "")), {})
            row["plagiarism_high_risk"] = bool(p.get("high_risk", False))
            row["plagiarism_max_similarity"] = float(p.get("max_similarity", 0.0))
            row["plagiarism_related_repos"] = p.get("related_repos", [])
            row["plagiarism_reasons"] = p.get("reasons", [])

        passed_repos = sum(1 for r in repo_rows if r.get("repo_status") == "PASS")
        warn_repos = sum(1 for r in repo_rows if r.get("repo_status") == "WARN")
        failed_repos = sum(1 for r in repo_rows if r.get("repo_status") == "FAIL")

        for row in repo_rows:
            row.pop("_similarity_sources", None)

        exercise_report = {
            "enabled": True,
            "section": spec.section,
            "required_files": spec.required_files,
            "assignment_text": spec.assignment_text,
            "repos_checked": len(repo_rows),
            "pass_count": passed_repos,
            "warn_count": warn_repos,
            "fail_count": failed_repos,
            "group_ranking": group_ranking_report,
            "repo_results": repo_rows,
        }
    else:
        exercise_report = {
            "enabled": False,
            "section": spec.section,
            "required_files": spec.required_files or [],
            "assignment_text": spec.assignment_text,
        }

    warnings = access_warnings + contrib_warnings + tree_warnings + exercise_warnings

    report = {
        "sheet_url": sheet_url,
        "csv_url_used": csv_url,
        "rows_read": len(rows),
        "submitted_links": total_submitted_links,
        "accessible_links": accessible_links,
        "accessible_rate_percent": round((accessible_links / total_submitted_links * 100.0), 2)
        if total_submitted_links
        else 0.0,
        "unique_accessible_repos": unique_accessible_repos,
        "contribution_summary": contribution_percent,
        "exercise_check": exercise_report,
        "similarity_check": similarity_report,
        "plagiarism_flags": plagiarism_flags,
        "submitter_overview": submission_overview,
        "warnings": warnings,
        "submission_details": [asdict(s) for s in submissions],
    }
    return report


def print_summary(report: Dict[str, object]) -> None:
    print("\n=== TOM TAT KET QUA ===")
    print(f"Rows read: {report['rows_read']}")
    print(f"Submitted GitHub links: {report['submitted_links']}")
    print(f"Accessible links: {report['accessible_links']}")
    print(f"Accessible rate: {report['accessible_rate_percent']}%")

    repos = report.get("unique_accessible_repos", [])
    print(f"Unique accessible repos: {len(repos)}")

    print("\n=== % DONG GOP THEO CONTRIBUTORS (dua tren commit count) ===")
    contribs = report.get("contribution_summary", [])
    if not contribs:
        print("Khong co du lieu contributors.")
    else:
        for item in contribs[:15]:
            print(f"  - {item['member']}: {item['commits']} commits ({item['percent']}%)")

    exercise_check = report.get("exercise_check", {})
    if exercise_check.get("enabled"):
        print("\n=== KIEM TRA BAI TAP ===")
        print(f"Section: {exercise_check.get('section', '')}")
        print(f"Required files: {', '.join(exercise_check.get('required_files', []))}")
        print(f"Repos checked: {exercise_check.get('repos_checked', 0)}")
        print(f"PASS/WARN/FAIL: {exercise_check.get('pass_count', 0)}/{exercise_check.get('warn_count', 0)}/{exercise_check.get('fail_count', 0)}")

        group_ranking = exercise_check.get("group_ranking", {})
        if group_ranking.get("enabled"):
            print("\n=== XEP HANG NHOM (THANG 10) ===")
            for g in group_ranking.get("groups", [])[:10]:
                print(
                    f"  - Rank {g.get('rank', 0)} | Nhom {g.get('group', '')}: "
                    f"avg={g.get('avg_score_10', 0)} "
                    f"PASS/WARN/FAIL={g.get('pass_count', 0)}/{g.get('warn_count', 0)}/{g.get('fail_count', 0)}"
                )

    similarity_check = report.get("similarity_check", {})
    if similarity_check.get("enabled"):
        print("\n=== KIEM TRA TUONG DONG CODE ===")
        print(f"Threshold: {similarity_check.get('threshold', 0)}")
        print(f"Exact duplicate groups: {len(similarity_check.get('exact_duplicate_groups', []))}")
        print(f"Near-duplicate pairs: {similarity_check.get('near_duplicate_count', 0)}")

    plagiarism_flags = report.get("plagiarism_flags", {})
    if plagiarism_flags:
        high_risk_count = sum(1 for v in plagiarism_flags.values() if v.get("high_risk"))
        print(f"High-risk plagiarism repos: {high_risk_count}")

    warnings = report.get("warnings", [])
    if warnings:
        print("\n=== CANH BAO ===")
        for w in warnings[:10]:
            print(f"  - {w}")


def build_spec_from_args(args: argparse.Namespace) -> RequirementSpec:
    required_files = parse_required_files(args.required_files, args.bai_range)
    enabled = bool(required_files or args.section.strip() or args.assignment.strip())

    return RequirementSpec(
        section=args.section.strip(),
        required_files=required_files,
        assignment_text=args.assignment.strip(),
        enabled=enabled,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kiem tra GitHub links trong Google Sheet, thong ke dong gop va cham bai theo yeu cau.",
    )
    parser.add_argument("--sheet-url", required=True, help="Google Sheet URL (hoac direct CSV URL)")
    parser.add_argument(
        "--output",
        default="baitapclass/github_sheet_report.json",
        help="Duong dan file JSON output",
    )
    parser.add_argument(
        "--token",
        default=os.getenv("GITHUB_TOKEN", ""),
        help="GitHub token (neu bo trong se doc tu env GITHUB_TOKEN)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=MAX_WORKERS,
        help="So luong luong toi da cho API calls",
    )

    parser.add_argument(
        "--section",
        default="",
        help="Phan/chuong can kiem tra. VD: 2.3 hoac Baitapchuong2/2.3",
    )
    parser.add_argument(
        "--required-files",
        default="",
        help="Danh sach file bat buoc, phan cach bang dau phay. VD: bai1.py,bai2.py,bai3.py",
    )
    parser.add_argument(
        "--bai-range",
        default="",
        help="Tao nhanh danh sach bai theo khoang. VD: 1-5 se sinh bai1.py..bai5.py",
    )
    parser.add_argument(
        "--assignment",
        default="",
        help="Noi dung de bai de tool cham muc do khop va logic code",
    )
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.9,
        help="Nguong phat hien tuong dong code (0..1)",
    )
    parser.add_argument(
        "--summary-csv",
        default="",
        help="Duong dan CSV tong hop ket qua cham bai",
    )

    args = parser.parse_args()

    token = args.token.strip() or None
    max_workers = max(1, min(32, args.max_workers))
    similarity_threshold = max(0.5, min(1.0, args.similarity_threshold))
    spec = build_spec_from_args(args)

    try:
        report = build_report(args.sheet_url, token, spec, max_workers, similarity_threshold)
    except Exception as e:
        print(f"Loi: {e}")
        return 1

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    csv_output_path = args.summary_csv.strip()
    if not csv_output_path and report.get("exercise_check", {}).get("enabled"):
        if args.output.lower().endswith(".json"):
            csv_output_path = args.output[:-5] + "_summary.csv"
        else:
            csv_output_path = args.output + "_summary.csv"

    if csv_output_path:
        write_exercise_summary_csv(report, csv_output_path)

    print_summary(report)
    print(f"\nDa luu bao cao JSON tai: {args.output}")
    if csv_output_path:
        print(f"Da luu bao cao CSV tai: {csv_output_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
