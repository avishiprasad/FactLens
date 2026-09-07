from typing import Dict

from app.reconciliation.normalizer import normalize_value
from app.reconciliation.comparator import (
    relative_difference,
    values_are_close
)


def classify_relationship(
    fact_a: Dict,
    fact_b: Dict
) -> Dict:
    """
    Compare two semantically matching numerical facts.
    """

    value_a = normalize_value(
        fact_a["value"],
        fact_a.get("unit")
    )

    value_b = normalize_value(
        fact_b["value"],
        fact_b.get("unit")
    )

    difference = relative_difference(
        value_a,
        value_b
    )

    close = values_are_close(
        value_a,
        value_b,
        tolerance=0.01
    )

    if close:

        return {
            "relationship": "CORROBORATES",
            "confidence": 0.99,
            "normalized_value_a": str(value_a),
            "normalized_value_b": str(value_b),
            "relative_difference": str(
                difference
            ),
            "reason": (
                "Both documents report the same "
                "underlying fact. Their values are "
                "consistent after unit normalization "
                "within the allowed tolerance."
            )
        }

    return {
        "relationship": "CONTRADICTS",
        "confidence": 0.90,
        "normalized_value_a": str(value_a),
        "normalized_value_b": str(value_b),
        "relative_difference": str(
            difference
        ),
        "reason": (
            "Both documents appear to describe "
            "the same fact and period, but their "
            "normalized numerical values differ "
            "beyond the allowed tolerance."
        )
    }