import json
import os
import time
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from google import genai


# ---------------------------------------------------------
# Environment setup
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

load_dotenv(BASE_DIR / ".env")


api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY is not set. "
        "Add it to backend/.env"
    )


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

client = genai.Client(
    api_key=api_key
)


PRIMARY_MODEL = "gemini-3.6-flash"


# ---------------------------------------------------------
# System prompt
# ---------------------------------------------------------

SYSTEM_PROMPT = """
You are a financial document intelligence system.

Your job is to extract meaningful numerical and semantic facts
from financial documents.

For every fact:

1. Identify the entity or subject.
2. Identify what the number or statement means.
3. Extract the value.
4. Identify the unit.
5. Identify the relevant period.
6. Identify the scope.
7. Preserve the exact source evidence.
8. Never infer a value that is not supported by the supplied text.

IMPORTANT RULES:

- Do not hallucinate facts.
- Do not invent values.
- Do not convert units.
- Do not combine values from different rows or columns.
- Do not guess table column relationships.
- If a table is ambiguous, do not create a fact.
- Evidence must come directly from the supplied text.
- Prefer meaningful business facts over incidental numbers.
- Every extracted fact must have evidence_text.
- If evidence cannot be identified, do not extract the fact.
"""


# ---------------------------------------------------------
# Gemini API call with retry handling
# ---------------------------------------------------------

def generate_with_retry(
    contents,
    max_retries=3
):
    """
    Call Gemini and retry temporary failures.

    Retryable errors:
    - 503 UNAVAILABLE
    - 429 RESOURCE_EXHAUSTED
    """

    for attempt in range(max_retries):

        try:

            response = client.models.generate_content(
                model=PRIMARY_MODEL,
                contents=contents,
                config={
                    "response_mime_type": "application/json"
                }
            )

            return response

        except Exception as error:

            error_text = str(error)

            is_retryable = (
                "503" in error_text
                or "429" in error_text
                or "UNAVAILABLE" in error_text
                or "RESOURCE_EXHAUSTED" in error_text
            )

            # Don't retry errors such as invalid requests,
            # authentication errors, malformed requests, etc.
            if not is_retryable:
                raise

            # We have exhausted our retries.
            if attempt == max_retries - 1:

                print(
                    "Gemini request failed after "
                    f"{max_retries} attempts."
                )

                raise

            wait_seconds = 2 ** attempt

            print(
                "Gemini temporarily unavailable. "
                f"Retrying in {wait_seconds} seconds..."
            )

            time.sleep(wait_seconds)


# ---------------------------------------------------------
# Fact extraction
# ---------------------------------------------------------

def extract_facts(
    text: str,
    document_id: str,
    page_number: int
) -> List[dict]:

    user_prompt = f"""
Extract meaningful facts from the following financial document page.

DOCUMENT ID:
{document_id}

PAGE:
{page_number}

TEXT:
{text}

Return a JSON object with exactly this structure:

{{
  "facts": [
    {{
      "subject": "string",
      "predicate": "string",
      "value": "number or string",
      "value_type": "number|string|percentage|date",
      "unit": "string or null",
      "period": "string or null",
      "scope": "string or null",
      "evidence_text": "exact text copied from the page",
      "confidence": 0.0
    }}
  ]
}}

Rules:

- Return an empty facts array if there are no reliable facts.
- Do not invent information.
- evidence_text must come from the supplied page.
- Do not paraphrase evidence_text.
- Do not perform unit conversion.
- Do not merge information from separate unrelated rows.
- If a table is ambiguous, return no fact rather than guessing.
"""


    response = generate_with_retry(
        contents=[
            SYSTEM_PROMPT,
            user_prompt
        ]
    )


    content = response.text


    try:

        result = json.loads(content)

    except json.JSONDecodeError as error:

        raise RuntimeError(
            "Gemini returned invalid JSON.\n"
            f"Response:\n{content}"
        ) from error


    if not isinstance(result, dict):

        raise RuntimeError(
            "Gemini response was not a JSON object."
        )


    facts = result.get(
        "facts",
        []
    )


    if not isinstance(facts, list):

        raise RuntimeError(
            "Gemini response contains an invalid "
            "'facts' field."
        )


    return facts