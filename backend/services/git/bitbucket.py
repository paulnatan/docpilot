"""Provider Bitbucket — implementazione di BaseGitProvider per Bitbucket.org."""
import httpx
import os
from typing import Optional
from .base import BaseGitProvider

BB_API = "https://api.bitbucket.org/2.0"


class BitbucketProvider(BaseGitProvider):

    async def get_repos(self) -> list:
        """Recupera tutti i repo Bitbucket dell'utente (tutti i workspace)."""
        repos = []
        url = f"{BB_API}/repositories"
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"role": "member", "pagelen": 50},
                )
                response.raise_for_status()
                data = response.json()
                for r in data.get("values", []):
                    repos.append({
                        "id": r["uuid"],
                        "name": r["slug"],
                        "full_name": r["full_name"],
                        "description": r.get("description"),
                        "private": r.get("is_private", False),
                        "html_url": r["links"]["html"]["href"],
                        "default_branch": r.get("mainbranch", {}).get("name", "main"),
                    })
                url = data.get("next")  # Bitbucket paginazione via URL
        return repos

    async def get_default_branch(self, repo_full_name: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BB_API}/repositories/{repo_full_name}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            response.raise_for_status()
            return response.json().get("mainbranch", {}).get("name", "main")

    async def get_repo_tree(self, repo_full_name: str, branch: str) -> list:
        """Recupera l'albero dei file del repo (paginato)."""
        items = []
        url = f"{BB_API}/repositories/{repo_full_name}/src/{branch}/"
        async with httpx.AsyncClient() as client:
            while url:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {self.access_token}"},
                    params={"pagelen": 100},
                )
                if response.status_code != 200:
                    break
                data = response.json()
                for entry in data.get("values", []):
                    items.append({
                        "path": entry["path"],
                        "type": "blob" if entry["type"] == "commit_file" else "tree",
                    })
                # Segui la paginazione
                next_url = data.get("next")
                url = next_url if next_url else None
        return items

    async def get_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BB_API}/repositories/{repo_full_name}/src/HEAD/{file_path}",
                headers={"Authorization": f"Bearer {self.access_token}"},
            )
            if response.status_code == 200:
                return response.text
            return None

    async def get_recent_commits(self, repo_full_name: str, per_page: int = 20) -> list:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{BB_API}/repositories/{repo_full_name}/commits",
                headers={"Authorization": f"Bearer {self.access_token}"},
                params={"pagelen": per_page},
            )
            response.raise_for_status()
            data = response.json()
            # Normalizza al formato GitHub usato dall'AI
            return [
                {
                    "sha": c["hash"],
                    "commit": {
                        "message": c["message"].strip(),
                        "author": {"name": c.get("author", {}).get("user", {}).get("display_name", "")},
                    },
                }
                for c in data.get("values", [])
            ]

    async def push_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
    ) -> dict:
        """Crea o aggiorna un file su Bitbucket via multipart form."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BB_API}/repositories/{repo_full_name}/src",
                headers={"Authorization": f"Bearer {self.access_token}"},
                data={
                    "message": commit_message,
                    "branch": branch,
                    file_path: content,
                },
            )
            response.raise_for_status()
            return {"success": True}


# ── Funzioni standalone per auth.py ─────────────────────────────────────────

async def exchange_code_for_token(code: str) -> str:
    """Bitbucket usa Basic Auth con client_id:client_secret per il token exchange."""
    import base64
    client_id = os.getenv("BITBUCKET_CLIENT_ID", "")
    client_secret = os.getenv("BITBUCKET_CLIENT_SECRET", "")
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://bitbucket.org/site/oauth2/access_token",
            headers={
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data={
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": os.getenv("BITBUCKET_REDIRECT_URI"),
            },
        )
        data = response.json()
        if "access_token" not in data:
            raise ValueError(f"Bitbucket OAuth fallito: {data}")
        return data["access_token"]


async def get_user_profile(access_token: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BB_API}/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()
        # Normalizza al formato GitHub
        return {
            "id": data.get("account_id", data.get("uuid", "")),
            "login": data.get("username", data.get("nickname", "")),
            "email": None,
            "avatar_url": data.get("links", {}).get("avatar", {}).get("href", ""),
        }
