"""Test deterministic calculations, severity matrices, and policy validations."""

from Agents.expense_reimbursement.amount_agent import calculate_deterministic_arithmetic
from Agents.expense_reimbursement.duplicate_agent import query_candidate_duplicates
from Agents.expense_reimbursement.policy_agent import query_policies_for_category
from Agents.incident_triage.severity_agent import calculate_deterministic_severity


def test_severity_matrix():
    # Tier-1 and users >= 5000 -> SEV-1
    res1 = calculate_deterministic_severity(impact_users=6000, service_tier="Tier-1", outage_minutes=30)
    assert res1["recommended_severity"] == "SEV-1"

    # Tier-1 and users >= 500 -> SEV-2
    res2 = calculate_deterministic_severity(impact_users=800, service_tier="Tier-1", outage_minutes=15)
    assert res2["recommended_severity"] == "SEV-2"

    # Outage >= 120 minutes -> SEV-1 regardless of initial count
    res3 = calculate_deterministic_severity(impact_users=50, service_tier="Tier-3", outage_minutes=150)
    assert res3["recommended_severity"] == "SEV-1"

    # Minor users and short duration -> SEV-4
    res4 = calculate_deterministic_severity(impact_users=25, service_tier="Tier-3", outage_minutes=5)
    assert res4["recommended_severity"] == "SEV-4"


def test_expense_arithmetic():
    # Valid sum
    v1 = calculate_deterministic_arithmetic(subtotal=100.00, tax=8.88, total=108.88)
    assert v1["is_arithmetically_valid"] is True
    assert v1["discrepancy"] == 0.0

    # Arithmetic mismatch
    v2 = calculate_deterministic_arithmetic(subtotal=100.00, tax=8.88, total=125.00)
    assert v2["is_arithmetically_valid"] is False
    assert v2["discrepancy"] == 16.12

    # Negative value
    v3 = calculate_deterministic_arithmetic(subtotal=-50.00, tax=5.00, total=-45.00)
    assert v3["has_negative_values"] is True


def test_policy_query():
    meals_policies = query_policies_for_category("Meals & Entertainment")
    assert len(meals_policies) > 0
    assert any("POL-EXP" in p["policy_id"] for p in meals_policies)


def test_duplicate_query():
    # Query non-existent
    dups = query_candidate_duplicates("EMP-NONEXISTENT", "Nowhere Cafe", 99999.99)
    assert isinstance(dups, list)
