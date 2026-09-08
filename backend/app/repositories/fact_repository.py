from typing import List

from sqlalchemy.orm import Session

from app.db.models import Fact


def create_fact(
    db: Session,
    subject: str,
    predicate: str,
    value: str,
    value_type: str,
    unit: str,
    period: str,
    scope: str,
    confidence: float,
    extraction_method: str,
    evidence_text: str,
    evidence_verified: bool,
    page_id: int,
) -> Fact:

    fact = Fact(
        subject=subject,
        predicate=predicate,
        value=value,
        value_type=value_type,
        unit=unit,
        period=period,
        scope=scope,
        confidence=confidence,
        extraction_method=extraction_method,
        evidence_text=evidence_text,
        evidence_verified=int(evidence_verified),
        page_id=page_id,
    )

    db.add(fact)
    db.commit()
    db.refresh(fact)

    return fact


def get_fact(
    db: Session,
    fact_id: int,
):

    return (
        db.query(Fact)
        .filter(
            Fact.id == fact_id
        )
        .first()
    )


def get_facts_for_page(
    db: Session,
    page_id: int,
) -> List[Fact]:

    return (
        db.query(Fact)
        .filter(
            Fact.page_id == page_id
        )
        .all()
    )


def get_all_facts(
    db: Session,
) -> List[Fact]:

    return (
        db.query(Fact)
        .order_by(
            Fact.id.desc()
        )
        .all()
    )