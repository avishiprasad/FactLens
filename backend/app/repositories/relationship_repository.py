from typing import List, Dict

from sqlalchemy.orm import Session

from app.db.models import (
    FactRelationship,
    RelationshipFact,
)


def create_relationship(
    db: Session,
    relationship_type: str,
    confidence: float,
    explanation: str,
    facts: List[Dict],
) -> FactRelationship:

    relationship = FactRelationship(
        relationship_type=relationship_type,
        confidence=confidence,
        explanation=explanation,
    )

    db.add(relationship)

    # Get an ID before creating association rows.
    db.flush()

    for fact_data in facts:

        membership = RelationshipFact(
            relationship_id=relationship.id,
            fact_id=fact_data["fact_id"],
            role=fact_data.get(
                "role",
                "supporting",
            ),
        )

        db.add(membership)

    db.commit()
    db.refresh(relationship)

    return relationship


def get_all_relationships(
    db: Session,
):
    return (
        db.query(FactRelationship)
        .order_by(
            FactRelationship.id.desc()
        )
        .all()
    )