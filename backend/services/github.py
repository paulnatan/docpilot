"""
Backward-compatibility shim.
Importa tutto da services.git.github per non rompere eventuali import diretti.
"""
from services.git.github import (
    GitHubProvider,
    exchange_code_for_token,
    get_user_profile,
)

# Funzioni standalone usate direttamente da vecchio codice
async def get_user_repos(access_token: str) -> list:
    return await GitHubProvider(access_token).get_repos()

async def get_default_branch(access_token: str, repo_full_name: str) -> str:
    return await GitHubProvider(access_token).get_default_branch(repo_full_name)

async def get_repo_tree(access_token: str, repo_full_name: str, branch: str = "main") -> list:
    return await GitHubProvider(access_token).get_repo_tree(repo_full_name, branch)

async def get_file_content(access_token: str, repo_full_name: str, file_path: str):
    return await GitHubProvider(access_token).get_file_content(repo_full_name, file_path)

async def get_recent_commits(access_token: str, repo_full_name: str, per_page: int = 20) -> list:
    return await GitHubProvider(access_token).get_recent_commits(repo_full_name, per_page)

async def push_file_to_repo(access_token: str, repo_full_name: str, file_path: str, content: str, commit_message: str, branch: str = "main") -> dict:
    return await GitHubProvider(access_token).push_file(repo_full_name, file_path, content, commit_message, branch)
