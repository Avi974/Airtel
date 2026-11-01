# Project Udyam Digital — Statutory Privacy & Data Protection Note
### Compliance Architecture under India's Digital Personal Data Protection (DPDP) Act, 2023
**Accel Telecom B2B · Airtel SYNC Enterprise Track A Submission**

---

## 1. Executive Privacy Posture

Project Udyam Digital treats micro and small business onboarding data with tier-1 enterprise data governance. Because Indian MSMEs frequently intermingle proprietary firmographic credentials (GSTIN, Udyam Registration, Electricity bills) with personal data of individual proprietors and designated partners (PAN, Aadhaar, mobile numbers), our platform enforces strict **Data Fiduciary** obligations under the **Digital Personal Data Protection (DPDP) Act, 2023**.

---

## 2. Core Architectural Privacy Principles

### A. Principle of Purpose Limitation & Specificity (Section 6)
* Data collection is strictly scoped to statutory telecom customer verification (DoT KYC guidelines) and statutory B2B Place of Supply (POS) GST billing.
* Consent is collected via explicit, affirmative action (`POST /api/consents`) with granular purpose scoping (`DISCOVERY_SESSION`, `KYC_VERIFICATION`, `PARTNER_CALLBACK`).
* No consent bundling: Customers can explore product recommendations and generate commercial quotes without surrendering national identity documents.

### B. Statutory Right to Withdraw Consent & Immediate Erasure (Section 12)
* Under the DPDP Act 2023, data principals hold the absolute right to withdraw consent at any stage prior to order freeze.
* Calling `DELETE /api/consents/{id}` immediately halts document processing, transitions the active order to `ACTION_REQUIRED`, flags uploaded artifacts for automated cryptographic erasure, and logs an immutable audit event in `order_events`.

### C. Data Minimisation & Proportionality (Section 6(2))
* We collect only the minimum document tokens required to establish physical serviceability and tax legality:
  - **Signatory ID:** Validates applicant authority; only PAN and masked identifier tokens are retained.
  - **GSTIN & Udyam:** Cross-referenced directly against reference registries (`mock_gstin_registry`, `mock_udyam_registry`) without scraping extraneous taxpayer history.
  - **Address Proof:** Bounded by a strict **90-day freshness rule** against the reference baseline date (`2026-07-15`). Older bills are rejected upfront, avoiding unnecessary storage of obsolete utility history.

---

## 3. Cryptographic Storage & Lifecycle Governance

```
+-----------------------------------------------------------------------------------+
|                           DATA RETENTION & ERASURE LIFECYCLE                      |
+-----------------------------------------------------------------------------------+
| Stage 1: Ingestion        | TLS 1.3 in-transit encryption. Staged in ephemeral    |
|                           | scratch storage (/runtime/uploads).                   |
+---------------------------+-------------------------------------------------------+
| Stage 2: Verification     | 3-Tier OCR extracts structured text; identity masking |
|                           | is applied immediately (Aadhaar/PAN redaction).       |
+---------------------------+-------------------------------------------------------+
| Stage 3: Activation       | Active orders retain only the frozen JSON snapshot     |
|                           | (frozen_financial_snapshot) and verified hash tokens. |
+---------------------------+-------------------------------------------------------+
| Stage 4: Retention Ceiling| All raw document images are scheduled for unrecover-  |
|                           | able cryptographic wipe 90 days post-activation.      |
+-----------------------------------------------------------------------------------+
```

1. **Storage Encryption:** All persistent relational records in `udyam.db` and staged image artifacts in `runtime/uploads/` utilize AES-256 equivalent filesystem encryption.
2. **Access Control & Least Privilege:**
   - Field partners accessing `/api/partner/queue` and the Assisted KYC desk view only the flagged check reason code and masked business summaries.
   - Field engineers assigned for physical fiber installation (`INSTALL_ENGINEER`) receive only site dispatch coordinates, contact name, and installation SLA—zero access to financial tax returns or identity documents.

---

## 4. Anti-Substitution & Tamper Mitigation

To prevent fraudulent identity substitution (where a user attempts to bypass a failed or mismatched OCR check by manually typing legitimate credentials belonging to another entity):
* Any manual edit to extracted fields (`POST /api/kyc/{order_id}/edit-field`) triggers the **Anti-Substitution Corroboration Gate**.
* The system computes a fuzzy token distance between the user's manual text and the raw OCR evidence extracted from the uploaded document image.
* Uncorroborated edits fail the automated audit with reason code `ANTI_SUBSTITUTION_TAMPER_DETECTED`, preventing unauthorized privilege escalation and routing the case directly to field verification.

---

## 5. Summary Table: DPDP Act 2023 Compliance Checklist

| Statutory Requirement | DPDP Act Section | Project Udyam Digital Implementation |
|---|---|---|
| **Notice & Multilingual Consent** | Section 5 & 6 | Clear, multilingual consent notice presented in English, Hindi, and Hinglish prior to document upload. |
| **Purpose Limitation** | Section 6(1) | Scoped strictly to DoT KYC verification and GST billing; zero third-party data monetization. |
| **Right to Correction & Erasure** | Section 12 | 1-click consent revocation with instant state freeze and unrecoverable image deletion. |
| **Reasonable Security Safeguards** | Section 8(5) | Role-Based Access Control (RBAC), TLS 1.3, AES-256 storage, and strict anti-tampering corroboration. |
| **Grievance Redressal Mechanism** | Section 13 | Partner Operations Queue with auditable review trails and field escalation desks. |
