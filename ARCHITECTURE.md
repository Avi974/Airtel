# Project Udyam Digital — Definitive Master Architecture (V5.2 Final Blueprint)
### Making Small Businesses Go Digital in One Sitting · Accel Telecom B2B

---

## 1. Executive Summary & Architectural Posture

Project Udyam Digital is an enterprise-grade digital acquisition and onboarding platform designed to compress the traditional **17.6-day, paper-heavy sales cycle** into an **instant, digital-first experience (<15 minutes)** for India's 6 crore+ MSMEs, backed by local partner fulfillment (1–2 days for FWA/SIMs, 3–5 days for Standard Fibre, with dynamic milestones for Leased Lines).

### Core Architectural Principles
1. **Hybrid GenAI Advisor (Safe by Construction):** The LLM never hallucinates catalogue products or prices. It acts as an empathetic conversational orchestrator that extracts structured business attributes into a typed state machine, while a deterministic suitability engine selects and prices bundles directly from `product_catalogue.csv`.
2. **Deterministic Commercial Pricing:** All catalogue price ranges are resolved via an explicit, reproducible formula based on city tier and contract commitment.
3. **Dual-Track KYC with Exception Resolution:** Clean applicants auto-provision; planted defects (cancelled GSTIN, expired docs, uncorroborated edits) route into a Partner Operations Queue where agents resolve them via an explicit **"Assisted KYC: Verify & Override"** action, preventing demo deadlocks.
4. **Zero-Dependency Resilience (The Fixture Vault):** An adaptive 3-tier OCR strategy with pre-extracted JSON vaults for the 12 specimen applicants ensures 100% test scenario reliability regardless of cloud API quotas or local C-library dependencies.
5. **Clean "One Sitting" Phase Boundary:** Digital onboarding (Discovery → Quoting → Consent → KYC → Order Freeze) is completed in one sitting on a mobile phone; physical fulfillment (Site survey, fiber pull, CPE delivery) is tracked transparently via a persistent, read-only event tracker.

---

## 2. End-to-End System Architecture

```text
+------------------------------------------------------------------------------------------------------------------+
|                                        CLIENT LAYER (Next.js 14 + Tailwind CSS)                                  |
|  +------------------------------------------------------+  +--------------------------------------------------+  |
|  | MSME Self-Serve Mobile Experience                    |  | Accel Partner & Operations Portal (/admin)       |  |
|  | - Multilingual Discovery (EN / HI / Hinglish)        |  | - Explainable Lead & Dropped-Cart Queue (HPI)    |  |
|  | - Conversational Advisor (Slot-Filling Guided Chat)  |  | - KYC Exception Desk (Assisted Verify & Override)|  |
|  | - Interactive Bundle Builder & Serviceability Check  |  | - Dispatch & Installation SLA Tracking           |  |
|  | - 3-Gate Consent Center & Document Uploader          |  | - Channel Partner Commission & Payout Audit      |  |
|  | - Persistent Real-Time Order Milestone Tracker       |  |                                                  |  |
|  +---------------------------+--------------------------+  +------------------------+-------------------------+  |
+------------------------------|------------------------------------------------------|----------------------------+
                               | HTTPS (Session Token / Partner RBAC Bearer)          |
                               v                                                      v
+------------------------------------------------------------------------------------------------------------------+
|                              FASTAPI MODULAR MONOLITH (Python 3.11+ Async Engine)                                |
|                                                                                                                  |
|  [ CORE RUNTIME: Session & Token Security | RBAC Middleware | Masked Audit Logger | Strict Rate Limiting ]       |
|                                                                                                                  |
|  1. CONVERSATIONAL ADVISOR & SUITABILITY MODULE       2. CATALOGUE PRICING & ATOMIC ORDER MODULE                 |
|  - LLM Dialogue Engine (Pydantic Structured Output)   - Deterministic Pricing Matrix (Spread x Tier/Term)        |
|  - Fact-Slot State Machine (KNOWN/UNKNOWN/AMBIGUOUS)  - Pre-Checkout Pincode Feasibility Check (Fibre vs AirFibre|
|  - Segment Classifier (Retail / Office / Multi / Mfg) - Line-Item B2B GST: Intra (CGST+SGST) vs Inter (IGST)     |
|  - Anti-Mis-Selling Soft Guard (Tool De-duplication)  - Idempotent Row-Locked Order Freeze (Zero PII in Snapshot)|
|                           |                                                      |                               |
|  3. ADAPTIVE SMART KYC & VALIDATION ENGINE            4. TRACKER & FULFILMENT SIMULATOR MODULE                   |
|  - 3-Tier OCR Engine: Cloud Vision -> Local Tesseract - Read-Only Idempotent Polling API (/tracker)              |
|    -> Specimen Fixture Vault (K01–K12 Zero-Fail)      - Dual-Track Order State Machine (Clean vs Exception)      |
|  - Mock Registry Gateway (mock_gstin, mock_udyam)     - Simulated Milestone Advancer (Synchronized Enums)        |
|  - Anti-Substitution Corroboration Gate (OCR Check)   - Dynamic SLA Engine (Tied to Catalogue Lead Times)        |
|  - Mandatory Document Checklist Audit (Catches K05)   - Automated Partner Dispatch on Provisioning Gate          |
+---------------------------+------------------------------------------------------+-------------------------------+
                            |                                                      |
                            v                                                      v
+--------------------------------------------------+   +-----------------------------------------------------------+
| EXTERNAL AI & TRUST BOUNDARY                     |   | POSTGRESQL PERSISTENCE & STORAGE                          |
| - LLM Provider (Gemini / Claude / OpenAI):       |   | - Reference Registries: product_catalogue,                |
|   Receives ONLY masked business profile + cat IDs|   |   mock_gstin_registry, mock_udyam_registry,               |
| - Zero PII disclosure: Customer names, phone     |   |   pincode_serviceability                                  |
|   numbers, and addresses are stripped at runtime |   | - Transactional Core: discovery_sessions, advisor_slots,  |
| - OCR Processing: Local Tesseract / Isolated     |   |   quotes, quote_line_items, orders, order_events          |
|   Vision API payload (auto-expiring buffer)      |   | - Security & KYC: consents (3 scopes), kyc_submissions,  |
|                                                  |   |   kyc_documents, kyc_check_results, partner_assignments   |
|                                                  |   | - File Store: runtime/uploads/ (DPDP Purgeable)           |
+--------------------------------------------------+   +-----------------------------------------------------------+
```

---

## 3. Detailed Component Workflows & State Machines

### A. Conversational Advisor & Suitability Engine

```mermaid
flowchart TD
    Start(["User Lands on Mobile Chat"]) --> AskLang["Language Selected (EN / HI / Hinglish)"]
    AskLang --> UserMsg["User Explains Business in Natural Language"]
    UserMsg --> LLMParse["LLM Orchestrator (Structured Pydantic Extraction)"]
    
    LLMParse --> SlotUpdate["Update Slot State Machine\n(segment, city_tier, locations, staff, has_gstin, existing_tools)"]
    
    SlotUpdate --> CheckSlots{"Are Minimum Viable Slots\nKnown? (Segment + Tier + Sites)"}
    
    CheckSlots -- No --> AskNext["LLM Asks Single Next Conversational Question"]
    AskNext --> UserMsg
    
    CheckSlots -- Yes --> SuitabilityRun["Suitability Engine (Pure Deterministic Python)"]
    SuitabilityRun --> HardFilter["Filter product_catalogue.csv on Tier Array, Size & Dependencies"]
    HardFilter --> AntiMisSell["Soft Warning: Check if Product overlaps with existing_tools[]"]
    AntiMisSell --> RankBundle["Rank Bundles: Need Coverage -> Lowest Monthly Cost"]
    RankBundle --> PresentRec["Present Tailored Bundle Card + Toggleable Add-ons"]
    PresentRec --> ToQuote["Customer Taps 'Customize & Checkout'"]
```

#### Deterministic Commercial Pricing Formula
$$\text{Unit Monthly Price} = P_{\min} + (\Delta_{\text{Tier}} \times 0.5 \times \text{Spread}) + (\Delta_{\text{Term}} \times 0.5 \times \text{Spread})$$

* **Baseline ($P_{\min}$):** Tier 2/3 city with standard 12-month contract commitment.
* **Tier 1 City Surcharge ($\Delta_{\text{Tier}} \in \{0, 1\}$):**
  * Tier 1 (Metro): $\Delta_{\text{Tier}} = 1$ ($+50\%$ of price spread).
  * Tier 2 / 3: $\Delta_{\text{Tier}} = 0$.
* **Contract Commitment Clamping ($\Delta_{\text{Term}} \in \{0, 1\}$):**
  * Short Term ($< 12$ months): $\Delta_{\text{Term}} = 1$ ($+50\%$ of price spread).
  * Standard Term ($= 12$ months): $\Delta_{\text{Term}} = 0$.
  * Extended Term ($\ge 24$ months): $\Delta_{\text{Term}} = 0$ (locked at baseline $P_{\min}$).

---

### B. Pre-Serviceability & Atomic Quote Engine

1. **Pincode Lookup:** The user enters the installation site pincode.
2. **Feasibility Gate:**
   * `SERVICEABLE`: Fiber available $\rightarrow$ Standard Biz Fibre added.
   * `SURVEY_REQUIRED`: Complex commercial zone $\rightarrow$ Line item marked with "Survey within 24h" badge.
   * `UNAVAILABLE (Fibre)`: Instant Auto-Pivot $\rightarrow$ System offers AirFiber / 5G FWA wireless backup from catalogue.
3. **Checkout Validation Invariant:** Quotes containing any item with `serviceability_status = 'UNAVAILABLE'` cannot be accepted.
4. **Atomic Acceptance Transaction:**
   ```sql
   BEGIN;
     SELECT * FROM quotes WHERE quote_id = $1 AND status = 'READY' FOR UPDATE;
     UPDATE quotes SET status = 'ACCEPTED';
     INSERT INTO orders (order_id, quote_id, session_id, status, frozen_financial_snapshot)
     VALUES ($order_id, $quote_id, $session_id, 'AWAITING_KYC_CONSENT', $snapshot);
   COMMIT;
   ```

---

### C. Smart KYC & Dual-Track Verification Engine

```mermaid
flowchart TD
    OrderAccepted["Order Created (Status: AWAITING_KYC_CONSENT)"] --> ConsentGate["Customer Grants KYC Consent (Scope: KYC_VERIFICATION)"]
    ConsentGate --> UploadDocs["Upload GST, Udyam, Signatory ID, Address Proof"]
    UploadDocs --> TriggerVerify["Trigger Holistic Cross-Verification (/api/kyc/verify)"]
    
    TriggerVerify --> DocAudit{"Mandatory Document Checklist Complete?\n(Checks if any required cert is missing)"}
    DocAudit -- "Missing (e.g. K05 No Udyam)" --> FlagMissing["Flag: MISSING_REQUIRED_DOCUMENT\nResult: REVIEW_REQUIRED"]
    FlagMissing --> TrackB["Track B: Exception Path (REVIEW_REQUIRED)\nStatus -> UNDER_REVIEW"]
    
    DocAudit -- "Complete" --> ThreeTierOCR["Adaptive 3-Tier OCR Pipeline\n(Tier 1: Cloud Vision -> Tier 2: Tesseract -> Tier 3: Fixture Vault)"]
    ThreeTierOCR --> ExtractData["Extracted Fields (GSTIN, Names, Addresses, Dates)"]
    
    ExtractData --> AntiSub{"Did User Manually\nEdit Any Extracted Text?"}
    AntiSub -- Yes --> Corroborate{"Does Edited Text Appear in\nRaw Document OCR Text?"}
    Corroborate -- No --> FlagSub["Flag: Uncorroborated Manual Input\nResult: REVIEW_REQUIRED"]
    Corroborate -- Yes --> RunChecks
    AntiSub -- No --> RunChecks["Run Registry & Formatting Checks"]
    
    RunChecks --> GSTCheck["mock_gstin_registry Match & Status Check"]
    RunChecks --> UdyamCheck["mock_udyam_registry Cross-Verification"]
    RunChecks --> DateCheck["Document Expiry Validation (≤90 Days from 2026-07-15)"]
    
    GSTCheck & UdyamCheck & DateCheck --> Decision{"Aggregate KYC Decision"}
    
    Decision -- "All Valid" --> TrackA["Track A: Clean Path (PASS)\nStatus -> READY_FOR_FULFILMENT\nAuto-Dispatch Partner"]
    Decision -- "Planted Defect / Flagged" --> TrackB
    
    TrackB --> PartnerAction["Partner / Field Agent Reviews Evidence in /admin"]
    PartnerAction --> OverrideBtn["Partner Taps 'Assisted KYC: Verify & Override'"]
    OverrideBtn --> TrackA
```

---

### D. Persistent Tracker & Simulated Fulfilment Engine

* **Read-Only Customer View:** `GET /api/orders/{order_id}/tracker` returns live milestone progression, assigned local partner details, and expected activation SLA.
* **Strict Idempotency:** Customer polling cannot trigger state mutations.
* **Demo Simulator Control:** `POST /api/simulator/orders/{order_id}/advance` advances orders strictly through the valid database state machine:
  $$\text{READY\_FOR\_FULFILMENT} \rightarrow \text{SURVEY\_SCHEDULED} \rightarrow \text{INSTALL\_IN\_PROGRESS} \rightarrow \text{ACTIVE}$$

---

### E. Explainable Heuristic Priority Index (HPI)

$$\text{HPI Score} = S_{\text{GST}} + S_{\text{Budget}} + S_{\text{Stage}} + S_{\text{Firmographic}} \quad [\text{Range: } 0 - 100]$$

| Factor | Condition | Points | Empirical Grounding |
|---|---|---|---|
| **Active GSTIN** | Verified active GSTIN | **+35 pts** | 9.56% baseline activation vs. 2.05% without GSTIN |
| **Budget / Segment** | Spend $\ge$ ₹5,000 / Pro or Multi-site | **+25 pts** | Professional & Multi-site have $\ge$ 11% conversion |
| **Funnel Momentum** | Reached Quote Acceptance within 24h | **+20 pts** | Highest intent cohort before paperwork drop |
| **Size / Scale** | Employee count $\ge 5$ or Multi-site | **+20 pts** | Higher lifetime value and operational stability |

---

## 4. Complete Database Relational Schema

```sql
-- ============================================================================
-- 1. REFERENCE REGISTRIES (Seeded from CSV at startup)
-- ============================================================================

CREATE TABLE products (
    product_id          VARCHAR(32) PRIMARY KEY,
    name                VARCHAR(128) NOT NULL,
    category            VARCHAR(64) NOT NULL,
    target_segments     TEXT[] NOT NULL,
    available_city_tiers INT[] NOT NULL DEFAULT '{1,2}', -- Explicit array check (e.g. ARRAY[1] for P03)
    requires_gstin      BOOLEAN DEFAULT FALSE,
    min_quantity        INT DEFAULT 1,
    max_quantity        INT DEFAULT 100,
    price_min_paise     BIGINT NOT NULL,
    price_max_paise     BIGINT NOT NULL,
    setup_fee_paise     BIGINT DEFAULT 0,
    contract_months     INT DEFAULT 12,
    requires_one_of     TEXT[] DEFAULT '{}', -- Pipe-separated OR dependencies (e.g. ARRAY['P01','P02','P03'])
    incompatible_with   TEXT[] DEFAULT '{}',
    sla_install_days    INT DEFAULT 3,
    description         TEXT
);

CREATE TABLE pincode_serviceability (
    pincode             VARCHAR(10) PRIMARY KEY,
    city                VARCHAR(64) NOT NULL,
    state               VARCHAR(64) NOT NULL,
    state_code          VARCHAR(2) NOT NULL, -- e.g. '27' for Maharashtra
    city_tier           INT NOT NULL CHECK (city_tier IN (1, 2, 3)),
    fibre_feasible      BOOLEAN DEFAULT TRUE,
    fwa_feasible        BOOLEAN DEFAULT TRUE
);

CREATE TABLE mock_gstin_registry (
    gstin               VARCHAR(15) PRIMARY KEY,
    legal_name          VARCHAR(255) NOT NULL,
    trade_name          VARCHAR(255),
    registered_address  TEXT NOT NULL,
    taxpayer_status     VARCHAR(32) NOT NULL, -- Active, Suspended, Cancelled
    state_code          VARCHAR(2) NOT NULL
);

CREATE TABLE mock_udyam_registry (
    udyam_number        VARCHAR(25) PRIMARY KEY,
    enterprise_name     VARCHAR(255) NOT NULL,
    enterprise_type     VARCHAR(32) NOT NULL, -- Micro, Small, Medium
    major_activity      VARCHAR(64),
    registered_address  TEXT NOT NULL,
    registration_date   DATE NOT NULL
);

-- ============================================================================
-- 2. DISCOVERY & ADVISOR SESSIONS
-- ============================================================================

CREATE TABLE discovery_sessions (
    session_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    preferred_language  VARCHAR(8) DEFAULT 'en', -- en, hi, hinglish
    contact_phone       VARCHAR(16),
    business_name       VARCHAR(255),
    resume_token        VARCHAR(64) UNIQUE DEFAULT gen_random_uuid()::text,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE advisor_slots (
    session_id          UUID REFERENCES discovery_sessions(session_id) ON DELETE CASCADE,
    slot_name           VARCHAR(64) NOT NULL,
    slot_value          JSONB,
    slot_state          VARCHAR(16) CHECK (slot_state IN ('KNOWN', 'UNKNOWN', 'AMBIGUOUS')),
    updated_at          TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (session_id, slot_name)
);

CREATE TABLE advisor_messages (
    message_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID REFERENCES discovery_sessions(session_id) ON DELETE CASCADE,
    sender_role         VARCHAR(16) CHECK (sender_role IN ('user', 'assistant', 'system')),
    content             TEXT NOT NULL,
    extracted_metadata  JSONB DEFAULT '{}',
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. QUOTES & COMMERCIAL ORDERS
-- ============================================================================

CREATE TABLE quotes (
    quote_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID REFERENCES discovery_sessions(session_id),
    status              VARCHAR(24) CHECK (status IN ('DRAFT', 'READY', 'ACCEPTED', 'EXPIRED')) DEFAULT 'DRAFT',
    monthly_subtotal_paise BIGINT DEFAULT 0,
    monthly_cgst_paise     BIGINT DEFAULT 0,
    monthly_sgst_paise     BIGINT DEFAULT 0,
    monthly_igst_paise     BIGINT DEFAULT 0,
    monthly_total_paise    BIGINT DEFAULT 0,
    one_time_subtotal_paise BIGINT DEFAULT 0,
    one_time_cgst_paise     BIGINT DEFAULT 0,
    one_time_sgst_paise     BIGINT DEFAULT 0,
    one_time_igst_paise     BIGINT DEFAULT 0,
    one_time_total_paise    BIGINT DEFAULT 0,
    pricing_formula_ver    VARCHAR(16) DEFAULT 'v1.0-deterministic',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    expires_at          TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '48 hours')
);

CREATE TABLE quote_line_items (
    line_item_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id            UUID REFERENCES quotes(quote_id) ON DELETE CASCADE,
    product_id          VARCHAR(32) REFERENCES products(product_id),
    site_identifier     VARCHAR(64) NOT NULL,
    site_pincode        VARCHAR(10) NOT NULL,
    site_state_code     VARCHAR(2) NOT NULL, -- Evaluates Intra vs Inter-State supply
    serviceability_status VARCHAR(24) CHECK (serviceability_status IN ('SERVICEABLE', 'SURVEY_REQUIRED', 'UNAVAILABLE')),
    quantity            INT DEFAULT 1,
    contract_months     INT NOT NULL,
    unit_monthly_paise  BIGINT NOT NULL,
    unit_setup_paise    BIGINT DEFAULT 0,
    cgst_paise          BIGINT DEFAULT 0, -- 9% Intra-State (e.g. MH to MH)
    sgst_paise          BIGINT DEFAULT 0, -- 9% Intra-State
    igst_paise          BIGINT DEFAULT 0  -- 18% Inter-State (e.g. MH to KA)
);

CREATE TABLE orders (
    order_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id            UUID UNIQUE REFERENCES quotes(quote_id),
    session_id          UUID REFERENCES discovery_sessions(session_id),
    status              VARCHAR(32) CHECK (status IN (
                            'AWAITING_KYC_CONSENT', 'KYC_IN_PROGRESS', 'UNDER_REVIEW',
                            'READY_FOR_FULFILMENT', 'SURVEY_SCHEDULED', 'INSTALL_IN_PROGRESS',
                            'ACTIVE', 'ACTION_REQUIRED', 'CANCELLED'
                        )) DEFAULT 'AWAITING_KYC_CONSENT',
    frozen_financial_snapshot JSONB NOT NULL,
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE order_events (
    event_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID REFERENCES orders(order_id) ON DELETE CASCADE,
    actor_type          VARCHAR(24) CHECK (actor_type IN ('system', 'customer', 'partner', 'simulator')),
    from_status         VARCHAR(32),
    to_status           VARCHAR(32) NOT NULL,
    customer_title      VARCHAR(128) NOT NULL,
    customer_detail     TEXT,
    created_at          TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. PRIVACY, CONSENT & VERIFICATION
-- ============================================================================

CREATE TABLE consents (
    consent_id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id          UUID REFERENCES discovery_sessions(session_id),
    purpose_scope       VARCHAR(32) CHECK (purpose_scope IN (
                            'DISCOVERY_SESSION', 'KYC_VERIFICATION', 'PARTNER_CALLBACK'
                        )),
    is_active           BOOLEAN DEFAULT TRUE,
    granted_at          TIMESTAMPTZ DEFAULT NOW(),
    withdrawn_at        TIMESTAMPTZ
);

CREATE TABLE kyc_submissions (
    submission_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID UNIQUE REFERENCES orders(order_id),
    consent_id          UUID REFERENCES consents(consent_id),
    processing_state    VARCHAR(24) CHECK (processing_state IN ('AWAITING_DOCS', 'EXTRACTING', 'VALIDATING', 'COMPLETE')),
    decision            VARCHAR(24) CHECK (decision IN ('PENDING', 'PASS', 'FAIL', 'REVIEW_REQUIRED')) DEFAULT 'PENDING',
    created_at          TIMESTAMPTZ DEFAULT NOW(),
    updated_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE kyc_documents (
    document_id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id       UUID REFERENCES kyc_submissions(submission_id) ON DELETE CASCADE,
    doc_type            VARCHAR(32) NOT NULL, -- gst_certificate, udyam_certificate, signatory_id, address_proof
    file_path           VARCHAR(255) NOT NULL,
    uploaded_at         TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE kyc_check_results (
    check_id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    submission_id       UUID REFERENCES kyc_submissions(submission_id) ON DELETE CASCADE,
    check_code          VARCHAR(32) NOT NULL, -- GSTIN_FORMAT, GSTIN_ACTIVE, UDYAM_NAME_MATCH, ANTI_SUBSTITUTION, ADDR_FRESHNESS
    verdict             VARCHAR(16) CHECK (verdict IN ('MATCH', 'MISMATCH', 'FLAGGED', 'SKIPPED')),
    reason_code         VARCHAR(64), -- Explicit machine-readable reason code (e.g. GSTIN_CANCELLED, DOCS_MISSING)
    confidence_score    REAL,
    raw_evidence        JSONB,
    checked_at          TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE partner_assignments (
    assignment_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id            UUID REFERENCES orders(order_id),
    session_id          UUID REFERENCES discovery_sessions(session_id),
    partner_id          VARCHAR(64) NOT NULL,
    assignment_role     VARCHAR(32) CHECK (assignment_role IN ('LEAD_RECOVERY', 'KYC_ASSISTANT', 'INSTALL_ENGINEER')),
    resolution_status   VARCHAR(24) CHECK (resolution_status IN ('PENDING', 'ACCEPTED', 'RESOLVED_OVERRIDE', 'COMPLETED')),
    priority_score      INT DEFAULT 50,
    assigned_at         TIMESTAMPTZ DEFAULT NOW(),
    resolved_at         TIMESTAMPTZ,
    CONSTRAINT chk_order_or_session CHECK (order_id IS NOT NULL OR session_id IS NOT NULL)
);
```

---

## 5. Standardized REST API Contract (23 Endpoints)

| Category | Method | Path | Request / Query | Response Entity | Description |
|---|---|---|---|---|---|
| **Discovery** | `POST` | `/api/sessions` | `{ language?: string }` | `SessionResponse` | Initialize session, set language cookie |
| | `POST` | `/api/sessions/{id}/identify` | `{ phone: string, name?: string }` | `SessionResponse` | Link phone number for tracking/recovery |
| | `POST` | `/api/sessions/{id}/magic-link` | `{ channel: "whatsapp" \| "sms" }`| `MagicLinkResult` | Generate 1-tap CA/accountant handoff link |
| | `GET` | `/api/sessions/resume/{token}` | — | `SessionResumeResponse` | Cross-device resumption on desktop/CA browser |
| **Advisor** | `POST` | `/api/advisor/chat` | `{ session_id, message }` | `AdvisorChatResponse` | Send natural language input, get next prompt |
| | `GET` | `/api/advisor/slots/{session_id}` | — | `SlotStateResponse` | Inspect current extracted fact slots |
| | `GET` | `/api/advisor/recommendation` | `?session_id={id}` | `BundleRecommendation` | Get ranked bundles & toggleable add-ons |
| **Catalogue** | `GET` | `/api/catalogue/products` | `?segment={seg}&tier={tier}` | `Product[]` | Filter eligible products |
| | `POST` | `/api/catalogue/serviceability` | `{ pincode: string, site_id }` | `ServiceabilityReport` | Deterministic site feasibility check |
| **Quote** | `POST` | `/api/quotes` | `{ session_id, bundle_id, addons[] }`| `QuoteResponse` | Calculate deterministic unit prices & taxes |
| | `PATCH`| `/api/quotes/{id}/items` | `{ add_products[], remove_ids[] }` | `QuoteResponse` | Toggle add-ons, recalculate integer paise |
| | `GET` | `/api/quotes/{id}` | — | `QuoteDetailResponse` | Get full line-item & tax breakdown |
| | `POST` | `/api/quotes/{id}/accept` | Header: `Idempotency-Key` | `OrderCreationResponse` | Atomic price freeze; block unserviceable items |
| **Consent** | `POST` | `/api/consents` | `{ session_id, purpose_scope }` | `ConsentRecord` | Grant explicit DPDP consent |
| | `DELETE`| `/api/consents/{id}` | — | `ConsentWithdrawalResult` | Withdraw consent, set order to ACTION_REQUIRED |
| **Smart KYC**| `POST` | `/api/kyc/{order_id}/upload` | Multipart: `doc_type`, `file` | `UploadJobResponse` | Staged upload to kyc_documents child table |
| | `POST` | `/api/kyc/{order_id}/verify` | — | `KycStatusResponse` | Run holistic 3-Tier OCR & cross-document checks |
| | `GET` | `/api/kyc/{order_id}/status` | — | `KycStatusResponse` | Real-time verification report & check items |
| | `POST` | `/api/kyc/{order_id}/edit-field` | `{ field_name, edited_value }` | `KycStatusResponse` | User edits field; triggers anti-substitution check |
| **Tracker** | `GET` | `/api/orders/{id}/tracker` | — | `OrderTrackerResponse` | Read-only timeline & fulfillment status |
| | `GET` | `/api/orders/by-phone/{phone}` | — | `OrderSummary[]` | Look up past/active orders by mobile number |
| **Simulator** | `POST` | `/api/simulator/orders/{id}/advance`| `{ to_milestone: string }` | `OrderEventResponse` | Demo-only forced state machine advance |
| **Partner** | `GET` | `/api/partner/queue` | `?role={role}&status={st}` | `PartnerQueueItem[]` | View HPI-scored dropped leads & KYC reviews |
| | `POST` | `/api/partner/kyc/{order_id}/override`| `{ reason: string, notes: string }`| `KycOverrideResult` | Unblock exception order (K01-K12 demo flow) |

---

## 6. Implementation Architecture vs Hackathon Deliverables

```mermaid
gantt
    title Hackathon Build Plan (48-Hour Execution Budget)
    dateFormat  HH
    axisFormat  Day %d / %H:00
    
    section Foundation
    DB Schema & Seed Loaders (Products, Registries) :done, d1, 00, 4h
    K01-K12 Specimen Fixture Vault Setup           :done, d2, 04, 3h
    
    section Core Backend
    Deterministic Pricing Matrix & Serviceability   :active, b1, 07, 5h
    LLM Structured Output Advisor & Guardrails      :b2, 12, 8h
    Adaptive Smart KYC & Anti-Substitution Gate    :b3, 20, 8h
    Order State Machine & Simulator Advancer       :b4, 28, 4h
    
    section Mobile Frontend
    Discovery & Multilingual Advisor Chat Screen    :f1, 16, 7h
    Interactive Quote Builder & Addon Toggles       :f2, 23, 5h
    Consent Screen & Upload / Verification UI       :f3, 28, 6h
    Customer Tracker & Partner Exception Portal     :f4, 34, 6h
    
    section Verification & Polish
    15-Judge Test Scenario Dry Runs                 :v1, 40, 4h
    3-Min Video Recording & 10-Slide Deck Sync      :v2, 44, 4h
```

---

## 7. Data Privacy & DPDP Compliance Posture (Deliverable #4 Blueprint)

1. **Notice & Affirmative Consent (Section 6, DPDP Act 2023):**
   * Three distinct, unbundled consent checkboxes: (1) Discovery & Session Retention, (2) KYC Document Verification, (3) Local Partner Assistance.
   * Consent notices displayed in the user’s selected regional language.
2. **Strict Purpose Limitation & Minimisation:**
   * Financial ledger snapshots preserve strictly product SKUs, counts, and frozen monetary values—**zero customer PII**.
   * Document uploads stored in an isolated, non-public directory (`runtime/uploads/`).
3. **Data Principal Rights & Erasure Mechanics:**
   * Customers can withdraw consent directly from the web client.
   * On consent withdrawal during onboarding, document files are unlinked and wiped, OCR text buffers cleared, and the order transitions cleanly to `ACTION_REQUIRED`.
4. **Trusted Process Boundaries:**
   * External LLM requests receive only abstracted business attributes (e.g., "Retail, Tier 2, 5 devices") with all phone numbers, names, and tax IDs scrubbed prior to network transit.
