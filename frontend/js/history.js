let currentDoc = { content: "", repo: "", type: "" };

const DOC_LABELS = { readme: "README", api_docs: "API Docs", changelog: "Changelog" };
const DOC_ICONS = { readme: "📄", api_docs: "🔌", changelog: "📋" };

function applyTranslations() {
  const lang = getLang();
  document.querySelectorAll(".lang-flag").forEach(el => {
    el.classList.toggle("active", el.dataset.lang === lang);
  });
  document.getElementById("back-btn").textContent = t("back_dashboard");
  document.getElementById("nav-logout").textContent = t("nav_logout");
  document.getElementById("history-title").textContent = t("history_title");
  document.getElementById("history-subtitle").textContent = t("history_subtitle");
  document.getElementById("btn-copy").textContent = t("btn_copy");
  document.getElementById("btn-download").textContent = t("btn_download");
}

async function init() {
  const user = await requireAuth();
  if (!user) return;

  applyTranslations();

  document.getElementById("username").textContent = user.username;
  if (user.avatar_url) {
    const img = document.getElementById("avatar");
    img.src = user.avatar_url;
    img.style.display = "block";
  }

  loadHistory();
}

async function loadHistory() {
  const token = getToken();
  const list = document.getElementById("history-list");

  list.innerHTML = `<div class="empty-state"><div class="icon">⏳</div><h3>Caricamento...</h3></div>`;

  try {
    const res = await fetch(`${API}/docs/history`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error("Errore nel caricamento storico");
    const docs = await res.json();

    if (docs.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <div class="icon">📂</div>
          <h3>Nessuna documentazione ancora</h3>
          <p>Torna alla dashboard e genera la tua prima doc.</p>
        </div>`;
      return;
    }

    list.innerHTML = docs.map((doc, i) => `
      <div class="history-item" onclick="openDoc(${i})">
        <div class="history-icon">${DOC_ICONS[doc.doc_type] || "📄"}</div>
        <div class="history-info">
          <div class="history-repo">${doc.repo_name}</div>
          <div class="history-meta">${DOC_LABELS[doc.doc_type] || doc.doc_type} · ${formatDate(doc.generated_at)}</div>
        </div>
        <div class="history-arrow">›</div>
      </div>
    `).join("");

    window._historyDocs = docs;

  } catch (err) {
    list.innerHTML = `<div class="empty-state"><div class="icon">❌</div><h3>${err.message}</h3></div>`;
  }
}

function openDoc(index) {
  const doc = window._historyDocs[index];
  currentDoc = { content: doc.content, repo: doc.repo_name, type: doc.doc_type };
  document.getElementById("modal-title").textContent = `${DOC_LABELS[doc.doc_type]} — ${doc.repo_name}`;
  document.getElementById("doc-output").textContent = doc.content;
  document.getElementById("modal").classList.add("open");
}

function closeModal() {
  document.getElementById("modal").classList.remove("open");
}

function copyDoc() {
  navigator.clipboard.writeText(currentDoc.content).then(() => showToast("Copiato negli appunti!"));
}

function downloadDoc() {
  const filename = `${currentDoc.repo.split("/")[1]}_${currentDoc.type}.md`;
  const blob = new Blob([currentDoc.content], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}

function formatDate(iso) {
  if (!iso) return "";
  const d = new Date(iso);
  return d.toLocaleDateString("it-IT", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

document.getElementById("modal").addEventListener("click", function (e) {
  if (e.target === this) closeModal();
});

init();
