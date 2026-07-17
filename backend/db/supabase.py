from supabase import create_client, Client
from dotenv import load_dotenv
import httpx
import os

load_dotenv()

_client: Client | None = None


def _get_key() -> str:
    """Prova prima la nuova secret key, poi la legacy service_role key."""
    return (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
    )


def get_client() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = _get_key()
        if not url or not key:
            raise RuntimeError("SUPABASE_URL e chiave Supabase mancanti")
        _client = create_client(url, key)
    return _client


def upsert_user(user_data: dict) -> dict:
    """Upsert intelligente: usa github_id per GitHub, gitlab_id per GitLab, bitbucket_id per Bitbucket."""
    client = get_client()
    provider = user_data.get("provider", "github")

    if provider == "gitlab":
        conflict_col = "gitlab_id"
    elif provider == "bitbucket":
        conflict_col = "bitbucket_id"
    else:
        conflict_col = "github_id"

    result = client.table("users").upsert(user_data, on_conflict=conflict_col).execute()
    return result.data[0] if result.data else {}


def get_user_by_github_id(github_id: int) -> dict | None:
    client = get_client()
    result = client.table("users").select("*").eq("github_id", github_id).execute()
    return result.data[0] if result.data else None


def save_doc(doc_data: dict) -> dict:
    client = get_client()
    result = client.table("docs").insert(doc_data).execute()
    return result.data[0] if result.data else {}


def get_docs_by_user(user_id: str) -> list:
    client = get_client()
    result = (
        client.table("docs")
        .select("*")
        .eq("user_id", user_id)
        .order("generated_at", desc=True)
        .execute()
    )
    return result.data or []
