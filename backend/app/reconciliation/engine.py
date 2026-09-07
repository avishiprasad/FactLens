from typing import Dict

from app.reconciliation.normalizer import normalize_value
from app.reconciliation.comparator import (
    relative_difference,
    values_are_close,
)


def classify_relationship(
    fact_a: Dict,
    fact_b: Dict
) -> Dict:

    # --------------------------------------------------
    # 1. Check whether evidence is trustworthy
    # --------------------------------------------------

    evidence_a = fact_a.get(
        "evidence_verified",
        True
    )

    evidence_b = fact_b.get(
        "evidence_verified",
        True
    )

    if not evidence_a or not evidence_b:

        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": (
                "At least one fact could not be reliably "
                "verified against its source evidence."
            )
        }

    # --------------------------------------------------
    # 2. Check for missing numerical values
    # --------------------------------------------------

    if fact_a.get("value") is None or fact_b.get("value") is None:

        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": (
                "One or both facts do not contain a reliable "
                "numerical value."
            )
        }

    # --------------------------------------------------
    # 3. Normalize units
    # --------------------------------------------------

    try:

        value_a = normalize_value(
            fact_a["value"],
            fact_a.get("unit")
        )

        value_b = normalize_value(
            fact_b["value"],
            fact_b.get("unit")
        )

    except ValueError as error:

        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.40,
            "reason": (
                "The values could not be normalized because "
                "one of the units is unsupported: "
                + str(error)
            )
        }

    # --------------------------------------------------
    # 4. Compare normalized values
    # --------------------------------------------------

    difference = relative_difference(
        value_a,
        value_b
    )

    close = values_are_close(
        value_a,
        value_b,
        tolerance=0.01
    )

    # --------------------------------------------------
    # 5. Exact / near-exact agreement
    # --------------------------------------------------

    if close:

        return {
            "relationship": "CORROBORATES",
            "confidence": 0.99,
            "normalized_value_a": str(value_a),
            "normalized_value_b": str(value_b),
            "relative_difference": str(difference),
            "reason": (
                "The two documents describe the same fact "
                "and period. Their values are consistent "
                "after unit normalization within the "
                "allowed tolerance."
            )
        }

    # --------------------------------------------------
    # 6. Different scope
    # --------------------------------------------------

    scope_a = fact_a.get("scope")
    scope_b = fact_b.get("scope")

    if scope_a and scope_b and scope_a != scope_b:

        return {
            "relationship": "CONTEXTUAL_DIFFERENCE",
            "confidence": 0.85,
            "normalized_value_a": str(value_a),
            "normalized_value_b": str(value_b),
            "relative_difference": str(difference),
            "reason": (
                "The values differ, but the facts explicitly "
                "refer to different scopes."
            )
        }

    # --------------------------------------------------
    # 7. Numerical disagreement
    # --------------------------------------------------

    return {
        "relationship": "CONTRADICTS",
        "confidence": 0.90,
        "normalized_value_a": str(value_a),
        "normalized_value_b": str(value_b),
        "relative_difference": str(difference),
        "reason": (
            "The facts appear to describe the same "
            "underlying metric and period, but their "
            "normalized values differ beyond the "
            "allowed tolerance."
        )
    }