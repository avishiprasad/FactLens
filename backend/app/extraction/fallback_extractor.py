import re
from typing import List, Dict


NUMBER_PATTERN = r"\d[\d,]*(?:\.\d+)?"


def extract_simple_facts(
    text: str,
    document_id: str,
    page_number: int,
) -> List[Dict]:
    """
    Conservative deterministic fallback extractor.

    It only extracts simple numerical statements where
    the meaning and value occur together.

    If the structure is ambiguous, it returns no fact
    rather than guessing.
    """

    facts = []

    # --------------------------------------------------
    # Revenue / income / sales
    # --------------------------------------------------

    revenue_pattern = re.compile(
        rf"(?P<predicate>"
        rf"(?:revenue|income|sales)"
        rf"(?:\s+\w+){{0,6}}"
        rf")"
        rf"\s*(?:was|is|of|:)?\s*"
        rf"(?:₹|Rs\.?|INR)?\s*"
        rf"(?P<value>{NUMBER_PATTERN})"
        rf"\s*(?P<unit>crore|crores|million|billion|mn|bn)?",
        re.IGNORECASE,
    )

    for match in revenue_pattern.finditer(text):

        evidence = match.group(0).strip()

        if not evidence:
            continue

        facts.append(
            {
                "subject": document_id,
                "predicate": match.group(
                    "predicate"
                ).strip(),
                "value": match.group(
                    "value"
                ).replace(",", ""),
                "value_type": "number",
                "unit": match.group("unit"),
                "period": None,
                "scope": None,
                "evidence_text": evidence,
                "confidence": 0.60,
                "extraction_method": "fallback",
            }
        )

    # --------------------------------------------------
    # Percentage statements
    # --------------------------------------------------

    percentage_pattern = re.compile(
        rf"(?P<predicate>"
        rf"(?:growth|margin|rate|inflation|increase|decrease)"
        rf"(?:\s+\w+){{0,6}}"
        rf")"
        rf"\s*(?:was|is|of|:)?\s*"
        rf"(?P<value>{NUMBER_PATTERN})\s*%",
        re.IGNORECASE,
    )

    for match in percentage_pattern.finditer(text):

        evidence = match.group(0).strip()

        facts.append(
            {
                "subject": document_id,
                "predicate": match.group(
                    "predicate"
                ).strip(),
                "value": match.group("value"),
                "value_type": "percentage",
                "unit": "%",
                "period": None,
                "scope": None,
                "evidence_text": evidence,
                "confidence": 0.60,
                "extraction_method": "fallback",
            }
        )

    return facts
