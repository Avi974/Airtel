"""
Quote & Order Lifecycle Service.
Handles deterministic pricing calculation, tax aggregation, add-on management,
and atomic quote acceptance.
"""

from typing import List, Dict, Any, Optional
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.entities import (
    Quote,
    QuoteLineItem,
    Order,
    OrderEvent,
    Product,
    DiscoverySession,
    KycSubmission,
)
from app.catalogue.engine import calculate_unit_price_paise, is_product_eligible
from app.catalogue.serviceability import check_serviceability
from app.quotes_orders.tax import calculate_tax_breakdown_paise


def recalculate_quote_financials(db: Session, quote: Quote) -> Quote:
    """
    Recalculates subtotals, GST distributions, and grand totals across all quote line items.
    """
    monthly_subtotal = 0
    monthly_cgst = 0
    monthly_sgst = 0
    monthly_igst = 0

    one_time_subtotal = 0
    one_time_cgst = 0
    one_time_sgst = 0
    one_time_igst = 0

    for item in quote.line_items:
        # Line item subtotal
        item_monthly_base = item.unit_monthly_paise * item.quantity
        item_setup_base = item.unit_setup_paise * item.quantity

        # Tax calculations
        m_tax = calculate_tax_breakdown_paise(item_monthly_base, item.site_state_code)
        s_tax = calculate_tax_breakdown_paise(item_setup_base, item.site_state_code)

        # Update line item tax columns
        item.cgst_paise = m_tax["cgst_paise"]
        item.sgst_paise = m_tax["sgst_paise"]
        item.igst_paise = m_tax["igst_paise"]

        # Aggregate monthly
        monthly_subtotal += item_monthly_base
        monthly_cgst += m_tax["cgst_paise"]
        monthly_sgst += m_tax["sgst_paise"]
        monthly_igst += m_tax["igst_paise"]

        # Aggregate one-time
        one_time_subtotal += item_setup_base
        one_time_cgst += s_tax["cgst_paise"]
        one_time_sgst += s_tax["sgst_paise"]
        one_time_igst += s_tax["igst_paise"]

    quote.monthly_subtotal_paise = monthly_subtotal
    quote.monthly_cgst_paise = monthly_cgst
    quote.monthly_sgst_paise = monthly_sgst
    quote.monthly_igst_paise = monthly_igst
    quote.monthly_total_paise = monthly_subtotal + monthly_cgst + monthly_sgst + monthly_igst

    quote.one_time_subtotal_paise = one_time_subtotal
    one_time_total_tax = one_time_cgst + one_time_sgst + one_time_igst
    quote.one_time_cgst_paise = one_time_cgst
    quote.one_time_sgst_paise = one_time_sgst
    quote.one_time_igst_paise = one_time_igst
    quote.one_time_total_paise = one_time_subtotal + one_time_total_tax

    db.add(quote)
    db.commit()
    db.refresh(quote)
    return quote


def create_quote(
    db: Session,
    session_id: str,
    product_ids: List[str],
    pincode: str,
    site_identifier: str = "Site-1",
    contract_months: int = 12,
) -> Quote:
    """
    Creates a new draft Quote with resolved serviceability, deterministic pricing, and POS tax.
    """
    session_obj = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
    if not session_obj:
        raise HTTPException(status_code=404, detail="Discovery session not found.")

    srv = check_serviceability(db, pincode)
    city_tier = srv["city_tier"]
    state_code = srv["state_code"]

    # Filter out empty or duplicate product ids
    unique_product_ids = list(dict.fromkeys(p for p in product_ids if p.strip()))
    if not unique_product_ids:
        # Default to baseline P01 or P04 depending on feasibility
        if not srv["fibre_feasible"]:
            unique_product_ids = ["P04"]  # Biz 5G AirFiber 100
        else:
            unique_product_ids = ["P01"]  # Biz Fibre 100

    quote = Quote(
        session_id=session_id,
        status="READY",
        pricing_formula_ver="v1.0-deterministic",
    )
    db.add(quote)
    db.flush()

    for pid in unique_product_ids:
        product = db.query(Product).filter(Product.product_id == pid).first()
        if not product:
            continue

        unit_price = calculate_unit_price_paise(
            price_min_paise=product.price_min_paise,
            price_max_paise=product.price_max_paise,
            city_tier=city_tier,
            contract_months=contract_months,
        )

        status_flag = "SERVICEABLE"
        if product.category == "Connectivity" and not srv["fibre_feasible"] and "fibre" in product.name.lower():
            status_flag = "SURVEY_REQUIRED"

        line_item = QuoteLineItem(
            quote_id=quote.quote_id,
            product_id=product.product_id,
            site_identifier=site_identifier,
            site_pincode=pincode,
            site_state_code=state_code,
            serviceability_status=status_flag,
            quantity=1,
            contract_months=contract_months,
            unit_monthly_paise=unit_price,
            unit_setup_paise=product.setup_fee_paise,
        )
        db.add(line_item)

    db.flush()
    return recalculate_quote_financials(db, quote)


def patch_quote_items(
    db: Session,
    quote_id: str,
    add_product_ids: List[str],
    remove_product_ids: List[str],
    contract_months: Optional[int] = None,
) -> Quote:
    """Toggles add-ons or changes contract duration on an existing draft quote."""
    quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")
    if quote.status == "ACCEPTED":
        raise HTTPException(status_code=400, detail="Cannot modify an already accepted and frozen quote.")

    # Remove items
    if remove_product_ids:
        for item in list(quote.line_items):
            if item.product_id in remove_product_ids:
                db.delete(item)
        db.flush()

    # Add items
    if add_product_ids:
        # Determine existing site params
        first_item = quote.line_items[0] if quote.line_items else None
        pincode = first_item.site_pincode if first_item else "400001"
        srv = check_serviceability(db, pincode)
        city_tier = srv["city_tier"]
        state_code = srv["state_code"]
        term = contract_months or (first_item.contract_months if first_item else 12)

        existing_pids = {item.product_id for item in quote.line_items}
        for pid in add_product_ids:
            if pid in existing_pids:
                continue
            product = db.query(Product).filter(Product.product_id == pid).first()
            if not product:
                continue

            unit_price = calculate_unit_price_paise(
                price_min_paise=product.price_min_paise,
                price_max_paise=product.price_max_paise,
                city_tier=city_tier,
                contract_months=term,
            )

            line_item = QuoteLineItem(
                quote_id=quote.quote_id,
                product_id=product.product_id,
                site_identifier=first_item.site_identifier if first_item else "Site-1",
                site_pincode=pincode,
                site_state_code=state_code,
                serviceability_status="SERVICEABLE",
                quantity=1,
                contract_months=term,
                unit_monthly_paise=unit_price,
                unit_setup_paise=product.setup_fee_paise,
            )
            db.add(line_item)
        db.flush()

    # If contract months updated, recalculate unit price for all items
    if contract_months is not None:
        first_item = quote.line_items[0] if quote.line_items else None
        pincode = first_item.site_pincode if first_item else "400001"
        srv = check_serviceability(db, pincode)
        for item in quote.line_items:
            item.contract_months = contract_months
            p = db.query(Product).filter(Product.product_id == item.product_id).first()
            if p:
                item.unit_monthly_paise = calculate_unit_price_paise(
                    price_min_paise=p.price_min_paise,
                    price_max_paise=p.price_max_paise,
                    city_tier=srv["city_tier"],
                    contract_months=contract_months,
                )
        db.flush()

    return recalculate_quote_financials(db, quote)


def accept_quote(db: Session, quote_id: str) -> Order:
    """
    Idempotently accepts a quote, freezes financials, and creates the order and initial tracking event.
    Enforces the invariant: Rejects acceptance if any item is UNAVAILABLE.
    """
    quote = db.query(Quote).filter(Quote.quote_id == quote_id).first()
    if not quote:
        raise HTTPException(status_code=404, detail="Quote not found.")

    # Idempotent return if already accepted
    existing_order = db.query(Order).filter(Order.quote_id == quote_id).first()
    if existing_order:
        return existing_order

    # Check unserviceable items
    for item in quote.line_items:
        if item.serviceability_status == "UNAVAILABLE":
            raise HTTPException(
                status_code=400,
                detail=f"Cannot accept quote: Product {item.product_id} is UNAVAILABLE at {item.site_pincode}.",
            )

    # Freeze financial snapshot
    snapshot = {
        "quote_id": quote.quote_id,
        "monthly_subtotal_paise": quote.monthly_subtotal_paise,
        "monthly_cgst_paise": quote.monthly_cgst_paise,
        "monthly_sgst_paise": quote.monthly_sgst_paise,
        "monthly_igst_paise": quote.monthly_igst_paise,
        "monthly_total_paise": quote.monthly_total_paise,
        "one_time_subtotal_paise": quote.one_time_subtotal_paise,
        "one_time_total_paise": quote.one_time_total_paise,
        "pricing_formula_ver": quote.pricing_formula_ver,
        "line_items": [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_monthly_paise": item.unit_monthly_paise,
                "unit_setup_paise": item.unit_setup_paise,
                "site_pincode": item.site_pincode,
                "site_state_code": item.site_state_code,
            }
            for item in quote.line_items
        ],
    }

    quote.status = "ACCEPTED"
    order = Order(
        quote_id=quote.quote_id,
        session_id=quote.session_id,
        status="AWAITING_KYC_CONSENT",
        frozen_financial_snapshot=snapshot,
    )
    db.add(order)
    db.flush()

    # Initial order timeline event
    evt = OrderEvent(
        order_id=order.order_id,
        actor_type="customer",
        from_status=None,
        to_status="AWAITING_KYC_CONSENT",
        customer_title="Commercial Quote Accepted",
        customer_detail="Order created. Proceeding to digital KYC consent and document upload.",
    )
    db.add(evt)

    # Create empty KYC submission container
    kyc_sub = KycSubmission(
        order_id=order.order_id,
        processing_state="AWAITING_DOCS",
        decision="PENDING",
    )
    db.add(kyc_sub)

    db.commit()
    db.refresh(order)
    return order
