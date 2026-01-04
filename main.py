from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from App.auth import router as auth_router
from App.movimenti import router as movimenti_router
from App.ui_routers import router as ui_router
from App.categories import router as categorie_router


app = FastAPI()
app.include_router(auth_router)
app.include_router(movimenti_router)
app.include_router(ui_router)
app.include_router(categorie_router)

BASE_DIR = Path(__file__).resolve().parent
app.mount(
        "/static",
        StaticFiles(directory=str(BASE_DIR / "App" / "Form" / "static")),
        name = "static",
)
