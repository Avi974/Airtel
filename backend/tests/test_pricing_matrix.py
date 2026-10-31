"""
Unit tests for deterministic pricing matrix and eligibility filtering.
"""

import pytest
from app.catalogue.engine import calculate_unit_price_paise, is_product_eligible
from app.models.entities import Product


def test_pricing_matrix_spread_and_discounts():
    # P01: Min = 999 INR (99,900 paise), Max = 1199 INR (119,900 paise), Spread = 20,000 paise
    p_min = 99900
    p_max = 119900
    spread = 20000

    # 1. Tier 2, 12 months (Baseline): Both deltas 0.0 -> P_min
    price_t2_12m = calculate_unit_price_paise(p_min, p_max, city_tier=2, contract_months=12)
    assert price_t2_12m == p_min

    # 2. Tier 1, 12 months: Delta_Tier = 1.0 (50% spread) -> 99900 + 10000 = 109900
    price_t1_12m = calculate_unit_price_paise(p_min, p_max, city_tier=1, contract_months=12)
    assert price_t1_12m == p_min + 10000

    # 3. Tier 1, 6 months (Short Term): Delta_Tier = 1.0, Delta_Term = 1.0 -> P_max
    price_t1_6m = calculate_unit_price_paise(p_min, p_max, city_tier=1, contract_months=6)
    assert price_t1_6m == p_max

    # 4. Tier 1, 24 months (Tenure Loyalty Discount): Locks to P_min despite Tier 1
    price_t1_24m = calculate_unit_price_paise(p_min, p_max, city_tier=1, contract_months=24)
    assert price_t1_24m == p_min


def test_product_eligibility_constraints():
    # P03: Tier 1 only, requires GSTIN, min 5 employees
    p03 = Product(
        product_id="P03",
        name="Biz Fibre 1G",
        category="Connectivity",
        target_segments=["prof", "multi"],
        available_city_tiers=[1],
        requires_gstin=True,
        min_quantity=5,
        price_min_paise=399900,
        price_max_paise=449900,
    )

    # Eligible case: Tier 1, Has GSTIN, 8 employees
    ok, reason = is_product_eligible(p03, city_tier=1, has_gstin=True, employee_count=8)
    assert ok is True
    assert reason is None

    # Ineligible: Tier 2 location
    ok, reason = is_product_eligible(p03, city_tier=2, has_gstin=True, employee_count=8)
    assert ok is False
    assert "Not available in City Tier 2" in reason

    # Ineligible: Missing GSTIN
    ok, reason = is_product_eligible(p03, city_tier=1, has_gstin=False, employee_count=8)
    assert ok is False
    assert "Requires verified GSTIN" in reason

    # Ineligible: Under employee threshold (e.g. 3 employees)
    ok, reason = is_product_eligible(p03, city_tier=1, has_gstin=True, employee_count=3)
    assert ok is False
    assert "Minimum employee scale required: 5" in reason


def test_addon_dependency_resolution():
    # P09: Managed Wi-Fi requires one of [P01, P02, P03, P05, P06]
    p09 = Product(
        product_id="P09",
        name="Managed Wi-Fi Pro",
        category="Value Added",
        target_segments=["prof"],
        available_city_tiers=[1, 2],
        requires_gstin=False,
        min_quantity=1,
        price_min_paise=49900,
        price_max_paise=49900,
        requires_one_of=["P01", "P02", "P03", "P05", "P06"],
    )

    # Ineligible without parent
    ok, reason = is_product_eligible(p09, city_tier=1, has_gstin=True, selected_product_ids={"P14"})
    assert ok is False
    assert "Requires at least one parent connectivity product" in reason

    # Eligible with P01 selected
    ok, reason = is_product_eligible(p09, city_tier=1, has_gstin=True, selected_product_ids={"P01"})
    assert ok is True
