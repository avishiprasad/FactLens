from app.reconciliation.macro_fixtures import RBI_IMF_FACTS
from app.reconciliation.engine import classify_forecast_relationship


rbi = RBI_IMF_FACTS[0]
imf = RBI_IMF_FACTS[1]


result = classify_forecast_relationship(
    rbi,
    imf
)


print("\n================================")
print("FORECAST RECONCILIATION")
print("================================\n")

print("Source A:")
print(
    rbi["scope"],
    "|",
    rbi["value"],
    rbi["unit"]
)

print("\nSource B:")
print(
    imf["scope"],
    "|",
    imf["value"],
    imf["unit"]
)

print("\nRelationship:")
print(result["relationship"])

print("\nConfidence:")
print(result["confidence"])

print("\nRelative difference:")
print(
    result.get(
        "relative_difference",
        "N/A"
    )
)

print("\nReason:")
print(result["reason"])

print("\n================================")

assert result["relationship"] == "LIKELY_DISAGREEMENT"

print("MACRO TEST PASSED")