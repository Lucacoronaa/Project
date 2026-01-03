from pathlib import Path
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

env_path = Path(__file__).parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL mancante (mettila in APP/.env in locale o env vars su Render)")

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
