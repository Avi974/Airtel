# 🧠 PROJECT CONTEXT — Read This First

> **Last updated**: 31 Oct 2026, 4:42 PM IST
> **If you're a new model/session**: Read this file + PROGRESS.md to get full context.

---

## What Are We Building? (Plain English)

We're building a **digital onboarding app for small businesses** (like kirana stores, clinics, salons) to buy telecom + IT bundles (internet, business phone, CCTV, email, etc.) from a fictional telecom company called **Accel Business**.

**Today's problem**: A salesperson visits the shop → takes days to send a quote → owner doesn't understand the quote → collects documents physically → takes 2+ weeks to activate. Result: only 7 out of 100 leads actually become customers.

**Our solution**: An app on the owner's phone where:
1. An **AI chatbot** (in Hindi/regional language) asks 3-4 questions about the business and recommends the right bundle
2. The owner sees a **clear price** and can toggle add-ons
3. **KYC happens instantly** — upload GST certificate, the system reads it automatically (OCR), validates it against a registry, done
4. An **order tracker** shows status so the owner never needs to call support

**Think of it as**: Jio's online recharge experience, but for business services (internet + phone + CCTV + email as one bundle).

---

## The Hackathon

- **Event**: YTL Hackathon 2026 (Airtel SYNC)
- **Track**: Enterprise Track A — "Project Udyam Digital"
- **Fictional company**: Accel Telecom / Accel Business
- **Deadline**: 7th November 2026, 11:59 PM
- **Submission**: 7-slide PPT (excluding intro) + working prototype (3-min demo video + code repo) + solution architecture + 1-page privacy note
- **Max file size**: 20 MB

---

## Key Files Location

```
/Users/abhikanand/Downloads/Airtel Haacathon/
├── CONTEXT.md                          ← YOU ARE HERE
├── PROGRESS.md                         ← Current status & decisions
├── 6ad9d4887d445_airtel_sync/
│   ├── Airtel_SYNC_Case.pdf            ← Problem statement (6 pages)
│   └── Submission Template_Sync.pptx   ← PPT template
└── YTL_TrackA_Udyam_Digital_Data/
    ├── README.md                       ← Column definitions, rules, notes
    ├── product_catalogue.csv           ← 25 products (the "menu")
    ├── smb_leads.csv                   ← 5,000 leads with funnel data
    ├── mock_gstin_registry.csv         ← 3,534 GSTIN records for mock API
    ├── mock_udyam_registry.csv         ← 2,723 Udyam records for mock API
    └── kyc_documents/                  ← 47 PNG images, 12 applicants (K01-K12)
```

---

## Data Summary

### Product Catalogue (25 products across 5 categories)
- **Connectivity** (11): Fibre broadband, 5G AirFiber, leased lines, mobile postpaid, failover, SD-WAN, static IP
- **Communication** (4): Cloud telephony, toll-free, SMS packs, WhatsApp Business API
- **Cloud & Productivity** (4): Email suite, cloud backup, website builder, cloud POS
- **Security** (3): Endpoint security, managed firewall, secure Wi-Fi
- **IoT & Physical** (3): Cloud CCTV, machine monitoring, fleet tracker

**Important rules**:
- 10 products require GSTIN (P03, P05, P06, P10, P12, P13, P14, P15, P21, P24)
- 7 products have dependencies (e.g., CCTV needs broadband, firewall needs broadband)
- Products have city tier restrictions, min employee/site requirements
- Prices are ranges (min-max), not fixed

### SMB Leads (5,000 leads)
- **Segments**: Micro retail 54%, Professional offices 25%, Multi-site 15%, Manufacturers 6%
- **Funnel**: 5,000 → 3,406 contacted → 1,974 needs assessed → 861 quote accepted → 588 KYC done → 368 activated (7.4%)
- **Avg activation time**: 17.6 days
- **Avg acquisition cost**: ₹15,000
- **Languages**: Hindi (43%), English (23%), Marathi (10%), Kannada (5%), Gujarati/Telugu/Tamil (~4% each)
- **GSTIN insight**: 9.6% activation with GSTIN vs 2.0% without — GSTIN is a huge qualifier

### GSTIN Registry (3,534 records)
- 3,266 Active, 101 Suspended, 167 Cancelled
- Must reject Suspended/Cancelled during KYC
- GSTINs have valid 15-char format but PAN char 4 = 'X' (fictional marker)

### Udyam Registry (2,723 records)
- 1,833 Micro, 737 Small, 153 Medium enterprises
- District code '00' (fictional marker)

### KYC Documents (47 images, 12 applicants)
- 4 doc types: GST certificate, Udyam certificate, signatory ID, address proof
- **Planted errors to catch**:
  - K05 is MISSING the Udyam certificate entirely (only 3 docs)
  - Some GSTIN records are Suspended/Cancelled
  - Address proof freshness check: must be ≤90 days old (use 2026-07-15 as "today")
  - Possible name mismatches between documents

---

## Top Drop Reasons & What We Fix

| Rank | Drop Reason | Count | Our Fix |
|------|------------|-------|---------|
| 1 | Unreachable after 3 attempts | 805 | Self-serve — no outbound call needed |
| 2 | Owner had no time for visit | 531 | No visit — do it on phone |
| 3 | Not interested on first call | 470 | Better targeting via propensity scoring |
| 4 | Price too high | 414 | Right-sized bundles, transparent pricing |
| 5 | Wrong/invalid number | 319 | Self-serve eliminates this |
| 6 | Visit not scheduled by sales | 296 | No visit needed |
| 7 | Only wanted a mobile plan | 280 | Start small, upsell later |
| 8 | Competitor cheaper | 207 | Instant quotes beat slow process |
| 9 | Quote too complex | 206 | Plain-language AI explanation |
| 10 | Quote took too long | 179 | Instant generation |

**Key insight**: ~62% of all drops are eliminated just by going digital (no calls, no visits, no waiting).

---

## Architecture Overview

```
User (Phone) → AI Advisor (GenAI chatbot, multilingual)
                    ↓
              Bundle Recommendation (rule-based engine + LLM explanation)
                    ↓
              Quote & Checkout (transparent pricing, toggleable add-ons)
                    ↓
              Smart KYC (OCR via Gemini Vision + GSTIN/Udyam lookup + DPDP consent)
                    ↓
              Order Tracker (real-time status, no need to call)
                    ↓
              Back-Office Dashboard (for field force — leads advisor couldn't close + propensity scores)
```

### Tech Stack (PENDING DECISION — see PROGRESS.md)

### Bundle Recommendation Approach
**Hybrid** (RECOMMENDED): LLM handles the conversation and language. But actual product selection and pricing comes from a deterministic function that checks:
- City tier eligibility
- Employee/site minimums
- GSTIN requirements
- Product dependencies
- Price calculation from catalogue

This prevents the AI from hallucinating prices or recommending ineligible products.

---

## What Judges Will Test
(from the case PDF — judges have a separate pack with):
- 15 advisor test scenarios to run live during demos
- KYC answer key (what errors to catch)
- Signals planted in the leads data
- Scripts that regenerate the data

---

## DPDP Act Compliance (Must address in 1-page note)
- Explicit consent before KYC doc collection
- Purpose limitation — docs only for verification
- Data minimisation — only collect what's needed for the specific bundle
- Masking — GSTIN/Aadhaar show last 4 chars only in UI and logs
- Retention — delete docs after verification + 90-day compliance window
- Right to erasure — customer can request deletion

