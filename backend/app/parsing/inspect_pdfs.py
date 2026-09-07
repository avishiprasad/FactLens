import fitz
from pathlib import Path

DATASET_DIR = Path(__file__).resolve().parents[3] / "starter-datasets"

def inspect_pdf(pdf_path: Path):
    print("=" * 100)
    print(f"FILE: {pdf_path.name}")
    print("=" * 100)

    doc = fitz.open(pdf_path)

    print(f"PDF pages: {len(doc)}")

    total_chars = 0
    pages_with_text = 0

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()

        if text:
            pages_with_text += 1
            total_chars += len(text)

    print(f"Pages containing text: {pages_with_text}")
    print(f"Total extracted characters: {total_chars}")

    print("\nFirst page preview:")
    print("-" * 100)

    first_page = doc[0]
    text = first_page.get_text("text")

    print(text[:3000])

    doc.close()


def main():
    pdfs = sorted(DATASET_DIR.rglob("*.pdf"))

    print(f"Found {len(pdfs)} PDFs\n")

    for pdf in pdfs:
        inspect_pdf(pdf)
        print("\n")


if __name__ == "__main__":
    main()