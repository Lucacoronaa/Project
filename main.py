from fastapi import FastAPI
from App.auth import router as auth_router
from App.movimenti import router as movimenti_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(movimenti_router)
