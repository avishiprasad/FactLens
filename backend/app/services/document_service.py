from pathlib import Path
from typing import Dict, List
import hashlib

from sqlalchemy.orm import Session

from app.db.models import Document
from app.parsing.pdf_parser import extract_pdf
from app.repositories.document_repository import (
    create_document,
    get_document,
)
from app.repositories.page_repository import create_page
from app.extraction.llm_extractor import extract_facts
from app.services.fact_service import store_extracted_facts


def calculate_file_hash(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.
    """

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:
        while True:
            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


def process_uploaded_document(
    db: Session,
    file_path: str,
    filename: str,
    pages_to_process: List[int] = None,
) -> Dict:
    """
    Store a PDF document and its selected pages.

    If pages_to_process is provided, only those pages
    are stored and processed.

    This function currently performs:
    1. SHA-256 hashing
    2. Duplicate detection
    3. Document creation
    4. PDF parsing
    5. Page storage
    6. Fact extraction
    7. Evidence verification
    8. Fact storage
    """

    # --------------------------------------------------
    # 1. Calculate file hash
    # --------------------------------------------------

    file_hash = calculate_file_hash(file_path)

    # --------------------------------------------------
    # 2. Check for duplicate document
    # --------------------------------------------------

    existing_document = (
        db.query(Document)
        .filter_by(file_hash=file_hash)
        .first()
    )

    if existing_document:
        return {
            "status": "duplicate",
            "document_id": existing_document.document_id,
            "filename": existing_document.filename,
        }

    # --------------------------------------------------
    # 3. Generate document ID
    # --------------------------------------------------

    document_id = Path(filename).stem

    # Avoid document_id collisions.
    existing_by_id = get_document(
        db,
        document_id,
    )

    if existing_by_id:
        document_id = (
            f"{document_id}-{file_hash[:8]}"
        )

    # --------------------------------------------------
    # 4. Create document record
    # --------------------------------------------------

    document = create_document(
        db=db,
        document_id=document_id,
        filename=filename,
        file_hash=file_hash,
    )

    # --------------------------------------------------
    # 5. Extract PDF pages
    # --------------------------------------------------

    pages = extract_pdf(file_path)

    stored_pages = []

    # --------------------------------------------------
    # 6. Process selected pages
    # --------------------------------------------------

    for page_data in pages:

        page_number = page_data["page_number"]

        # If specific pages were requested,
        # skip all other pages.
        if (
            pages_to_process is not None
            and page_number not in pages_to_process
        ):
            continue

        # --------------------------------------------------
        # 7. Store page
        # --------------------------------------------------

        page = create_page(
            db=db,
            document_id=document.id,
            page_number=page_number,
            text=page_data["text"],
        )

        stored_pages.append(page)

        # Skip completely empty pages.
        if not page_data["text"].strip():
            continue

        print(
            f"Extracting facts from "
            f"{document.document_id} "
            f"page {page_number}..."
        )

        # --------------------------------------------------
        # 8. Extract facts using LLM
        # --------------------------------------------------

        facts = extract_facts(
            text=page_data["text"],
            document_id=document.document_id,
            page_number=page_number,
        )

        # --------------------------------------------------
        # 9. Verify evidence and store facts
        # --------------------------------------------------

        store_extracted_facts(
            db=db,
            page_id=page.id,
            page_text=page_data["text"],
            facts=facts,
        )

    # --------------------------------------------------
    # 10. Return processing result
    # --------------------------------------------------

    return {
        "status": "processed",
        "document_id": document.document_id,
        "filename": document.filename,
        "file_hash": file_hash,
        "page_count": len(stored_pages),
    }
