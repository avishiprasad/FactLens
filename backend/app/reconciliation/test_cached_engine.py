from app.reconciliation.fixtures import (
    ANNUAL_REPORT_FACTS,
    PRESENTATION_FACTS,
)

from app.reconciliation.matcher import (
    find_matching_facts,
)

from app.reconciliation.engine import (
    classify_relationship,
)


matches = find_matching_facts(
    ANNUAL_REPORT_FACTS,
    PRESENTATION_FACTS
)


print("\n================================")
print("CACHED FACT RECONCILIATION")
print("================================\n")


for match in matches:

    fact_a = match["fact_a"]
    fact_b = match["fact_b"]

    print("Document A:")
    print(
        fact_a["predicate"],
        "|",
        fact_a["value"],
        fact_a.get("unit"),
        "|",
        fact_a.get("period")
    )

    print("\nDocument B:")
    print(
        fact_b["predicate"],
        "|",
        fact_b["value"],
        fact_b.get("unit"),
        "|",
        fact_b.get("period")
    )

    print(
        "\nPredicate similarity:",
        match["predicate_similarity"]
    )

    relationship = classify_relationship(
        fact_a,
        fact_b
    )

    print(
        "Relationship:",
        relationship["relationship"]
    )

    print(
        "Normalized A:",
        relationship.get("normalized_value_a")
    )

    print(
        "Normalized B:",
        relationship.get("normalized_value_b")
    )

    print(
        "Relative difference:",
        relationship.get("relative_difference")
    )

    print(
        "Reason:",
        relationship["reason"]
    )

    print("\n----------------------------")