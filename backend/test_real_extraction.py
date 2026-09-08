from app.parsing.pdf_parser import extract_pdf
from app.extraction.llm_extractor import extract_facts


PDF_PATH = (
    "../data/docs/delhivery/"
    "02-delhivery-annual-report-fy24-excerpt.pdf"
)


pages = extract_pdf(PDF_PATH)

page_number = 6
page = pages[page_number - 1]

print("=" * 70)
print("REAL PDF -> GEMINI EXTRACTION")
print("=" * 70)

print(f"PDF: {PDF_PATH}")
print(f"Page: {page_number}")
print("=" * 70)

facts = extract_facts(
    text=page["text"],
    document_id="delhivery-annual-report-fy24",
    page_number=page_number,
)

print()
print("=" * 70)
print(f"EXTRACTED {len(facts)} FACT(S)")
print("=" * 70)

for index, fact in enumerate(facts, start=1):

    print()
    print(f"FACT #{index}")
    print("-" * 70)

    for key, value in fact.items():
        print(f"{key}: {value}")