from typing import List, Dict


def normalize_string(value: str) -> str:
    """
    Normalize text for simple matching.
    """

    return (
        value
        .lower()
        .strip()
        .replace("_", " ")
    )


def facts_match_semantically(
    fact_a: Dict,
    fact_b: Dict
) -> bool:
    """
    Determine whether two facts are likely describing
    the same underlying business fact.
    """

    subject_a = normalize_string(
        fact_a.get("subject", "")
    )

    subject_b = normalize_string(
        fact_b.get("subject", "")
    )

    predicate_a = normalize_string(
        fact_a.get("predicate", "")
    )

    predicate_b = normalize_string(
        fact_b.get("predicate", "")
    )

    period_a = normalize_string(
        fact_a.get("period", "")
    )

    period_b = normalize_string(
        fact_b.get("period", "")
    )

    same_subject = (
        subject_a == subject_b
    )

    same_period = (
        period_a == period_b
    )

    # For the first version, allow the predicate
    # to contain the same important words.
    predicate_words_a = set(
        predicate_a.split()
    )

    predicate_words_b = set(
        predicate_b.split()
    )

    predicate_overlap = (
        len(
            predicate_words_a
            & predicate_words_b
        ) > 0
    )

    return (
        same_subject
        and same_period
        and predicate_overlap
    )


def find_matching_facts(
    facts_a: List[Dict],
    facts_b: List[Dict]
) -> List[Dict]:

    matches = []

    for fact_a in facts_a:

        for fact_b in facts_b:

            if facts_match_semantically(
                fact_a,
                fact_b
            ):

                matches.append({
                    "fact_a": fact_a,
                    "fact_b": fact_b
                })

    return matches