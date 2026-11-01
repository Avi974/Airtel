from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.core.database import get_db
from app.models.entities import AdvisorSlot, DiscoverySession
from app.models.schemas import (
    AdvisorChatRequest,
    AdvisorChatResponse,
    SlotStateResponse,
    BundleRecommendation,
)
from app.advisor.orchestrator import process_advisor_turn
from app.advisor.bundles import get_bundle_recommendation

router = APIRouter(prefix="/advisor", tags=["Advisor & Suitability"])


@router.post("/chat", response_model=AdvisorChatResponse)
def advisor_chat(payload: AdvisorChatRequest, db: Session = Depends(get_db)):
    return process_advisor_turn(db, payload.session_id, payload.message)


@router.get("/slots/{session_id}", response_model=SlotStateResponse)
def get_advisor_slots(session_id: str, db: Session = Depends(get_db)):
    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found.")

    slots_rows = db.query(AdvisorSlot).filter(AdvisorSlot.session_id == session_id).all()
    slots_dict = {s.slot_name: s.slot_value for s in slots_rows}
    return SlotStateResponse(session_id=session_id, slots=slots_dict)


@router.get("/recommendation", response_model=BundleRecommendation)
def get_recommendation(session_id: str = Query(...), db: Session = Depends(get_db)):
    slots_rows = db.query(AdvisorSlot).filter(AdvisorSlot.session_id == session_id).all()
    slots_dict = {s.slot_name: s.slot_value for s in slots_rows}
    return get_bundle_recommendation(db, slots_dict)
