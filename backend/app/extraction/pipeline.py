from pathlib import Path

from app.parsing.pdf_parser import extract_pdf
from app.extraction.llm_extractor import extract_facts
from app.extraction.evidence import verify_evidence


def process_pdf(pdf_path: str):

    pdf_path = Path(pdf_path)

    document_id = pdf_path.stem

    pages = extract_pdf(
        str(pdf_path)
    )

    all_facts = []

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        # Skip empty pages
        if not text.strip():
            continue

        print(
            f"Processing {document_id} "
            f"page {page_number}..."
        )

        facts = extract_facts(
            text=text,
            document_id=document_id,
            page_number=page_number
        )

        for fact in facts:

            evidence_text = fact.get(
                "evidence_text",
                ""
            )

            evidence_valid = verify_evidence(
                text,
                evidence_text
            )

            fact["document_id"] = document_id
            fact["page_number"] = page_number
            fact["evidence_verified"] = evidence_valid

            all_facts.append(fact)

    return all_facts


if __name__ == "__main__":

    import json
    import sys

    if len(sys.argv) != 2:

        print(
            "Usage: "
            "python pipeline.py <pdf>"
        )

        sys.exit(1)

    pdf_path = sys.argv[1]

    facts = process_pdf(pdf_path)

    print("\n\nEXTRACTED FACTS\n")

    print(
        json.dumps(
            facts,
            indent=2,
            ensure_ascii=False
        )
    )