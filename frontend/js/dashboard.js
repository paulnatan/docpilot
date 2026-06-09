let currentDoc = { content: "", repo: "", type: "" };

function applyTranslations() {
  const lang = getLang();
  // Evidenzia bandiera attiva
  document.querySelectorAll(".lang-flag").forEach(el => {
    el.classList.toggle("active", el.dataset.lang === lang);
  });
  document.getElementById("nav-home").textContent = t("nav_home");
  document.getElementById("nav-history").textContent = "📋 " + t("nav_history");
  document.getElementById("nav-logout").textContent = t("nav_logout");
  document.getElementById("page-title").textContent = t("page_title");
  document.getElementById("page-subtitle").textContent = t("page_subtitle");
  document.getElementById("btn-copy").textContent = t("btn_copy");
  document.getElementById("btn-download").textContent = t("btn_download");
  document.getElementById("push-btn").textContent = t("btn_push");

  // Rigenera le card nella nuova lingua se già caricate
  const grid = document.getElementById("repo-grid");
  if (window._loadedRepos && window._loadedRepos.length > 0) {
    renderRepos(window._loadedRepos);
  }
}

async function startCheckout(plan) {
  const token = getToken();
  if (!token) { location.href = "index.html"; return; }
  const btn = event ? event.target : null;
  if (btn) { btn.textContent = "⏳ Caricamento..."; btn.disabled = true; }
  try {
    const res = await fetch(`${API}/payments/create-checkout`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "Authorization": `Bearer ${token}` },
      body: JSON.stringify({ plan }),
    });
    const data = await res.json();
    if (data.checkout_url) {
      window.location.href = data.checkout_url;
    } else {
      showToast(data.detail || "Errore nel checkout", true);
      if (btn) { btn.textContent = "🚀 Upgrade a Pro — €19/mese"; btn.disabled = false; }
    }
  } catch {
    showToast("Errore di connessione. Riprova.", true);
    if (btn) { btn.textContent = "🚀 Upgrade a Pro — €19/mese"; btn.disabled = false; }
  }
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

  // Mostra banner in base al piano
  const plan = user.plan || "free";
  if (plan === "free") {
    const banner = document.getElementById("upgrade-banner");
    if (banner) banner.style.display = "flex";
  } else if (plan === "pro") {
    const banner = document.getElementById("pro-banner");
    if (banner) banner.style.display = "flex";
  }
  // Team: nessun banner (piano massimo)

  loadRepos();
}

function renderRepos(repos) {
  const grid = document.getElementById("repo-grid");

  if (repos.length === 0) {
    grid.innerHTML = `
      <div class="empty-state">
        <div class="icon">📂</div>
        <h3>${t('no_repos')}</h3>
        <p>${t('no_repos_sub')}</p>
      </div>`;
    return;
  }

  // Salva il branch corrente per ogni repo prima di rigenerare
  const currentBranches = {};
  repos.forEach(repo => {
    const input = document.getElementById(`branch-${repo.full_name.replace('/', '-')}`);
    if (input) currentBranches[repo.full_name] = input.value;
  });

  grid.innerHTML = repos.map(repo => `
    <div class="repo-card">
      <div>
        <div class="repo-name">📁 ${repo.name}</div>
        ${repo.private ? `<span class="badge">${t('badge_private')}</span>` : `<span class="badge">${t('badge_public')}</span>`}
      </div>
      <div class="repo-desc">${repo.description || t('no_description')}</div>
      <div style="display:flex; align-items:center; gap:8px;">
        <label style="font-size:12px; color:var(--text-muted);">${t('branch_label')}</label>
        <input
          id="branch-${repo.full_name.replace('/', '-')}"
          type="text"
          value="${currentBranches[repo.full_name] || repo.default_branch || 'main'}"
          style="background:var(--bg); border:1px solid var(--border); border-radius:4px; color:var(--text); padding:4px 8px; font-size:12px; width:90px;"
        />
      </div>
      <div class="actions">
        <button class="btn btn-primary" onclick="generate('${repo.full_name}', 'readme')">${t('btn_readme')}</button>
        <button class="btn btn-secondary" onclick="generate('${repo.full_name}', 'api_docs')">${t('btn_api')}</button>
        <button class="btn btn-secondary" onclick="generate('${repo.full_name}', 'changelog')">${t('btn_changelog')}</button>
        <button class="btn btn-secondary" onclick="selectFileForComments('${repo.full_name}')">${t('btn_comments')}</button>
        <button class="btn btn-secondary" style="border-color: #bc8cff; color: #bc8cff;" onclick="generate('${repo.full_name}', 'overview')">${t('btn_overview')}</button>
        <button class="btn btn-secondary" style="border-color: #f0883e; color: #f0883e;" onclick="generate('${repo.full_name}', 'openapi')">${t('btn_openapi')}</button>
        <button class="btn btn-secondary" style="border-color: #58a6ff; color: #58a6ff;" onclick="generate('${repo.full_name}', 'sdk')">${t('btn_sdk')}</button>
      </div>
    </div>
  `).join("");
}

async function loadRepos() {
  const token = getToken();
  const grid = document.getElementById("repo-grid");

  try {
    const res = await fetch(`${API}/docs/repos`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!res.ok) throw new Error(t('toast_error_load'));
    const repos = await res.json();

    window._loadedRepos = repos;
    renderRepos(repos);

  } catch (err) {
    grid.innerHTML = `<div class="empty-state"><div class="icon">❌</div><h3>${err.message}</h3></div>`;
  }
}

async function generate(repoFullName, docType) {
  const token = getToken();
  const labels = {
    readme: t("label_readme"),
    api_docs: t("label_api_docs"),
    changelog: t("label_changelog"),
    overview: t("label_overview"),
    comments: t("label_comments"),
    openapi: t("label_openapi"),
    sdk: t("label_sdk"),
  };

  const branchInput = document.getElementById(`branch-${repoFullName.replace("/", "-")}`);
  const branch = branchInput ? branchInput.value.trim() || "main" : "main";

  const isOverview = docType === "overview";
  openModal(
    `Generazione ${labels[docType]}...`,
    isOverview ? getOverviewLoadingHtml() : '<div style="display:flex;align-items:center;gap:12px;font-family:var(--font);color:var(--text-muted);"><div class="spinner"></div> Sto analizzando il codice con AI...</div>',
    true
  );

  // Per overview aggiorna i messaggi di stato ogni 3 secondi
  let loadingInterval = null;
  if (isOverview) {
    loadingInterval = startOverviewLoading();
  }

  try {
    const res = await fetch(`${API}/docs/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ repo_full_name: repoFullName, doc_type: docType, branch, lang: getLang() }),
    });

    if (loadingInterval) clearInterval(loadingInterval);

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Errore nella generazione");
    }

    const data = await res.json();
    currentDoc = { content: data.content, repo: repoFullName, type: docType, branch };

    openModal(`${labels[docType]} — ${repoFullName}`, data.content);

    // Mostra bottone push solo per tipi pushabili
    const pushBtn = document.getElementById("push-btn");
    pushBtn.style.display = ["readme", "changelog", "api_docs", "overview", "openapi", "sdk"].includes(docType) ? "inline-flex" : "none";

    showToast("Documentazione generata con successo!");

  } catch (err) {
    if (loadingInterval) clearInterval(loadingInterval);
    closeModal();
    const msg = err.message === "Failed to fetch"
      ? "Errore di connessione al server. Riprova tra qualche secondo."
      : err.message;
    showToast(msg, true);
  }
}

function getOverviewLoadingHtml() {
  return `
    <div id="overview-loading" style="font-family:var(--font); padding: 8px 0;">
      <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
        <div class="spinner"></div>
        <span style="color:var(--text); font-weight:600; font-size:15px;">Analisi architettura in corso...</span>
      </div>
      <div id="overview-steps" style="display:flex; flex-direction:column; gap:10px;">
        <div class="ov-step active" id="step-1">🔍 Lettura struttura del repository...</div>
        <div class="ov-step" id="step-2">📂 Analisi dei file sorgente...</div>
        <div class="ov-step" id="step-3">🧠 Identificazione architettura e pattern...</div>
        <div class="ov-step" id="step-4">🔗 Mappatura dei componenti e flussi...</div>
        <div class="ov-step" id="step-5">📝 Generazione documento tecnico...</div>
        <div class="ov-step" id="step-6">✨ Rifinitura e formattazione...</div>
      </div>
      <div style="margin-top:24px; background:var(--bg); border-radius:6px; padding:12px 16px;">
        <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px; font-family:var(--mono);">Questo può richiedere 15-30 secondi per repo grandi.</div>
        <div style="background:var(--border); border-radius:100px; height:4px; overflow:hidden;">
          <div id="overview-progress" style="height:100%; background:linear-gradient(90deg,#3fb950,#58a6ff); width:0%; transition:width 3s ease; border-radius:100px;"></div>
        </div>
      </div>
    </div>`;
}

function startOverviewLoading() {
  const steps = document.querySelectorAll('.ov-step');
  const progress = document.getElementById('overview-progress');
  let current = 0;

  // Stile steps
  steps.forEach(s => {
    s.style.cssText = 'font-size:14px; color:var(--text-subtle); padding:6px 0; transition:all 0.3s;';
  });
  if (steps[0]) {
    steps[0].style.color = 'var(--text)';
    steps[0].style.fontWeight = '600';
  }

  const interval = setInterval(() => {
    current++;
    if (current < steps.length) {
      steps.forEach((s, i) => {
        if (i < current) {
          s.style.color = 'var(--green)';
          s.style.fontWeight = '400';
          if (!s.innerHTML.startsWith('✅')) s.innerHTML = '✅ ' + s.innerHTML.replace(/^[^\s]+\s/, '');
        } else if (i === current) {
          s.style.color = 'var(--text)';
          s.style.fontWeight = '600';
        }
      });
      if (progress) progress.style.width = `${(current / steps.length) * 85}%`;
    }
  }, 4000);

  if (progress) setTimeout(() => { progress.style.width = '15%'; }, 100);
  return interval;
}

async function selectFileForComments(repoFullName) {
  const token = getToken();
  const branchInput = document.getElementById(`branch-${repoFullName.replace("/", "-")}`);
  const branch = branchInput ? branchInput.value.trim() || "main" : "main";

  openModal("Seleziona un file", '<div class="spinner"></div> Caricamento file del repo...', true);

  try {
    const res = await fetch(`${API}/docs/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ repo_full_name: repoFullName, doc_type: "comments", branch }),
    });

    if (!res.ok) throw new Error("Errore nel caricamento dei file");
    const data = await res.json();

    if (data.select_file && data.files) {
      const fileList = data.files.map(f => `
        <div class="file-item" onclick="generateComments('${repoFullName}', '${f}', '${branch}')">📄 ${f}</div>
      `).join("");

      document.getElementById("modal-title").textContent = `Seleziona file — ${repoFullName}`;
      const output = document.getElementById("doc-output");
      output.style.padding = "0";
      output.style.background = "none";
      output.style.border = "none";
      output.innerHTML = `
        <p style="color:var(--text-muted); margin-bottom:6px; font-family:var(--font); font-size:13px;">Seleziona un file per aggiungere i commenti inline con AI:</p>
        <div class="file-list">${fileList}</div>
      `;
    }
  } catch (err) {
    closeModal();
    showToast(err.message, true);
  }
}

async function generateComments(repoFullName, filePath, branch) {
  const token = getToken();

  document.getElementById("modal-title").textContent = `Generazione commenti — ${filePath}`;
  document.getElementById("doc-output").innerHTML = '<div class="spinner"></div> Sto commentando il codice con AI...';

  try {
    const res = await fetch(`${API}/docs/generate`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ repo_full_name: repoFullName, doc_type: "comments", branch, file_path: filePath }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Errore nella generazione");
    }

    const data = await res.json();
    currentDoc = { content: data.content, repo: repoFullName, type: "comments" };

    document.getElementById("modal-title").textContent = `Commenti — ${filePath}`;
    document.getElementById("doc-output").textContent = data.content;
    showToast("Commenti generati con successo!");

  } catch (err) {
    closeModal();
    showToast(err.message, true);
  }
}

function openModal(title, content, isHtml = false) {
  document.getElementById("modal-title").textContent = title;
  const output = document.getElementById("doc-output");
  if (isHtml) {
    output.innerHTML = content;
  } else {
    output.textContent = content;
  }
  document.getElementById("modal").classList.add("open");
}

function closeModal() {
  document.getElementById("modal").classList.remove("open");
}

function copyDoc() {
  navigator.clipboard.writeText(currentDoc.content).then(() => showToast("Copiato negli appunti!"));
}

async function pushToGitHub() {
  const token = getToken();
  const btn = document.getElementById("push-btn");
  btn.disabled = true;
  btn.textContent = "⏳ Push in corso...";

  try {
    const res = await fetch(`${API}/docs/push-to-github`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        doc_id: "",
        repo_full_name: currentDoc.repo,
        doc_type: currentDoc.type,
        content: currentDoc.content,
        branch: currentDoc.branch || "main",
      }),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Errore nel push");
    }

    const data = await res.json();
    showToast(`✅ ${data.file} pushato su GitHub!`);
    btn.textContent = "✅ Pushato!";
    setTimeout(() => {
      btn.textContent = "🚀 Push su GitHub";
      btn.disabled = false;
    }, 3000);

  } catch (err) {
    showToast(err.message, true);
    btn.textContent = "🚀 Push su GitHub";
    btn.disabled = false;
  }
}

function downloadDoc() {
  const ext = currentDoc.type === "changelog" ? "md" : "md";
  const filename = `${currentDoc.repo.split("/")[1]}_${currentDoc.type}.${ext}`;
  const blob = new Blob([currentDoc.content], { type: "text/markdown" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = filename;
  a.click();
}

// Chiudi modal cliccando fuori
document.getElementById("modal").addEventListener("click", function (e) {
  if (e.target === this) closeModal();
});

init();
