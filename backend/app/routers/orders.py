from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.entities import Order, OrderEvent, DiscoverySession, PartnerAssignment
from app.models.schemas import (
    OrderTrackerResponse,
    OrderTimelineEvent,
    OrderSummary,
)

router = APIRouter(prefix="/orders", tags=["Order Lifecycle & Persistent Tracker"])


@router.get("/{order_id}/tracker", response_model=OrderTrackerResponse)
def get_order_tracker(
    order_id: str,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == order.session_id).first()
    b_name = sess.business_name if sess else "Valued Enterprise Customer"

    events_rows = db.query(OrderEvent).filter(OrderEvent.order_id == order_id).order_by(OrderEvent.created_at.asc()).all()
    events = [
        OrderTimelineEvent(
            event_id=e.event_id,
            actor_type=e.actor_type,
            from_status=e.from_status,
            to_status=e.to_status,
            customer_title=e.customer_title,
            customer_detail=e.customer_detail,
            created_at=e.created_at,
        )
        for e in events_rows
    ]

    assignment = db.query(PartnerAssignment).filter(PartnerAssignment.order_id == order_id).first()
    partner_dict = None
    if assignment:
        partner_dict = {
            "partner_id": assignment.partner_id,
            "role": assignment.assignment_role,
            "resolution_status": assignment.resolution_status,
            "contact_name": "Airtel Local Channel Partner",
            "support_phone": "1800-103-0101",
        }

    snapshot = order.frozen_financial_snapshot or {}

    return OrderTrackerResponse(
        order_id=order.order_id,
        quote_id=order.quote_id,
        status=order.status,
        customer_business_name=b_name,
        expected_sla_days=snapshot.get("max_sla_days", 4),
        assigned_partner=partner_dict,
        events=events,
        financial_summary=snapshot,
    )


@router.get("/by-phone/{phone}", response_model=List[OrderSummary])
def get_orders_by_phone(
    phone: str,
    db: Session = Depends(get_db),
):
    clean_phone = phone.strip()
    sessions = db.query(DiscoverySession).filter(DiscoverySession.contact_phone == clean_phone).all()
    session_ids = [s.session_id for s in sessions]

    orders = db.query(Order).filter(Order.session_id.in_(session_ids)).order_by(Order.created_at.desc()).all()
    summaries = []
    for o in orders:
        snapshot = o.frozen_financial_snapshot or {}
        sess = next((s for s in sessions if s.session_id == o.session_id), None)
        summaries.append(
            OrderSummary(
                order_id=o.order_id,
                quote_id=o.quote_id,
                status=o.status,
                business_name=sess.business_name if sess else "My Business",
                monthly_total_inr=snapshot.get("monthly_total_inr", 0.0),
                created_at=o.created_at,
            )
        )
    return summaries
