# from .agent import ValidationAgent
# from .schemas import DocCategory

# def main():
#     agent = ValidationAgent()

#     # --- Test Case 1: Correct PAN Card ---
#     print("\n--- TEST 1: Uploading a PAN Card (Expecting PAN) ---")
#     # Replace with a real path on your machine to test
#     result = agent.validate(
#         file_path="sample_documents/my_pan_card_2.jpg", 
#         expected_type=DocCategory.PAN_CARD
#     )
#     print("Result:", result)

#     # --- Test Case 2: Wrong Document (Upload Aadhaar, Expect PAN) ---
#     print("\n--- TEST 2: Uploading Aadhaar (Expecting PAN) ---")
#     result = agent.validate(
#         file_path="sample_documents/my_aadhaar_2.png", 
#         expected_type=DocCategory.PAN_CARD
#     )
#     print("Result:", result)

#     # In main.py
#     print("\n--- TEST 3: Farmer Document (7/12 Extract) ---")
#     # Find a sample "7/12 extract image" on google and save it
#     result = agent.validate(
#         file_path="sample_documents/sample_7_12_extract.jpg", 
#         expected_type=DocCategory.LAND_RECORD
#     )
#     print("Result:", result)

# if __name__ == "__main__":
#     main()



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

    print(f"🚀 Starting Batch Validation for {len(test_cases)} Scenarios...\n")

    for description, file_path, expected_type in test_cases:
        print(f"---------------------------------------------------------------")
        print(f"📂 TEST: {description}")
        print(f"   path: {file_path}")
        
        # 1. Check if file exists to prevent crashing
        if not os.path.exists(file_path):
            print(f"   ⚠️  SKIPPING: File not found in 'sample_documents/'")
            continue

        # 2. Run the Agent
        result = agent.validate(file_path=file_path, expected_type=expected_type)
        
        # 3. Print Result nicely
        status_icon = "✅" if result.get("status") == "APPROVED" else "❌"
        if "FAIL CASE" in description and result.get("status") == "REJECTED":
            status_icon = "✅ (Correctly Rejected)"
            
        print(f"   STATUS: {status_icon} {result.get('status')}")
        print(f"   Detected: {result.get('detected_type')}")
        print(f"   Confidence: {result.get('confidence_score')}")
        
        if result.get("rejection_reason"):
            print(f"   Reason: {result.get('rejection_reason')}")
        
        print(f"---------------------------------------------------------------\n")

if __name__ == "__main__":
    main()