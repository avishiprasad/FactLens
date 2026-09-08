from app.reconciliation.failure_fixtures import AMBIGUOUS_FACT
from app.reconciliation.engine import classify_relationship


reference_fact = {
    "subject": "Delhivery",
    "predicate": "Revenue from services",
    "value": "8142",
    "value_type": "number",
    "unit": "₹ crore",
    "period": "FY24",
    "scope": None,
    "evidence_verified": True,
    "document_id": "03-delhivery-q4-fy24-earnings-presentation",
    "page_number": 9,
}


result = classify_relationship(
    AMBIGUOUS_FACT,
    reference_fact
)


print("\n================================")
print("EXTRACTION FAILURE HANDLING")
print("================================\n")

print("Extracted fact:")
print(
    AMBIGUOUS_FACT["predicate"],
    "|",
    AMBIGUOUS_FACT["value"],
    AMBIGUOUS_FACT["unit"]
)

print("\nEvidence verified:")
print(
    AMBIGUOUS_FACT["evidence_verified"]
)

print("\nFailure reason:")
print(
    AMBIGUOUS_FACT["failure_reason"]
)

print("\nRelationship:")
print(
    result["relationship"]
)

print("\nConfidence:")
print(
    result["confidence"]
)

print("\nEngine reason:")
print(
    result["reason"]
)

print("\n================================")

assert result["relationship"] == "UNRESOLVED"
assert result["confidence"] < 0.5

print("EXTRACTION FAILURE TEST PASSED")