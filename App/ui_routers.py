from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["ui"])
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "Form" / "templates"))


@router.get("/")
def root():
    #Manda direttamente alla Login
    return RedirectResponse(url="/login")

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/movimenti")
def movimenti_page(request: Request):
    return templates.TemplateResponse("movimenti.html", {"request": request})

@router.get("/register")
def register_page(request:Request):
    return templates.TemplateResponse("register.html", {"request": request})