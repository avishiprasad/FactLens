import re
from typing import List, Dict


def extract_numbers_from_text(text: str) -> List[Dict]:
    """
    Basic numerical candidate extractor.

    This is NOT the final fact extractor.
    It simply identifies numerical candidates that
    an LLM can later interpret.
    """

    results = []

    pattern = r"""
        (?:
            ₹\s?
        )?
        \b
        \d{1,3}
        (?:
            ,\d{2,3}
        )*
        (?:
            \.\d+
        )?
        \b
    """

    matches = re.finditer(
        pattern,
        text,
        re.VERBOSE
    )

    for match in matches:

        value = match.group(0).strip()

        start = max(0, match.start() - 150)
        end = min(len(text), match.end() + 150)

        context = text[start:end]

        results.append({
            "value": value,
            "context": context
        })

    return results


if __name__ == "__main__":

    sample = """
    Revenue from services for FY24 was ₹81,415 million.
    The company had 98,135 employees and partners.
    """

    results = extract_numbers_from_text(sample)

    for result in results:
        print("\nVALUE:", result["value"])
        print("CONTEXT:", result["context"])