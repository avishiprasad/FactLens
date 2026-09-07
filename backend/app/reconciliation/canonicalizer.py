import re
from typing import Dict


def normalize_text(value: str) -> str:
    if not value:
        return ""

    value = value.lower()
    value = re.sub(r"\([^)]*\)", "", value)
    value = re.sub(r"[^\w\s]", " ", value)
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def canonicalize_fact(fact: Dict) -> Dict:
    subject = normalize_text(
        fact.get("subject", "")
    )

    predicate = normalize_text(
        fact.get("predicate", "")
    )

    period = normalize_text(
        fact.get("period", "")
    )

    # Remove period from predicate because period
    # is already represented separately.
    if period:
        predicate = predicate.replace(period, "")

    predicate = re.sub(
        r"\s+",
        " ",
        predicate
    ).strip()

    # Some LLM outputs place the actual entity in
    # the predicate/subject inconsistently.
    #
    # For financial metrics, the metric itself is
    # the strongest matching signal.
    metric_text = predicate

    return {
        **fact,
        "canonical_subject": subject,
        "canonical_predicate": metric_text,
        "canonical_period": period,
    }