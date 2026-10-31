"""
B2B GST Place of Supply (POS) Tax Engine.
Evaluates Intra-State (CGST 9% + SGST 9%) vs Inter-State (IGST 18%) based on site location.
"""

from typing import Tuple, Dict
from app.core.config import settings


def calculate_tax_breakdown_paise(
    amount_paise: int,
    site_state_code: str,
    operator_state_code: str = settings.OPERATOR_STATE_CODE,
) -> Dict[str, int]:
    """
    Computes statutory GST split in integer Paise.
    
    If site_state_code == operator_state_code (Intra-State, e.g. MH to MH):
        CGST = 9%
        SGST = 9%
        IGST = 0
    Else (Inter-State, e.g. MH to KA, DL, TN):
        CGST = 0
        SGST = 0
        IGST = 18%
    """
    if amount_paise <= 0:
        return {"cgst_paise": 0, "sgst_paise": 0, "igst_paise": 0, "total_paise": 0}

    is_intra_state = str(site_state_code).strip() == str(operator_state_code).strip()

    if is_intra_state:
        cgst = int(round(amount_paise * 0.09))
        sgst = int(round(amount_paise * 0.09))
        igst = 0
    else:
        cgst = 0
        sgst = 0
        igst = int(round(amount_paise * 0.18))

    total = amount_paise + cgst + sgst + igst
    return {
        "cgst_paise": cgst,
        "sgst_paise": sgst,
        "igst_paise": igst,
        "total_paise": total,
    }
