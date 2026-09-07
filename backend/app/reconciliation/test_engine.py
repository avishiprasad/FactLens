from app.extraction.document_processor import process_document
from app.reconciliation.matcher import find_matching_facts
from app.reconciliation.engine import classify_relationship


ANNUAL_REPORT = (
    "../data/docs/delhivery/"
    "02-delhivery-annual-report-fy24-excerpt.pdf"
)

EARNINGS_PRESENTATION = (
    "../data/docs/delhivery/"
    "03-delhivery-q4-fy24-earnings-presentation.pdf"
)


annual_facts = process_document(
    ANNUAL_REPORT,
    pages_to_process=[6]
)

presentation_facts = process_document(
    EARNINGS_PRESENTATION,
    pages_to_process=[9]
)


matches = find_matching_facts(
    annual_facts,
    presentation_facts
)


print("\n================================")
print("MATCHES")
print("================================\n")


for match in matches:

    fact_a = match["fact_a"]
    fact_b = match["fact_b"]

    print(
        f"{fact_a['predicate']} "
        f"{fact_a['period']}"
    )

    print(
        f"Document A: "
        f"{fact_a['value']} "
        f"{fact_a.get('unit')}"
    )

    print(
        f"Document B: "
        f"{fact_b['value']} "
        f"{fact_b.get('unit')}"
    )

    relationship = classify_relationship(
        fact_a,
        fact_b
    )

    print(
        "\nRelationship:",
        relationship["relationship"]
    )

    print(
        "Confidence:",
        relationship["confidence"]
    )

    print(
        "Reason:",
        relationship["reason"]
    )

    print(
        "Relative difference:",
        relationship["relative_difference"]
    )

    print("\n----------------------------")