from pathlib import Path
from typing import List, Optional

from app.parsing.pdf_parser import extract_pdf
from app.extraction.llm_extractor import extract_facts
from app.extraction.evidence import verify_evidence


def process_document(
    pdf_path: str,
    pages_to_process: Optional[List[int]] = None
) -> List[dict]:
    """
    Extract structured facts from selected PDF pages.

    Args:
        pdf_path:
            Path to PDF.

        pages_to_process:
            1-based page numbers.
            If None, process every page.

    Returns:
        List of extracted facts with verified evidence.
    """

    pdf_path = Path(pdf_path)

    document_id = pdf_path.stem

    pages = extract_pdf(
        str(pdf_path)
    )

    all_facts = []

    for page in pages:

        page_number = page["page_number"]

        # Skip pages not requested
        if (
            pages_to_process is not None
            and page_number not in pages_to_process
        ):
            continue

        text = page["text"]

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

            evidence_verified = verify_evidence(
                text,
                evidence_text
            )

            fact["document_id"] = document_id
            fact["page_number"] = page_number
            fact["evidence_verified"] = evidence_verified

            all_facts.append(fact)

    return all_facts