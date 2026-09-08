from typing import List, Dict

from app.reconciliation.canonicalizer import canonicalize_fact


GENERIC_WORDS = {
    "revenue",
    "income",
    "amount",
    "value",
    "total",
    "growth",
    "rate",
    "number",
    "projected",
    "expected",
    "under",
    "baseline",
    "scenario",
    "approximately",
    "approximate",
}


STOPWORDS = {
    "from",
    "in",
    "for",
    "the",
    "of",
    "and",
    "on",
    "to",
    "a",
    "an",
    "during",
    "at",
    "is",
    "was",
    "were",
    "with",
    "by",
    "over",
}


METRIC_TYPES = {
    "revenue": {
        "revenue",
        "income",
        "sales",
    },

    "volume": {
        "volume",
        "shipments",
        "shipment",
        "tons",
        "tonnage",
        "quantity",
        "units",
    },

    "percentage": {
        "%",
        "percent",
        "percentage",
        "margin",
        "rate",
    },

    "time": {
        "days",
        "hours",
        "months",
        "years",
    },
}


def meaningful_words(value: str) -> set:
    words = value.lower().split()

    return {
        word
        for word in words
        if word not in STOPWORDS
    }


def specific_words(value: str) -> set:
    words = meaningful_words(value)

    return {
        word
        for word in words
        if word not in GENERIC_WORDS
    }


def build_metric_text(fact: Dict) -> str:
    """
    Build a semantic metric representation using both
    subject and predicate.

    This handles cases where an LLM places the metric
    inconsistently between subject and predicate.

    Example:

        RBI:
        subject   = "real GDP growth"
        predicate = "projected at"

        IMF:
        subject   = "India"
        predicate = "projected real GDP growth under baseline scenario"

    Both become comparable metric representations.
    """

    subject = fact.get("canonical_subject", "")
    predicate = fact.get("canonical_predicate", "")

    combined = f"{subject} {predicate}".strip()

    return combined


def detect_metric_type(text: str) -> str:
    words = set(text.lower().split())

    detected_types = []

    for metric_type, keywords in METRIC_TYPES.items():

        if words & keywords:
            detected_types.append(metric_type)

    if len(detected_types) == 1:
        return detected_types[0]

    if len(detected_types) > 1:
        return "mixed"

    return "unknown"


def metric_types_compatible(
    metric_a: str,
    metric_b: str
) -> bool:

    type_a = detect_metric_type(metric_a)
    type_b = detect_metric_type(metric_b)

    if type_a != "unknown" and type_b != "unknown":
        return type_a == type_b

    return True


def predicate_similarity(
    predicate_a: str,
    predicate_b: str
) -> float:

    if not metric_types_compatible(
        predicate_a,
        predicate_b
    ):
        return 0.0

    words_a = meaningful_words(predicate_a)
    words_b = meaningful_words(predicate_b)

    specific_a = specific_words(predicate_a)
    specific_b = specific_words(predicate_b)

    if not specific_a or not specific_b:
        return 0.0

    specific_intersection = specific_a & specific_b

    if not specific_intersection:
        return 0.0

    denominator = min(
        len(specific_a),
        len(specific_b)
    )

    return len(specific_intersection) / denominator


def same_period(
    fact_a: Dict,
    fact_b: Dict
) -> bool:

    period_a = fact_a.get(
        "canonical_period",
        ""
    )

    period_b = fact_b.get(
        "canonical_period",
        ""
    )

    return period_a == period_b


def facts_match_semantically(
    fact_a: Dict,
    fact_b: Dict,
    similarity_threshold: float = 0.50,
) -> bool:

    fact_a = canonicalize_fact(fact_a)
    fact_b = canonicalize_fact(fact_b)

    # Period must match.
    if not same_period(
        fact_a,
        fact_b
    ):
        return False

    # IMPORTANT:
    # Use both subject and predicate because LLMs may
    # place the metric in either field.
    metric_a = build_metric_text(fact_a)
    metric_b = build_metric_text(fact_b)

    similarity = predicate_similarity(
        metric_a,
        metric_b
    )

    return similarity >= similarity_threshold


def find_matching_facts(
    facts_a: List[Dict],
    facts_b: List[Dict]
) -> List[Dict]:

    matches = []

    for original_a in facts_a:

        for original_b in facts_b:

            fact_a = canonicalize_fact(
                original_a
            )

            fact_b = canonicalize_fact(
                original_b
            )

            metric_a = build_metric_text(
                fact_a
            )

            metric_b = build_metric_text(
                fact_b
            )

            similarity = predicate_similarity(
                metric_a,
                metric_b
            )

            if facts_match_semantically(
                original_a,
                original_b
            ):

                matches.append({
                    "fact_a": original_a,
                    "fact_b": original_b,
                    "predicate_similarity": similarity,
                })

    return matches