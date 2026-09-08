from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import FactRelationship

router = APIRouter()


@router.get("/")
def list_relationships(
    db: Session = Depends(get_db),
):
    relationships = (
        db.query(FactRelationship)
        .order_by(FactRelationship.id.desc())
        .all()
    )

    results = []

    for relationship in relationships:

        facts = []

        for membership in relationship.facts:

            fact = membership.fact
            page = fact.page
            document = page.document

            facts.append({
                "fact_id": fact.id,
                "role": membership.role,

                "subject": fact.subject,
                "predicate": fact.predicate,

                "value": fact.value,
                "value_type": fact.value_type,
                "unit": fact.unit,

                "period": fact.period,
                "scope": fact.scope,

                "confidence": fact.confidence,

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

        results.append({
            "id": relationship.id,
            "relationship_type": relationship.relationship_type,
            "confidence": relationship.confidence,
            "explanation": relationship.explanation,
            "facts": facts,
        })

    return results