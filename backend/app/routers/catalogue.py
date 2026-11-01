from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.entities import Product
from app.models.schemas import (
    ProductResponse,
    ServiceabilityRequest,
    ServiceabilityReport,
)
from app.catalogue.serviceability import check_serviceability

router = APIRouter(prefix="/catalogue", tags=["Product Catalogue & Serviceability"])


@router.get("/products", response_model=List[ProductResponse])
def list_products(
    segment: Optional[str] = Query(None, description="micro, prof, multi, mfg"),
    tier: Optional[int] = Query(None, description="City Tier (1, 2, or 3)"),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    products = query.all()

    filtered = []
    for p in products:
        if segment and p.target_segments:
            if segment.lower() not in [s.lower() for s in p.target_segments]:
                continue
        if tier and p.available_city_tiers:
            if tier not in p.available_city_tiers:
                continue

        filtered.append(
            ProductResponse(
                product_id=p.product_id,
                name=p.name,
                category=p.category,
                target_segments=p.target_segments or [],
                available_city_tiers=p.available_city_tiers or [1, 2],
                requires_gstin=p.requires_gstin,
                min_quantity=p.min_quantity,
                max_quantity=p.max_quantity,
                price_min_inr=p.price_min_paise / 100.0,
                price_max_inr=p.price_max_paise / 100.0,
                setup_fee_inr=p.setup_fee_paise / 100.0,
                contract_months=p.contract_months,
                requires_one_of=p.requires_one_of or [],
                incompatible_with=p.incompatible_with or [],
                sla_install_days=p.sla_install_days,
                description=p.description,
            )
        )
    return filtered


@router.post("/serviceability", response_model=ServiceabilityReport)
def check_pincode_feasibility(
    payload: ServiceabilityRequest,
    db: Session = Depends(get_db),
):
    res = check_serviceability(db, payload.pincode)
    return ServiceabilityReport(**res)
