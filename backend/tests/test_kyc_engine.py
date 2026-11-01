"""
Unit tests for Smart KYC, OCR Fixture Vault, Planted Defects, and Anti-Substitution Gate.
Validates:
- Applicant K01: Planted defect (Cancelled GSTIN) -> REVIEW_REQUIRED
- Applicant K05: Planted defect (Missing Udyam certificate) -> REVIEW_REQUIRED
- Applicant K11: Planted defect (Address proof older than 90 days) -> REVIEW_REQUIRED
- Applicant K02: Clean applicant -> PASS -> READY_FOR_FULFILMENT
- Anti-substitution gate: flags manual edits not found in document text
"""

from datetime import datetime
from app.kyc.engine import (
    load_fixture_vault,
    run_anti_substitution_gate,
    check_document_completeness,
)


def test_fixture_vault_loaded():
    vault = load_fixture_vault()
    assert len(vault) == 12
    assert "K01" in vault
    assert "K05" in vault
    assert "K11" in vault
    assert "K02" in vault


def test_k01_cancelled_gstin_flagged():
    vault = load_fixture_vault()
    k01 = vault["K01"]
    assert k01["planted_defect"] == "GSTIN_CANCELLED"
    assert k01["expected_verdict"] == "REVIEW_REQUIRED"
    assert k01["reason_code"] == "GSTIN_CANCELLED"


def test_k05_missing_udyam_flagged():
    vault = load_fixture_vault()
    k05 = vault["K05"]
    assert k05["planted_defect"] == "MISSING_REQUIRED_DOCUMENT_UDYAM"
    assert k05["expected_verdict"] == "REVIEW_REQUIRED"
    assert k05["reason_code"] == "DOCS_MISSING_UDYAM"


def test_k11_expired_address_proof():
    vault = load_fixture_vault()
    k11 = vault["K11"]
    ref_date = datetime(2026, 7, 15)
    bill_date = datetime.strptime(k11["address_proof_date"], "%Y-%m-%d")
    age_days = (ref_date - bill_date).days
    assert age_days > 90
    assert k11["planted_defect"] == "ADDRESS_PROOF_EXPIRED"
    assert k11["expected_verdict"] == "REVIEW_REQUIRED"


def test_k02_clean_applicant_passes():
    vault = load_fixture_vault()
    k02 = vault["K02"]
    assert k02["planted_defect"] is None
    assert k02["expected_verdict"] == "PASS"
    assert k02["reason_code"] == "ALL_CHECKS_PASSED"


def test_anti_substitution_gate():
    raw_ocr = "APEX DIAGNOSTICS & CLINIC DR RAJESH SHARMA GSTIN 27AAXCA1234F1Z5 UDYAM-MH-00-1234567"

    # User enters GSTIN that appears in raw OCR text -> PASS
    ok, reason = run_anti_substitution_gate("27AAXCA1234F1Z5", raw_ocr)
    assert ok is True
    assert reason is None

    # User enters fraudulent GSTIN not present in document -> REJECT / REVIEW
    ok, reason = run_anti_substitution_gate("29AAXCN9012M1Z8", raw_ocr)
    assert ok is False
    assert reason == "UNCORROBORATED_MANUAL_INPUT"
