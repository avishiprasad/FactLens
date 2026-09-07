from app.reconciliation.matcher import (
    predicate_similarity,
    facts_match_semantically,
)


def make_fact(
    predicate,
    period="FY24"
):
    return {
        "subject": "Delhivery",
        "predicate": predicate,
        "value": "100",
        "unit": "₹ crore",
        "period": period,
    }


tests = [
    (
        "Revenue from services",
        "Revenue from services",
        True,
    ),

    (
        "Revenue from services",
        "Revenue from services in FY24",
        True,
    ),

    (
        "Revenue from services",
        "Express Parcel revenue",
        False,
    ),

    (
        "Revenue from services",
        "PTL freight revenue",
        False,
    ),

    (
        "Express parcel shipment volume",
        "Express Parcel shipments",
        True,
    ),

    (
        "Express parcel shipment volume",
        "Express Parcel revenue",
        False,
    ),

    (
        "PTL freight tonnage",
        "PTL freight revenue",
        False,
    ),
]


for predicate_a, predicate_b, expected in tests:

    fact_a = make_fact(predicate_a)
    fact_b = make_fact(predicate_b)

    similarity = predicate_similarity(
        predicate_a,
        predicate_b
    )

    result = facts_match_semantically(
        fact_a,
        fact_b
    )

    print("--------------------------------")
    print("A:", predicate_a)
    print("B:", predicate_b)
    print("Similarity:", similarity)
    print("Expected:", expected)
    print("Actual:", result)

    assert result == expected


print("\nALL MATCHER TESTS PASSED")