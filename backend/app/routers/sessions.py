from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.entities import DiscoverySession, AdvisorSlot, Quote, Order
from app.models.schemas import (
    SessionCreate,
    SessionIdentify,
    SessionResponse,
    MagicLinkRequest,
    MagicLinkResult,
    SessionResumeResponse,
)

router = APIRouter(prefix="/sessions", tags=["Discovery & Sessions"])


@router.post("", response_model=SessionResponse)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    sess = DiscoverySession(preferred_language=payload.preferred_language)
    db.add(sess)
    db.commit()
    db.refresh(sess)
    return sess


@router.post("/{session_id}/identify", response_model=SessionResponse)
def identify_session(session_id: str, payload: SessionIdentify, db: Session = Depends(get_db)):
    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")
    sess.contact_phone = payload.phone
    if payload.business_name:
        sess.business_name = payload.business_name
    db.commit()
    db.refresh(sess)
    return sess


@router.post("/{session_id}/magic-link", response_model=MagicLinkResult)
def generate_magic_link(session_id: str, payload: MagicLinkRequest, db: Session = Depends(get_db)):
    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")

    magic_url = f"https://accel.digital/resume/{sess.resume_token}"
    return MagicLinkResult(
        session_id=sess.session_id,
        resume_token=sess.resume_token,
        magic_url=magic_url,
        channel=payload.channel,
        delivered=True,
    )


@router.get("/resume/{token}", response_model=SessionResumeResponse)
def resume_session(token: str, db: Session = Depends(get_db)):
    sess = db.query(DiscoverySession).filter(DiscoverySession.resume_token == token).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Invalid or expired resume token.")

    slots_rows = db.query(AdvisorSlot).filter(AdvisorSlot.session_id == sess.session_id).all()
    slots_dict = {s.slot_name: s.slot_value for s in slots_rows}

    active_quote = db.query(Quote).filter(Quote.session_id == sess.session_id).order_by(Quote.created_at.desc()).first()
    active_order = db.query(Order).filter(Order.session_id == sess.session_id).order_by(Order.created_at.desc()).first()

    return SessionResumeResponse(
        session_id=sess.session_id,
        business_name=sess.business_name,
        contact_phone=sess.contact_phone,
        slots=slots_dict,
        active_quote_id=active_quote.quote_id if active_quote else None,
        active_order_id=active_order.order_id if active_order else None,
    )
