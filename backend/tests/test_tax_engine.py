"""
Unit tests for B2B GST Place of Supply (POS) and atomic quote-to-order lifecycle.
"""

import pytest
from app.core.database import SessionLocal
from app.quotes_orders.tax import calculate_tax_breakdown_paise
from app.quotes_orders.service import create_quote, accept_quote, patch_quote_items
from app.models.entities import DiscoverySession, Order


def test_tax_breakdown_intra_vs_inter():
    amount = 100000  # 1,000.00 INR in paise

    # 1. Intra-State (Maharashtra 27 -> Maharashtra 27)
    mh_tax = calculate_tax_breakdown_paise(amount, site_state_code="27", operator_state_code="27")
    assert mh_tax["cgst_paise"] == 9000
    assert mh_tax["sgst_paise"] == 9000
    assert mh_tax["igst_paise"] == 0
    assert mh_tax["total_paise"] == 118000

    # 2. Inter-State (Maharashtra 27 -> Karnataka 29)
    ka_tax = calculate_tax_breakdown_paise(amount, site_state_code="29", operator_state_code="27")
    assert ka_tax["cgst_paise"] == 0
    assert ka_tax["sgst_paise"] == 0
    assert ka_tax["igst_paise"] == 18000
    assert ka_tax["total_paise"] == 118000


def test_quote_creation_and_acceptance():
    db = SessionLocal()
    try:
        # Create dummy session
        sess = DiscoverySession(business_name="Apex Dental Clinic")
        db.add(sess)
        db.commit()

        # Create Quote for Mumbai (400001, Tier 1, MH 27)
        quote = create_quote(
            db=db,
            session_id=sess.session_id,
            product_ids=["P01"],
            pincode="400001",
            contract_months=12,
        )

        assert quote.status == "READY"
        assert len(quote.line_items) == 1
        item = quote.line_items[0]
        assert item.product_id == "P01"
        assert item.site_state_code == "27"
        assert item.cgst_paise > 0
        assert item.sgst_paise > 0
        assert item.igst_paise == 0

        # Patch Quote: Add P09 (Managed Wi-Fi)
        patched = patch_quote_items(db, quote.quote_id, add_product_ids=["P09"], remove_product_ids=[])
        assert len(patched.line_items) == 2

        # Accept Quote
        order = accept_quote(db, quote.quote_id)
        assert order.status == "AWAITING_KYC_CONSENT"
        assert order.quote_id == quote.quote_id
        assert "monthly_total_paise" in order.frozen_financial_snapshot

        # Verify idempotency
        order_again = accept_quote(db, quote.quote_id)
        assert order_again.order_id == order.order_id
    finally:
        db.close()
