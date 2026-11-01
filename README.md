# Project Udyam Digital 🚀
### Making Small Businesses Go Digital in One Sitting (<15 Minutes)
**Airtel SYNC · Enterprise Track A Submission · Accel Telecom B2B**

---

## 🌟 Executive Summary

Project Udyam Digital is an enterprise-grade digital acquisition and onboarding platform designed for India's 6 Crore+ Micro, Small, and Medium Enterprises (MSMEs). It compresses the traditional **17.6-day sales cycle and ₹15,000 CAC** into an **instant, digital-first experience in under 15 minutes**, backed by local partner fulfillment (1–2 days for FWA/SIMs, 3–5 days for Fibre).

### 🏆 Key Technical & Architectural Innovations
1. **Hybrid GenAI Advisor (Safe by Construction):** An empathetic conversational slot extractor (supporting English, Hindi, and Hinglish) paired with a 100% deterministic eligibility and pricing matrix from `product_catalogue.csv`. Zero LLM hallucinations on pricing or product catalog.
2. **Deterministic B2B Commercial Pricing:** Explicit pricing formula based on city tier and contract tenure ($\text{Price}_{\min} + \Delta_{\text{Tier}} \times 0.5 \times \text{Spread} + \Delta_{\text{Term}} \times 0.5 \times \text{Spread}$) with tenure loyalty discounts locking at $\text{Price}_{\min}$ for $\ge$24-month terms.
3. **Statutory Place of Supply (POS) GST Engine:** Evaluates intra-state supply (Maharashtra to Maharashtra $\rightarrow$ CGST 9% + SGST 9%) vs. inter-state supply (Maharashtra to other states $\rightarrow$ IGST 18%) at the individual site level for multi-site enterprises.
4. **Upfront Pincode Serviceability & AirFiber Fallback:** Validates physical infrastructure at discovery time. If fibre is unfeasible in a sector (e.g. Kolhapur Suburban `416001`), the engine automatically falls back to **Biz 5G AirFiber 100 (P04)** for 48-hour rapid activation.
5. **Dual-Track Smart KYC with Planted Defect Detection:**
   - **Track A (Clean Path):** Auto-provisions clean applicants (e.g. Specimen K02) straight into `READY_FOR_FULFILMENT`.
   - **Track B (Exception Escrow):** Catches planted defects:
     - **K01:** Detects Cancelled GSTIN via `mock_gstin_registry.csv` $\rightarrow$ `GSTIN_CANCELLED`.
     - **K05:** Detects missing Udyam certificate $\rightarrow$ `DOCS_MISSING_UDYAM`.
     - **K11:** Detects expired utility bill (>90 days from `2026-07-15`) $\rightarrow$ `ADDRESS_PROOF_EXPIRED`.
     - **Anti-Substitution Gate:** Verifies manually edited form fields against raw OCR tokens to prevent text injection.
   - **Partner Exception Override:** Field partners can inspect physical evidence on-site and execute **"Assisted KYC: Verify & Override"**, unblocking live demos without stalls.
6. **Zero-Dependency Specimen Fixture Vault:** Pre-calibrated golden representations for applicants K01–K12 ensuring 100% offline test and demo reliability.
7. **Transparent Order Tracker & Milestone Simulator:** Real-time milestone tracker driven by dynamic catalog SLAs with an administrative simulator for live judge walkthroughs.

---

## 🛠️ Architecture & Tech Stack

- **Backend:** Python 3.11+, FastAPI (Modular Monolith), SQLAlchemy, SQLite (`udyam.db` with WAL mode & foreign keys), Pydantic v2, PyTesseract.
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide Icons.
- **Compliance:** Purpose-bound DPDP Act 2023 consent ledger with 1-click revocation.

---

## ⚡ Quickstart Guide

### 1. Backend Setup & Seeding

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run seed pipeline (seeds 25 products, 3,534 GSTINs, 2,723 Udyam records, and 3,531 pincodes)
python scripts/seed_db.py

# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```
*API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)*

---

### 2. Frontend Setup

In a new terminal window:

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Start Next.js development server
npm run dev
```
*Web application will be live at: [http://localhost:3000](http://localhost:3000)*

---

## 🧪 Running Automated Test Suite

We maintain unit test coverage across all domain logic, pricing, taxes, KYC checks, and simulator state machines:

```bash
# Run all tests
PYTHONPATH=backend backend/venv/bin/pytest backend/tests/
```

Test coverage includes:
- `test_pricing_matrix.py`: Tier spreads, short-term additions, tenure loyalty discounts, and eligibility constraints.
- `test_tax_engine.py`: Place of Supply (POS) GST distributions (MH intra-state vs. inter-state IGST).
- `test_advisor.py`: Multilingual slot extraction and upfront AirFiber P04 feasibility fallback.
- `test_kyc_engine.py`: Specimen Vault validation, K01 Cancelled GSTIN, K05 Missing Udyam, K11 Expired Bill, K02 Clean Path, and Anti-Substitution tamper gate.
- `test_partner_and_simulator.py`: HPI scoring algorithm and order milestone progression.

---

## 📱 Application Screens

1. **Conversational Advisor (`/`):** Guided natural language onboarding in English, Hindi, or Hinglish.
2. **Quote & Add-on Builder (`/quote`):** Itemized B2B line items with tax breakdown and tenure toggling.
3. **Smart KYC Hub (`/kyc`):** Purpose-bound consent, specimen testing (K01–K12), and anti-substitution corroboration.
4. **Order Tracker (`/tracker`):** Live milestone progress, catalogue-driven SLA countdown, and demo step advance simulator.
5. **Partner Desk (`/partner`):** Heuristic Priority Index (HPI) dropped lead queue and Assisted KYC Override action.

---

## 📄 Privacy & DPDP Act 2023 Compliance
All customer data collection adheres strictly to the Digital Personal Data Protection Act 2023. Explicit purpose-bound consent is mandated before document extraction, all identifiers are masked in client logs, and customers hold the statutory right to withdraw consent at any stage.
