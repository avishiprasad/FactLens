from app.reconciliation.normalizer import normalize_value


tests = [
    (81415, "₹ million"),
    (8142, "₹ crore"),
    (8.142, "₹ billion")
]


for value, unit in tests:

    result = normalize_value(
        value,
        unit
    )

    print(
        f"{value} {unit}"
        f" -> "
        f"{result} INR"
    )