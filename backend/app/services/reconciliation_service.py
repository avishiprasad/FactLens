from typing import Dict, List

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


def fact_to_dict(
    fact: Fact,
) -> Dict:

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

        "page_text": (
            fact.page.text
            if fact.page
            else ""
        ),

        "document_id": (
            fact.page.document_id
            if fact.page and fact.page.document
            else None
        ),
    }


def relationship_already_exists(
    db: Session,
    fact_a_id: int,
    fact_b_id: int,
) -> bool:

    from app.db.models import (
        FactRelationship,
        RelationshipFact,
    )

    relationships = (
        db.query(FactRelationship)
        .all()
    )

    target_ids = {
        fact_a_id,
        fact_b_id,
    }

    for relationship in relationships:

        relationship_fact_ids = {
            membership.fact_id
            for membership in relationship.facts
        }

        if relationship_fact_ids == target_ids:
            return True

    return False


def reconcile_fact(
    db: Session,
    new_fact: Fact,
) -> List[Dict]:

    # ---------------------------------------------------------
    # Only compare against facts from OTHER documents.
    # ---------------------------------------------------------

    new_document_id = (
        new_fact.page.document.id
        if new_fact.page
        else None
    )

    existing_facts = (
        db.query(Fact)
        .filter(
            Fact.id != new_fact.id
        )
        .all()
    )

    existing_facts = [
        fact
        for fact in existing_facts
        if (
            fact.page
            and fact.page.document
            and fact.page.document.id != new_document_id
        )
    ]

    if not existing_facts:
        return []

    new_fact_dict = fact_to_dict(
        new_fact
    )

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

        relationship_type = classification.get(
            "relationship_type"
        )

        if not relationship_type:
            print(
                "Skipping malformed classification:",
                classification,
            )
            continue

        fact_a_id = fact_a["id"]
        fact_b_id = fact_b["id"]

        if relationship_already_exists(
            db,
            fact_a_id,
            fact_b_id,
        ):
            continue

        relationship = create_relationship(
            db=db,
            relationship_type=relationship_type,
            confidence=classification.get(
                "confidence",
                0.30,
            ),
            explanation=classification.get(
                "explanation",
                "No explanation available.",
            ),
            facts=[
                {
                    "fact_id": fact_a_id,
                    "role": "source",
                },
                {
                    "fact_id": fact_b_id,
                    "role": "compared",
                },
            ],
        )

        relationships.append(
            {
                "id": relationship.id,
                "fact_a_id": fact_a_id,
                "fact_b_id": fact_b_id,
                "relationship_type": relationship_type,
                "confidence": classification.get(
                    "confidence",
                    0.30,
                ),
                "explanation": classification.get(
                    "explanation",
                    "",
                ),
            }
        )

    return relationships