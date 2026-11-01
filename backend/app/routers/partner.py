from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.schemas import (
    PartnerQueueItem,
    KycOverrideRequest,
    KycOverrideResult,
)
from app.partner.service import get_partner_queue, override_kyc_decision

router = APIRouter(prefix="/partner", tags=["Partner & Field Operations"])


@router.get("/queue", response_model=List[PartnerQueueItem])
def view_partner_queue(
    role: Optional[str] = Query(None, description="LEAD_RECOVERY, KYC_ASSISTANT"),
    status: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return get_partner_queue(db, role, status)


@router.post("/kyc/{order_id}/override", response_model=KycOverrideResult)
def partner_kyc_override(
    order_id: str,
    payload: KycOverrideRequest,
    db: Session = Depends(get_db),
):
    return override_kyc_decision(
        db=db,
        order_id=order_id,
        reason=payload.reason,
        notes=payload.notes,
    )
