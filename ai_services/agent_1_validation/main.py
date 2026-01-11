

import os
from .agent import ValidationAgent
from .schemas import DocCategory

def main():
    agent = ValidationAgent()

    # Define all the scenarios you want to test
    # Format: (Description, File Path, Expected Category)
    test_cases = [
        # --- A. KYC & Identity ---
        ("PAN Card Validation", "sample_documents/my_pan_card_2.jpg", DocCategory.PAN_CARD),
        ("Aadhaar Card Validation", "sample_documents/my_aadhaar_2.png", DocCategory.AADHAAR_CARD),
        ("Voter ID Validation", "sample_documents/voter_id_sample.jpg", DocCategory.VOTER_ID),
        ("Driving License Validation", "sample_documents/dl_sample.jpeg", DocCategory.DRIVING_LICENSE),
        
        # --- Residence Proof ---
        ("Electricity Bill", "sample_documents/electricity_bill.jpg", DocCategory.UTILITY_BILL),
        ("Rent Agreement", "sample_documents/rent_agreement.jpg", DocCategory.RENT_AGREEMENT),

        # --- 1. Salaried Documents ---
        ("Salary Slip (3 months)", "sample_documents/salary_slip_nov.png", DocCategory.SALARY_SLIP),
        ("Form 16 Part A/B", "sample_documents/form_16.png", DocCategory.FORM_16),
        ("Bank Statement (Salary)", "sample_documents/sbi_statement.pdf", DocCategory.BANK_STATEMENT),
        ("ITR V Acknowledgement", "sample_documents/itr_v_2024.pdf", DocCategory.ITR_V),

        # --- 2. Business Documents ---
        ("GST Registration", "sample_documents/gst_cert.pdf", DocCategory.BUSINESS_REGISTRATION),
        ("P&L Statement", "sample_documents/pnl_sheet.pdf", DocCategory.FINANCIAL_STATEMENT),
        ("Udyam Aadhar", "sample_documents/udyam_cert.jpg", DocCategory.BUSINESS_REGISTRATION),

        # --- 3. Farmer Documents ---
        ("7/12 Extract (Satbara)", "sample_documents/sample_7_12_extract.jpg", DocCategory.LAND_RECORD),
        ("Mandi Receipt (J-Form)", "sample_documents/mandi_receipt.jpg", DocCategory.CROP_SALE_RECEIPT),
        ("Kisan Credit Card", "sample_documents/kcc_statement.jpg", DocCategory.KISAN_CREDIT_CARD_STMT),
        
        # --- Negative Tests (Checking if it catches errors) ---
        ("FAIL CASE: Aadhaar uploaded as PAN", "sample_documents/my_aadhaar_2.png", DocCategory.PAN_CARD),
        ("FAIL CASE: Random Selfie", "sample_documents/random_selfie.jpg", DocCategory.PAN_CARD),
    ]

    results = []

    for description, file_path, expected_type in test_cases:
        if not os.path.exists(file_path):
            results.append({
                "test": description,
                "status": "SKIPPED",
                "reason": "File not found"
            })
            continue

        result = agent.validate(
            file_path=file_path,
            expected_type=expected_type
        )

        results.append({
            "test": description,
            "file_path": file_path,
            "expected_type": expected_type.name,
            **result
        })

    return results

if __name__ == "__main__":
    main()