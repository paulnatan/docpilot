from fastapi import APIRouter, HTTPException
from fastapi.responses import RedirectResponse
from db.supabase import upsert_user
from jose import jwt
import os

router = APIRouter()

# Protezione doppia chiamata — codici già usati
_used_codes: set = set()


def create_session_token(user_id: str) -> str:
    return jwt.encode(
        {"sub": user_id},
        os.getenv("SECRET_KEY", "dev_secret"),
        algorithm="HS256",
    )


# ── GitHub ────────────────────────────────────────────────────────────────────

@router.get("/login")
@router.get("/login/github")
def login_github():
    client_id = os.getenv("GITHUB_CLIENT_ID")
    redirect_uri = os.getenv("GITHUB_REDIRECT_URI")
    scope = "read:user user:email repo"
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope={scope}"
    )
    return RedirectResponse(url)


@router.get("/callback/github")
@router.get("/callback")
async def callback_github(code: str):
    from services.git.github import exchange_code_for_token, get_user_profile
    if code in _used_codes:
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(f"{frontend_url}/index.html?error=already_used")
    _used_codes.add(code)
    try:
        print(f"[AUTH] Scambio codice GitHub...")
        access_token = await exchange_code_for_token(code)
        print(f"[AUTH] Token ottenuto OK")
        profile = await get_user_profile(access_token)
        print(f"[AUTH] Profilo ottenuto: {profile.get('login')}")

        user_data = {
            "github_id": profile["id"],
            "username": profile["login"],
            "email": profile.get("email"),
            "avatar_url": profile.get("avatar_url"),
            "access_token": access_token,
            "provider": "github",
        }
        print(f"[AUTH] Upsert su Supabase...")
        user = upsert_user(user_data)
        print(f"[AUTH] Upsert OK: {user.get('id')}")

        session_token = create_session_token(str(user["id"]))
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(f"{frontend_url}/dashboard.html?token={session_token}")

    except Exception as e:
        print(f"[AUTH ERROR] {type(e).__name__}: {e}")
        raise HTTPException(status_code=400, detail=str(e))


# ── GitLab ────────────────────────────────────────────────────────────────────

@router.get("/login/gitlab")
def login_gitlab():
    client_id = os.getenv("GITLAB_CLIENT_ID")
    redirect_uri = os.getenv("GITLAB_REDIRECT_URI")
    scope = "read_user read_api read_repository write_repository"
    url = (
        f"https://gitlab.com/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
        f"&scope={scope}"
    )
    return RedirectResponse(url)


@router.get("/callback/gitlab")
async def callback_gitlab(code: str):
    from services.git.gitlab import exchange_code_for_token, get_user_profile
    try:
        access_token = await exchange_code_for_token(code)
        profile = await get_user_profile(access_token)

        user_data = {
            "gitlab_id": profile["id"],
            "username": profile.get("username", profile.get("login", "")),
            "email": profile.get("email"),
            "avatar_url": profile.get("avatar_url"),
            "access_token": access_token,
            "provider": "gitlab",
        }
        user = upsert_user(user_data)

        session_token = create_session_token(str(user["id"]))
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(f"{frontend_url}/dashboard.html?token={session_token}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Bitbucket ─────────────────────────────────────────────────────────────────

@router.get("/login/bitbucket")
def login_bitbucket():
    client_id = os.getenv("BITBUCKET_CLIENT_ID")
    redirect_uri = os.getenv("BITBUCKET_REDIRECT_URI")
    url = (
        f"https://bitbucket.org/site/oauth2/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri={redirect_uri}"
        f"&response_type=code"
    )
    return RedirectResponse(url)


@router.get("/callback/bitbucket")
async def callback_bitbucket(code: str):
    from services.git.bitbucket import exchange_code_for_token, get_user_profile
    try:
        access_token = await exchange_code_for_token(code)
        profile = await get_user_profile(access_token)

        user_data = {
            "bitbucket_id": str(profile["id"]),
            "username": profile.get("login", ""),
            "email": profile.get("email"),
            "avatar_url": profile.get("avatar_url"),
            "access_token": access_token,
            "provider": "bitbucket",
        }
        user = upsert_user(user_data)

        session_token = create_session_token(str(user["id"]))
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
        return RedirectResponse(f"{frontend_url}/dashboard.html?token={session_token}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ── Me (comune a tutti i provider) ───────────────────────────────────────────

@router.get("/me")
async def me(token: str):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "dev_secret"), algorithms=["HS256"])
        user_id = payload["sub"]
        from db.supabase import get_client
        result = get_client().table("users").select("id,username,avatar_url,email,provider,plan").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return result.data[0]
    except Exception:
        raise HTTPException(status_code=401, detail="Token non valido")
