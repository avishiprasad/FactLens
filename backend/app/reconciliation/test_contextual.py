from app.reconciliation.context_fixtures import WORKFORCE_FACTS
from app.reconciliation.engine import classify_contextual_reconciliation


team_size = WORKFORCE_FACTS[0]
partner_agents = WORKFORCE_FACTS[1]
workforce = WORKFORCE_FACTS[2]


result = classify_contextual_reconciliation(
    component_facts=[
        team_size,
        partner_agents,
    ],
    total_fact=workforce,
)


print("\n================================")
print("CONTEXTUAL RECONCILIATION")
print("================================\n")

print("Team size:")
print(
    team_size["value"],
    team_size["unit"]
)

print("\nPartner agents:")
print(
    partner_agents["value"],
    partner_agents["unit"]
)

print("\nReported workforce:")
print(
    workforce["value"],
    workforce["unit"]
)

print("\nCalculation:")
print(
    f'{team_size["value"]} + '
    f'{partner_agents["value"]} = '
    f'{int(team_size["value"]) + int(partner_agents["value"])}'
)

print("\nRelationship:")
print(result["relationship"])

print("\nConfidence:")
print(result["confidence"])

print("\nReason:")
print(result["reason"])

print("\n================================")

assert result["relationship"] == "RECONCILED"

print("CONTEXTUAL TEST PASSED")