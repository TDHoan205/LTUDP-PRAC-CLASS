"""
Tool: Kiem tra link GitHub trong Google Sheet va thong ke dong gop code.

Muc tieu:
1) Dem bao nhieu link GitHub trong sheet co truy cap duoc.
2) Tinh % dong gop cua moi thanh vien dua tren contributors API.

Yeu cau sheet:
- Sheet co the la link public.
- Tool tu dong doc CSV export tu Google Sheet URL.

Vi du chay:
python baitapclass/github_sheet_tool.py --sheet-url "https://docs.google.com/spreadsheets/d/<SHEET_ID>/edit#gid=0"

Co the dung token de tang gioi han API:
set GITHUB_TOKEN=ghp_xxx
python baitapclass/github_sheet_tool.py --sheet-url "..."
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import parse_qs, urlencode, urlparse
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


GITHUB_REPO_PATTERN = re.compile(r"https?://github\.com/[^\s,;]+", re.IGNORECASE)
DEFAULT_TIMEOUT = 20
MAX_WORKERS = min(16, max(4, (os.cpu_count() or 4) * 2))


@dataclass
class Submission:
    row_number: int
    repo_url: str
    repo_full_name: str
    accessible: bool = False
    status_code: int = 0
    error: str = ""


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


def fetch_csv_rows(csv_url: str, timeout: int = 20) -> List[Dict[str, str]]:
    req = Request(csv_url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=timeout) as resp:
        content = resp.read().decode("utf-8-sig", errors="replace")

    reader = csv.DictReader(content.splitlines())
    return [dict(row) for row in reader]


def sanitize_github_url(url: str) -> str:
    return url.strip().rstrip(").,;\"' ")


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
    # Deduplicate URLs inside one row to reduce duplicated checks.
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


def github_api_get_json(path: str, token: Optional[str], timeout: int = DEFAULT_TIMEOUT) -> Tuple[Optional[object], int, str]:
    url = f"https://api.github.com{path}"
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "github-sheet-tool",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data, resp.status, ""
    except HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
        except Exception:
            body = str(e)
        return None, e.code, body
    except URLError as e:
        return None, 0, str(e)


def check_repo_access(repo_full_name: str, token: Optional[str]) -> Tuple[bool, int, str]:
    data, status, error = github_api_get_json(f"/repos/{repo_full_name}", token)
    if data is not None and 200 <= status < 300:
        return True, status, ""
    return False, status, error


def fetch_all_contributors(repo_full_name: str, token: Optional[str]) -> Tuple[List[Dict[str, object]], str]:
    contributors: List[Dict[str, object]] = []
    page = 1

    while True:
        data, status, error = github_api_get_json(
            f"/repos/{repo_full_name}/contributors?per_page=100&page={page}",
            token,
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


def check_repo_access_parallel(repo_names: Iterable[str], token: Optional[str]) -> Dict[str, Tuple[bool, int, str]]:
    results: Dict[str, Tuple[bool, int, str]] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(check_repo_access, repo, token): repo for repo in repo_names}
        for future in as_completed(futures):
            repo = futures[future]
            try:
                results[repo] = future.result()
            except Exception as e:
                results[repo] = (False, 0, str(e))
    return results


def fetch_contributors_parallel(repo_names: Iterable[str], token: Optional[str]) -> Tuple[Dict[str, List[Dict[str, object]]], List[str]]:
    contributor_data: Dict[str, List[Dict[str, object]]] = {}
    warnings: List[str] = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_all_contributors, repo, token): repo for repo in repo_names}
        for future in as_completed(futures):
            repo = futures[future]
            try:
                contributors, warn = future.result()
                contributor_data[repo] = contributors
                if warn:
                    warnings.append(warn)
            except Exception as e:
                warnings.append(f"[{repo}] contributors fetch failed: {e}")
    return contributor_data, warnings


def collect_submissions(rows: List[Dict[str, str]]) -> List[Submission]:
    submissions: List[Submission] = []
    for idx, row in enumerate(rows, start=2):
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
                )
            )
    return submissions


def build_report(sheet_url: str, token: Optional[str]) -> Dict[str, object]:
    csv_url = normalize_google_sheet_to_csv_url(sheet_url)
    rows = fetch_csv_rows(csv_url)
    submissions = collect_submissions(rows)

    unique_repos = sorted({s.repo_full_name for s in submissions})
    repo_access_cache = check_repo_access_parallel(unique_repos, token)

    for item in submissions:
        ok, status, err = repo_access_cache.get(item.repo_full_name, (False, 0, "unknown error"))
        item.accessible = ok
        item.status_code = status
        item.error = err[:200]

    total_submitted_links = len(submissions)
    accessible_links = sum(1 for s in submissions if s.accessible)

    unique_accessible_repos = sorted({s.repo_full_name for s in submissions if s.accessible})

    contribution_counts: Dict[str, int] = defaultdict(int)
    contributor_data, warnings = fetch_contributors_parallel(unique_accessible_repos, token)
    for repo in unique_accessible_repos:
        contributors = contributor_data.get(repo, [])
        for c in contributors:
            login = str(c.get("login", "unknown"))
            commits = int(c.get("contributions", 0))
            contribution_counts[login] += commits

    total_commits = sum(contribution_counts.values())
    contribution_percent = []
    for login, commits in sorted(contribution_counts.items(), key=lambda x: x[1], reverse=True):
        percent = (commits / total_commits * 100.0) if total_commits else 0.0
        contribution_percent.append(
            {
                "member": login,
                "commits": commits,
                "percent": round(percent, 2),
            }
        )

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
    for repo in repos[:10]:
        print(f"  - {repo}")
    if len(repos) > 10:
        print(f"  ... and {len(repos) - 10} more")

    print("\n=== % DONG GOP THEO CONTRIBUTORS (dua tren commit count) ===")
    contribs = report.get("contribution_summary", [])
    if not contribs:
        print("Khong co du lieu contributors.")
    else:
        for item in contribs:
            print(f"  - {item['member']}: {item['commits']} commits ({item['percent']}%)")

    warnings = report.get("warnings", [])
    if warnings:
        print("\n=== CANH BAO ===")
        for w in warnings[:10]:
            print(f"  - {w}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Kiem tra GitHub links trong Google Sheet va thong ke dong gop code.",
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
    args = parser.parse_args()

    token = args.token.strip() or None

    try:
        report = build_report(args.sheet_url, token)
    except Exception as e:
        print(f"Loi: {e}")
        return 1

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print_summary(report)
    print(f"\nDa luu bao cao JSON tai: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
