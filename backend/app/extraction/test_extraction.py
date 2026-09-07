from app.parsing.pdf_parser import extract_pdf
from app.extraction.llm_extractor import extract_facts
from app.extraction.evidence import verify_evidence


PDF = "../data/docs/delhivery/02-delhivery-annual-report-fy24-excerpt.pdf"


pages = extract_pdf(PDF)

# PDF page 6
page = pages[5]

print(f"Testing page {page['page_number']}")


facts = extract_facts(
    text=page["text"],
    document_id="delhivery_annual_report_fy24",
    page_number=page["page_number"]
)


for fact in facts:

    evidence_text = fact.get(
        "evidence_text",
        ""
    )

    verified = verify_evidence(
        page["text"],
        evidence_text
    )

    print("\n----------------------------")

    print("Subject:", fact["subject"])
    print("Predicate:", fact["predicate"])
    print("Value:", fact["value"])
    print("Unit:", fact.get("unit"))
    print("Period:", fact.get("period"))
    print("Scope:", fact.get("scope"))

    print(
        "Evidence verified:",
        verified
    )

    print(
        "Evidence:",
        evidence_text
    )