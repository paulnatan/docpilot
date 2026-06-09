from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

from routes.auth import router as auth_router
from routes.docs import router as docs_router

app = FastAPI(title="DocPilot API", version="1.0.0")

# CORS: in produzione usa FRONTEND_URL, in locale accetta tutto
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
origins = [
    frontend_url,
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


@app.get("/")
def root():
    return {"service": "DocPilot API", "version": "1.0.0", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}
