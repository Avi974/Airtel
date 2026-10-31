"""
Conversational Dialogue Orchestrator and Empathy Engine.
Guides the MSME owner smoothly through discovery in under 2 minutes.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from app.models.entities import DiscoverySession, AdvisorMessage
from app.models.schemas import AdvisorChatResponse
from app.advisor.slots import (
    extract_slots_from_text,
    update_session_slots,
    CORE_REQUIRED_SLOTS,
)
from app.advisor.bundles import get_bundle_recommendation


def process_advisor_turn(
    db: Session,
    session_id: str,
    user_message: str,
) -> AdvisorChatResponse:
    """
    Processes a single conversational turn with an MSME customer.
    Extracts business slots, manages dialogue progression, and determines quote readiness.
    """
    sess = db.query(DiscoverySession).filter(DiscoverySession.session_id == session_id).first()
    if not sess:
        sess = DiscoverySession(session_id=session_id)
        db.add(sess)
        db.commit()

    # 1. Log incoming customer message
    user_msg_entry = AdvisorMessage(
        session_id=session_id,
        sender_role="user",
        content=user_message,
    )
    db.add(user_msg_entry)
    db.flush()

    # 2. Extract and persist slots
    new_extracted = extract_slots_from_text(user_message)
    known_slots = update_session_slots(db, session_id, new_extracted)

    # 3. Determine missing critical slots
    missing_slots = [slot for slot in CORE_REQUIRED_SLOTS if slot not in known_slots]
    lang = sess.preferred_language or "en"

    # 4. Craft conversational response
    if missing_slots:
        is_ready = False
        bundle_id = None
        missing = missing_slots[0]

        if lang == "hi":
            if missing == "segment":
                reply = "नमस्ते! आपके व्यवसाय का क्या प्रकार है? (जैसे: क्लिनिक, दुकान/रिटेल, कंसल्टिंग ऑफिस, या कारखाना?)"
            elif missing == "employee_count":
                reply = "धन्यवाद! आपके कार्यालय या दुकान में कितने कर्मचारी या टीम सदस्य काम करते हैं?"
            elif missing == "pincode":
                reply = "शानदार! कृपया अपने कार्यस्थल का 6-अंकों का पिनकोड (PIN code) बताएं ताकि हम कनेक्टिविटी की जांच कर सकें।"
            else:
                reply = "कृपया अपने व्यवसाय के बारे में कुछ और बताएं ताकि हम सटीक प्लान बना सकें।"
        elif lang == "hinglish":
            if missing == "segment":
                reply = "Hello! Aapka business kis category mein hai? (e.g., Clinic, Retail Store, CA/Consulting Office, ya Factory?)"
            elif missing == "employee_count":
                reply = "Great! Aapke office ya shop mein total kitne log (employees/team) kaam karte hain?"
            elif missing == "pincode":
                reply = "Perfect! Apne site ka 6-digit PIN code batayein taaki hum instant network speed aur feasibility check kar sakein."
            else:
                reply = "Aapka requirement note ho gaya hai. Ek aur details bata dein."
        else:  # English
            if missing == "segment":
                reply = "Welcome to Accel Digital! What type of business do you operate? (e.g. Retail Store, Healthcare Clinic, Professional Services office, or Manufacturing?)"
            elif missing == "employee_count":
                reply = "Got it! How many employees or workstations need connectivity at this location?"
            elif missing == "pincode":
                reply = "Understood. Could you share your 6-digit installation PIN code so we can check immediate network feasibility?"
            else:
                reply = "Could you tell us a bit more about your daily internet and communication requirements?"

    else:
        # All required slots are known -> Ready for instant quote!
        is_ready = True
        rec = get_bundle_recommendation(db, known_slots)
        bundle_id = rec.bundle_id
        b_name = known_slots.get("business_name") or sess.business_name or "your business"

        if lang == "hi":
            reply = (
                f"बहुत बढ़िया! हमने {b_name} के लिए पिनकोड {known_slots['pincode']} पर "
                f"सर्वश्रेष्ठ '{rec.title}' तैयार किया है। {rec.feasibility_notes} "
                f"आपका अनुमानित मासिक शुल्क केवल ₹{rec.estimated_monthly_inr:,.0f} + GST होगा।"
            )
        elif lang == "hinglish":
            reply = (
                f"Superb! Humne {b_name} ke liye PIN {known_slots['pincode']} par "
                f"tailored '{rec.title}' recommend kiya hai. {rec.feasibility_notes} "
                f"Monthly price: around ₹{rec.estimated_monthly_inr:,.0f} + GST. Aap abhi 1-click mein quote view kar sakte hain!"
            )
        else:
            reply = (
                f"Excellent! We have mapped the ideal solution for {b_name} at pincode {known_slots['pincode']}: "
                f"'{rec.title}'. {rec.feasibility_notes} "
                f"Estimated monthly price is ₹{rec.estimated_monthly_inr:,.0f} + GST. Click below to inspect your instant commercial quote!"
            )

    # 5. Log assistant response
    asst_msg_entry = AdvisorMessage(
        session_id=session_id,
        sender_role="assistant",
        content=reply,
        extracted_metadata={"known_slots": known_slots, "missing_slots": missing_slots},
    )
    db.add(asst_msg_entry)
    db.commit()

    return AdvisorChatResponse(
        session_id=session_id,
        reply=reply,
        known_slots=known_slots,
        missing_slots=missing_slots,
        is_ready_for_quote=is_ready,
        recommended_bundle_id=bundle_id,
    )
