import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.entities import Order, KycSubmission, KycDocument
from app.models.schemas import (
    KycUploadResponse,
    KycStatusResponse,
    KycFieldEditRequest,
)
from app.kyc.engine import run_kyc_verification, run_anti_substitution_gate

router = APIRouter(prefix="/kyc", tags=["Smart KYC & Verification"])


@router.post("/{order_id}/upload", response_model=KycUploadResponse)
async def upload_kyc_document(
    order_id: str,
    doc_type: str = Form(..., description="gst_certificate, udyam_certificate, signatory_id, address_proof"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    order = db.query(Order).filter(Order.order_id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # Find or initialize KYC submission
    sub = db.query(KycSubmission).filter(KycSubmission.order_id == order_id).first()
    if not sub:
        sub = KycSubmission(
            order_id=order_id,
            processing_state="AWAITING_DOCS",
            decision="PENDING",
        )
        db.add(sub)
        db.commit()
        db.refresh(sub)

    # Save uploaded file to runtime/uploads
    filename = f"{order_id[:8]}_{doc_type}_{file.filename}"
    target_path = settings.UPLOAD_PATH / filename
    with open(target_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    doc = KycDocument(
        submission_id=sub.submission_id,
        doc_type=doc_type.strip().lower(),
        file_path=str(target_path),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return KycUploadResponse(
        document_id=doc.document_id,
        submission_id=sub.submission_id,
        doc_type=doc.doc_type,
        file_path=str(target_path),
        uploaded_at=doc.uploaded_at,
    )


@router.post("/{order_id}/verify", response_model=KycStatusResponse)
def trigger_kyc_verification(
    order_id: str,
    db: Session = Depends(get_db),
):
    return run_kyc_verification(db, order_id)


@router.get("/{order_id}/status", response_model=KycStatusResponse)
def get_kyc_status(
    order_id: str,
    db: Session = Depends(get_db),
):
    return run_kyc_verification(db, order_id)


@router.post("/{order_id}/edit-field", response_model=KycStatusResponse)
def edit_kyc_field(
    order_id: str,
    payload: KycFieldEditRequest,
    db: Session = Depends(get_db),
):
    sub = db.query(KycSubmission).filter(KycSubmission.order_id == order_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="KYC submission not found.")

    docs = db.query(KycDocument).filter(KycDocument.submission_id == sub.submission_id).all()
    # Anti-substitution check
    corpus = " ".join([Path(d.file_path).name for d in docs])
    corroborated, reason = run_anti_substitution_gate(payload.edited_value, corpus)

    # Re-run full deterministic verification
    resp = run_kyc_verification(db, order_id)
    return resp
