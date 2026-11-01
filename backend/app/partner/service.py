"""
Partner & Field Operations Service.
Implements:
1. Explainable Heuristic Priority Index (HPI) scoring [0-100]
2. Partner queue retrieval (dropped leads + exception review desk)
3. Assisted KYC Verify & Override action unblocking order lifecycle
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.entities import (
    Order,
    OrderEvent,
    KycSubmission,
    KycCheckResult,
    DiscoverySession,
    PartnerAssignment,
    AdvisorSlot,
)
from app.models.schemas import PartnerQueueItem, KycOverrideResult


def calculate_hpi_score(
    has_gstin: bool = False,
    monthly_budget_inr: float = 0.0,
    segment: str = "micro",
    employee_count: int = 1,
    reached_quote: bool = False,
    num_sites: int = 1,
) -> int:
    """
    Computes explainable Heuristic Priority Index (0-100) calibrated against smb_leads.csv.
    - Verified Active GSTIN: +35 pts (9.56% vs 2.05% baseline conversion)
    - Monthly spend >= ₹5,000 or Pro/Multi/Mfg: +25 pts
    - High-intent funnel momentum (reached quote): +20 pts
    - Enterprise scale (employees >= 5 or multi-site): +20 pts
    """
    score = 0
    if has_gstin:
        score += 35
    if monthly_budget_inr >= 5000.0 or segment.lower() in ["prof", "multi", "mfg"]:
        score += 25
    if reached_quote:
        score += 20
    if employee_count >= 5 or num_sites > 1:
        score += 20
    return min(100, max(0, score))


def get_partner_queue(
    db: Session,
    role: Optional[str] = None,
    status_filter: Optional[str] = None
) -> List[PartnerQueueItem]:
    """
    Retrieves prioritized partner queue items covering both KYC exceptions and high-propensity dropped leads.
    """
    items: List[PartnerQueueItem] = []

    # 1. Fetch Orders under review (Planted defects & exceptions: K01, K05, K11)
    review_orders = db.query(Order).filter(Order.status == "UNDER_REVIEW").all()
    for order in review_orders:
        sub = db.query(KycSubmission).filter(KycSubmission.order_id == order.order_id).first()
        reasons = []
        if sub:
            failed_checks = db.query(KycCheckResult).filter(
                KycCheckResult.submission_id == sub.submission_id,
                KycCheckResult.verdict == "FLAGGED"
            ).all()
            reasons = [c.reason_code or c.check_code for c in failed_checks]

        reason_str = ", ".join(reasons) if reasons else "MANUAL_VERIFICATION_REQUIRED"
        
        sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == order.session_id).first()
        b_name = sess.business_name if sess else "Enterprise Account"
        phone = sess.contact_phone if sess else "9876500000"

        items.append(PartnerQueueItem(
            item_id=f"KYC-{order.order_id[:8]}",
            order_id=order.order_id,
            session_id=order.session_id,
            business_name=b_name,
            contact_phone=phone,
            role="KYC_ASSISTANT",
            priority_score=85,  # High priority because customer has already accepted quote
            status="PENDING_REVIEW",
            flagged_reason=reason_str,
            created_at=order.updated_at or order.created_at,
        ))

    # 2. Fetch Sessions that stalled / dropped carts
    stalled_sessions = db.query(DiscoverySession).filter(DiscoverySession.contact_phone.isnot(None)).limit(10).all()
    for sess in stalled_sessions:
        # Check if already converted to order
        existing_order = db.query(Order).filter(Order.session_id == sess.session_id).first()
        if existing_order and existing_order.status != "UNDER_REVIEW":
            continue

        slots_query = db.query(AdvisorSlot).filter(AdvisorSlot.session_id == sess.session_id).all()
        slots = {s.slot_name: s.slot_value for s in slots_query}

        hpi = calculate_hpi_score(
            has_gstin=bool(slots.get("has_gstin", False)),
            monthly_budget_inr=float(slots.get("budget", 2500)),
            segment=str(slots.get("segment", "micro")),
            employee_count=int(slots.get("employee_count", 3)),
            reached_quote=False,
            num_sites=int(slots.get("num_sites", 1)),
        )

        if hpi >= 40:
            items.append(PartnerQueueItem(
                item_id=f"LEAD-{sess.session_id[:8]}",
                order_id=None,
                session_id=sess.session_id,
                business_name=sess.business_name or "Potential SMB Lead",
                contact_phone=sess.contact_phone,
                role="LEAD_RECOVERY",
                priority_score=hpi,
                status="OFFERED",
                flagged_reason=f"Stalled Cart (+{hpi} HPI Propensity Score)",
                created_at=sess.created_at,
            ))

    # Sort queue descending by priority score
    items.sort(key=lambda x: x.priority_score, reverse=True)
    return items


def override_kyc_decision(
    db: Session,
    order_id: str,
    reason: str,
    notes: Optional[str] = None,
    partner_id: str = "P-MUMBAI-042"
) -> KycOverrideResult:
    """
    Partner action: 'Assisted KYC: Verify & Override'.
    Unblocks orders in UNDER_REVIEW to showcase the full downstream tracker and activation milestones.
    """
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    sub = db.query(KycSubmission).filter(KycSubmission.order_id == order_id).first()
    if not sub:
        raise HTTPException(status_code=400, detail="No KYC submission found for this order.")

    # 1. Update KYC state to PASS via partner override
    sub.decision = "PASS"
    sub.processing_state = "COMPLETE"

    # 2. Advance Order to READY_FOR_FULFILMENT
    prev_status = order.status
    order.status = "READY_FOR_FULFILMENT"
    order.updated_at = datetime.now(timezone.utc)

    # 3. Create audit event in timeline
    event = OrderEvent(
        order_id=order.order_id,
        actor_type="partner",
        from_status=prev_status,
        to_status="READY_FOR_FULFILMENT",
        customer_title="KYC Verified via Partner Assistance",
        customer_detail=f"Partner ({partner_id}) performed in-person document verification. Reason: {reason}. {notes or ''}",
    )
    db.add(event)

    # 4. Record/update partner assignment
    assignment = db.query(PartnerAssignment).filter(PartnerAssignment.order_id == order_id).first()
    if not assignment:
        assignment = PartnerAssignment(
            order_id=order_id,
            partner_id=partner_id,
            assignment_role="KYC_ASSISTANT",
            resolution_status="RESOLVED_OVERRIDE",
            priority_score=90,
            resolved_at=datetime.now(timezone.utc),
        )
        db.add(assignment)
    else:
        assignment.resolution_status = "RESOLVED_OVERRIDE"
        assignment.resolved_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(order)

    return KycOverrideResult(
        order_id=order.order_id,
        submission_id=sub.submission_id,
        new_order_status=order.status,
        new_kyc_decision=sub.decision,
        partner_id=partner_id,
        message=f"Order successfully unblocked via partner override. Status advanced to {order.status}."
    )
