# APP/routes/movimenti.py
from fastapi import APIRouter, Form, Request, HTTPException
from sqlalchemy import text
from .db import engine
from .auth import get_user_id

router = APIRouter(prefix="/api", tags=["movimenti"])



#Fa solo vedere elenco dei movimenti -- SELECT
@router.get("/movimenti")
def list_movimenti(request: Request, limit: int = 50):
    uid = get_user_id(request)
    with engine.connect() as conn:
        rows = conn.execute(text("""
            SELECT id, user_id, datestate, descrizione, amount, subcategoryid
            FROM movimenti
            WHERE user_id = :uid
            ORDER BY datestate DESC
            LIMIT :limit;
        """), {"uid": uid, "limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]



# Fa inserire un movimento nuovo -- INSERT
@router.post("/movimenti")
def create_movimento(
    request: Request,
    descrizione: str = Form(...),
    amount: float = Form(...),
    subcategoryid: int = Form(...),
    datestate: str = Form(None),
):
    uid = get_user_id(request)

    occurred_at = None
    if datestate and datestate.strip():
        from dateutil import parser
        occurred_at = parser.parse(datestate)

    with engine.begin() as conn:
        if occurred_at is None:
            row = conn.execute(text("""
                INSERT INTO movimenti (user_id, descrizione, amount, subcategoryid)
                VALUES (:user_id, :descrizione, :amount, :subcategoryid)
                RETURNING id;
            """), {"user_id": uid, "descrizione": descrizione, "amount": amount, "subcategoryid": subcategoryid}).fetchone()
        else:
            row = conn.execute(text("""
                INSERT INTO movimenti (user_id, datestate, descrizione, amount, subcategoryid)
                VALUES (:user_id, :datestate, :descrizione, :amount, :subcategoryid)
                RETURNING id;
            """), {"user_id": uid, "datestate": occurred_at, "descrizione": descrizione, "amount": amount, "subcategoryid": subcategoryid}).fetchone()

    return {"status": "ok", "id": row[0]}



@router.delete("/movimenti/{mov_id}")
def delete_movimento(request: Request, mov_id: int):

    user_id = get_user_id(request)

    with engine.begin() as conn:
        row = conn.execute(text("""
                                DELETE FROM movimenti
                                where id = :id and user_id = :user_id
                                returning id;""" ), {"id": mov_id, "user_id": user_id}).fetchone()
    
        if not row:
            raise HTTPException(status_code=400, detail = "Movimento non trovato")
        
        return {"ok": True, "delete_id": row[0]}