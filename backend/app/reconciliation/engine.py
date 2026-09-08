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
def classify_contextual_reconciliation(
    component_facts,
    total_fact
):
    """
    Determine whether multiple component facts reconcile
    to a broader total despite having different scopes.
    """

    if not component_facts:
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": "No component facts were provided."
        }

    if not total_fact:
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": "No total fact was provided."
        }

    try:
        component_values = [
            normalize_value(
                fact["value"],
                fact.get("unit")
            )
            for fact in component_facts
        ]

        total_value = normalize_value(
            total_fact["value"],
            total_fact.get("unit")
        )

    except (ValueError, KeyError) as error:
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.40,
            "reason": (
                "The component values could not be normalized: "
                + str(error)
            )
        }

    component_sum = sum(component_values)

    difference = relative_difference(
        component_sum,
        total_value
    )

    if values_are_close(
        component_sum,
        total_value,
        tolerance=0.01
    ):
        return {
            "relationship": "RECONCILED",
            "confidence": 0.98,
            "component_sum": str(component_sum),
            "total_value": str(total_value),
            "relative_difference": str(difference),
            "reason": (
                "The broader total is mathematically reconciled "
                "by the component facts after unit normalization. "
                "The apparent difference is explained by their "
                "different scopes."
            )
        }

    return {
        "relationship": "UNRESOLVED",
        "confidence": 0.45,
        "component_sum": str(component_sum),
        "total_value": str(total_value),
        "relative_difference": str(difference),
        "reason": (
            "The component facts do not reconcile to the reported total."
        )
    }
def classify_forecast_relationship(
    fact_a: Dict,
    fact_b: Dict
) -> Dict:
    """
    Compare independently produced forecasts for the same
    metric and period.

    Small differences between forecasts are classified as
    LIKELY_DISAGREEMENT rather than a hard contradiction.
    """

    if not fact_a.get("evidence_verified", True) or not fact_b.get(
        "evidence_verified", True
    ):
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": (
                "At least one forecast could not be reliably "
                "verified against its source evidence."
            )
        }

    if fact_a.get("value") is None or fact_b.get("value") is None:
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.30,
            "reason": (
                "One or both forecasts do not contain a reliable value."
            )
        }

    try:
        value_a = normalize_value(
            fact_a["value"],
            fact_a.get("unit")
        )

        value_b = normalize_value(
            fact_b["value"],
            fact_b.get("unit")
        )

    except (ValueError, KeyError) as error:
        return {
            "relationship": "UNRESOLVED",
            "confidence": 0.40,
            "reason": (
                "The forecast values could not be normalized: "
                + str(error)
            )
        }

    difference = relative_difference(value_a, value_b)

    source_a = fact_a.get("scope", "")
    source_b = fact_b.get("scope", "")

    # Same forecast
    if values_are_close(
        value_a,
        value_b,
        tolerance=0.01
    ):
        return {
            "relationship": "CORROBORATES",
            "confidence": 0.98,
            "normalized_value_a": str(value_a),
            "normalized_value_b": str(value_b),
            "relative_difference": str(difference),
            "reason": (
                "The independently reported forecasts are "
                "consistent within the allowed tolerance."
            )
        }

    # Different forecast values from independent sources
    if source_a and source_b and source_a != source_b:
        return {
            "relationship": "LIKELY_DISAGREEMENT",
            "confidence": 0.90,
            "normalized_value_a": str(value_a),
            "normalized_value_b": str(value_b),
            "relative_difference": str(difference),
            "reason": (
                "The forecasts describe the same metric and period "
                "but differ slightly because they are independently "
                "produced by different sources. This is treated as "
                "a likely disagreement rather than a hard contradiction."
            )
        }

    return {
        "relationship": "CONTRADICTS",
        "confidence": 0.90,
        "normalized_value_a": str(value_a),
        "normalized_value_b": str(value_b),
        "relative_difference": str(difference),
        "reason": (
            "The forecasts describe the same metric and period "
            "but have materially different values."
        )
    }