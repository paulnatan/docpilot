from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class User(BaseModel):
    id: Optional[str] = None
    github_id: int
    username: str
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    access_token: str
    created_at: Optional[datetime] = None


class Repo(BaseModel):
    id: int
    name: str
    full_name: str
    description: Optional[str] = None
    private: bool
    html_url: str
    default_branch: str


class GenerateRequest(BaseModel):
    repo_full_name: str  # es. "paulblack/my-project"
    doc_type: str        # "readme" | "api_docs" | "changelog" | "comments" | "overview"
    branch: Optional[str] = "main"
    file_path: Optional[str] = None  # solo per doc_type="comments"
    lang: Optional[str] = "it"       # "it" | "en" | "fr" | "de"


class GeneratedDoc(BaseModel):
    id: Optional[str] = None
    user_id: str
    repo_name: str
    doc_type: str
    content: str
    generated_at: Optional[datetime] = None


class WebhookPayload(BaseModel):
    repository: dict
    commits: Optional[list] = None
    pull_request: Optional[dict] = None
    ref: Optional[str] = None
