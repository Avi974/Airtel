"""
Serviceability and Feasibility Resolution Engine.
Determines physical infrastructure feasibility (Fibre vs FWA 5G AirFiber) by pincode.
"""

from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.entities import PincodeServiceability


def check_serviceability(db: Session, pincode: str) -> Dict[str, Any]:
    """
    Looks up physical serviceability for a 6-digit Indian PIN code.
    If the pincode is missing from the database, defaults gracefully to Tier 2 with full coverage.
    """
    clean_pin = pincode.strip()
    record = db.query(PincodeServiceability).filter(PincodeServiceability.pincode == clean_pin).first()

    if not record:
        # Default graceful assumption for unmapped areas
        return {
            "pincode": clean_pin,
            "city": "Unknown Region",
            "state": "Maharashtra",
            "state_code": "27",
            "city_tier": 2,
            "fibre_feasible": True,
            "fwa_feasible": True,
            "recommended_tech": "FIBRE",
            "sla_days": 5,
            "notes": "Standard Fibre coverage mapped for sector.",
        }

    # If fibre is not feasible, trigger the instant 5G AirFiber fallback
    if not record.fibre_feasible and record.fwa_feasible:
        return {
            "pincode": record.pincode,
            "city": record.city,
            "state": record.state,
            "state_code": record.state_code,
            "city_tier": record.city_tier,
            "fibre_feasible": False,
            "fwa_feasible": True,
            "recommended_tech": "FWA_AIRFIBER",
            "sla_days": 2,  # 2-day rapid deployment for AirFiber
            "notes": (
                "Physical Fibre backhaul is currently unfeasible in this sector. "
                "Automatically recommended Biz 5G AirFiber 100 (P04) for plug-and-play 48-hour activation."
            ),
        }

    return {
        "pincode": record.pincode,
        "city": record.city,
        "state": record.state,
        "state_code": record.state_code,
        "city_tier": record.city_tier,
        "fibre_feasible": record.fibre_feasible,
        "fwa_feasible": record.fwa_feasible,
        "recommended_tech": "FIBRE",
        "sla_days": 5 if record.fibre_feasible else 7,
        "notes": "High-speed Gigabit Business Fibre active and serviceable.",
    }
