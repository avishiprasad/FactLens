from app.parsing.pdf_parser import extract_pdf


PDF_PATH = (
    "../data/docs/delhivery/"
    "02-delhivery-annual-report-fy24-excerpt.pdf"
)


pages = extract_pdf(PDF_PATH)

page_number = 6
page = pages[page_number - 1]

print("=" * 70)
print("REAL PDF PARSER TEST")
print("=" * 70)

print(f"PDF: {PDF_PATH}")
print(f"Total pages: {len(pages)}")
print(f"Testing page: {page_number}")
print("=" * 70)

print(page["text"])