from fastapi import FastAPI

from app.api.routes import documents
from app.api.routes import facts
from app.api.routes import relationships


app = FastAPI(
    title="FactLens API",
    description=(
        "Fact Knowledge Layer for financial documents. "
        "Extracts, grounds, and reconciles numerical facts."
    ),
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "FactLens API"
    }


app.include_router(
    documents.router,
    prefix="/documents",
    tags=["Documents"]
)

app.include_router(
    facts.router,
    prefix="/facts",
    tags=["Facts"]
)

app.include_router(
    relationships.router,
    prefix="/relationships",
    tags=["Relationships"]
)