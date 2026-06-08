"""Provider GitLab — implementazione di BaseGitProvider per GitLab.com."""
import httpx
import base64
import os
from urllib.parse import quote
from typing import Optional
from .base import BaseGitProvider

GITLAB_API = "https://gitlab.com/api/v4"


def _encode(path: str) -> str:
    """URL-encode un path per le API GitLab (es. 'owner/repo' → 'owner%2Frepo')."""
    return quote(path, safe="")


class GitLabProvider(BaseGitProvider):

    async def get_repos(self) -> list:
        """Restituisce i progetti dell'utente (membership=true, ordinati per ultima attività)."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITLAB_API}/projects",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={
                    "membership": "true",
                    "per_page": 50,
                    "order_by": "last_activity_at",
                    "sort": "desc",
                },
            )
            response.raise_for_status()
            data = response.json()
            return [
                {
                    "id": r["id"],
                    "name": r["name"],
                    "full_name": r["path_with_namespace"],
                    "description": r.get("description"),
                    "private": r.get("visibility") == "private",
                    "html_url": r.get("web_url", ""),
                    "default_branch": r.get("default_branch", "main"),
                }
                for r in data
            ]

    async def get_default_branch(self, repo_full_name: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITLAB_API}/projects/{_encode(repo_full_name)}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("default_branch", "main")

    async def get_repo_tree(self, repo_full_name: str, branch: str) -> list:
        """Recupera l'albero ricorsivo di tutti i file del repo."""
        items = []
        page = 1
        async with httpx.AsyncClient() as client:
            while True:
                response = await client.get(
                    f"{GITLAB_API}/projects/{_encode(repo_full_name)}/repository/tree",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={
                        "ref": branch,
                        "recursive": "true",
                        "per_page": 100,
                        "page": page,
                    },
                )
                response.raise_for_status()
                batch = response.json()
                if not batch:
                    break
                # Normalizza al formato usato da GitHub (type: blob/tree, path)
                for item in batch:
                    items.append({
                        "path": item["path"],
                        "type": "blob" if item["type"] == "blob" else "tree",
                    })
                # GitLab usa X-Next-Page per la paginazione
                next_page = response.headers.get("X-Next-Page")
                if not next_page:
                    break
                page = int(next_page)
        return items

    async def get_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITLAB_API}/projects/{_encode(repo_full_name)}/repository/files/{_encode(file_path)}/raw",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            if response.status_code == 200:
                return response.text
            return None

    async def get_recent_commits(self, repo_full_name: str, per_page: int = 20) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{GITLAB_API}/projects/{_encode(repo_full_name)}/repository/commits",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"per_page": per_page},
            )
            response.raise_for_status()
            data = response.json()
            # Normalizza al formato GitHub usato dall'AI
            return [
                {
                    "sha": c["id"],
                    "commit": {
                        "message": c["title"],
                        "author": {"name": c.get("author_name", "")},
                    },
                }
                for c in data
            ]

    async def push_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
    ) -> dict:
        encoded_project = _encode(repo_full_name)
        encoded_file = _encode(file_path)
        content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

        async with httpx.AsyncClient() as client:
            # Controlla se il file esiste già
            check = await client.get(
                f"{GITLAB_API}/projects/{encoded_project}/repository/files/{encoded_file}",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"ref": branch},
            )

            payload = {
                "branch": branch,
                "content": content_b64,
                "encoding": "base64",
                "commit_message": commit_message,
            }

            if check.status_code == 200:
                # File esiste → aggiorna (PUT)
                response = await client.put(
                    f"{GITLAB_API}/projects/{encoded_project}/repository/files/{encoded_file}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=payload,
                )
            else:
                # File non esiste → crea (POST)
                response = await client.post(
                    f"{GITLAB_API}/projects/{encoded_project}/repository/files/{encoded_file}",
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    json=payload,
                )

            response.raise_for_status()
            return response.json()


# ── Funzioni standalone per auth.py ─────────────────────────────────────────

async def exchange_code_for_token(code: str) -> str:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://gitlab.com/oauth/token",
            data={
                "client_id": os.getenv("GITLAB_CLIENT_ID"),
                "client_secret": os.getenv("GITLAB_CLIENT_SECRET"),
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": os.getenv("GITLAB_REDIRECT_URI"),
            },
        )
        data = response.json()
        if "access_token" not in data:
            raise ValueError(f"GitLab OAuth fallito: {data}")
        return data["access_token"]


async def get_user_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{GITLAB_API}/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        return response.json()
