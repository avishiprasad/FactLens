from typing import List, Dict

from sqlalchemy.orm import Session

from app.db.models import Fact
from app.repositories.relationship_repository import (
    create_relationship,
)
from app.reconciliation.matcher import (
    find_matching_facts,
)
from app.reconciliation.engine import (
    classify_relationship,
)


def fact_to_dict(fact: Fact) -> Dict:
    """
    Convert a database Fact object into the dictionary
    format expected by the reconciliation engine.
    """

    return {
        "id": fact.id,
        "subject": fact.subject,
        "predicate": fact.predicate,
        "value": fact.value,
        "value_type": fact.value_type,
        "unit": fact.unit,
        "period": fact.period,
        "scope": fact.scope,
        "confidence": fact.confidence,
        "evidence_text": fact.evidence_text,
        "evidence_verified": bool(
            fact.evidence_verified
        ),
    }


def reconcile_fact(
    db: Session,
    new_fact: Fact,
) -> List[Dict]:
    """
    Find existing facts that may correspond to a newly
    extracted fact and create relationships.

    The process is intentionally incremental:

        new fact
             ↓
        existing facts
             ↓
        candidate matching
             ↓
        relationship classification
             ↓
        relationship storage
    """

    existing_facts = (
        db.query(Fact)
        .filter(Fact.id != new_fact.id)
        .all()
    )

    if not existing_facts:
        return []

    new_fact_dict = fact_to_dict(new_fact)

    existing_fact_dicts = [
        fact_to_dict(fact)
        for fact in existing_facts
    ]

    matches = find_matching_facts(
        [new_fact_dict],
        existing_fact_dicts,
    )

    relationships = []

    for match in matches:

        fact_a = match["fact_a"]
        fact_b = match["fact_b"]

        classification = classify_relationship(
            fact_a,
            fact_b,
        )

        relationship = create_relationship(
            db=db,
            fact_a_id=fact_a["id"],
            fact_b_id=fact_b["id"],
            relationship_type=classification[
                "relationship_type"
            ],
            confidence=classification[
                "confidence"
            ],
            explanation=classification[
                "explanation"
            ],
        )

        relationships.append(
            {
                "relationship_id": relationship.id,
                "fact_a_id": fact_a["id"],
                "fact_b_id": fact_b["id"],
                "relationship_type": classification[
                    "relationship_type"
                ],
                "confidence": classification[
                    "confidence"
                ],
                "explanation": classification[
                    "explanation"
                ],
            }
        )

    return relationships







