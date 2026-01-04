const $ = (id) => document.getElementById(id);
function setMsg(id, text){
    const el = $(id);
    el.textContent = text || "";
    el.classList.toggle("hidden", !text);
}

async function api(path, opts={}) {
    const res = await fetch(path, {...opts, credentials: "include"});
    const text = await res.text();
    let data;
    try{data = text ? JSON.parse(text) : null } catch{data = text;}
    if (!res.ok) throw new Error((data && data.detail) ? data.detail: (text || "Errore"));
    return data;
}


async function ensureLogged(){
    try{
        const me = await api ("/api/me");
        $("me").textContent = `Codice_Utente: ${me.user_id}`;
    }catch {
        window.location.href = "/login";
    }
}

function renderList(rows){
    const list = $("list");
    list.innerHTML = "";
    $("empty").classList.toggle("hidden", rows.length !== 0);
    if (!rows.length) {
      $("list").innerHTML = "";
      return;
    }
    for (const r of rows) {
    const div = document.createElement("div");
    div.className = "item";
    div.innerHTML = `
      <div class="row">
        <div class="desc">${escapeHtml(r.descrizione ?? "")}</div>
        <div class="amt">${escapeHtml(String(r.amount ?? ""))}</div>
      </div>
      <div class="meta">${escapeHtml(String(r.datestate ?? ""))} · subcat ${escapeHtml(String(r.subcategoryid ?? ""))}</div>
    `;
    list.appendChild(div);
  }
}

function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

async function loadMovimenti() {
  setMsg("msg", "");
  try {
    const rows = await api("/api/movimenti?limit=30");
    renderList(rows);
  } catch (e) {
    setMsg("msg", e.message);
  }
}

async function addMovimento() {
  setMsg("msg", "");
  setMsg("ok", "");

  const body = new URLSearchParams();

  const subId = $("subcategoryid").value;
  if (!subId) {
    setMsg("msg", "Seleziona ua categoria.");
    return;
  }
  body.set("subcategoryid", subId);

  body.set("descrizione", $("descrizione").value.trim());
  body.set("amount", $("amount").value);
  const d = $("datestate").value.trim();
  if (d) body.set("datestate", d);

  try {
    const out = await api("/api/movimenti", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });
    setMsg("ok", "Salvato! id=" + out.id);
    $("descrizione").value = "";
    $("amount").value = "";
    $("subcategoryid").value = "";
    $("datestate").value = "";
    await loadMovimenti();
  } catch (e) {
    setMsg("msg", e.message);
  }
}

async function logout() {
  await api("/api/logout", { method: "POST" });
  window.location.href = "/login";
}

$("btnReload").addEventListener("click", loadMovimenti);
$("btnAdd").addEventListener("click", addMovimento);
$("btnLogout").addEventListener("click", logout);

async function loadSubCategories() {
  const sel = $("subcategoryid");
  if (!sel) return;
  sel.innerHTML = `<option value="">Caricamento...</option>`;

  const rows = await api("/api/sub-categories");

  sel.innerHTML = `<option value="">Seleziona una categoria...</option>`;
  
  
  for (const r of rows){

    const id = r.id
    const name = r.sub_category

    if (!id || !name) continue;


    const opt = document.createElement("option");
    opt.value = r.id;
    opt.textContent = name;
    sel.appendChild(opt);
  }
}

(async function init(){
  await ensureLogged();
  await loadSubCategories();
  await loadMovimenti();
})();