const API = "https://docpilot-production-ff6b.up.railway.app";

function getToken() {
  return localStorage.getItem("docpilot_token") || new URLSearchParams(location.search).get("token");
}

function saveToken(token) {
  localStorage.setItem("docpilot_token", token);
  // Rimuove il token dall'URL senza reload
  const url = new URL(location.href);
  url.searchParams.delete("token");
  history.replaceState(null, "", url);
}

function logout() {
  localStorage.removeItem("docpilot_token");
  location.href = "index.html";
}

async function requireAuth() {
  const token = getToken();
  if (!token) {
    location.href = "index.html";
    return null;
  }
  saveToken(token);

  try {
    const res = await fetch(`${API}/auth/me?token=${token}`);
    if (!res.ok) throw new Error();
    return await res.json();
  } catch {
    logout();
    return null;
  }
}

function showToast(msg, isError = false) {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = "toast show" + (isError ? " error" : "");
  setTimeout(() => { toast.className = "toast"; }, 3000);
}
