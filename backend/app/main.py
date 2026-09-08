from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import documents, facts, relationships

app = FastAPI(
    title="FactLens",
    description="Fact Knowledge Layer for document intelligence",
    version="1.0.0",
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


@app.get("/")
def root():
    return {
        "name": "FactLens",
        "status": "online",
        "message": "Fact Knowledge Layer API",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}