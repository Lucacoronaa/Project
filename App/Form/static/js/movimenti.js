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

function renderList(rows) {
  const list = $("list");
  list.innerHTML = "";

  for (const r of rows) {
    const wrapper = document.createElement("div");
    wrapper.className = "swipe-row";

    wrapper.innerHTML = `
      <div class="swipe-actions">
        <div class="swipe-action left" data-action="edit" title="Modifica">✏️</div>
        <div class="swipe-action right" data-action="delete" title="Cancella">🗑️</div>
      </div>

      <div class="swipe-content item">
        <div class="line">
          <div class="desc">${escapeHtml(r.descrizione ?? "")}</div>
          <div class="amt">${escapeHtml(String(r.amount ?? ""))}</div>
        </div>
        <div class="meta">${escapeHtml(String(r.datestate ?? ""))}</div>
      </div>
    `;

    const contentEl = wrapper.querySelector(".swipe-content");

    enableSwipe(wrapper, contentEl, {
      onDelete: async () => {
        if (!confirm("Vuoi cancellare questo movimento?")) return;
        await api(`/api/movimenti/${r.id}`, { method: "DELETE" });
        await loadMovimenti();
      },
      onEdit: async () => {
        // per ora non facciamo nulla
        alert("Modifica: la facciamo nello step successivo 🙂");
      }
    });

    list.appendChild(wrapper);
  }
}




function escapeHtml(s) {
  return s.replace(/[&<>"']/g, (c) => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c]));
}

function clamp(n, min, max) { return Math.max(min, Math.min(max, n)); }

function enableSwipe(rowEl, contentEl, { onDelete, onEdit }) {
  let startX = 0;
  let currentX = 0;
  let dragging = false;

  const THRESH = 70;   // quanto devi trascinare per “attivare”
  const MAX = 90;      // limite spostamento

  function setX(x) {
    currentX = clamp(x, -MAX, MAX);
    contentEl.style.transform = `translateX(${currentX}px)`;
  }

  contentEl.addEventListener("touchstart", (e) => {
    if (e.touches.length !== 1) return;
    dragging = true;
    startX = e.touches[0].clientX;
    contentEl.style.transition = "none";
  }, { passive: true });

  contentEl.addEventListener("touchmove", (e) => {
    if (!dragging) return;
    const x = e.touches[0].clientX;
    const dx = x - startX;
    setX(dx);
  }, { passive: true });

  contentEl.addEventListener("touchend", async () => {
    if (!dragging) return;
    dragging = false;
    contentEl.style.transition = "transform 0.12s ease-out";

    // swipe a destra (delete) → dx negativo o positivo? dipende.
    // qui: se trascini verso sinistra (dx < 0) mostro delete a destra
    if (currentX < -THRESH) {
      setX(-MAX);
    } else if (currentX > THRESH) {
      setX(MAX);
    } else {
      setX(0);
    }
  });

  // click azioni (tap)
  rowEl.querySelector("[data-action='delete']")?.addEventListener("click", async () => {
    await onDelete();
    setX(0);
  });

  rowEl.querySelector("[data-action='edit']")?.addEventListener("click", async () => {
    if (onEdit) await onEdit();
    setX(0);
  });

  // tap sul contenuto richiude
  contentEl.addEventListener("click", () => {
    if (Math.abs(currentX) > 0) setX(0);
  });
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