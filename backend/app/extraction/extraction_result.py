from typing import List, Dict


def build_extraction_result(
    facts: List[Dict],
    method: str,
    status: str,
    error: str = None,
) -> Dict:
    """
    Standardize extraction results.
    """

    return {
        "facts": facts,
        "method": method,
        "status": status,
        "error": error,
    }
