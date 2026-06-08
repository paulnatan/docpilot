"""
Factory — restituisce il provider Git giusto in base al campo 'provider' dell'utente.
Uso:
    provider = get_git_provider(user["provider"], user["access_token"])
    repos = await provider.get_repos()
"""
from services.git.base import BaseGitProvider
from services.git.github import GitHubProvider
from services.git.gitlab import GitLabProvider
from services.git.bitbucket import BitbucketProvider


def get_git_provider(provider_name: str, access_token: str) -> BaseGitProvider:
    provider_name = (provider_name or "github").lower()
    if provider_name == "github":
        return GitHubProvider(access_token)
    elif provider_name == "gitlab":
        return GitLabProvider(access_token)
    elif provider_name == "bitbucket":
        return BitbucketProvider(access_token)
    else:
        raise ValueError(f"Provider non supportato: {provider_name}")
