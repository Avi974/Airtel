from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.schemas import (
    QuoteCreateRequest,
    QuotePatchRequest,
    QuoteResponse,
    OrderAcceptanceResponse,
)
from app.quotes_orders.service import (
    create_quote,
    modify_quote_items,
    get_quote_response,
    accept_quote_and_create_order,
)

router = APIRouter(prefix="/quotes", tags=["Quotes & Checkout"])


@router.post("", response_model=QuoteResponse)
def api_create_quote(
    payload: QuoteCreateRequest,
    db: Session = Depends(get_db),
):
    # If bundle_id provided but product_ids empty, default to base products
    p_ids = payload.product_ids
    if not p_ids:
        if payload.bundle_id == "micro_starter":
            p_ids = ["P01", "P07"]
        elif payload.bundle_id == "multi_connect":
            p_ids = ["P02", "P09", "P11"]
        elif payload.bundle_id == "mfg_power":
            p_ids = ["P03", "P11", "P21"]
        else:
            p_ids = ["P02", "P07", "P09"]  # Growth Pro default

    quote = create_quote(
        db=db,
        session_id=payload.session_id,
        product_ids=p_ids,
        pincode=payload.pincode,
        site_identifier=payload.site_identifier,
        contract_months=payload.contract_months,
    )
    return get_quote_response(db, quote.quote_id)


@router.patch("/{quote_id}/items", response_model=QuoteResponse)
def api_modify_quote(
    quote_id: str,
    payload: QuotePatchRequest,
    db: Session = Depends(get_db),
):
    quote = modify_quote_items(
        db=db,
        quote_id=quote_id,
        add_product_ids=payload.add_product_ids,
        remove_product_ids=payload.remove_product_ids,
        contract_months=payload.contract_months,
    )
    return get_quote_response(db, quote.quote_id)


@router.get("/{quote_id}", response_model=QuoteResponse)
def api_get_quote(
    quote_id: str,
    db: Session = Depends(get_db),
):
    return get_quote_response(db, quote_id)


@router.post("/{quote_id}/accept", response_model=OrderAcceptanceResponse)
def api_accept_quote(
    quote_id: str,
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
    db: Session = Depends(get_db),
):
    return accept_quote_and_create_order(
        db=db,
        quote_id=quote_id,
        idempotency_key=idempotency_key,
    )
