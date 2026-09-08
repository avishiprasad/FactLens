from pathlib import Path
from typing import Optional, List

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.document_service import (
    process_uploaded_document,
)


router = APIRouter()


UPLOAD_DIR = Path(
    __file__
).resolve().parents[4] / "data" / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def parse_pages(
    pages: Optional[str],
) -> Optional[List[int]]:
    """
    Convert the UI input:

        "6"

    or:

        "6,9"

    into:

        [6]

    or:

        [6, 9]

    Blank input means process the entire document.
    """

    if pages is None:
        return None

    pages = pages.strip()

    if not pages:
        return None

    try:

        parsed_pages = []

        for value in pages.split(","):

            value = value.strip()

            if not value:
                continue

            page_number = int(value)

            if page_number < 1:
                raise ValueError

            parsed_pages.append(page_number)

        if not parsed_pages:
            raise ValueError

        return sorted(
            set(parsed_pages)
        )

    except ValueError:

        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid pages value. "
                "Use format like '6' or '6,9'."
            ),
        )


@router.get("/")
def list_documents(
    db: Session = Depends(get_db),
):

    from app.repositories.document_repository import (
        get_all_documents,
    )

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
    pages: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):

    # ---------------------------------------------------------
    # Validate file
    # ---------------------------------------------------------

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # ---------------------------------------------------------
    # Parse page selection
    # ---------------------------------------------------------

    pages_to_process = parse_pages(
        pages
    )

    # ---------------------------------------------------------
    # Save uploaded file
    # ---------------------------------------------------------

    safe_filename = Path(
        file.filename
    ).name

    destination = (
        UPLOAD_DIR / safe_filename
    )

    content = await file.read()

    with open(
        destination,
        "wb",
    ) as output_file:

        output_file.write(content)

    # ---------------------------------------------------------
    # Process document
    # ---------------------------------------------------------

    try:

        result = process_uploaded_document(
            db=db,
            file_path=str(destination),
            filename=safe_filename,
            pages_to_process=pages_to_process,
        )

        return result

    except Exception as error:

        # Do not expose internal stack traces
        # through the API.

        print(
            "Document processing failed:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Document processing failed. "
                "Check the FastAPI terminal for details."
            ),
        )