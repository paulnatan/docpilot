from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel as _BaseModel
from models.schemas import GenerateRequest
from services.provider_factory import get_git_provider
from services.ai import generate_doc
from services.email import send_doc_ready_email
from db.supabase import save_doc, get_docs_by_user, get_client
from jose import jwt
import os

router = APIRouter()

SUPPORTED_EXTENSIONS = {".py", ".js", ".ts", ".go", ".java", ".rb", ".php", ".cs", ".cpp", ".rs", ".dart", ".swift", ".kt", ".vue", ".jsx", ".tsx"}
MAX_FILES = 30
MAX_CHARS_PER_FILE = 3000


def _get_user_from_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY", "dev_secret"), algorithms=["HS256"])
        user_id = payload["sub"]
        result = get_client().table("users").select("*").eq("id", user_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Utente non trovato")
        return result.data[0]
    except Exception:
        raise HTTPException(status_code=401, detail="Token non valido")


@router.get("/repos")
async def list_repos(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)
    provider = get_git_provider(user.get("provider", "github"), user["access_token"])
    repos = await provider.get_repos()
    return repos


@router.post("/generate")
async def generate(request: GenerateRequest, authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)
    provider = get_git_provider(user.get("provider", "github"), user["access_token"])
    try:
        return await _generate_inner(request, user, provider)
    except HTTPException:
        raise
    except Exception as e:
        print(f"[GENERATE ERROR] {request.doc_type} — {request.repo_full_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Errore nella generazione: {str(e)}")


async def _generate_inner(request: GenerateRequest, user: dict, provider):

    file_tree_str = ""
    file_contents_str = ""
    commits_str = ""

    if request.doc_type in ("readme", "api_docs", "overview", "openapi", "sdk"):
        branch = request.branch or await provider.get_default_branch(request.repo_full_name)
        tree = await provider.get_repo_tree(request.repo_full_name, branch)

        file_limit = 60 if request.doc_type == "overview" else MAX_FILES

        code_files = [
            item["path"] for item in tree
            if item["type"] == "blob"
            and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
        ][:file_limit]

        file_tree_str = "\n".join(item["path"] for item in tree if item["type"] == "blob")

        contents = []
        for path in code_files:
            content = await provider.get_file_content(request.repo_full_name, path)
            if content:
                contents.append(f"### {path}\n```\n{content[:MAX_CHARS_PER_FILE]}\n```")
        file_contents_str = "\n\n".join(contents)

    elif request.doc_type == "changelog":
        commits = await provider.get_recent_commits(request.repo_full_name)
        commits_str = "\n".join(
            f"- {c['sha'][:7]} {c['commit']['message']} ({c['commit']['author']['name']})"
            for c in commits
        )

    elif request.doc_type == "comments":
        if not request.file_path:
            branch = request.branch or await provider.get_default_branch(request.repo_full_name)
            tree = await provider.get_repo_tree(request.repo_full_name, branch)
            code_files = [
                item["path"] for item in tree
                if item["type"] == "blob"
                and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
            ]
            return {"files": code_files, "select_file": True}
        else:
            content = await provider.get_file_content(request.repo_full_name, request.file_path)
            if not content:
                raise HTTPException(status_code=404, detail="File non trovato")
            file_contents_str = content

    doc_content = generate_doc(
        doc_type=request.doc_type,
        repo_name=request.repo_full_name,
        file_tree=file_tree_str,
        file_contents=file_contents_str,
        commits=commits_str,
        file_path=request.file_path or "",
        lang=request.lang or "it",
    )

    saved = save_doc({
        "user_id": user["id"],
        "repo_name": request.repo_full_name,
        "doc_type": request.doc_type,
        "content": doc_content,
        "provider": user.get("provider", "github"),
    })

    # Notifica email (non bloccante — ignora errori)
    try:
        user_email = user.get("email", "")
        if user_email and request.doc_type != "comments":
            send_doc_ready_email(
                to_email=user_email,
                username=user.get("username", ""),
                repo_name=request.repo_full_name,
                doc_type=request.doc_type,
            )
    except Exception:
        pass

    return {"id": saved.get("id"), "content": doc_content}


class PushDocRequest(_BaseModel):
    doc_id: str = ""
    repo_full_name: str
    doc_type: str
    content: str
    branch: str = "main"


@router.post("/push-to-github")
async def push_to_github(request: PushDocRequest, authorization: str = Header(...)):
    """Endpoint compatibile con tutti i provider (GitHub, GitLab, Bitbucket)."""
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)
    provider = get_git_provider(user.get("provider", "github"), user["access_token"])

    file_map = {
        "readme": "README.md",
        "changelog": "CHANGELOG.md",
        "api_docs": "docs/API.md",
        "overview": "docs/PROJECT_OVERVIEW.md",
        "openapi": "docs/openapi.yaml",
        "sdk": "docs/SDK.md",
        "comments": None,
    }

    file_path = file_map.get(request.doc_type)
    if not file_path:
        raise HTTPException(status_code=400, detail="Questo tipo di documentazione non può essere pushato")

    branch = request.branch or await provider.get_default_branch(request.repo_full_name)
    commit_message = f"docs: aggiorna {file_path} con ReadyGen 🤖"

    await provider.push_file(
        repo_full_name=request.repo_full_name,
        file_path=file_path,
        content=request.content,
        commit_message=commit_message,
        branch=branch,
    )

    return {"success": True, "file": file_path, "repo": request.repo_full_name}


@router.get("/history")
async def history(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    user = _get_user_from_token(token)
    docs = get_docs_by_user(user["id"])
    return docs


@router.post("/webhook")
async def webhook(payload: dict):
    """Riceve eventi da n8n dopo un push e genera documentazione automaticamente."""
    import asyncio

    try:
        # Supporta sia GitHub che GitLab nel payload
        repo_name = (
            payload.get("repository", {}).get("full_name")          # GitHub
            or payload.get("project", {}).get("path_with_namespace") # GitLab
            or ""
        )
        if not repo_name:
            return {"received": True, "skipped": "repo non trovato nel payload"}

        owner_username = repo_name.split("/")[0]
        result = get_client().table("users").select("*").eq("username", owner_username).execute()
        if not result.data:
            return {"received": True, "skipped": f"utente {owner_username} non trovato"}

        user = result.data[0]
        asyncio.create_task(_auto_generate(user, repo_name))

        return {"received": True, "repo": repo_name, "status": "generazione avviata"}

    except Exception as e:
        return {"received": True, "error": str(e)}


async def _auto_generate(user: dict, repo_name: str):
    """Genera README e Changelog automaticamente dopo un push (qualsiasi provider)."""
    try:
        provider = get_git_provider(user.get("provider", "github"), user["access_token"])
        branch = await provider.get_default_branch(repo_name)

        # 1. Genera README
        tree = await provider.get_repo_tree(repo_name, branch)
        code_files = [
            item["path"] for item in tree
            if item["type"] == "blob"
            and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
        ][:MAX_FILES]

        file_tree_str = "\n".join(item["path"] for item in tree if item["type"] == "blob")
        contents = []
        for path in code_files:
            content = await provider.get_file_content(repo_name, path)
            if content:
                contents.append(f"### {path}\n```\n{content[:MAX_CHARS_PER_FILE]}\n```")
        file_contents_str = "\n\n".join(contents)

        readme_content = generate_doc(
            doc_type="readme",
            repo_name=repo_name,
            file_tree=file_tree_str,
            file_contents=file_contents_str,
        )
        save_doc({"user_id": user["id"], "repo_name": repo_name, "doc_type": "readme", "content": readme_content, "provider": user.get("provider", "github")})

        # 2. Genera Changelog
        commits = await provider.get_recent_commits(repo_name)
        commits_str = "\n".join(
            f"- {c['sha'][:7]} {c['commit']['message']} ({c['commit']['author']['name']})"
            for c in commits
        )
        changelog_content = generate_doc(
            doc_type="changelog",
            repo_name=repo_name,
            commits=commits_str,
        )
        save_doc({"user_id": user["id"], "repo_name": repo_name, "doc_type": "changelog", "content": changelog_content, "provider": user.get("provider", "github")})

    except Exception as e:
        print(f"[AUTO-GENERATE ERROR] {repo_name}: {e}")
