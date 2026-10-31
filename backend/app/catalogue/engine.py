"""
Deterministic Catalogue & Pricing Matrix Engine.
Implements the exact mathematical pricing formula and eligibility filtering from V5.2 Architecture.
Zero LLM hallucination: 100% deterministic, audit-traceable arithmetic.
"""

from typing import List, Dict, Any, Optional, Set
from app.models.entities import Product


def calculate_unit_price_paise(
    price_min_paise: int,
    price_max_paise: int,
    city_tier: int,
    contract_months: int,
) -> int:
    """
    Computes deterministic monthly unit price in integer Paise.
    
    Formula:
      Delta_Tier = 1.0 if Tier == 1 else 0.0
      Delta_Term = 1.0 if Contract < 12 else 0.0
      Base Spread = P_max - P_min
      Calculated Price = P_min + (Delta_Tier * 0.5 * Spread) + (Delta_Term * 0.5 * Spread)
      Tenure clamp: If Contract >= 24, clamped to P_min.
      Upper bound: clamped to P_max.
    """
    if price_max_paise <= price_min_paise:
        return price_min_paise

    # Tenure loyalty discount: contracts of 24 months or more lock in bottom-of-band pricing
    if contract_months >= 24:
        return price_min_paise

    spread = price_max_paise - price_min_paise
    delta_tier = 1.0 if city_tier == 1 else 0.0
    delta_term = 1.0 if contract_months < 12 else 0.0

    tier_adjustment = int(round(delta_tier * 0.5 * spread))
    term_adjustment = int(round(delta_term * 0.5 * spread))

    calculated_price = price_min_paise + tier_adjustment + term_adjustment
    return min(price_max_paise, calculated_price)


def is_product_eligible(
    product: Product,
    city_tier: int = 1,
    has_gstin: bool = True,
    employee_count: int = 1,
    num_sites: int = 1,
    selected_product_ids: Optional[Set[str]] = None,
) -> tuple[bool, Optional[str]]:
    """
    Evaluates hard eligibility constraints for a catalogue product against business attributes.
    Returns (eligible: bool, reason_if_ineligible: Optional[str]).
    """
    selected_ids = selected_product_ids or set()

    # 1. City Tier availability
    if product.available_city_tiers and city_tier not in product.available_city_tiers:
        return False, f"Not available in City Tier {city_tier} (Available in: {product.available_city_tiers})"

    # 2. GSTIN Requirement
    if product.requires_gstin and not has_gstin:
        return False, "Requires verified GSTIN registration"

    # 3. Minimum employee scale check
    if product.min_quantity and employee_count < product.min_quantity:
        return False, f"Minimum employee scale required: {product.min_quantity} (Current: {employee_count})"

    # 4. Dependency check: requires_one_of
    if product.requires_one_of and len(product.requires_one_of) > 0:
        has_required_parent = any(parent_id in selected_ids for parent_id in product.requires_one_of)
        if not has_required_parent:
            req_str = " | ".join(product.requires_one_of)
            return False, f"Requires at least one parent connectivity product: {req_str}"

    # 5. Incompatibility check
    if product.incompatible_with:
        conflicts = [p_id for p_id in product.incompatible_with if p_id in selected_ids]
        if conflicts:
            return False, f"Incompatible with selected product: {', '.join(conflicts)}"

    return True, None


def filter_eligible_products(
    products: List[Product],
    city_tier: int = 1,
    has_gstin: bool = True,
    employee_count: int = 1,
    num_sites: int = 1,
    selected_product_ids: Optional[Set[str]] = None,
) -> List[Product]:
    """Filters a collection of products down to strictly eligible items."""
    eligible = []
    for p in products:
        ok, _ = is_product_eligible(
            p,
            city_tier=city_tier,
            has_gstin=has_gstin,
            employee_count=employee_count,
            num_sites=num_sites,
            selected_product_ids=selected_product_ids,
        )
        if ok:
            eligible.append(p)
    return eligible
