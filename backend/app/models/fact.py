from pydantic import BaseModel, Field
from typing import Optional, Any

class Evidence(BaseModel):
    document_id: str
    page_number: int
    text: str


class Fact(BaseModel):
    id: str

    subject: str
    predicate: str

    value: Any
    value_type: str

    unit: Optional[str] = None
    period: Optional[str] = None
    scope: Optional[str] = None

    evidence: Evidence

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    extraction_method: str = "llm"