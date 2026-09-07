from decimal import Decimal


def relative_difference(
    value_a: Decimal,
    value_b: Decimal
) -> Decimal:

    if value_a == 0 and value_b == 0:
        return Decimal("0")

    denominator = max(
        abs(value_a),
        abs(value_b)
    )

    return abs(
        value_a - value_b
    ) / denominator


def values_are_close(
    value_a: Decimal,
    value_b: Decimal,
    tolerance: float = 0.01
) -> bool:

    difference = relative_difference(
        value_a,
        value_b
    )

    return difference <= Decimal(
        str(tolerance)
    )