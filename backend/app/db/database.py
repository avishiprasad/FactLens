from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


# ---------------------------------------------------------
# Database location
# ---------------------------------------------------------

# This file is:
# FactLens/backend/app/db/database.py
#
# parents[0] = db
# parents[1] = app
# parents[2] = backend
#
# Therefore BASE_DIR points to:
# FactLens/backend

BASE_DIR = Path(__file__).resolve().parents[2]

DATABASE_PATH = BASE_DIR / "factlens.db"

DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


# ---------------------------------------------------------
# SQLAlchemy engine
# ---------------------------------------------------------

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# ---------------------------------------------------------
# Session
# ---------------------------------------------------------

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


# ---------------------------------------------------------
# Declarative base
# ---------------------------------------------------------

Base = declarative_base()


# ---------------------------------------------------------
# Database dependency
# ---------------------------------------------------------

def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
