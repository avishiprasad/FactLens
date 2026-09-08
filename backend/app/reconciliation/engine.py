from decimal import Decimal
from typing import Dict, List

from app.extraction.evidence import verify_evidence
from app.reconciliation.normalizer import normalize_value


def unresolved(
    explanation: str,
    confidence: float = 0.30,
) -> Dict:
    """
    Every classification path returns the same schema.
    This prevents downstream KeyError failures.
    """

    return {
        "relationship_type": "UNRESOLVED",
        "confidence": confidence,
        "explanation": explanation,
    }


def classify_relationship(
    fact_a: Dict,
    fact_b: Dict,
) -> Dict:

    # ---------------------------------------------------------
    # 1. Evidence validation
    # ---------------------------------------------------------

    evidence_a = fact_a.get("evidence_text", "")
    evidence_b = fact_b.get("evidence_text", "")

    page_text_a = fact_a.get("page_text", "")
    page_text_b = fact_b.get("page_text", "")

    # If page text is available, verify evidence against it.
    if page_text_a and evidence_a:
        if not verify_evidence(page_text_a, evidence_a):
            return unresolved(
                "Fact A could not be grounded in its source evidence."
            )

    if page_text_b and evidence_b:
        if not verify_evidence(page_text_b, evidence_b):
            return unresolved(
                "Fact B could not be grounded in its source evidence."
            )

    # Also respect the stored verification flag.
    if fact_a.get("evidence_verified") is False:
        return unresolved(
            "Fact A has unverified source evidence."
        )

    if fact_b.get("evidence_verified") is False:
        return unresolved(
            "Fact B has unverified source evidence."
        )

    # ---------------------------------------------------------
    # 2. Required values
    # ---------------------------------------------------------

    value_a = fact_a.get("value")
    value_b = fact_b.get("value")

    if value_a in (None, "") or value_b in (None, ""):
        return unresolved(
            "One or both facts are missing a numerical value."
        )

    # ---------------------------------------------------------
    # 3. Normalize units
    # ---------------------------------------------------------

    try:
        normalized_a = normalize_value(
            value_a,
            fact_a.get("unit"),
        )

        normalized_b = normalize_value(
            value_b,
            fact_b.get("unit"),
        )

    except (ValueError, TypeError, ArithmeticError) as error:

        return unresolved(
            "The facts could not be compared because their units "
            f"could not be normalized: {error}"
        )

    # ---------------------------------------------------------
    # 4. Same normalized value
    # ---------------------------------------------------------

    denominator = max(
        abs(normalized_a),
        abs(normalized_b),
    )

    if denominator == 0:

        relative_difference = Decimal("0")

    else:

        relative_difference = (
            abs(normalized_a - normalized_b)
            / denominator
        )

    # 1% tolerance handles rounding differences.
    if relative_difference <= Decimal("0.01"):

        return {
            "relationship_type": "CORROBORATES",
            "confidence": 0.99,
            "explanation": (
                "The two facts report consistent values after "
                "normalizing their units."
            ),
        }

    # ---------------------------------------------------------
    # 5. Different scopes
    # ---------------------------------------------------------

    scope_a = fact_a.get("scope")
    scope_b = fact_b.get("scope")

    if scope_a and scope_b and scope_a != scope_b:

        return {
            "relationship_type": "CONTEXTUAL_DIFFERENCE",
            "confidence": 0.85,
            "explanation": (
                "The values differ, but the facts have different "
                "scopes or definitions. The difference may therefore "
                "be explained by context rather than a contradiction."
            ),
        }

    # ---------------------------------------------------------
    # 6. Genuine contradiction
    # ---------------------------------------------------------

    return {
        "relationship_type": "CONTRADICTS",
        "confidence": 0.90,
        "explanation": (
            "The facts refer to the same metric and period but "
            "their normalized values differ materially."
        ),
    }


def classify_contextual_reconciliation(
    component_facts: List[Dict],
    total_fact: Dict,
) -> Dict:

    if not component_facts:
        return unresolved(
            "No component facts were provided."
        )

    total_value = total_fact.get("value")

    if total_value in (None, ""):
        return unresolved(
            "The total fact is missing a value."
        )

    try:

        total_normalized = normalize_value(
            total_value,
            total_fact.get("unit"),
        )

        component_sum = Decimal("0")

        for fact in component_facts:

            value = fact.get("value")

            if value in (None, ""):
                return unresolved(
                    "A component fact is missing a value."
                )

            component_sum += normalize_value(
                value,
                fact.get("unit"),
            )

    except (ValueError, TypeError, ArithmeticError) as error:

        return unresolved(
            "The reconciliation could not be calculated because "
            f"a value or unit could not be normalized: {error}"
        )

    denominator = max(
        abs(total_normalized),
        abs(component_sum),
    )

    if denominator == 0:

        relative_difference = Decimal("0")

    else:

        relative_difference = (
            abs(total_normalized - component_sum)
            / denominator
        )

    if relative_difference <= Decimal("0.01"):

        component_text = " + ".join(
            str(fact.get("value"))
            for fact in component_facts
        )

        return {
            "relationship_type": "RECONCILED",
            "confidence": 0.98,
            "explanation": (
                f"The component values reconcile to the reported "
                f"total: {component_text} = "
                f"{total_fact.get('value')}. "
                "The apparent difference is explained by the "
                "different scopes of the component and total facts."
            ),
        }

    return unresolved(
        "The component facts do not mathematically reconcile "
        "to the reported total.",
        confidence=0.45,
    )


def classify_forecast_relationship(
    fact_a: Dict,
    fact_b: Dict,
) -> Dict:

    value_a = fact_a.get("value")
    value_b = fact_b.get("value")

    if value_a in (None, "") or value_b in (None, ""):

        return unresolved(
            "One or both forecast facts are missing a value."
        )

    try:

        normalized_a = normalize_value(
            value_a,
            fact_a.get("unit"),
        )

        normalized_b = normalize_value(
            value_b,
            fact_b.get("unit"),
        )

    except (ValueError, TypeError, ArithmeticError) as error:

        return unresolved(
            "Forecast values could not be normalized: "
            f"{error}"
        )

    denominator = max(
        abs(normalized_a),
        abs(normalized_b),
    )

    if denominator == 0:

        relative_difference = Decimal("0")

    else:

        relative_difference = (
            abs(normalized_a - normalized_b)
            / denominator
        )

    if relative_difference <= Decimal("0.01"):

        return {
            "relationship_type": "CORROBORATES",
            "confidence": 0.99,
            "explanation": (
                "The independently produced forecasts are "
                "effectively equal after normalization."
            ),
        }

    source_a = fact_a.get("scope")
    source_b = fact_b.get("scope")

    if source_a and source_b and source_a != source_b:

        return {
            "relationship_type": "LIKELY_DISAGREEMENT",
            "confidence": 0.90,
            "explanation": (
                "Both forecasts describe the same metric and "
                "period, but independently produced estimates "
                f"differ: {value_a}% versus {value_b}%. "
                "This is treated as a likely disagreement rather "
                "than a hard contradiction."
            ),
        }

    return {
        "relationship_type": "CONTRADICTS",
        "confidence": 0.90,
        "explanation": (
            "The forecasts refer to the same metric and period "
            "but differ materially."
        ),
    }