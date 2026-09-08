from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    documents,
    facts,
    relationships,
)


app = FastAPI(
    title="FactLens API",
    description=(
        "Fact Knowledge Layer for financial documents. "
        "Extracts, grounds, and reconciles numerical facts."
    ),
    version="0.1.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "FactLens API",
    }


app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"],
)

app.include_router(
    facts.router,
    prefix="/facts",
    tags=["Facts"],
)

app.include_router(
    relationships.router,
    prefix="/relationships",
    tags=["Relationships"],
)