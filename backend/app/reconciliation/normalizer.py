from decimal import Decimal
from typing import Optional


UNIT_MULTIPLIERS = {
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
    "lac": Decimal("100000")
}


def normalize_unit(unit: Optional[str]) -> Optional[str]:

    if not unit:
        return None

    unit = unit.lower().strip()

    return unit


def normalize_value(
    value,
    unit: Optional[str]
) -> Decimal:
    """
    Convert monetary values into absolute INR.

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