# 📋 Project Progress & Decisions Log

> **Last Updated**: 1 Nov 2026, 3:16 PM IST  
> **Status**: V5.2 Modular Monolith Backend complete and pushed to `bussiness-logic` and `main` branches. Next: Frontend & presentation deck.

---

## 🎯 Milestones Progress

- [x] **Case & Dataset Analysis**:
  - `product_catalogue.csv` (25 products, constraints, pipe-separated `requires_one_of`, tier rules)
  - `smb_leads.csv` (5,000 leads, funnel drop-off analysis, HPI calibration)
  - `mock_gstin_registry.csv` (3,534 records, status checks)
  - `mock_udyam_registry.csv` (2,723 records, enterprise categories)
  - `kyc_documents/` (47 sample images, K01-K12 applicants, planted issues)
- [x] **Architecture Specification V5.2 (Final Master Blueprint)**:
  - Hybrid GenAI Advisor (safe by construction)
  - Deterministic pricing matrix ($\text{Price}_{\min} + \Delta_{\text{Tier}} \times 0.5 \times \text{Spread} + \Delta_{\text{Term}} \times 0.5 \times \text{Spread}$)
  - Dual-track KYC (Clean $\rightarrow$ auto-provision; Exception $\rightarrow$ Partner Queue with "Assisted KYC: Verify & Override")
  - Zero-dependency K01–K12 Fixture Vault for air-gapped demo safety
  - Place of Supply (POS) B2B GST tax calculation (Intra 9%+9% vs Inter 18%)
- [x] **Backend Implementation (FastAPI Modular Monolith)**:
  - **Models & Schemas**: SQLAlchemy relational models with Pydantic v2 schemas (`Product`, `PincodeServiceability`, `MockGstinRegistry`, `MockUdyamRegistry`, `DiscoverySession`, `AdvisorSlot`, `AdvisorMessage`, `Quote`, `QuoteLineItem`, `Order`, `OrderEvent`, `Consent`, `KycSubmission`, `KycDocument`, `KycCheckResult`, `PartnerAssignment`)
  - **Advisor Engine**: Multilingual slot extraction (EN, HI, Hinglish) & upfront feasibility checks
  - **Catalogue & Pricing Engine**: Spread calculations, tier restrictions (e.g. P03 Tier 1 only), tenure loyalty discounts
  - **B2B GST POS Tax Engine**: Itemized CGST, SGST, IGST per site location
  - **Smart KYC & Verification Engine**:
    - `DocCompletenessCheck` (catches K05 missing Udyam)
    - 3-Tier OCR Engine (Cloud Vision $\rightarrow$ Tesseract $\rightarrow$ Fixture Vault)
    - Registry cross-validation (catches K01 Cancelled GSTIN)
    - Address proof freshness ($\le$ 90 days from `2026-07-15`, catches K11 expired bill)
    - Anti-Substitution Corroboration Gate (flags manual entries absent from document text)
  - **Partner Operations**: Explainable Heuristic Priority Index (HPI) scoring (0-100) & Assisted KYC Override
  - **Simulator Engine**: Synchronized state machine progression (`READY_FOR_FULFILMENT` $\rightarrow$ `SURVEY_SCHEDULED` $\rightarrow$ `INSTALL_IN_PROGRESS` $\rightarrow$ `ACTIVE`)
  - **23 REST Endpoints Registered in FastAPI**: Across 9 modular routers (`sessions`, `advisor`, `catalogue`, `quotes`, `consents`, `kyc`, `orders`, `simulator`, `partner`)
  - **Database Seed Script**: `seed_db.py` ingesting products, registries, and pincodes
  - **Unit Tests**: Coverage for pricing, tax, KYC planted defects, HPI, and simulator
- [ ] **Next Steps**:
  - Scaffold mobile-first Next.js 14 frontend (6 customer screens + partner desk)
  - Prepare 7-slide pitch deck using `Submission Template_Sync.pptx`
