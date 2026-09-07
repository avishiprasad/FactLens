from app.reconciliation.normalizer import normalize_value
from app.reconciliation.comparator import (
    relative_difference,
    values_are_close
)


annual_report = normalize_value(
    81415,
    "₹ million"
)

earnings_presentation = normalize_value(
    8142,
    "₹ crore"
)


difference = relative_difference(
    annual_report,
    earnings_presentation
)


print(
    "Annual Report:",
    annual_report
)

print(
    "Earnings Presentation:",
    earnings_presentation
)

print(
    "Relative difference:",
    difference
)

print(
    "Are values close?",
    values_are_close(
        annual_report,
        earnings_presentation
    )
)