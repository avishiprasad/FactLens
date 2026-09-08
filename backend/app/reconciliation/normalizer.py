from decimal import Decimal
from typing import Optional


UNIT_MULTIPLIERS = {
    # Currency
    "inr": Decimal("1"),
    "₹": Decimal("1"),

    "inr thousand": Decimal("1000"),
    "₹ thousand": Decimal("1000"),
    "thousand": Decimal("1000"),
    "k": Decimal("1000"),

    "inr million": Decimal("1000000"),
    "₹ million": Decimal("1000000"),
    "million": Decimal("1000000"),
    "mn": Decimal("1000000"),

    "inr billion": Decimal("1000000000"),
    "₹ billion": Decimal("1000000000"),
    "billion": Decimal("1000000000"),
    "bn": Decimal("1000000000"),

    "inr crore": Decimal("10000000"),
    "₹ crore": Decimal("10000000"),
    "inr cr": Decimal("10000000"),
    "₹ cr": Decimal("10000000"),
    "cr": Decimal("10000000"),
    "crore": Decimal("10000000"),

    "inr lakh": Decimal("100000"),
    "₹ lakh": Decimal("100000"),
    "inr lac": Decimal("100000"),
    "₹ lac": Decimal("100000"),
    "lakh": Decimal("100000"),
    "lac": Decimal("100000"),

    # People / counts
    "people": Decimal("1"),
    "person": Decimal("1"),
    "employees": Decimal("1"),
    "agents": Decimal("1"),

    # Percentages
    "percent": Decimal("1"),
    "%": Decimal("1"),
    "percentage": Decimal("1"),
    "per cent": Decimal("1"),
    "per-cent": Decimal("1"),
}


def normalize_unit(unit: Optional[str]) -> Optional[str]:
    """
    Normalize equivalent unit representations.

    Examples:
        "%"          -> "percent"
        "percentage" -> "percent"
        "per cent"   -> "percent"
        "per-cent"   -> "percent"
    """

    if not unit:
        return None

    unit = str(unit).lower().strip()

    # Normalize whitespace and hyphens
    unit = unit.replace("-", " ")
    unit = " ".join(unit.split())

    # Normalize percentage terminology
    if unit in {
        "%",
        "percent",
        "percentage",
        "per cent",
    }:
        return "percent"

    return unit


def normalize_value(
    value,
    unit: Optional[str]
) -> Decimal:
    """
    Convert a value into a normalized numeric representation.

    Monetary values are converted to absolute INR.

    Example:

        81415 + INR million
        ->
        81415000000 INR
    """

    if unit is None:
        return Decimal(str(value))

    normalized_unit = normalize_unit(unit)

    multiplier = UNIT_MULTIPLIERS.get(
        normalized_unit
    )

    if multiplier is None:
        raise ValueError(
            "Unsupported unit: {}".format(unit)
        )

    numeric_value = Decimal(
        str(value).replace(",", "")
    )

    return numeric_value * multiplier