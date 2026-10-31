"""
Curated MSME Bundles & Upfront Serviceability Fallback Generator.
Builds tailored, high-converting product packages aligned with SMB needs.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.entities import Product
from app.models.schemas import BundleRecommendation, BundleItem
from app.catalogue.serviceability import check_serviceability
from app.catalogue.engine import calculate_unit_price_paise


def get_bundle_recommendation(
    db: Session,
    slots: Dict[str, Any],
) -> BundleRecommendation:
    """
    Synthesizes a tailored bundle based on extracted slots.
    Performs upfront feasibility checking and automatic AirFiber P04 fallback if fibre is unavailable.
    """
    pincode = str(slots.get("pincode", "400001")).strip()
    srv = check_serviceability(db, pincode)
    city_tier = srv["city_tier"]
    fibre_available = srv["fibre_feasible"]

    segment = slots.get("segment", "micro")
    employee_count = int(slots.get("employee_count", 3))
    has_gstin = bool(slots.get("has_gstin", True))

    # Determine Primary Connectivity Product
    if not fibre_available:
        primary_id = "P04"  # Biz 5G AirFiber 100 (Rapid 2-day wireless deployment)
        feasibility_note = "Site has limited physical fibre ducting. Pre-configured Biz 5G AirFiber 100 for instant 48h activation."
    elif segment in ["mfg", "multi"] or employee_count >= 15:
        primary_id = "P03" if (city_tier == 1 and has_gstin) else "P02"
        feasibility_note = f"Gigabit Fibre backhaul verified for {srv['city']}. Priority B2B SLA mapped."
    elif segment == "prof" or employee_count >= 5:
        primary_id = "P02"  # Biz Fibre 300
        feasibility_note = f"Fibre broadband serviceable with dedicated static IP support in {srv['city']}."
    else:
        primary_id = "P01"  # Biz Fibre 100
        feasibility_note = f"High-speed business fibre serviceable at pincode {pincode}."

    # Load Primary Product
    p_primary = db.query(Product).filter(Product.product_id == primary_id).first()
    p_price_paise = calculate_unit_price_paise(
        price_min_paise=p_primary.price_min_paise,
        price_max_paise=p_primary.price_max_paise,
        city_tier=city_tier,
        contract_months=12,
    )

    primary_item = BundleItem(
        product_id=p_primary.product_id,
        name=p_primary.name,
        category=p_primary.category,
        unit_monthly_inr=p_price_paise / 100.0,
        unit_setup_inr=p_primary.setup_fee_paise / 100.0,
        quantity=1,
        sla_install_days=p_primary.sla_install_days,
    )

    # Determine Add-on items based on segment
    included_addons_pids = []
    optional_addons_pids = []

    if segment == "prof":
        included_addons_pids = ["P09", "P07"]  # Managed Wi-Fi + Biz Voice
        optional_addons_pids = ["P11", "P10"]  # Static IP + Cloud Firewall
    elif segment in ["mfg", "multi"]:
        included_addons_pids = ["P09", "P11"]  # Managed Wi-Fi + Static IP
        optional_addons_pids = ["P10", "P14"]  # Cloud Firewall + Attendance
    else:  # micro / retail
        included_addons_pids = ["P07"]         # Biz Voice Unlimited
        optional_addons_pids = ["P09", "P14"]  # Managed Wi-Fi + Attendance

    included_items = []
    total_monthly_paise = p_price_paise
    total_setup_paise = p_primary.setup_fee_paise

    for aid in included_addons_pids:
        p_addon = db.query(Product).filter(Product.product_id == aid).first()
        if p_addon:
            a_price = calculate_unit_price_paise(
                p_addon.price_min_paise, p_addon.price_max_paise, city_tier, 12
            )
            included_items.append(
                BundleItem(
                    product_id=p_addon.product_id,
                    name=p_addon.name,
                    category=p_addon.category,
                    unit_monthly_inr=a_price / 100.0,
                    unit_setup_inr=p_addon.setup_fee_paise / 100.0,
                    quantity=1,
                    sla_install_days=p_addon.sla_install_days,
                )
            )
            total_monthly_paise += a_price
            total_setup_paise += p_addon.setup_fee_paise

    optional_items = []
    for aid in optional_addons_pids:
        p_addon = db.query(Product).filter(Product.product_id == aid).first()
        if p_addon:
            a_price = calculate_unit_price_paise(
                p_addon.price_min_paise, p_addon.price_max_paise, city_tier, 12
            )
            optional_items.append(
                BundleItem(
                    product_id=p_addon.product_id,
                    name=p_addon.name,
                    category=p_addon.category,
                    unit_monthly_inr=a_price / 100.0,
                    unit_setup_inr=p_addon.setup_fee_paise / 100.0,
                    quantity=1,
                    sla_install_days=p_addon.sla_install_days,
                )
            )

    bundle_id = "starter_digital" if segment == "micro" else ("enterprise_throughput" if segment in ["mfg", "multi"] else "growth_pro")
    title = {
        "starter_digital": "Smart Retailer Connect Pack",
        "growth_pro": "Professional Digital Growth Suite",
        "enterprise_throughput": "Enterprise High-Performance Bundle",
    }.get(bundle_id, "Digital Growth Suite")

    tagline = {
        "starter_digital": "Zero downtime Wi-Fi & unlimited calling for your shop or retail counter.",
        "growth_pro": "High-speed broadband, secure employee Wi-Fi, and multi-line voice in one sitting.",
        "enterprise_throughput": "Uncapped throughput with static IP and fortified enterprise firewall.",
    }.get(bundle_id, "Fast, reliable B2B digital connectivity.")

    return BundleRecommendation(
        bundle_id=bundle_id,
        title=title,
        tagline=tagline,
        suitability_score=95 if has_gstin else 88,
        target_segment=segment,
        primary_product=primary_item,
        included_addons=included_items,
        optional_addons=optional_items,
        estimated_monthly_inr=total_monthly_paise / 100.0,
        estimated_setup_inr=total_setup_paise / 100.0,
        feasibility_notes=feasibility_note,
    )
