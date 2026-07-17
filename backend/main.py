from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import asyncio
import httpx
import os

load_dotenv("/etc/secrets/.env", override=True)
load_dotenv(override=False)

async def _keepalive():
    """Pinga il proprio /health ogni 10 minuti per evitare il cold start su Render free tier."""
    await asyncio.sleep(60)
    url = os.getenv("RENDER_EXTERNAL_URL", "http://localhost:8000") + "/health"
    while True:
        try:
            async with httpx.AsyncClient() as client:
                await client.get(url, timeout=10)
        except Exception:
            pass
        await asyncio.sleep(600)

@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_keepalive())
    yield
    task.cancel()

from routes.auth import router as auth_router
from routes.docs import router as docs_router
from routes.payments import router as payments_router

app = FastAPI(title="ReadyGen API", version="1.0.0", lifespan=lifespan)

# CORS: in produzione usa FRONTEND_URL, in locale accetta tutto
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
origins = [
    frontend_url,
    "https://readygen-app.netlify.app",
    "https://docpilot-app.netlify.app",
    "https://splendorous-chebakia-31f7c6.netlify.app",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

class CORSErrorMiddleware(BaseHTTPMiddleware):
    """Garantisce CORS headers anche sulle risposte di errore 500."""
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as exc:
            origin = request.headers.get("origin", "*")
            allowed = origin if origin in origins else (origins[0] if origins else "*")
            return JSONResponse(
                status_code=500,
                content={"detail": f"Errore interno: {str(exc)}"},
                headers={"Access-Control-Allow-Origin": allowed,
                         "Access-Control-Allow-Credentials": "false"},
            )

app.add_middleware(CORSErrorMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(docs_router, prefix="/docs", tags=["docs"])
app.include_router(payments_router, prefix="/payments", tags=["payments"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Gestisce eccezioni non catturate aggiungendo sempre i CORS headers."""
    origin = request.headers.get("origin", "")
    allow_origin = origin if origin in origins else origins[0]
    return JSONResponse(
        status_code=500,
        content={"detail": f"Errore interno: {str(exc)}"},
        headers={"Access-Control-Allow-Origin": allow_origin},
    )


@app.get("/")
def root():
    return {"service": "ReadyGen API", "version": "1.0.0", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/debug-env")
def debug_env():
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    url = os.getenv("SUPABASE_URL", "")
    test_result = "non testato"
    try:
        from supabase import create_client
        client = create_client(url, key)
        result = client.table("users").select("id").limit(1).execute()
        test_result = f"OK - {len(result.data)} righe"
    except Exception as e:
        test_result = f"ERRORE: {str(e)}"
    return {
        "supabase_url": url or "MANCANTE",
        "key_length": len(key),
        "key_start": key[:20] if key else "MANCANTE",
        "key_end": key[-10:] if key else "MANCANTE",
        "frontend_url": os.getenv("FRONTEND_URL", "MANCANTE"),
        "supabase_test": test_result,
    }
