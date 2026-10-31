"""
Database seed pipeline for Project Udyam Digital.
Loads products, mock registries, and serviceability records into the database.
"""

import csv
import re
from datetime import datetime
from pathlib import Path
import sys

# Ensure backend root is on sys.path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.config import settings
from app.core.database import engine, SessionLocal, Base
from app.models.entities import (
    Product,
    MockGstinRegistry,
    MockUdyamRegistry,
    PincodeServiceability,
    DiscoverySession,
    AdvisorSlot,
)


# Known Tier-1 Indian Cities
TIER_1_CITIES = {
    "mumbai", "delhi", "new delhi", "bengaluru", "bangalore",
    "chennai", "hyderabad", "kolkata", "pune", "ahmedabad"
}

# Indian State to 2-digit GST State Code mapping
STATE_NAME_TO_CODE = {
    "jammu and kashmir": "01",
    "himachal pradesh": "02",
    "punjab": "03",
    "chandigarh": "04",
    "uttarakhand": "05",
    "haryana": "06",
    "delhi": "07",
    "rajasthan": "08",
    "uttar pradesh": "09",
    "bihar": "10",
    "sikkim": "11",
    "arunachal pradesh": "12",
    "nagaland": "13",
    "manipur": "14",
    "mizoram": "15",
    "tripura": "16",
    "meghalaya": "17",
    "assam": "18",
    "west bengal": "19",
    "jharkhand": "20",
    "odisha": "21",
    "chhattisgarh": "22",
    "madhya pradesh": "23",
    "gujarat": "24",
    "daman and diu": "25",
    "dadra and nagar haveli": "26",
    "maharashtra": "27",
    "andhra pradesh": "37",
    "karnataka": "29",
    "goa": "30",
    "lakshadweep": "31",
    "kerala": "32",
    "tamil nadu": "33",
    "puducherry": "34",
    "andaman and nicobar islands": "35",
    "telangana": "36",
    "ladakh": "38",
}


def seed_products(session, catalogue_path: Path):
    print(f"[*] Seeding Products from {catalogue_path}...")
    with open(catalogue_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            tiers = [int(t.strip()) for t in row["available_city_tiers"].split(";") if t.strip()]
            req_one_of = [p.strip() for p in (row.get("requires_one_of") or "").split("|") if p.strip()]
            segments = [s.strip() for s in (row.get("target_segments") or "").split(";") if s.strip()]
            
            p = Product(
                product_id=row["product_id"].strip(),
                name=row["product_name"].strip(),
                category=row["category"].strip(),
                target_segments=segments,
                available_city_tiers=tiers,
                requires_gstin=row["requires_gstin"].strip().upper() == "Y",
                min_quantity=int(row.get("min_employees") or 1),
                max_quantity=100,
                price_min_paise=int(row["price_min_inr_per_month"]) * 100,
                price_max_paise=int(row["price_max_inr_per_month"]) * 100,
                setup_fee_paise=int(row["one_time_setup_inr"]) * 100,
                contract_months=int(row["min_contract_months"]),
                requires_one_of=req_one_of,
                incompatible_with=[],
                sla_install_days=int(row["typical_install_days"]),
                description=row["description"].strip(),
            )
            session.merge(p)
            count += 1
        session.commit()
        print(f"[+] Successfully seeded {count} products.")


def seed_gstin_registry(session, gstin_path: Path):
    print(f"[*] Seeding Mock GSTIN Registry from {gstin_path}...")
    with open(gstin_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        pincode_map = {}
        for row in reader:
            gstin = row["gstin"].strip()
            state_code = gstin[:2]
            address = row["principal_place_of_business"].strip()
            state = row["state"].strip()
            
            # Extract 6-digit Indian PIN code from address
            pin_match = re.search(r"-\s*(\d{6})", address)
            if pin_match:
                pincode = pin_match.group(1)
                # Extract city: token before state or 3rd token from end
                parts = [p.strip() for p in address.split(",")]
                city = "City"
                if len(parts) >= 3:
                    city = parts[-2].split("-")[0].strip()
                
                tier = 1 if city.lower() in TIER_1_CITIES else 2
                if pincode not in pincode_map:
                    pincode_map[pincode] = (city, state, state_code, tier)

            rec = MockGstinRegistry(
                gstin=gstin,
                legal_name=row["legal_name"].strip(),
                trade_name=row.get("trade_name", "").strip() or None,
                registered_address=address,
                taxpayer_status=row["status"].strip(),
                state_code=state_code,
            )
            session.merge(rec)
            count += 1
            if count % 1000 == 0:
                session.commit()
                print(f"    Loaded {count} GSTINs...")

        session.commit()
        print(f"[+] Successfully seeded {count} GSTIN records.")
        return pincode_map


def seed_udyam_registry(session, udyam_path: Path):
    print(f"[*] Seeding Mock Udyam Registry from {udyam_path}...")
    with open(udyam_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        count = 0
        for row in reader:
            reg_date_str = row["date_of_registration"].strip()
            try:
                reg_date = datetime.strptime(reg_date_str, "%Y-%m-%d").date()
            except ValueError:
                reg_date = datetime(2022, 1, 1).date()

            rec = MockUdyamRegistry(
                udyam_number=row["udyam_number"].strip(),
                enterprise_name=row["enterprise_name"].strip(),
                enterprise_type=row["enterprise_type"].strip(),
                major_activity=row.get("major_activity", "").strip() or None,
                registered_address=f"{row.get('city', '')}, {row.get('state', '')}",
                registration_date=reg_date,
            )
            session.merge(rec)
            count += 1
            if count % 1000 == 0:
                session.commit()
                print(f"    Loaded {count} Udyam records...")

        session.commit()
        print(f"[+] Successfully seeded {count} Udyam records.")


def seed_pincodes(session, extracted_pincodes: dict):
    print("[*] Seeding Pincode Serviceability table...")
    count = 0
    # Add extracted pincodes
    for pincode, (city, state, state_code, tier) in extracted_pincodes.items():
        # Set 15% of pincodes to fibre_feasible=False, fwa_feasible=True to test AirFiber P04 fallback
        is_fibre_feasible = not (pincode.endswith("7") or pincode.endswith("9"))
        ps = PincodeServiceability(
            pincode=pincode,
            city=city,
            state=state,
            state_code=state_code,
            city_tier=tier,
            fibre_feasible=is_fibre_feasible,
            fwa_feasible=True,
        )
        session.merge(ps)
        count += 1

    # Standard Specimen Test Pincodes
    specimen_pincodes = [
        # Mumbai (Tier 1, MH) - Fully Fibre and FWA feasible
        ("400001", "Mumbai", "Maharashtra", "27", 1, True, True),
        ("400050", "Mumbai", "Maharashtra", "27", 1, True, True),
        # Bengaluru (Tier 1, KA) - Fully feasible
        ("560001", "Bengaluru", "Karnataka", "29", 1, True, True),
        ("560100", "Bengaluru", "Karnataka", "29", 1, True, True),
        # Delhi (Tier 1, DL) - Fully feasible
        ("110001", "Delhi", "Delhi", "07", 1, True, True),
        # Pune (Tier 1, MH)
        ("411001", "Pune", "Maharashtra", "27", 1, True, True),
        # Remote/Suburban Pincode - FIBRE DOWN, FWA AIRFIBER ONLY (For P04 Demo!)
        ("416001", "Kolhapur Suburban", "Maharashtra", "27", 2, False, True),
        ("580001", "Hubli Outskirts", "Karnataka", "29", 2, False, True),
        ("600001", "Chennai", "Tamil Nadu", "33", 1, True, True),
        ("500001", "Hyderabad", "Telangana", "36", 1, True, True),
    ]

    for pin, city, state, scode, tier, fibre, fwa in specimen_pincodes:
        ps = PincodeServiceability(
            pincode=pin,
            city=city,
            state=state,
            state_code=scode,
            city_tier=tier,
            fibre_feasible=fibre,
            fwa_feasible=fwa,
        )
        session.merge(ps)
        count += 1

    session.commit()
    print(f"[+] Successfully seeded {count} pincode serviceability records.")


def main():
    print("=================================================================")
    print(" Project Udyam Digital — Database Seeding Pipeline (V5.2)")
    print("=================================================================")
    
    # 1. Create tables
    print("[*] Creating database schema tables...")
    Base.metadata.create_all(bind=engine)
    print("[+] Database schema verified.")

    db = SessionLocal()
    try:
        # 2. Seed catalogue
        catalogue_csv = settings.DATA_PATH / "product_catalogue.csv"
        seed_products(db, catalogue_csv)

        # 3. Seed registries
        gstin_csv = settings.DATA_PATH / "mock_gstin_registry.csv"
        pincodes = seed_gstin_registry(db, gstin_csv)

        udyam_csv = settings.DATA_PATH / "mock_udyam_registry.csv"
        seed_udyam_registry(db, udyam_csv)

        # 4. Seed pincodes
        seed_pincodes(db, pincodes)

        print("\n[✔] ALL REFERENCE DATA SEEDED SUCCESSFULLY INTO udyam.db!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
