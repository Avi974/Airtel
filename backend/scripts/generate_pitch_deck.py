"""
Generates the official 8-slide submission presentation for Project Udyam Digital
using the Airtel SYNC template dimensions and branding.
"""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

TEMPLATE_PATH = Path("6ad9d4887d445_airtel_sync/Submission Template_Sync.pptx")
OUTPUT_PATH = Path("Project_Udyam_Digital_Airtel_SYNC_Submission.pptx")

# Palette
RED = RGBColor(228, 0, 0)          # Airtel / Accel Brand Red
DARK_SLATE = RGBColor(15, 23, 42)  # Primary text / dark card
WHITE = RGBColor(255, 255, 255)
MUTED = RGBColor(100, 116, 139)
CARD_BG = RGBColor(248, 250, 252)
BORDER_GRAY = RGBColor(226, 232, 240)
EMERALD = RGBColor(16, 185, 129)
AMBER = RGBColor(217, 119, 6)


def create_presentation():
    prs = Presentation(str(TEMPLATE_PATH))
    slide_width = prs.slide_width
    slide_height = prs.slide_height

    # Clear existing slides and build from scratch matching exact 16:9 dimensions
    # First slide in template has the Title background
    # We will build clean, high-impact executive slides
    
    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide1 = prs.slides[0]
    
    # Title Box
    tb = slide1.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(2.5))
    tf = tb.text_frame
    tf.word_wrap = True
    
    p = tf.paragraphs[0]
    p.text = "PROJECT UDYAM DIGITAL"
    p.font.size = Pt(36)
    p.font.bold = True
    p.font.color.rgb = RED
    
    p2 = tf.add_paragraph()
    p2.text = "Making Small Businesses Go Digital in One Sitting (<15 Minutes)"
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = DARK_SLATE
    p2.space_before = Pt(8)

    p3 = tf.add_paragraph()
    p3.text = "Accel Telecom B2B · Airtel SYNC Hackathon 2026 · Enterprise Track A"
    p3.font.size = Pt(13)
    p3.font.color.rgb = MUTED
    p3.space_before = Pt(12)

    # Remove the second template placeholder slide if present
    if len(prs.slides) > 1:
        rId = prs.slides._sldIdLst[1].rId
        prs.part.drop_rel(rId)
        del prs.slides._sldIdLst[1]

    # -------------------------------------------------------------
    # Helper to create content slide
    # -------------------------------------------------------------
    blank_layout = prs.slide_layouts[6] if len(prs.slide_layouts) > 6 else prs.slide_layouts[0]

    def add_content_slide(title_text, subtitle_text):
        slide = prs.slides.add_slide(blank_layout)
        
        # Header banner
        hb = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(8.4), Inches(1.0))
        htf = hb.text_frame
        htf.word_wrap = True
        
        hp = htf.paragraphs[0]
        hp.text = title_text.upper()
        hp.font.size = Pt(20)
        hp.font.bold = True
        hp.font.color.rgb = RED

        sp = htf.add_paragraph()
        sp.text = subtitle_text
        sp.font.size = Pt(11)
        sp.font.color.rgb = MUTED
        sp.space_before = Pt(2)
        return slide

    # -------------------------------------------------------------
    # SLIDE 2: THE MSME FUNNEL PROBLEM & CAC ECONOMICS
    # -------------------------------------------------------------
    s2 = add_content_slide(
        "1. The MSME Acquisition Funnel & Economics",
        "Analyzing 5,000 SMB leads from smb_leads.csv (Apr–Jun 2026)"
    )
    
    # 3 Stat Cards across top
    stats = [
        ("7.36%", "Current Activation Rate", "Only 368 of 5,000 leads convert; 92.6% drop off"),
        ("17.6 Days", "Average Lead-to-Live", "Lengthy manual paper cycle with 3 chasing calls"),
        ("₹15,000", "Blended CAC per Win", "Heavy sales overhead erodes year-1 customer margin"),
    ]
    for i, (metric, label, desc) in enumerate(stats):
        box = s2.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i*2.9), Inches(1.4), Inches(2.7), Inches(1.2))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = BORDER_GRAY
        
        btf = box.text_frame
        btf.word_wrap = True
        bp = btf.paragraphs[0]
        bp.text = metric
        bp.font.size = Pt(24)
        bp.font.bold = True
        bp.font.color.rgb = RED
        bp.alignment = PP_ALIGN.CENTER
        
        lp = btf.add_paragraph()
        lp.text = label
        lp.font.size = Pt(10)
        lp.font.bold = True
        lp.font.color.rgb = DARK_SLATE
        lp.alignment = PP_ALIGN.CENTER
        
        dp = btf.add_paragraph()
        dp.text = desc
        dp.font.size = Pt(8)
        dp.font.color.rgb = MUTED
        dp.alignment = PP_ALIGN.CENTER

    # Funnel insights table / narrative
    body = s2.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(8.4), Inches(2.4))
    btf = body.text_frame
    btf.word_wrap = True
    
    p = btf.paragraphs[0]
    p.text = "Steepest Drop-off Points & Root Cause Analysis:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_SLATE

    bullets = [
        ("Discovery & Quote Gap (62% Loss Pre-Quote): ", "Customers wait days for field reps to calculate quotes and check local fiber ducting. We solve this with instant Conversational Discovery and upfront Pincode Feasibility mapping."),
        ("KYC Paperwork Friction (32% Post-Quote Drop): ", "Physical collection of GSTIN and Udyam certs stalls momentum. We solve this with 3-Tier Smart KYC, OCR validation, and anti-substitution corroboration in one sitting."),
        ("Post-Sale Status Black Hole: ", "Customers average 3 anxious follow-up calls chasing activation. We eliminate anxiety with a Transparent Real-Time Tracker and catalogue-driven SLAs."),
    ]
    for bold_prefix, text in bullets:
        bp = btf.add_paragraph()
        bp.space_before = Pt(6)
        run1 = bp.add_run()
        run1.text = bold_prefix
        run1.font.bold = True
        run1.font.size = Pt(10)
        run1.font.color.rgb = RED
        run2 = bp.add_run()
        run2.text = text
        run2.font.size = Pt(10)
        run2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 3: CUSTOMER SEGMENTS & CURATED BUNDLES
    # -------------------------------------------------------------
    s3 = add_content_slide(
        "2. Prioritised Customer Segments & Curated Packs",
        "Targeting India's 6 Crore+ MSMEs with tailored, high-converting packages"
    )

    packs = [
        ("Micro Retail (55% Base)", "₹999 / mo", "Biz Fibre 100 (P01) or 5G AirFiber (P04)", "Unlimited Voice (P07) + Cloud Attendance", "UPI/POS connectivity, zero hotspot tethering"),
        ("Professional Offices (25%)", "₹1,499 / mo", "Biz Fibre 300 (P02)", "Managed Wi-Fi (P09) + Static IP (P11)", "Clinics, CA firms, agencies; cloud uptime & static IP"),
        ("Multi-Site & Mfg (20%)", "₹3,999 / mo", "Biz Fibre 1G (P03)", "Cloud Firewall (P10) + Static IP (P11)", "High-throughput branches, ERP access, B2B priority SLA"),
    ]
    for i, (seg, price, primary, addons, rationale) in enumerate(packs):
        card = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8 + i*2.9), Inches(1.5), Inches(2.7), Inches(3.6))
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = BORDER_GRAY
        
        ctf = card.text_frame
        ctf.word_wrap = True
        
        p = ctf.paragraphs[0]
        p.text = seg
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = DARK_SLATE
        
        p2 = ctf.add_paragraph()
        p2.text = price
        p2.font.size = Pt(18)
        p2.font.bold = True
        p2.font.color.rgb = RED
        p2.space_before = Pt(4)

        items = [
            ("Primary Product: ", primary),
            ("Included Add-ons: ", addons),
            ("Strategic Fit: ", rationale),
        ]
        for h, val in items:
            ip = ctf.add_paragraph()
            ip.space_before = Pt(8)
            r1 = ip.add_run()
            r1.text = h
            r1.font.bold = True
            r1.font.size = Pt(9)
            r1.font.color.rgb = RED
            r2 = ip.add_run()
            r2.text = val
            r2.font.size = Pt(9)
            r2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 4: END-TO-END SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    s4 = add_content_slide(
        "3. System Architecture & Technical Flow",
        "Safe-by-Construction Hybrid GenAI + Deterministic Telecom Engine"
    )

    arch_box = s4.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(8.4), Inches(3.8))
    atf = arch_box.text_frame
    atf.word_wrap = True

    arch_steps = [
        ("Module 1: Conversational Discovery & Feasibility", "LLM acts purely as empathetic slot extractor (EN/HI/Hinglish). Checks PIN code serviceability immediately. If fibre is unfeasible, automatically falls back to Biz 5G AirFiber 100 (P04) for 48h rapid wireless delivery."),
        ("Module 2: Deterministic Commercial Pricing & B2B Tax", "Zero price hallucinations. Formula: Price = Pmin + (Delta_Tier * 0.5 * Spread) + (Delta_Term * 0.5 * Spread). Computes Place of Supply (POS) GST (Intra MH 9%+9% vs Inter 18%) per site."),
        ("Module 3: Dual-Track Smart KYC & DPDP Consent Vault", "Purpose-bound DPDP consent check. 3-Tier OCR (Cloud -> Tesseract -> Specimen Vault). Catches planted defects (K01 Cancelled GSTIN, K05 Missing Udyam, K11 Expired Bill) and enforces Anti-Substitution gate on manual edits."),
        ("Module 4: Order Tracker & Simulated Fulfilment Engine", "Read-only idempotent customer tracker with dynamic SLAs (2d FWA vs 5d Fibre). Includes administrative demo simulator to showcase complete lifecycle progression."),
        ("Module 5: Partner Ops Queue & Assisted KYC Override", "Heuristic Priority Index (HPI 0-100) scores dropped leads. Partners execute 'Assisted KYC: Verify & Override' on-site, unblocking exception orders with auditable justification."),
    ]
    for i, (title, desc) in enumerate(arch_steps):
        p = atf.paragraphs[0] if i == 0 else atf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = f"{title}: "
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 5: DETERMINISTIC PRICING & B2B GST TAX ENGINE
    # -------------------------------------------------------------
    s5 = add_content_slide(
        "4. Deterministic Pricing & Place of Supply (POS) Tax",
        "Mathematical certainty and enterprise GST compliance for Indian businesses"
    )

    tbox = s5.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    ttf = tbox.text_frame
    ttf.word_wrap = True

    p = ttf.paragraphs[0]
    p.text = "Mathematical Pricing Matrix Formula:"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_SLATE

    p_eq = ttf.add_paragraph()
    p_eq.space_before = Pt(4)
    p_eq.text = "Unit Price (Paise) = Pmin + (Delta_Tier * 0.5 * Spread) + (Delta_Term * 0.5 * Spread)"
    p_eq.font.size = Pt(12)
    p_eq.font.bold = True
    p_eq.font.color.rgb = RED

    tax_bullets = [
        ("Tier Spread Factor (Delta_Tier): ", "Tier 1 Metros pay 50% spread; Tier 2/3 pay 0% base spread."),
        ("Tenure Commitment Factor (Delta_Term): ", "Contracts < 12 months pay 50% spread. Contracts >= 12 months pay 0%."),
        ("Tenure Loyalty Discount: ", "Contracts of 24 months or longer lock in bottom-of-band price Pmin, rewarding long-term MSME commitments."),
        ("Integer Arithmetic in Paise: ", "All computations execute in integer Paise (100 Paise = ₹1), preventing floating point rounding errors across bulk orders."),
        ("Statutory B2B GST Place of Supply (POS): ", "Accel bills out of Maharashtra (State 27). Intra-state supply (MH to MH) splits to CGST 9% + SGST 9%. Inter-state supply (MH to KA, DL, TN) applies IGST 18% evaluated on a per-site basis for multi-site companies."),
    ]
    for b_title, b_desc in tax_bullets:
        bp = ttf.add_paragraph()
        bp.space_before = Pt(6)
        r1 = bp.add_run()
        r1.text = b_title
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RED
        r2 = bp.add_run()
        r2.text = b_desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 6: DUAL-TRACK SMART KYC & PLANT DEFECT RESOLUTION
    # -------------------------------------------------------------
    s6 = add_content_slide(
        "5. Dual-Track Smart KYC & Exception Resolution",
        "Automated fast-track for clean applicants with zero-deadlock partner override"
    )

    kbox = s6.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    ktf = kbox.text_frame
    ktf.word_wrap = True

    kyc_items = [
        ("Track A — Clean Auto-Provisioning: ", "Clean applicants (e.g. Specimen K02) match mock_gstin_registry and mock_udyam_registry with fresh bills (<=90d). Automatically advances to READY_FOR_FULFILMENT in seconds."),
        ("Planted Defect 1 (K01 Cancelled GSTIN): ", "Detected via mock_gstin_registry status check. System flags check code GSTIN_ACTIVE with reason GSTIN_CANCELLED and routes to partner queue."),
        ("Planted Defect 2 (K05 Missing Udyam): ", "DocCompletenessCheck audits the 4 mandatory files. Detects missing certificate and raises DOCS_MISSING_UDYAM."),
        ("Planted Defect 3 (K11 Expired Address Proof): ", "Audits bill date (2025-10-31) against baseline reference date (2026-07-15). Detects age = 257 days (>90-day ceiling) -> ADDRESS_PROOF_EXPIRED."),
        ("Anti-Substitution Corroboration Gate: ", "If a user attempts to manually bypass an OCR failure by typing a third-party GSTIN, the system computes string similarity against the raw document image. Uncorroborated edits fail with ANTI_SUBSTITUTION_TAMPER_DETECTED."),
        ("Assisted KYC: Verify & Override: ", "Field partners inspect original trade licenses on-site and execute an auditable override (POST /api/partner/kyc/{id}/override), unblocking the order without demo stalls."),
    ]
    for i, (title, desc) in enumerate(kyc_items):
        p = ktf.paragraphs[0] if i == 0 else ktf.add_paragraph()
        p.space_before = Pt(6)
        r1 = p.add_run()
        r1.text = title
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RED
        r2 = p.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 7: CHANNEL PARTNER MODEL & HPI SCORING
    # -------------------------------------------------------------
    s7 = add_content_slide(
        "6. Local Channel Partner Integration & HPI Scoring",
        "Empowering 5,000+ local telecom partners with explainable lead prioritization"
    )

    pbox = s7.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    ptf = pbox.text_frame
    ptf.word_wrap = True

    p = ptf.paragraphs[0]
    p.text = "Explainable Heuristic Priority Index (HPI 0–100):"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = DARK_SLATE

    hpi_factors = [
        ("Active GSTIN (+35 pts): ", "Empirical evidence from smb_leads shows verified GSTIN leads convert at 9.56% vs 2.05% for unregistered leads."),
        ("Budget & Segment (+25 pts): ", "Monthly telecom spend >= ₹5,000 or Professional/Multi-site segment converts at >= 11%."),
        ("Funnel Momentum (+20 pts): ", "Leads reaching Quote Accepted within 24 hours exhibit highest intent."),
        ("Firmographic Scale (+20 pts): ", "Businesses with >= 5 employees or multiple sites exhibit 4x higher LTV and lower churn."),
        ("Local Partner Value Shift: ", "Channel partners shift from low-converting cold calling to high-margin managed onboarding, site surveys, and fiber CPE deployment, receiving automated dispatches with guaranteed SLAs."),
    ]
    for title, desc in hpi_factors:
        bp = ptf.add_paragraph()
        bp.space_before = Pt(6)
        r1 = bp.add_run()
        r1.text = title
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RED
        r2 = bp.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_SLATE

    # -------------------------------------------------------------
    # SLIDE 8: ROLLOUT ROADMAP & PROJECTED IMPACT
    # -------------------------------------------------------------
    s8 = add_content_slide(
        "7. Rollout Plan, Business Impact & Risk Matrix",
        "Scaling from Tier 1 pilot to national MSME coverage"
    )

    rbox = s8.shapes.add_textbox(Inches(0.8), Inches(1.5), Inches(8.4), Inches(3.6))
    rtf = rbox.text_frame
    rtf.word_wrap = True

    roadmap_items = [
        ("Phase 1: Tier 1 Metro Pilot (Months 1–3): ", "Launch in Mumbai, Bengaluru, Delhi NCR targeting Professional Offices and Retail chains with AirFiber 100 & Fibre 300."),
        ("Phase 2: Tier 2 State Capital Expansion (Months 4–6): ", "Roll out to 25 Tier 2 cities with localized partner networks and vernacular onboarding."),
        ("Phase 3: National Scale & Auto-Fulfillment (Months 7–12): ", "Deploy full self-service portal across 6 Crore MSMEs with seamless bank e-mandates."),
        ("Target Financial Impact: ", "CAC reduced from ₹15,000 to ₹4,800 (-68%); Conversion rate raised from 7.36% to 24.5% (+3.3x); Activation cycle compressed from 17.6 days to 2–4 days."),
        ("Risk Governance & Mitigation: ", "DPDP Act compliance guaranteed via purpose-bound consent and 90-day auto-erasure; local fiber feasibility gaps solved via instant 5G AirFiber fallback."),
    ]
    for title, desc in roadmap_items:
        bp = rtf.paragraphs[0] if title == roadmap_items[0][0] else rtf.add_paragraph()
        bp.space_before = Pt(6)
        r1 = bp.add_run()
        r1.text = title
        r1.font.bold = True
        r1.font.size = Pt(10)
        r1.font.color.rgb = RED
        r2 = bp.add_run()
        r2.text = desc
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = DARK_SLATE

    # Save presentation
    prs.save(str(OUTPUT_PATH))
    print(f"[✔] Presentation successfully generated at: {OUTPUT_PATH}")


if __name__ == "__main__":
    create_presentation()
