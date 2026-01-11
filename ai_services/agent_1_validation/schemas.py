

from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Optional

class DocCategory(str, Enum):
    # --- A. KYC & Identity (Common) ---
    LOAN_APPLICATION_FORM = "loan_application_form"
    PHOTOGRAPH = "photograph"
    PAN_CARD = "pan_card"
    AADHAAR_CARD = "aadhaar_card"
    PASSPORT = "passport"
    VOTER_ID = "voter_id"
    DRIVING_LICENSE = "driving_license"
    
    # --- Residence Proof ---
    UTILITY_BILL = "utility_bill" # Electricity, Gas, Telephone
    RENT_AGREEMENT = "rent_agreement"
    
    # --- B. Property Documents (Collateral) ---
    CONSTRUCTION_PLAN = "construction_plan" # Blueprint/Layout
    SALE_AGREEMENT = "sale_agreement" # Registered Agreement/Allotment Letter
    OCCUPANCY_CERTIFICATE = "occupancy_certificate"
    SHARE_CERTIFICATE = "share_certificate" # Co-op society
    NOC_SOCIETY = "noc_society"
    PAYMENT_RECEIPT_BUILDER = "payment_receipt_builder" # Margin money proof
    
    # --- 1. Salaried / Employed ---
    SALARY_SLIP = "salary_slip"
    BANK_STATEMENT = "bank_statement"
    FORM_16 = "form_16"
    ITR_V = "itr_v" # Income Tax Return Acknowledgement
    COMPANY_ID_CARD = "company_id_card"
    APPOINTMENT_LETTER = "appointment_letter" # Job continuity
    
    # --- 2. Self-Employed (Business) ---
    BUSINESS_REGISTRATION = "business_registration" # Udyam, Shop Est, GST Cert
    COMPUTATION_OF_INCOME = "computation_of_income" # COI Sheet
    FINANCIAL_STATEMENT = "financial_statement" # P&L, Balance Sheet
    FORM_26AS = "form_26as" # Tax Credit Statement
    PROFESSIONAL_DEGREE = "professional_degree" # CA/Doctor cert
    BUSINESS_CONTINUITY_PROOF = "business_continuity_proof" # Old license
    
    # --- 3. Farmer / Agriculturist ---
    LAND_RECORD = "land_record" # 7/12, 8-A, Khasra, Khatauni
    INCOME_CERTIFICATE_AGRI = "income_certificate_agri" # Tehsildar/Talati issued
    CROP_SALE_RECEIPT = "crop_sale_receipt" # Mandi/J-Form
    KISAN_CREDIT_CARD_STMT = "kisan_credit_card_stmt"
    NO_DUES_CERTIFICATE = "no_dues_certificate"
    ALLIED_ACTIVITY_PROOF = "allied_activity_proof" # Milk pouring card, RC book
    
    # --- Fallback ---
    UNKNOWN = "unknown"

class ValidationResult(BaseModel):
    detected_type: DocCategory = Field(
        ..., 
        description="The specific category of the document detected."
    )
    confidence_score: float = Field(
        ..., 
        description="Confidence score between 0.0 and 1.0."
    )
    is_readable: bool = Field(
        ..., 
        description="True if text is sharp and legible. False if blurry, too dark, or cut off."
    )
    visible_entities: List[str] = Field(
        ..., 
        description="List 3-5 key visible text headers or keywords found (e.g., 'Form 16', '7/12 Extract', 'Mandi Samiti')."
    )
    document_date: Optional[str] = Field(
        None,
        description="Extract the main date if visible (e.g., '2023-04-01'). Useful for checking validity."
    )
    rejection_reason: Optional[str] = Field(
        None, 
        description="If rejected (unreadable or wrong type), explain why briefly."
    )