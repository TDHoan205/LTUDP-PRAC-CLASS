from __future__ import annotations

from typing import Any, Dict

from github_sheet_tool_lib.core import GithubClient


class GitHubService:
    def __init__(self, token: str | None = None) -> None:
        self.client = GithubClient(token)

    def latest_commit(self, repo_full_name: str) -> str:
        data, status, _ = self.client._request_json(f"/repos/{repo_full_name}/commits?per_page=1")  # pylint: disable=protected-access
        if status >= 400 or not isinstance(data, list) or not data:
            return ""
        first = data[0]
        commit_obj = first.get("commit", {}) if isinstance(first, dict) else {}
        author_obj = commit_obj.get("author", {}) if isinstance(commit_obj, dict) else {}
        return str(author_obj.get("date", "")) if isinstance(author_obj, dict) else ""

    def repo_overview(self, repo_full_name: str) -> Dict[str, Any]:
        data, status, _ = self.client._request_json(f"/repos/{repo_full_name}")  # pylint: disable=protected-access
        if status >= 400 or not isinstance(data, dict):
            return {"ok": False, "repo": repo_full_name}
        return {
            "ok": True,
            "repo": repo_full_name,
            "default_branch": data.get("default_branch", ""),
            "stargazers_count": data.get("stargazers_count", 0),
            "forks_count": data.get("forks_count", 0),
        }
