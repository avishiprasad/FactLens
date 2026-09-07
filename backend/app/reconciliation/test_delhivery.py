import json

from app.extraction.document_processor import process_document


ANNUAL_REPORT = (
    "../data/docs/delhivery/"
    "02-delhivery-annual-report-fy24-excerpt.pdf"
)

EARNINGS_PRESENTATION = (
    "../data/docs/delhivery/"
    "03-delhivery-q4-fy24-earnings-presentation.pdf"
)


print("\n================================")
print("PROCESSING ANNUAL REPORT")
print("================================\n")

annual_facts = process_document(
    ANNUAL_REPORT,
    pages_to_process=[6]
)


print("\n================================")
print("PROCESSING EARNINGS PRESENTATION")
print("================================\n")

presentation_facts = process_document(
    EARNINGS_PRESENTATION,
    pages_to_process=[9]
)


print("\n================================")
print("ANNUAL REPORT FACTS")
print("================================\n")

print(
    json.dumps(
        annual_facts,
        indent=2,
        ensure_ascii=False
    )
)


print("\n================================")
print("PRESENTATION FACTS")
print("================================\n")

print(
    json.dumps(
        presentation_facts,
        indent=2,
        ensure_ascii=False
    )
)