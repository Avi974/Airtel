# 📋 Project Progress & Decisions Log

> **Last Updated**: 31 Oct 2026, 4:51 PM IST  
> **Status**: Problem statement parsed, data analyzed, architecture drafted, awaiting user confirmation on tech stack and presentation format before coding.

---

## 🎯 Current Milestone: Discovery & Architecture Review
- [x] Read & parsed case PDF: `Airtel_SYNC_Case.pdf`
- [x] Explored and analyzed synthetic dataset files:
  - `product_catalogue.csv` (25 products, constraints, dependencies, tier rules)
  - `smb_leads.csv` (5,000 leads, funnel analysis, drop-off root causes)
  - `mock_gstin_registry.csv` (3,534 records, status flags)
  - `mock_udyam_registry.csv` (2,723 records, enterprise categories)
  - `kyc_documents/` (47 sample images across 12 test applicants, planted issues identified e.g., missing K05 Udyam)
- [x] Generated high-level architecture & problem deep dive (`architecture-discussion.md`)
- [x] Created `CONTEXT.md` for rapid cross-model context handoff
- [x] Extracted clean problem statement text for external prompting/sharing
- [ ] Finalize tech stack & repo layout
- [ ] Finalize PPT structure (7 content slides + title + annexure)
- [ ] Prototype implementation (Advisor, Quote/Checkout, Smart KYC, Order Tracker, Back-office)

---

## 💡 Key Architectural Alignments
1. **Advisor Strategy**: Hybrid approach — Deterministic business logic rules engine for product eligibility & catalogue dependencies + LLM for natural language multilingual conversation (prevents pricing/catalogue hallucinations).
2. **Smart KYC Pipeline**: Document OCR extraction (Gemini Vision) + Mock registry cross-verification (Active/Suspended/Cancelled status) + 90-day address proof validity check against simulated date `2026-07-15`.
3. **DPDP Compliance**: Purpose-limited consent capture, data minimisation, masked PII display (`****-****-1234`).
4. **Field Force / Channel Integration**: Bi-directional handoff for drop-offs or complex multi-site requirements via back-office leads queue.

---

## 📝 Next Actions
1. Confirm Tech Stack (recommended: React/Next.js frontend + FastAPI Python backend, or unified Next.js + Python microservice for OCR/analytics).
2. Prepare slide outline for the 7-slide pitch deck matching template `Submission Template_Sync.pptx`.
3. Scaffold the working prototype.

