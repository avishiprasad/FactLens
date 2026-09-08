from typing import List, Dict

from sqlalchemy.orm import Session

from app.extraction.evidence import verify_evidence
from app.repositories.fact_repository import create_fact
from app.services.reconciliation_service import reconcile_fact


def store_extracted_facts(
    db: Session,
    page_id: int,
    page_text: str,
    facts: List[Dict],
) -> List:
    """
    Verify evidence, store facts, and reconcile each
    newly stored fact against existing facts.
    """

    stored_facts = []

    for fact in facts:

        evidence_text = fact.get(
            "evidence_text",
            "",
        )

        # --------------------------------------------------
        # Evidence verification
        # --------------------------------------------------

        evidence_verified = verify_evidence(
            page_text,
            evidence_text,
        )

        # --------------------------------------------------
        # Store fact
        # --------------------------------------------------

        stored_fact = create_fact(
            db=db,
            subject=fact.get(
                "subject",
                "",
            ),
            predicate=fact.get(
                "predicate",
                "",
            ),
            value=str(
                fact.get(
                    "value",
                    "",
                )
            ),
            value_type=fact.get(
                "value_type",
                "string",
            ),
            unit=fact.get(
                "unit"
            ),
            period=fact.get(
                "period"
            ),
            scope=fact.get(
                "scope"
            ),
            confidence=float(
                fact.get(
                    "confidence",
                    0.0,
                )
            ),
            extraction_method=fact.get(
                "extraction_method",
                "llm",
            ),
            evidence_text=evidence_text,
            evidence_verified=evidence_verified,
            page_id=page_id,
        )

        stored_facts.append(
            stored_fact
        )

        # --------------------------------------------------
        # Reconcile against existing facts
        # --------------------------------------------------

        relationships = reconcile_fact(
            db=db,
            new_fact=stored_fact,
        )

        print(
            f"Fact {stored_fact.id}: "
            f"created {len(relationships)} "
            f"relationship(s)."
        )

    return stored_facts


