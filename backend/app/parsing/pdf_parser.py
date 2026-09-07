from pathlib import Path
from typing import List, Dict
import fitz


def extract_pdf(pdf_path: str) -> List[Dict]:
    """
    Extract text page-by-page from a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "...",
                "char_count": 1234
            },
            ...
        ]
    """

    pdf_path = Path(pdf_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    pages = []

    with fitz.open(pdf_path) as document:
        for page_number, page in enumerate(document, start=1):

            text = page.get_text("text").strip()

            pages.append({
                "page_number": page_number,
                "text": text,
                "char_count": len(text)
            })

    return pages


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("Usage:")
        print("python pdf_parser.py <path-to-pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    pages = extract_pdf(pdf_path)

    print(f"Extracted {len(pages)} pages")

    for page in pages[:5]:
        print(
            f"\nPage {page['page_number']} "
            f"({page['char_count']} characters)"
        )
        print(page["text"][:500])