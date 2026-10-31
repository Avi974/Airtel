"""
Pydantic v2 schemas for typed API request/response payloads.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ============================================================================
# DISCOVERY & SESSIONS
# ============================================================================

class SessionCreate(BaseModel):
    preferred_language: str = "en"  # "en", "hi", "hinglish"


class SessionIdentify(BaseModel):
    phone: str
    business_name: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    preferred_language: str
    contact_phone: Optional[str] = None
    business_name: Optional[str] = None
    resume_token: str
    created_at: datetime

    class Config:
        from_attributes = True


class MagicLinkRequest(BaseModel):
    channel: str = "whatsapp"  # "whatsapp" or "sms"


class MagicLinkResult(BaseModel):
    session_id: str
    resume_token: str
    magic_url: str
    channel: str
    delivered: bool


class SessionResumeResponse(BaseModel):
    session_id: str
    business_name: Optional[str]
    contact_phone: Optional[str]
    slots: Dict[str, Any]
    active_quote_id: Optional[str] = None
    active_order_id: Optional[str] = None


# ============================================================================
# ADVISOR
# ============================================================================

class AdvisorChatRequest(BaseModel):
    session_id: str
    message: str


class AdvisorChatResponse(BaseModel):
    session_id: str
    reply: str
    known_slots: Dict[str, Any]
    missing_slots: List[str]
    is_ready_for_quote: bool
    recommended_bundle_id: Optional[str] = None


class SlotStateResponse(BaseModel):
    session_id: str
    slots: Dict[str, Any]


class BundleItem(BaseModel):
    product_id: str
    name: str
    category: str
    unit_monthly_inr: float
    unit_setup_inr: float
    quantity: int = 1
    sla_install_days: int


class BundleRecommendation(BaseModel):
    bundle_id: str
    title: str
    tagline: str
    suitability_score: int
    target_segment: str
    primary_product: BundleItem
    included_addons: List[BundleItem]
    optional_addons: List[BundleItem]
    estimated_monthly_inr: float
    estimated_setup_inr: float
    feasibility_notes: str


# ============================================================================
# CATALOGUE & SERVICEABILITY
# ============================================================================

class ProductResponse(BaseModel):
    product_id: str
    name: str
    category: str
    target_segments: List[str]
    available_city_tiers: List[int]
    requires_gstin: bool
    min_quantity: int
    max_quantity: int
    price_min_inr: float
    price_max_inr: float
    setup_fee_inr: float
    contract_months: int
    requires_one_of: List[str]
    incompatible_with: List[str]
    sla_install_days: int
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ServiceabilityRequest(BaseModel):
    pincode: str
    site_identifier: str = "Primary Office"


class ServiceabilityReport(BaseModel):
    pincode: str
    city: str
    state: str
    state_code: str
    city_tier: int
    fibre_feasible: bool
    fwa_feasible: bool
    recommended_tech: str  # "FIBRE" or "FWA_AIRFIBER"
    sla_days: int
    notes: str


# ============================================================================
# QUOTES
# ============================================================================

class QuoteCreateRequest(BaseModel):
    session_id: str
    bundle_id: Optional[str] = "growth_pro"
    product_ids: List[str] = []
    pincode: str
    site_identifier: str = "Site-1"
    contract_months: int = 12


class QuotePatchRequest(BaseModel):
    add_product_ids: List[str] = []
    remove_product_ids: List[str] = []
    contract_months: Optional[int] = None


class QuoteLineItemSchema(BaseModel):
    line_item_id: str
    product_id: str
    product_name: str
    category: str
    site_identifier: str
    site_pincode: str
    site_state_code: str
    serviceability_status: str
    quantity: int
    contract_months: int
    unit_monthly_inr: float
    unit_setup_inr: float
    cgst_inr: float
    sgst_inr: float
    igst_inr: float
    total_monthly_inr: float
    sla_install_days: int


class QuoteResponse(BaseModel):
    quote_id: str
    session_id: str
    status: str
    line_items: List[QuoteLineItemSchema]
    
    # Financial breakdown (in INR)
    monthly_subtotal_inr: float
    monthly_cgst_inr: float
    monthly_sgst_inr: float
    monthly_igst_inr: float
    monthly_total_inr: float
    
    one_time_subtotal_inr: float
    one_time_cgst_inr: float
    one_time_sgst_inr: float
    one_time_igst_inr: float
    one_time_total_inr: float
    
    pricing_formula_ver: str
    expires_at: datetime


class OrderAcceptanceResponse(BaseModel):
    order_id: str
    quote_id: str
    session_id: str
    status: str
    monthly_total_inr: float
    one_time_total_inr: float
    created_at: datetime
    next_step: str


# ============================================================================
# PRIVACY & CONSENT
# ============================================================================

class ConsentGrantRequest(BaseModel):
    session_id: str
    purpose_scope: str = "KYC_VERIFICATION"  # DISCOVERY_SESSION, KYC_VERIFICATION, PARTNER_CALLBACK


class ConsentResponse(BaseModel):
    consent_id: str
    session_id: str
    purpose_scope: str
    is_active: bool
    granted_at: datetime

    class Config:
        from_attributes = True


class ConsentWithdrawalResult(BaseModel):
    consent_id: str
    is_active: bool
    withdrawn_at: datetime
    impacted_order_status: str
    message: str


# ============================================================================
# SMART KYC
# ============================================================================

class KycUploadResponse(BaseModel):
    document_id: str
    submission_id: str
    doc_type: str
    file_path: str
    uploaded_at: datetime


class KycCheckItem(BaseModel):
    check_code: str
    verdict: str  # MATCH, MISMATCH, FLAGGED, SKIPPED
    reason_code: Optional[str]
    confidence_score: Optional[float]
    detail: str


class KycStatusResponse(BaseModel):
    submission_id: str
    order_id: str
    processing_state: str  # AWAITING_DOCS, EXTRACTING, VALIDATING, COMPLETE
    decision: str          # PENDING, PASS, FAIL, REVIEW_REQUIRED
    uploaded_docs: List[str]
    extracted_data: Dict[str, Any]
    checks: List[KycCheckItem]
    resolution_path: str  # "AUTO_APPROVED", "PARTNER_OVERRIDE_REQUIRED", "PENDING_DOCS"


class KycFieldEditRequest(BaseModel):
    field_name: str  # e.g., "gstin", "business_name", "address"
    edited_value: str


# ============================================================================
# ORDER TRACKER & SIMULATOR
# ============================================================================

class OrderTimelineEvent(BaseModel):
    event_id: str
    actor_type: str
    from_status: Optional[str]
    to_status: str
    customer_title: str
    customer_detail: Optional[str]
    created_at: datetime


class OrderTrackerResponse(BaseModel):
    order_id: str
    quote_id: str
    status: str
    customer_business_name: Optional[str]
    expected_sla_days: int
    assigned_partner: Optional[Dict[str, Any]]
    events: List[OrderTimelineEvent]
    financial_summary: Dict[str, Any]


class OrderSummary(BaseModel):
    order_id: str
    quote_id: str
    status: str
    business_name: Optional[str]
    monthly_total_inr: float
    created_at: datetime


class OrderMilestoneAdvance(BaseModel):
    to_milestone: str  # SURVEY_SCHEDULED, INSTALL_IN_PROGRESS, ACTIVE


# ============================================================================
# PARTNER OPERATIONS QUEUE
# ============================================================================

class PartnerQueueItem(BaseModel):
    item_id: str
    order_id: Optional[str]
    session_id: Optional[str]
    business_name: Optional[str]
    contact_phone: Optional[str]
    role: str
    priority_score: int
    status: str
    flagged_reason: Optional[str]
    created_at: datetime


class KycOverrideRequest(BaseModel):
    reason: str
    notes: Optional[str] = None


class KycOverrideResult(BaseModel):
    order_id: str
    submission_id: str
    new_order_status: str
    new_kyc_decision: str
    partner_id: str
    message: str
