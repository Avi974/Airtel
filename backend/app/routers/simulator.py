from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.entities import Order, OrderEvent
from app.models.schemas import OrderMilestoneAdvance, OrderTimelineEvent

router = APIRouter(prefix="/simulator", tags=["Demo Milestone Simulator"])

VALID_TRANSITIONS = {
    "AWAITING_KYC_CONSENT": ["KYC_IN_PROGRESS", "ACTION_REQUIRED"],
    "KYC_IN_PROGRESS": ["UNDER_REVIEW", "READY_FOR_FULFILMENT"],
    "UNDER_REVIEW": ["READY_FOR_FULFILMENT"],
    "READY_FOR_FULFILMENT": ["SURVEY_SCHEDULED", "INSTALL_IN_PROGRESS"],
    "SURVEY_SCHEDULED": ["INSTALL_IN_PROGRESS"],
    "INSTALL_IN_PROGRESS": ["ACTIVE"],
    "ACTIVE": [],
}

MILESTONE_TITLES = {
    "SURVEY_SCHEDULED": ("Physical Site Survey Scheduled", "Airtel Field Engineer dispatched for route survey and cabling layout check."),
    "INSTALL_IN_PROGRESS": ("Fibre Pull & CPE Installation in Progress", "Outdoor drop-cable connected and Gigabit Optical Network Terminal (ONT) installed."),
    "ACTIVE": ("Service Successfully Activated", "Network provisioning completed. Bandwidth test verified at 100% committed SLA. Your single consolidated billing is active."),
}


@router.post("/orders/{order_id}/advance", response_model=OrderTimelineEvent)
def advance_order_milestone(
    order_id: str,
    payload: OrderMilestoneAdvance,
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    target = payload.to_milestone.upper()
    if target not in MILESTONE_TITLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid target milestone '{target}'. Supported simulator milestones: {list(MILESTONE_TITLES.keys())}"
        )

    prev_status = order.status
    order.status = target
    order.updated_at = datetime.now(timezone.utc)

    title, detail = MILESTONE_TITLES[target]
    event = OrderEvent(
        order_id=order.order_id,
        actor_type="simulator",
        from_status=prev_status,
        to_status=target,
        customer_title=title,
        customer_detail=detail,
    )
    db.add(event)
    db.commit()
    db.refresh(event)

    return OrderTimelineEvent(
        event_id=event.event_id,
        actor_type=event.actor_type,
        from_status=event.from_status,
        to_status=event.to_status,
        customer_title=event.customer_title,
        customer_detail=event.customer_detail,
        created_at=event.created_at,
    )
