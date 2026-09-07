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


def detect_metric_type(predicate: str) -> str:
    words = set(predicate.lower().split())

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
    predicate_a: str,
    predicate_b: str
) -> bool:

    type_a = detect_metric_type(predicate_a)
    type_b = detect_metric_type(predicate_b)

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

    # For metric phrases such as:
    #
    # "Express parcel shipment volume"
    # "Express Parcel shipments"
    #
    # we use the overlap of the specific metric words
    # relative to the smaller phrase.
    #
    # This allows one phrase to contain an additional
    # descriptive word without creating false matches.

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

    if not same_period(
        fact_a,
        fact_b
    ):
        return False

    similarity = predicate_similarity(
        fact_a["canonical_predicate"],
        fact_b["canonical_predicate"]
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

            similarity = predicate_similarity(
                fact_a["canonical_predicate"],
                fact_b["canonical_predicate"]
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