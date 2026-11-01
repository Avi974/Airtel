from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.core.database import get_db
from app.models.entities import Consent, Order, DiscoverySession
from app.models.schemas import (
    ConsentGrantRequest,
    ConsentResponse,
    ConsentWithdrawalResult,
)

router = APIRouter(prefix="/consents", tags=["Privacy & DPDP Consent"])


@router.post("", response_model=ConsentResponse)
def grant_consent(
    payload: ConsentGrantRequest,
    db: Session = Depends(get_db),
):
    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == payload.session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Discovery session not found.")

    consent = Consent(
        session_id=payload.session_id,
        purpose_scope=payload.purpose_scope,
        is_active=True,
    )
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent


@router.delete("/{consent_id}", response_model=ConsentWithdrawalResult)
def withdraw_consent(
    consent_id: str,
    db: Session = Depends(get_db),
):
    consent = db.query(Consent).filter(Consent.consent_id == consent_id).first()
    if not consent:
        raise HTTPException(status_code=404, detail="Consent record not found.")

    consent.is_active = False
    consent.withdrawn_at = datetime.now(timezone.utc)

    # Impact on associated orders: transition from KYC_IN_PROGRESS to ACTION_REQUIRED
    orders = db.query(Order).filter(Order.session_id == consent.session_id).all()
    impacted_status = "ACTION_REQUIRED"
    for o in orders:
        if o.status in ["KYC_IN_PROGRESS", "AWAITING_KYC_CONSENT", "UNDER_REVIEW"]:
            o.status = "ACTION_REQUIRED"
            o.updated_at = datetime.now(timezone.utc)

    db.commit()

    return ConsentWithdrawalResult(
        consent_id=consent.consent_id,
        is_active=False,
        withdrawn_at=consent.withdrawn_at,
        impacted_order_status=impacted_status,
        message="Consent successfully withdrawn under DPDP Act Section 6. Associated processing halted.",
    )
