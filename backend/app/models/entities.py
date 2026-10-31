"""
SQLAlchemy relational entities matching the V5.2 Relational Schema.
Supports SQLite and PostgreSQL transparently with clean JSON serialization.
"""

from datetime import datetime, timezone, timedelta
import uuid
from typing import List, Optional

from sqlalchemy import (
    Column,
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Date,
    Float,
    Text,
    ForeignKey,
    CheckConstraint,
    JSON,
)
from sqlalchemy.orm import relationship

from app.core.database import Base


def utc_now():
    return datetime.now(timezone.utc)


def default_expiry():
    return datetime.now(timezone.utc) + timedelta(hours=48)


def generate_uuid():
    return str(uuid.uuid4())


# ============================================================================
# 1. REFERENCE REGISTRIES
# ============================================================================

class Product(Base):
    __tablename__ = "products"

    product_id = Column(String(32), primary_key=True)
    name = Column(String(128), nullable=False)
    category = Column(String(64), nullable=False)
    target_segments = Column(JSON, nullable=False, default=list)  # e.g. ["Retailer", "Professional"]
    available_city_tiers = Column(JSON, nullable=False, default=lambda: [1, 2])  # e.g. [1, 2]
    requires_gstin = Column(Boolean, default=False)
    min_quantity = Column(Integer, default=1)
    max_quantity = Column(Integer, default=100)
    price_min_paise = Column(BigInteger, nullable=False)
    price_max_paise = Column(BigInteger, nullable=False)
    setup_fee_paise = Column(BigInteger, default=0)
    contract_months = Column(Integer, default=12)
    requires_one_of = Column(JSON, default=list)  # Pipe-separated OR dependencies: ["P01", "P02"]
    incompatible_with = Column(JSON, default=list)
    sla_install_days = Column(Integer, default=3)
    description = Column(Text, nullable=True)


class PincodeServiceability(Base):
    __tablename__ = "pincode_serviceability"

    pincode = Column(String(10), primary_key=True)
    city = Column(String(64), nullable=False)
    state = Column(String(64), nullable=False)
    state_code = Column(String(2), nullable=False)  # e.g. "27" for Maharashtra
    city_tier = Column(Integer, nullable=False)
    fibre_feasible = Column(Boolean, default=True)
    fwa_feasible = Column(Boolean, default=True)


class MockGstinRegistry(Base):
    __tablename__ = "mock_gstin_registry"

    gstin = Column(String(15), primary_key=True)
    legal_name = Column(String(255), nullable=False)
    trade_name = Column(String(255), nullable=True)
    registered_address = Column(Text, nullable=False)
    taxpayer_status = Column(String(32), nullable=False)  # Active, Suspended, Cancelled
    state_code = Column(String(2), nullable=False)


class MockUdyamRegistry(Base):
    __tablename__ = "mock_udyam_registry"

    udyam_number = Column(String(25), primary_key=True)
    enterprise_name = Column(String(255), nullable=False)
    enterprise_type = Column(String(32), nullable=False)  # Micro, Small, Medium
    major_activity = Column(String(64), nullable=True)
    registered_address = Column(Text, nullable=False)
    registration_date = Column(Date, nullable=False)


# ============================================================================
# 2. DISCOVERY & ADVISOR SESSIONS
# ============================================================================

class DiscoverySession(Base):
    __tablename__ = "discovery_sessions"

    session_id = Column(String(36), primary_key=True, default=generate_uuid)
    preferred_language = Column(String(8), default="en")  # en, hi, hinglish
    contact_phone = Column(String(16), nullable=True, index=True)
    business_name = Column(String(255), nullable=True)
    resume_token = Column(String(64), unique=True, default=generate_uuid, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    slots = relationship("AdvisorSlot", back_populates="session", cascade="all, delete-orphan")
    messages = relationship("AdvisorMessage", back_populates="session", cascade="all, delete-orphan")
    quotes = relationship("Quote", back_populates="session")
    consents = relationship("Consent", back_populates="session")


class AdvisorSlot(Base):
    __tablename__ = "advisor_slots"

    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id", ondelete="CASCADE"), primary_key=True)
    slot_name = Column(String(64), primary_key=True)
    slot_value = Column(JSON, nullable=True)
    slot_state = Column(String(16), default="UNKNOWN")  # KNOWN, UNKNOWN, AMBIGUOUS
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    session = relationship("DiscoverySession", back_populates="slots")


class AdvisorMessage(Base):
    __tablename__ = "advisor_messages"

    message_id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id", ondelete="CASCADE"), nullable=False, index=True)
    sender_role = Column(String(16), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    extracted_metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    session = relationship("DiscoverySession", back_populates="messages")


# ============================================================================
# 3. QUOTES & COMMERCIAL ORDERS
# ============================================================================

class Quote(Base):
    __tablename__ = "quotes"

    quote_id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id"), nullable=True, index=True)
    status = Column(String(24), default="DRAFT")  # DRAFT, READY, ACCEPTED, EXPIRED
    
    # Financial breakdown (in Paise)
    monthly_subtotal_paise = Column(BigInteger, default=0)
    monthly_cgst_paise = Column(BigInteger, default=0)
    monthly_sgst_paise = Column(BigInteger, default=0)
    monthly_igst_paise = Column(BigInteger, default=0)
    monthly_total_paise = Column(BigInteger, default=0)
    
    one_time_subtotal_paise = Column(BigInteger, default=0)
    one_time_cgst_paise = Column(BigInteger, default=0)
    one_time_sgst_paise = Column(BigInteger, default=0)
    one_time_igst_paise = Column(BigInteger, default=0)
    one_time_total_paise = Column(BigInteger, default=0)
    
    pricing_formula_ver = Column(String(16), default="v1.0-deterministic")
    created_at = Column(DateTime(timezone=True), default=utc_now)
    expires_at = Column(DateTime(timezone=True), default=default_expiry)

    session = relationship("DiscoverySession", back_populates="quotes")
    line_items = relationship("QuoteLineItem", back_populates="quote", cascade="all, delete-orphan")
    order = relationship("Order", back_populates="quote", uselist=False)


class QuoteLineItem(Base):
    __tablename__ = "quote_line_items"

    line_item_id = Column(String(36), primary_key=True, default=generate_uuid)
    quote_id = Column(String(36), ForeignKey("quotes.quote_id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(String(32), ForeignKey("products.product_id"), nullable=False)
    site_identifier = Column(String(64), nullable=False)
    site_pincode = Column(String(10), nullable=False)
    site_state_code = Column(String(2), nullable=False)  # For POS GST split
    serviceability_status = Column(String(24), default="SERVICEABLE")  # SERVICEABLE, SURVEY_REQUIRED, UNAVAILABLE
    quantity = Column(Integer, default=1)
    contract_months = Column(Integer, nullable=False, default=12)
    
    unit_monthly_paise = Column(BigInteger, nullable=False)
    unit_setup_paise = Column(BigInteger, default=0)
    cgst_paise = Column(BigInteger, default=0)
    sgst_paise = Column(BigInteger, default=0)
    igst_paise = Column(BigInteger, default=0)

    quote = relationship("Quote", back_populates="line_items")
    product = relationship("Product")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(String(36), primary_key=True, default=generate_uuid)
    quote_id = Column(String(36), ForeignKey("quotes.quote_id"), unique=True, nullable=False)
    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id"), nullable=True, index=True)
    status = Column(
        String(32),
        default="AWAITING_KYC_CONSENT",
        index=True,
    )  # AWAITING_KYC_CONSENT, KYC_IN_PROGRESS, UNDER_REVIEW, READY_FOR_FULFILMENT, SURVEY_SCHEDULED, INSTALL_IN_PROGRESS, ACTIVE, ACTION_REQUIRED, CANCELLED
    frozen_financial_snapshot = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    quote = relationship("Quote", back_populates="order")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan", order_by="OrderEvent.created_at")
    kyc_submission = relationship("KycSubmission", back_populates="order", uselist=False)
    partner_assignment = relationship("PartnerAssignment", back_populates="order", uselist=False)


class OrderEvent(Base):
    __tablename__ = "order_events"

    event_id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False, index=True)
    actor_type = Column(String(24), nullable=False)  # system, customer, partner, simulator
    from_status = Column(String(32), nullable=True)
    to_status = Column(String(32), nullable=False)
    customer_title = Column(String(128), nullable=False)
    customer_detail = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    order = relationship("Order", back_populates="events")


# ============================================================================
# 4. PRIVACY, CONSENT & VERIFICATION
# ============================================================================

class Consent(Base):
    __tablename__ = "consents"

    consent_id = Column(String(36), primary_key=True, default=generate_uuid)
    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id"), nullable=False, index=True)
    purpose_scope = Column(String(32), nullable=False)  # DISCOVERY_SESSION, KYC_VERIFICATION, PARTNER_CALLBACK
    is_active = Column(Boolean, default=True)
    granted_at = Column(DateTime(timezone=True), default=utc_now)
    withdrawn_at = Column(DateTime(timezone=True), nullable=True)

    session = relationship("DiscoverySession", back_populates="consents")


class KycSubmission(Base):
    __tablename__ = "kyc_submissions"

    submission_id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.order_id"), unique=True, nullable=False)
    consent_id = Column(String(36), ForeignKey("consents.consent_id"), nullable=True)
    processing_state = Column(String(24), default="AWAITING_DOCS")  # AWAITING_DOCS, EXTRACTING, VALIDATING, COMPLETE
    decision = Column(String(24), default="PENDING")  # PENDING, PASS, FAIL, REVIEW_REQUIRED
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    order = relationship("Order", back_populates="kyc_submission")
    documents = relationship("KycDocument", back_populates="submission", cascade="all, delete-orphan")
    checks = relationship("KycCheckResult", back_populates="submission", cascade="all, delete-orphan")


class KycDocument(Base):
    __tablename__ = "kyc_documents"

    document_id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("kyc_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    doc_type = Column(String(32), nullable=False)  # gst_certificate, udyam_certificate, signatory_id, address_proof
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=utc_now)

    submission = relationship("KycSubmission", back_populates="documents")


class KycCheckResult(Base):
    __tablename__ = "kyc_check_results"

    check_id = Column(String(36), primary_key=True, default=generate_uuid)
    submission_id = Column(String(36), ForeignKey("kyc_submissions.submission_id", ondelete="CASCADE"), nullable=False, index=True)
    check_code = Column(String(32), nullable=False)  # GSTIN_FORMAT, GSTIN_ACTIVE, UDYAM_NAME_MATCH, ANTI_SUBSTITUTION, ADDR_FRESHNESS
    verdict = Column(String(16), nullable=False)  # MATCH, MISMATCH, FLAGGED, SKIPPED
    reason_code = Column(String(64), nullable=True)  # GSTIN_CANCELLED, DOCS_MISSING, ADDRESS_EXPIRED, etc.
    confidence_score = Column(Float, nullable=True)
    raw_evidence = Column(JSON, default=dict)
    checked_at = Column(DateTime(timezone=True), default=utc_now)

    submission = relationship("KycSubmission", back_populates="checks")


class PartnerAssignment(Base):
    __tablename__ = "partner_assignments"

    assignment_id = Column(String(36), primary_key=True, default=generate_uuid)
    order_id = Column(String(36), ForeignKey("orders.order_id"), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("discovery_sessions.session_id"), nullable=True, index=True)
    partner_id = Column(String(64), nullable=False)
    assignment_role = Column(String(32), nullable=False)  # LEAD_RECOVERY, KYC_ASSISTANT, INSTALL_ENGINEER
    resolution_status = Column(String(24), default="PENDING")  # PENDING, ACCEPTED, RESOLVED_OVERRIDE, COMPLETED
    priority_score = Column(Integer, default=50)
    assigned_at = Column(DateTime(timezone=True), default=utc_now)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    order = relationship("Order", back_populates="partner_assignment")
    session = relationship("DiscoverySession")

    __table_args__ = (
        CheckConstraint("order_id IS NOT NULL OR session_id IS NOT NULL", name="chk_order_or_session"),
    )
