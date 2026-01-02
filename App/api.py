import os
from pathlib import Path
from datetime import datetime
from dateutil import parser
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

env_path = Path(__file__).parent / ".env"
if env_path.exists(): 
    load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL mancante (mettila in .env locale o in Render env vars)")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

app = FastAPI()



# --------- API: READ GET --------

@app.get("/api/Movimenti")
def api_list_Movimenti(limit: int = 50):
    with engine.connect() as conn:
        rows = conn.execute(text("""
                        SELECT id, datestate, descrizione, amount, subcategoryid
                        FROM movimenti
                        ORDER BY datestate DESC
                        LIMIT :limit;
                    """), {"limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]



# --------- API: CREATE (POST) --------

@app.post("/api/Movimenti")
def api_create_Movimenti(descrizione: str= Form(...), amount: float = Form(...), subcategoryid: int = Form(...) , datestate: str = Form(None),): 
    
    occurred_at = None
    if datestate and datestate.strip():
        occurred_at = parser.parse(datestate)

    with engine.begin() as conn:
        if occurred_at is None:
            row = conn.execute(text("""
                INSERT INTO movimenti (descrizione, amount, subcategoryid)
                VALUES (:descrizione, :amount, :subcategoryid)
                RETURNING id;
            """), {
                "descrizione": descrizione,
                "amount": amount,
                "subcategoryid": subcategoryid,
            }).fetchone()
        else:
            row = conn.execute(text("""
                INSERT INTO movimenti ( descrizione, amount, subcategoryid, datestate)
                VALUES ( :descrizione, :amount, :subcategoryid, :datestate)
                RETURNING id;
            """), {
                "descrizione": descrizione,
                "amount": amount,
                "subcategoryid": subcategoryid,
                "datestate": occurred_at,
            }).fetchone()

    return {"status": "ok", "id": row[0]}


print("=== ROUTES REGISTRATE ===")
for r in app.routes:
    try:
        methods = ",".join(sorted(r.methods))
    except Exception:
        methods = "?"
    print(r.path, methods)
print("=========================")



# ---------- UI MOBILE (GET /) ----------
@app.get("/", response_class = HTMLResponse)
def home():
    with engine.connect() as conn:
        rows = conn.execute(text("""
                            SELECT id,  descrizione, amount, subcategoryid,datestate
                            FROM movimenti
                            ORDER BY datestate DESC
                            LIMIT 50;
                        """)).fetchall()
    
    items_html = ""
    for r in rows:
        d = dict(r._mapping)
        items_html += f"""
        <div class="item">
          <div class="muted">{d['datestate']}</div>
          <div class="title">{d['descrizione']}</div>
          <div class="amount">{d['amount']}</div>
          <div class="muted">subcat: {d['subcategoryid']}</div>
        </div>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Movimenti</title>
  <style>
    body {{ font-family: system-ui; padding: 16px; background:#f4f4f4; }}
    h2 {{ margin: 8px 0 12px; }}
    .card {{ background:white; padding:16px; border-radius:14px; box-shadow:0 6px 16px rgba(0,0,0,.06); }}
    input, button {{ width: 100%; padding: 14px; margin: 8px 0; font-size:16px; border-radius:12px; border:1px solid #ddd; }}
    button {{ background:#007aff; color:white; border:none; font-weight:600; }}
    .list {{ margin-top: 16px; display:grid; gap: 10px; }}
    .item {{ background:white; padding:12px; border-radius:14px; box-shadow:0 4px 14px rgba(0,0,0,.05); }}
    .muted {{ color:#666; font-size:12px; }}
    .title {{ font-weight:700; margin-top:4px; }}
    .amount {{ margin-top:6px; font-size:18px; font-weight:800; }}
  </style>
</head>
<body>

<h2>Nuovo Movimento</h2>

<div class="card">
  <form method="post" action="/api/movimenti">
    <input name="descrizione" placeholder="Descrizione" required />
    <input name="amount" type="number" step="0.01" placeholder="Importo (es. -250.00 / 1200.00)" required />
    <input name="subcategoryid" type="number" placeholder="SubCategory ID" required />
    <input name="datestate" placeholder="Data (opzionale: 2026-01-01 13:08:27.269 +0100)" />
    <button type="submit">Salva</button>
  </form>
</div>

<h2>Ultimi 50</h2>
<div class="list">
  {items_html}
</div>

</body>
</html>
"""


# (OPZIONALE) redirect post-form: se vuoi tornare alla home dopo il post,
# in futuro possiamo fare POST /movimenti (UI) e farlo redirectare a "/".

