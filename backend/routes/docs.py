import asyncio
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

# Messaggi di errore "umani" mostrati all'utente al posto del raw error dell'AI provider,
# tradotti nelle lingue supportate dall'app.
FRIENDLY_ERRORS = {
    "overloaded": {
        "it": "Il servizio AI è momentaneamente sovraccarico. Riprova tra qualche minuto.",
        "en": "The AI service is temporarily overloaded. Please try again in a few minutes.",
        "fr": "Le service IA est temporairement surchargé. Réessayez dans quelques minutes.",
        "de": "Der KI-Dienst ist vorübergehend überlastet. Bitte versuche es in ein paar Minuten erneut.",
        "es": "El servicio de IA está momentáneamente sobrecargado. Inténtalo de nuevo en unos minutos.",
    },
    "rate_limit": {
        "it": "Abbiamo raggiunto il limite di richieste momentaneo. Riprova tra qualche minuto.",
        "en": "We've hit a temporary request limit. Please try again in a few minutes.",
        "fr": "Nous avons atteint une limite de requêtes temporaire. Réessayez dans quelques minutes.",
        "de": "Wir haben vorübergehend ein Anfragelimit erreicht. Bitte versuche es in ein paar Minuten erneut.",
        "es": "Hemos alcanzado un límite temporal de solicitudes. Inténtalo de nuevo en unos minutos.",
    },
    "auth": {
        "it": "Errore di configurazione del servizio AI. Il nostro team è stato avvisato.",
        "en": "AI service configuration error. Our team has been notified.",
        "fr": "Erreur de configuration du service IA. Notre équipe a été informée.",
        "de": "Konfigurationsfehler des KI-Dienstes. Unser Team wurde benachrichtigt.",
        "es": "Error de configuración del servicio de IA. Nuestro equipo ha sido notificado.",
    },
    "timeout": {
        "it": "La generazione ha impiegato troppo tempo. Riprova, magari su un repository più piccolo.",
        "en": "The generation took too long. Please try again, maybe with a smaller repository.",
        "fr": "La génération a pris trop de temps. Réessayez, éventuellement avec un dépôt plus petit.",
        "de": "Die Generierung hat zu lange gedauert. Versuche es erneut, eventuell mit einem kleineren Repository.",
        "es": "La generación tardó demasiado. Inténtalo de nuevo, quizás con un repositorio más pequeño.",
    },
    "generic": {
        "it": "Si è verificato un errore imprevisto durante la generazione. Riprova più tardi.",
        "en": "An unexpected error occurred during generation. Please try again later.",
        "fr": "Une erreur inattendue s'est produite lors de la génération. Réessayez plus tard.",
        "de": "Während der Generierung ist ein unerwarteter Fehler aufgetreten. Bitte versuche es später erneut.",
        "es": "Se produjo un error inesperado durante la generación. Inténtalo de nuevo más tarde.",
    },
}


def _friendly_error_message(e: Exception, lang: str = "it") -> str:
    """Converte un'eccezione tecnica in un messaggio comprensibile per l'utente."""
    lang = lang if lang in ("it", "en", "fr", "de", "es") else "it"
    text = str(e).lower()

    if "503" in text or "overloaded" in text or "unavailable" in text:
        key = "overloaded"
    elif "429" in text or "rate limit" in text or "resource_exhausted" in text or "quota" in text:
        key = "rate_limit"
    elif "401" in text or "403" in text or "api_key" in text or "permission" in text:
        key = "auth"
    elif "timeout" in text or "timed out" in text:
        key = "timeout"
    else:
        key = "generic"

    return FRIENDLY_ERRORS[key][lang]

SUPPORTED_EXTENSIONS = {
    # Backend / general purpose
    ".py", ".js", ".ts", ".go", ".java", ".rb", ".php", ".cs", ".cpp", ".c", ".h", ".hpp",
    ".rs", ".dart", ".swift", ".kt", ".scala", ".ex", ".exs", ".lua", ".r", ".pl", ".m", ".mm",
    # Frontend
    ".vue", ".jsx", ".tsx", ".html", ".css", ".scss", ".sass", ".less",
    # Config / infra / db
    ".sql", ".sh", ".yaml", ".yml", ".json", ".toml",
}

# File da escludere anche se hanno estensione supportata (lock file, build, dipendenze)
EXCLUDE_PATTERNS = (
    "node_modules/", "dist/", "build/", "vendor/", ".min.", "__pycache__/",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "composer.lock",
    "Pipfile.lock", "Gemfile.lock", ".next/", "target/", ".venv/", "venv/",
)

# File "importanti" — se trovati, hanno priorità nell'analisi
PRIORITY_NAMES = (
    "main", "index", "app", "server", "api", "router", "routes",
    "config", "settings", "schema", "models",
)

MAX_FILES = 60
MAX_CHARS_PER_FILE = 3000


def _select_relevant_files(tree: list, limit: int) -> list:
    """Seleziona i file di codice più rilevanti da analizzare, fino a `limit`.

    Priorità:
    1. Esclude file in cartelle di build/dipendenze e lock file
    2. File con nomi "importanti" (main, index, app, ecc.) per primi
    3. File nella root o a basso livello di annidamento
    4. Ordine alfabetico come fallback
    """
    candidates = [
        item["path"] for item in tree
        if item["type"] == "blob"
        and any(item["path"].endswith(ext) for ext in SUPPORTED_EXTENSIONS)
        and not any(pattern in item["path"] for pattern in EXCLUDE_PATTERNS)
    ]

    def score(path: str):
        depth = path.count("/")
        filename = path.rsplit("/", 1)[-1].lower()
        is_priority = any(name in filename for name in PRIORITY_NAMES)
        return (0 if is_priority else 1, depth, path.lower())

    candidates.sort(key=score)
    return candidates[:limit]


async def _fetch_files_content(provider, repo_full_name: str, code_files: list, max_chars: int = MAX_CHARS_PER_FILE) -> str:
    """Scarica il contenuto di più file in parallelo (limite di concorrenza) per
    velocizzare la generazione su repository con molti file."""
    semaphore = asyncio.Semaphore(10)

    async def fetch_one(path: str):
        async with semaphore:
            content = await provider.get_file_content(repo_full_name, path)
            return path, content

    results = await asyncio.gather(*(fetch_one(p) for p in code_files))

    contents = []
    for path, content in results:
        if content:
            contents.append(f"### {path}\n```\n{content[:max_chars]}\n```")
    return "\n\n".join(contents)


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
        raise HTTPException(status_code=500, detail=_friendly_error_message(e, request.lang or "it"))


async def _generate_inner(request: GenerateRequest, user: dict, provider):

    file_tree_str = ""
    file_contents_str = ""
    commits_str = ""

    if request.doc_type in ("readme", "api_docs", "overview", "openapi", "sdk"):
        branch = request.branch or await provider.get_default_branch(request.repo_full_name)
        tree = await provider.get_repo_tree(request.repo_full_name, branch)

        code_files = _select_relevant_files(tree, MAX_FILES)

        file_tree_str = "\n".join(item["path"] for item in tree if item["type"] == "blob")

        file_contents_str = await _fetch_files_content(provider, request.repo_full_name, code_files)

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
                and not any(pattern in item["path"] for pattern in EXCLUDE_PATTERNS)
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
        code_files = _select_relevant_files(tree, MAX_FILES)

        file_tree_str = "\n".join(item["path"] for item in tree if item["type"] == "blob")
        file_contents_str = await _fetch_files_content(provider, repo_name, code_files)

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
