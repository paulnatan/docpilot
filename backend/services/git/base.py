"""
Interfaccia astratta comune a tutti i provider Git.
Ogni provider (GitHub, GitLab, Bitbucket) implementa questi 6 metodi.
"""
from abc import ABC, abstractmethod
from typing import Optional


class BaseGitProvider(ABC):
    def __init__(self, access_token: str):
        self.access_token = access_token

    @abstractmethod
    async def get_repos(self) -> list:
        """Restituisce lista repo dell'utente in formato normalizzato:
        [{id, name, full_name, description, private, html_url, default_branch}]
        """
        ...

    @abstractmethod
    async def get_default_branch(self, repo_full_name: str) -> str:
        """Restituisce il branch di default del repo (es. 'main' o 'master')."""
        ...

    @abstractmethod
    async def get_repo_tree(self, repo_full_name: str, branch: str) -> list:
        """Restituisce l'albero dei file del repo in formato normalizzato:
        [{path, type}]  dove type è 'blob' (file) o 'tree' (directory)
        """
        ...

    @abstractmethod
    async def get_file_content(self, repo_full_name: str, file_path: str) -> Optional[str]:
        """Restituisce il contenuto di un file come stringa, o None se non trovato."""
        ...

    @abstractmethod
    async def get_recent_commits(self, repo_full_name: str, per_page: int = 20) -> list:
        """Restituisce lista commit recenti in formato normalizzato:
        [{sha, commit: {message, author: {name}}}]
        """
        ...

    @abstractmethod
    async def push_file(
        self,
        repo_full_name: str,
        file_path: str,
        content: str,
        commit_message: str,
        branch: str,
    ) -> dict:
        """Crea o aggiorna un file nel repo. Restituisce la risposta dell'API."""
        ...
