"""
Advisor Slot Extraction and Typed State Machine.
Tracks factual slots extracted from user conversation with deterministic confidence.
"""

import re
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.entities import AdvisorSlot, DiscoverySession


# Required core slots to unlock commercial quote recommendation
CORE_REQUIRED_SLOTS = ["pincode", "employee_count", "segment"]


def extract_slots_from_text(text: str) -> Dict[str, Any]:
    """
    Extracts structured business attributes from user conversational text.
    Handles Indian SMB patterns (pincodes, employee mentions, GSTINs, business domains).
    """
    extracted = {}
    lower_text = text.lower()

    # 1. 6-digit Indian PIN code
    pin_match = re.search(r"\b([1-9][0-9]{5})\b", text)
    if pin_match:
        extracted["pincode"] = pin_match.group(1)

    # 2. Employee count: "8 people", "12 employees", "we are 5", "team of 10"
    emp_match = re.search(r"\b(\d{1,3})\s*(people|employees|staff|members|persons|workers)\b", lower_text)
    if emp_match:
        extracted["employee_count"] = int(emp_match.group(1))
    else:
        team_match = re.search(r"\b(team of|we are|around)\s*(\d{1,3})\b", lower_text)
        if team_match:
            extracted["employee_count"] = int(team_match.group(2))

    # 3. GSTIN detection (15-character standard alphanumeric)
    gstin_match = re.search(r"\b([0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1})\b", text)
    if gstin_match:
        extracted["gstin"] = gstin_match.group(1)
        extracted["has_gstin"] = True
    elif "no gst" in lower_text or "without gst" in lower_text or "not registered" in lower_text:
        extracted["has_gstin"] = False
    elif "have gst" in lower_text or "gst registered" in lower_text or "gst available" in lower_text:
        extracted["has_gstin"] = True

    # 4. Business Domain / Segment
    if any(k in lower_text for k in ["clinic", "hospital", "dental", "doctor", "diagnostic", "pharma"]):
        extracted["segment"] = "prof"
        extracted["business_type"] = "Healthcare / Clinic"
    elif any(k in lower_text for k in ["shop", "retail", "store", "bakers", "supermarket", "showroom"]):
        extracted["segment"] = "micro"
        extracted["business_type"] = "Retail / Trading"
    elif any(k in lower_text for k in ["factory", "manufacturing", "plant", "workshop", "industrial"]):
        extracted["segment"] = "mfg"
        extracted["business_type"] = "Manufacturing"
    elif any(k in lower_text for k in ["branch", "branches", "sites", "offices", "locations", "multi"]):
        extracted["segment"] = "multi"
        extracted["business_type"] = "Multi-Site Enterprise"
    elif any(k in lower_text for k in ["office", "firm", "consulting", "agency", "tech", "software", "law"]):
        extracted["segment"] = "prof"
        extracted["business_type"] = "Professional Services"

    # 5. Business Name extraction heuristics (e.g. "We run Apex Dental", "We are Apex Dental", "My shop is Saffron Bakers")
    name_match = re.search(r"(?:we are|we run|my shop is|my firm is|company is|business name is)\s+([A-Za-z0-9\s&]+?)(?:,|\.|\bfor\b|\bin\b|$)", text, re.IGNORECASE)
    if name_match:
        name = name_match.group(1).strip()
        if len(name) > 2 and len(name) < 60:
            extracted["business_name"] = name

    return extracted


def update_session_slots(db: Session, session_id: str, new_slots: Dict[str, Any]) -> Dict[str, Any]:
    """Saves newly extracted slots into advisor_slots table and returns aggregated known state."""
    for slot_name, slot_val in new_slots.items():
        existing = (
            db.query(AdvisorSlot)
            .filter(AdvisorSlot.session_id == session_id, AdvisorSlot.slot_name == slot_name)
            .first()
        )
        if existing:
            existing.slot_value = slot_val
            existing.slot_state = "KNOWN"
        else:
            new_entry = AdvisorSlot(
                session_id=session_id,
                slot_name=slot_name,
                slot_value=slot_val,
                slot_state="KNOWN",
            )
            db.add(new_entry)

    # Sync business name to discovery_sessions if extracted
    if "business_name" in new_slots:
        sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
        if sess and not sess.business_name:
            sess.business_name = str(new_slots["business_name"])

    db.commit()

    # Query all active slots
    all_slots = db.query(AdvisorSlot).filter(AdvisorSlot.session_id == session_id).all()
    return {s.slot_name: s.slot_value for s in all_slots}
