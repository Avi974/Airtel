"""
Unit tests for Conversational Advisor slot extraction and bundle recommendation.
"""

import pytest
from app.core.database import SessionLocal
from app.models.entities import DiscoverySession
from app.advisor.slots import extract_slots_from_text
from app.advisor.orchestrator import process_advisor_turn
from app.advisor.bundles import get_bundle_recommendation


def test_slot_extraction_patterns():
    # Test case 1: Pincode + Employees + Segment
    text1 = "We run Apex Dental Clinic in Mumbai 400001 with 8 staff members. We have GST."
    slots1 = extract_slots_from_text(text1)
    assert slots1["pincode"] == "400001"
    assert slots1["employee_count"] == 8
    assert slots1["segment"] == "prof"
    assert slots1["has_gstin"] is True
    assert "Dental Clinic" in slots1.get("business_name", "")

    # Test case 2: Retail shop without GST
    text2 = "I have a small grocery store, team of 3, no GST, pin code 560001."
    slots2 = extract_slots_from_text(text2)
    assert slots2["pincode"] == "560001"
    assert slots2["employee_count"] == 3
    assert slots2["segment"] == "micro"
    assert slots2["has_gstin"] is False


def test_advisor_turn_and_airfiber_fallback():
    db = SessionLocal()
    try:
        sess = DiscoverySession(preferred_language="en")
        db.add(sess)
        db.commit()

        # Turn 1: Partial info
        resp1 = process_advisor_turn(db, sess.session_id, "We have a clinic with 6 employees.")
        assert resp1.is_ready_for_quote is False
        assert "pincode" in resp1.missing_slots

        # Turn 2: Provide pincode where fibre is down (416001 - Kolhapur Suburban)
        resp2 = process_advisor_turn(db, sess.session_id, "Our installation pincode is 416001.")
        assert resp2.is_ready_for_quote is True
        assert resp2.recommended_bundle_id is not None

        # Verify bundle recommendation recommends P04 AirFiber when Fibre is unfeasible
        rec = get_bundle_recommendation(db, resp2.known_slots)
        assert rec.primary_product.product_id == "P04"
        assert "5G AirFiber" in rec.primary_product.name
        assert rec.primary_product.sla_install_days == 2
    finally:
        db.close()
