from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.document_repository import get_all_documents
from app.services.document_service import process_uploaded_document


router = APIRouter()


@router.get("/")
def list_documents(db: Session = Depends(get_db)):
    documents = get_all_documents(db)

    return [
        {
            "id": document.id,
            "document_id": document.document_id,
            "filename": document.filename,
            "uploaded_at": document.uploaded_at,
        }
        for document in documents
    ]


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    Upload and process a PDF document.
    """

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    upload_directory = Path("data/uploads")
    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    file_path = upload_directory / file.filename

    contents = await file.read()

    with open(file_path, "wb") as output_file:
        output_file.write(contents)

    result = process_uploaded_document(
        db=db,
        file_path=str(file_path),
        filename=file.filename,
    )

    return result