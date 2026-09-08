from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import Fact

router = APIRouter()


@router.get("/")
def list_facts(
    db: Session = Depends(get_db),
):
    facts = (
        db.query(Fact)
        .order_by(Fact.id.desc())
        .all()
    )

    results = []

    for fact in facts:

        page = fact.page
        document = page.document

        results.append({
            "id": fact.id,

            "subject": fact.subject,
            "predicate": fact.predicate,

            "value": fact.value,
            "value_type": fact.value_type,
            "unit": fact.unit,

            "period": fact.period,
            "scope": fact.scope,

            "confidence": fact.confidence,
            "extraction_method": fact.extraction_method,

            "evidence": {
                "text": fact.evidence_text,
                "verified": bool(
                    fact.evidence_verified
                ),
            },

            "source": {
                "document_id": document.document_id,
                "filename": document.filename,
                "page": page.page_number,
            },
        })

    return results