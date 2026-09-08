from typing import Optional

from sqlalchemy.orm import Session

from app.db.models import Document


def create_document(
    db: Session,
    document_id: str,
    filename: str,
    file_hash: Optional[str] = None,
) -> Document:

    document = Document(
        document_id=document_id,
        filename=filename,
        file_hash=file_hash,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document


def get_document(
    db: Session,
    document_id: str,
) -> Optional[Document]:

    return (
        db.query(Document)
        .filter(
            Document.document_id == document_id
        )
        .first()
    )


def get_all_documents(
    db: Session,
):

    return (
        db.query(Document)
        .order_by(
            Document.uploaded_at.desc()
        )
        .all()
    )