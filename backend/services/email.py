import os
import httpx

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@readygen.eu")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://readygen-app.netlify.app")


def send_doc_ready_email(to_email: str, username: str, repo_name: str, doc_type: str) -> bool:
    """Invia email di notifica quando la documentazione è pronta."""
    if not RESEND_API_KEY or not to_email:
        return False

    doc_labels = {
        "readme": "README",
        "api_docs": "API Documentation",
        "changelog": "Changelog",
        "overview": "Project Overview",
        "openapi": "OpenAPI / Swagger",
        "sdk": "SDK Client",
        "comments": "Inline Comments",
    }
    doc_label = doc_labels.get(doc_type, doc_type.upper())

    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Inter', sans-serif; background: #060910; color: #e6edf3; margin: 0; padding: 40px 20px; }}
    .container {{ max-width: 560px; margin: 0 auto; }}
    .logo {{ font-size: 22px; font-weight: 800; margin-bottom: 32px; }}
    .logo span {{ color: #3fb950; }}
    .card {{ background: #0d1117; border: 1px solid #21262d; border-radius: 12px; padding: 32px; }}
    h2 {{ font-size: 20px; font-weight: 700; margin: 0 0 12px; }}
    p {{ color: #7d8590; font-size: 15px; line-height: 1.7; margin: 0 0 20px; }}
    .badge {{ display: inline-block; background: rgba(63,185,80,0.1); border: 1px solid rgba(63,185,80,0.3); color: #3fb950; padding: 4px 12px; border-radius: 100px; font-size: 13px; font-weight: 600; margin-bottom: 20px; }}
    .repo {{ background: #161b22; border: 1px solid #30363d; border-radius: 8px; padding: 12px 16px; font-family: monospace; font-size: 14px; color: #58a6ff; margin-bottom: 24px; }}
    .btn {{ display: inline-block; background: #3fb950; color: #000; font-weight: 700; font-size: 15px; padding: 12px 24px; border-radius: 8px; text-decoration: none; }}
    .footer {{ margin-top: 32px; font-size: 12px; color: #484f58; text-align: center; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="logo">Ready<span>Gen</span></div>
    <div class="card">
      <div class="badge">✅ Documentazione pronta</div>
      <h2>La tua {doc_label} è pronta, {username}!</h2>
      <p>ReadyGen ha generato automaticamente la documentazione per il tuo repository:</p>
      <div class="repo">📁 {repo_name}</div>
      <p>Accedi alla dashboard per visualizzarla, copiarla o pushare direttamente nel repo.</p>
      <a href="{FRONTEND_URL}/dashboard.html" class="btn">🚀 Vai alla Dashboard</a>
    </div>
    <div class="footer">
      ReadyGen — Documentazione automatica per sviluppatori<br>
      <a href="{FRONTEND_URL}" style="color: #484f58;">readygen.eu</a>
    </div>
  </div>
</body>
</html>
"""

    try:
        response = httpx.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {RESEND_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "from": f"ReadyGen <{FROM_EMAIL}>",
                "to": [to_email],
                "subject": f"✅ {doc_label} generata — {repo_name.split('/')[-1]}",
                "html": html,
            },
            timeout=10,
        )
        return response.status_code == 200
    except Exception as e:
        print(f"[EMAIL ERROR] {e}")
        return False
