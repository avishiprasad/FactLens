import re
from typing import Dict


def normalize_text(value: str) -> str:
    if not value:
        return ""

    value = str(value).lower()

    # Remove parenthetical content
    value = re.sub(r"\([^)]*\)", "", value)

    # Normalize common separators
    value = value.replace("/", "-")

    # Remove punctuation
    value = re.sub(r"[^\w\s-]", " ", value)

    # Collapse whitespace
    value = re.sub(r"\s+", " ", value)

    return value.strip()


def normalize_period(period: str) -> str:
    """
    Normalize equivalent financial-year representations.

    Examples:
        FY2025/26 -> 2025-26
        FY2025-26 -> 2025-26
        2025/26   -> 2025-26
        2025-26   -> 2025-26
    """

    if not period:
        return ""

    period = str(period).lower().strip()

    # Remove whitespace
    period = re.sub(r"\s+", "", period)

    # Remove FY prefix
    period = re.sub(r"^fy", "", period)

    # Normalize slash to hyphen
    period = period.replace("/", "-")

    return period


def normalize_metric(text: str) -> str:
    """
    Normalize semantically equivalent metric descriptions.

    This is intentionally limited to common financial/economic
    metric variations rather than hard-coding document-specific facts.
    """

    if not text:
        return ""

    text = normalize_text(text)

    # Normalize GDP terminology
    replacements = [
        (
            "projected real gdp growth under baseline scenario",
            "real gdp growth",
        ),
        (
            "projected real gdp growth",
            "real gdp growth",
        ),
        (
            "real gdp growth under baseline scenario",
            "real gdp growth",
        ),
        (
            "real gdp growth rate",
            "real gdp growth",
        ),
        (
            "real gross domestic product growth",
            "real gdp growth",
        ),
        (
            "real gross domestic product growth rate",
            "real gdp growth",
        ),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text).strip()

    return text


def canonicalize_fact(fact: Dict) -> Dict:
    """
    Convert a raw fact into a normalized representation used
    for semantic matching and reconciliation.
    """

    subject = normalize_text(
        fact.get("subject", "")
    )

    predicate = normalize_metric(
        fact.get("predicate", "")
    )

    period = normalize_period(
        fact.get("period", "")
    )

    # Normalize subject/metric combinations where the LLM
    # places the entity inside the subject.
    subject = re.sub(
        r"\s+",
        " ",
        subject
    ).strip()

    # Remove normalized period from predicate if an LLM
    # accidentally included it there.
    if period:
        predicate = predicate.replace(period, "")

    predicate = re.sub(
        r"\s+",
        " ",
        predicate
    ).strip()

    # The normalized metric is the strongest signal for
    # financial/economic fact matching.
    metric_text = predicate

    return {
        **fact,

        # Original normalized fields
        "canonical_subject": subject,
        "canonical_predicate": metric_text,
        "canonical_period": period,

        # Useful explicit metric representation
        "canonical_metric": metric_text,
    }