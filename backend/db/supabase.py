from dotenv import load_dotenv
import httpx
import os

load_dotenv()


def _url() -> str:
    return os.getenv("SUPABASE_URL", "").rstrip("/")


def _headers() -> dict:
    key = (
        os.getenv("SUPABASE_SECRET_KEY") or
        os.getenv("SUPABASE_SERVICE_ROLE_KEY") or ""
    )
    return {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def upsert_user(user_data: dict) -> dict:
    provider = user_data.get("provider", "github")
    if provider == "gitlab":
        conflict_col = "gitlab_id"
    elif provider == "bitbucket":
        conflict_col = "bitbucket_id"
    else:
        conflict_col = "github_id"

    with httpx.Client() as client:
        res = client.post(
            f"{_url()}/rest/v1/users",
            headers={**_headers(), "Prefer": f"resolution=merge-duplicates,return=representation"},
            params={"on_conflict": conflict_col},
            json=user_data,
        )
        res.raise_for_status()
        data = res.json()
        return data[0] if data else {}


def get_user_by_id(user_id: str) -> dict | None:
    with httpx.Client() as client:
        res = client.get(
            f"{_url()}/rest/v1/users",
            headers=_headers(),
            params={"id": f"eq.{user_id}", "select": "*"},
        )
        res.raise_for_status()
        data = res.json()
        return data[0] if data else None


def get_user_by_github_id(github_id: int) -> dict | None:
    with httpx.Client() as client:
        res = client.get(
            f"{_url()}/rest/v1/users",
            headers=_headers(),
            params={"github_id": f"eq.{github_id}", "select": "*"},
        )
        res.raise_for_status()
        data = res.json()
        return data[0] if data else None


def save_doc(doc_data: dict) -> dict:
    with httpx.Client() as client:
        res = client.post(
            f"{_url()}/rest/v1/docs",
            headers=_headers(),
            json=doc_data,
        )
        res.raise_for_status()
        data = res.json()
        return data[0] if data else {}


def get_docs_by_user(user_id: str) -> list:
    with httpx.Client() as client:
        res = client.get(
            f"{_url()}/rest/v1/docs",
            headers=_headers(),
            params={"user_id": f"eq.{user_id}", "select": "*", "order": "generated_at.desc"},
        )
        res.raise_for_status()
        return res.json() or []


def get_client():
    """Compatibilità con codice esistente che chiama get_client()."""
    class _Compat:
        def table(self, name):
            return _Table(name)
    return _Compat()


class _Table:
    def __init__(self, name):
        self._name = name
        self._filters = {}
        self._select_cols = "*"
        self._order_col = None
        self._limit_n = None

    def select(self, cols="*"):
        self._select_cols = cols
        return self

    def eq(self, col, val):
        self._filters[col] = f"eq.{val}"
        return self

    def order(self, col, desc=False):
        self._order_col = f"{col}.{'desc' if desc else 'asc'}"
        return self

    def limit(self, n):
        self._limit_n = n
        return self

    def upsert(self, data, on_conflict=None):
        self._upsert_data = data
        self._on_conflict = on_conflict
        return self

    def insert(self, data):
        self._insert_data = data
        return self

    def execute(self):
        params = {"select": self._select_cols}
        for col, val in self._filters.items():
            params[col] = val
        if self._order_col:
            params["order"] = self._order_col
        if self._limit_n:
            params["limit"] = self._limit_n

        base = f"{_url()}/rest/v1/{self._name}"

        with httpx.Client() as client:
            if hasattr(self, "_upsert_data"):
                headers = {**_headers(), "Prefer": f"resolution=merge-duplicates,return=representation"}
                if self._on_conflict:
                    params["on_conflict"] = self._on_conflict
                res = client.post(base, headers=headers, params=params, json=self._upsert_data)
            elif hasattr(self, "_insert_data"):
                res = client.post(base, headers=_headers(), json=self._insert_data)
            else:
                res = client.get(base, headers=_headers(), params=params)
            res.raise_for_status()
            return type("R", (), {"data": res.json()})()

