import os
from datetime import datetime, timedelta
from pathlib import Path
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi import APIRouter, Form, Request, Response, HTTPException
from sqlalchemy import text
from .db import engine


router = APIRouter(prefix= "/api", tags = ["auth"])
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY", "CHANGE_ME")
ALGORITHM = "HS256"
TOKEN_DAYS = 30

def check_password_len(password: str) -> None:
    if len(password.encode("utf-8")) > 72:
        raise HTTPException(status_code=400, detail= "Passowrd troppo lunga. Us auna password piu corta")

def hash_password(p: str) -> str:
    return pwd_context.hash(p)

def verify_password(p: str, hashed:str) -> bool:
    return pwd_context.verify(p, hashed)

def create_token(user_id: int) -> str:
    exp = datetime.utcnow() + timedelta(days = TOKEN_DAYS)
    return jwt.encode({"uid": user_id, "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def get_user_id(request: Request) -> int:
    token = request.cookies.get("token")
    if not token:
        raise HTTPException(status_code= 401, detail = "NOT LOGGED IN")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid = payload.get("uid")
        if not uid:
            raise HTTPException(status_code=401, detail= "INvalid TOKEN")
        return int(uid)
    except JWTError:
        raise HTTPException(status_code=401, detail= "Invalid TOKEN")



@router.post("/signup")
def signup(email:str = Form(...), password: str = Form(...)):
    check_password_len(password)
    pw_hash = hash_password(password)
    with engine.begin() as conn:
        row = conn.execute(text("""
                               INSERT INTO users (email, passwordhash)
            VALUES (:email, :passwordhash)
            RETURNING id;
        """), {"email": email, "passwordhash": pw_hash}).fetchone()
    return {"ok": True, "user_id": row[0]} 


@router.post("/login")
def login(response: Response, email: str = Form(...), password: str = Form(...)):
    check_password_len(password)
    with engine.connect() as conn:
        row = conn.execute(text("""
                               SELECT id, passwordhash FROM users WHERE email = :email;
        """), {"email": email}).fetchone()

    if not row or not verify_password(password, row[1]):
        raise HTTPException(status_code = 401, detail="Wrong CREDENTIALSS!!!")
    
    token = create_token(row[0])
    is_https = os.getenv("COOKIE_SECURE", "0") == "1"
    response.set_cookie("token", token, httponly=True, samesite="lax", secure= is_https)
    return {"ok": True}


@router.get("/me")
def me(request: Request):
    uid = get_user_id(request)
    return {"ok": True, "user_id":uid}

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("token")
    return {"ok": True}



