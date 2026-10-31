"""
Core configuration and runtime settings for Project Udyam Digital.
"""

from pathlib import Path
from pydantic import BaseModel
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "YTL_TrackA_Udyam_Digital_Data"
RUNTIME_DIR = BASE_DIR / "runtime"
UPLOAD_DIR = RUNTIME_DIR / "uploads"

# Ensure runtime directories exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    PROJECT_NAME: str = "Project Udyam Digital"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/udyam.db")
    DATA_PATH: Path = DATA_DIR
    KYC_DOCS_PATH: Path = DATA_DIR / "kyc_documents"
    UPLOAD_PATH: Path = UPLOAD_DIR
    
    # Domain specifics
    OPERATOR_STATE_CODE: str = "27"  # Maharashtra (Accel Business HQ)
    OPERATOR_STATE_NAME: str = "Maharashtra"
    REFERENCE_DATE: str = "2026-07-15"  # Fixed baseline audit date for hackathon
    ADDRESS_PROOF_MAX_AGE_DAYS: int = 90
    
    # OCR & LLM config
    TESSERACT_CMD: str = os.getenv("TESSERACT_CMD", "/usr/local/bin/tesseract")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")


settings = Settings()
