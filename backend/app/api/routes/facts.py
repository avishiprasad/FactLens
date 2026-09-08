from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.repositories.fact_repository import get_all_facts


router = APIRouter()


@router.get("/")
def list_facts(db: Session = Depends(get_db)):
    facts = get_all_facts(db)

    return [
        {
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
            "evidence_text": fact.evidence_text,
            "evidence_verified": bool(fact.evidence_verified),
            "page_id": fact.page_id,
        }
        for fact in facts
    ]