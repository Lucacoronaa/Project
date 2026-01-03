const $ = (id) => document.getElementById(id);

function setMsg(id, text) {
  const el = $(id);
  el.textContent = text || "";
  el.classList.toggle("hidden", !text);
}

async function api(path, opts={}) {
  const res = await fetch(path, { ...opts, credentials: "include" });
  const text = await res.text();
  let data;
  try { data = text ? JSON.parse(text) : null; } catch { data = text; }
  if (!res.ok) throw new Error((data && data.detail) ? data.detail : (text || "Errore"));
  return data;
}

async function register() {
  setMsg("msg", "");
  setMsg("ok", "");

  const email = $("email").value.trim();
  const password = $("password").value;

  if (!email || !password) {
    setMsg("msg", "Inserisci email e password.");
    return;
  }

  const body = new URLSearchParams();
  body.set("email", email);
  body.set("password", password);

  try {
    await api("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });

    // login automatico dopo signup
    await api("/api/login", {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body
    });

    setMsg("ok", "Account creato! Ti porto ai movimenti...");
    setTimeout(() => window.location.href = "/movimenti", 600);
  } catch (e) {
    setMsg("msg", e.message);
  }
}

$("btnRegister").addEventListener("click", register);
$("btnGoLogin").addEventListener("click", () => window.location.href = "/login");
