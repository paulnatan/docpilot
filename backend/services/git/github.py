"""Provider GitHub — implementazione di BaseGitProvider per GitHub."""
import httpx
import base64
import os
from typing import Optional
from .base import BaseGitProvider

GITHUB_API = "https://api.github.com"


class GitHubProvider(BaseGitProvider):

    async def get_repos(self) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API}/user/repos",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"sort": "updated", "per_page": 50},
            )
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "full_name": r["full_name"],
                    "description": r.get("description"),
                    "private": r["private"],
                    "html_url": r["html_url"],
                    "default_branch": r.get("default_branch", "main"),
                }
                for r in data
            ]

    async def get_default_branch(self, repo_full_name: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API}/repos/{repo_full_name}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("default_branch", "main")

    async def get_repo_tree(self, repo_full_name: str, branch: str) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API}/repos/{repo_full_name}/git/trees/{branch}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"recursive": "1"},
            )
            response.raise_for_status()
            return response.json().get("tree", [])

    async def get_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API}/repos/{repo_full_name}/contents/{file_path}",
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Accept": "application/vnd.github.raw+json",
                },
            )
            if response.status_code == 200:
                return response.text
            return None

    async def get_recent_commits(self, repo_full_name: str, per_page: int = 20) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITHUB_API}/repos/{repo_full_name}/commits",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"per_page": per_page},
            )
            response.raise_for_status()
            return response.json()

    async def push_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
    ) -> dict:
        async with httpx.AsyncClient() as client:
            # Controlla se il file esiste già (serve SHA per aggiornare)
            check = await client.get(
                f"{GITHUB_API}/repos/{repo_full_name}/contents/{file_path}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"ref": branch},
            )
            payload = {
                "message": commit_message,
                "content": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                "branch": branch,
            }
            if check.status_code == 200:
                payload["sha"] = check.json().get("sha")

            response = await client.put(
                f"{GITHUB_API}/repos/{repo_full_name}/contents/{file_path}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()


# ── Funzioni standalone (backward-compat per auth.py) ─────────────────────────

async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "code": code,
                "redirect_uri": os.getenv("GITHUB_REDIRECT_URI"),
            },
        )
        data = response.json()
        if "access_token" not in data:
            raise ValueError(f"GitHub OAuth fallito: {data}")
        return data["access_token"]


async def get_user_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITHUB_API}/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
