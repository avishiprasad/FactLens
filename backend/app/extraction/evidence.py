import re


def normalize_text(text: str) -> str:

    text = text.lower()

    # Remove spaces around commas
    text = re.sub(
        r"\s*,\s*",
        ",",
        text
    )

    # Normalize whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def verify_evidence(
    page_text: str,
    evidence_text: str
) -> bool:

    page = normalize_text(page_text)
    evidence = normalize_text(evidence_text)

    if evidence in page:
        return True

    # Fallback: check important numerical tokens
    numbers = re.findall(
        r"\d[\d,]*(?:\.\d+)?",
        evidence
    )

    if not numbers:
        return False

    return all(
        number in page
        for number in numbers
    )