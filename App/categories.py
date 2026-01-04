from fastapi import APIRouter, Request
from sqlalchemy import text
from .db import engine
from .auth import get_user_id

router = APIRouter(prefix ="/api", tags=["categories"])

@router.get("/sub-categories")
def list_sub_categories(request: Request):
    get_user_id(request)

    with engine.connect() as conn:
        rows = conn.execute(text("""
                                SELECT s.id,s.sub_category, s.macroid,  m.macro_category, m.type
                                FROM sub_categories s
                                JOIN macro_categories m ON m.id = s.macroid
                                WHERE s.is_active = true AND m.is_active = TRUE
                                ORDER BY m.type, m.macro_category, s.sub_category
                            """)).fetchall()

    return [dict(r._mapping) for r in rows]

