from typing import List

from sqlalchemy.orm import Session

from app.db.models import Page


def create_page(
    db: Session,
    document_id: int,
    page_number: int,
    text: str,
    printed_page: str = None,
) -> Page:

    page = Page(
        document_id=document_id,
        page_number=page_number,
        text=text,
        printed_page=printed_page,
    )

    db.add(page)
    db.commit()
    db.refresh(page)

    return page


def get_page(
    db: Session,
    page_id: int,
):

    return (
        db.query(Page)
        .filter(
            Page.id == page_id
        )
        .first()
    )


def get_pages_for_document(
    db: Session,
    document_id: int,
) -> List[Page]:

    return (
        db.query(Page)
        .filter(
            Page.document_id == document_id
        )
        .order_by(
            Page.page_number
        )
        .all()
    )