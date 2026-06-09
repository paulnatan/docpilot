from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

load_dotenv()

from routes.auth import router as auth_router
from routes.docs import router as docs_router
from routes.payments import router as payments_router

app = FastAPI(title="ReadyGen API", version="1.0.0")

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
