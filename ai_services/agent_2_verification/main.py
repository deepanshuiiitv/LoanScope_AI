# # ai_services/agent_2_forensics/main.py

# import os
# from .agent import ForensicAgent

# def main():
#     agent = ForensicAgent()
    
#     test_files = [
#         "sample_documents/real_doc_2.jpeg",       # Should PASS
#         "sample_documents/real_doc.jpg" # Should FAIL (or flag Warning)
#     ]
    
#     print("Starting Forensic Analysis...\n")
    
#     for f in test_files:
#         if not os.path.exists(f):
#             print(f"Missing file: {f}")
#             continue
            
#         result = agent.analyze(f)
        
#         # Print results nicely
#         print(f"File: {f}")
#         print(f"   Integrity Score: {result['integrity_score']}/100")
#         print(f"   Status: {result['status']}")
        
#         if result['flags']:
#             print(f"FLAGS FOUND:")
#             for flag in result['flags']:
#                 print(f"      - {flag}")
#         else:
#             print("No anomalies detected.")
            
#         print("-" * 40)

# if __name__ == "__main__":
#     main()



import os
from .agent import ForensicAgent

def main():
    agent = ForensicAgent()

    # Define all the scenarios to test forensic integrity
    # Format: (Description, File Path)
    # Note: You should ideally have "Real" and "Fake" versions of some of these to test efficiently.
    test_cases = [
        # --- A. KYC & Identity (High Risk for Forgery) ---
        ("PAN Card (Real/Camera)", "sample_documents/my_pan_card.jpg"),
        ("Aadhaar Card (WhatsApp Source)", "sample_documents/my_aadhaar.jpg"), 
        ("Voter ID (Scanned)", "sample_documents/voter_id_sample.jpg"),
        
        # --- Residence Proof ---
        ("Electricity Bill (PDF converted to Img)", "sample_documents/electricity_bill.jpg"),
        
        # --- 1. Salaried Documents (Income Proofs often forged) ---
        ("Salary Slip (Digital PDF)", "sample_documents/salary_slip_nov.png"),
        ("Bank Statement (Original PDF)", "sample_documents/sbi_statement.jpg"),
        ("Form 16 (Scanned)", "sample_documents/form_16.jpg"),

        # --- 2. Business Documents ---
        ("GST Certificate (Digital Original)", "sample_documents/gst_cert.jpg"),
        ("P&L Statement (Excel Export)", "sample_documents/pnl_sheet.jpg"),

        # --- 3. Farmer Documents (Manual/Handwritten often messy) ---
        ("7/12 Extract (Satbara - Online Download)", "sample_documents/sample_7_12_extract.jpg"),
        ("Mandi Receipt (Handwritten - Camera)", "sample_documents/mandi_receipt.jpg"),
        
        # ---ATTACK SIMULATIONS (The "Fail" Cases) ---
        ("ATTACK: Edited Bank Balance (Photoshop)", "sample_documents/fake_edited_doc.jpg"),
        ("ATTACK: AI Generated ID (Midjourney/DALL-E)", "sample_documents/ai_generated_id.jpg"),
        ("ATTACK: 'Laundered' Fake (Screenshot of Word Doc)", "sample_documents/laundered_fake.jpg"),
    ]

    print(f"🕵️ Starting Forensic Batch Analysis for {len(test_cases)} Scenarios...\n")

    for description, file_path in test_cases:
        print(f"---------------------------------------------------------------")
        print(f"CASE: {description}")
        print(f"   path: {file_path}")
        
        # 1. Check existence
        if not os.path.exists(file_path):
            print(f"   ⚠️  SKIPPING: File not found in 'sample_documents/'")
            continue

        # 2. Run Forensic Analysis
        result = agent.analyze(file_path)
        
        # 3. Print Results
        score = result.get('integrity_score', 0)
        status = result.get('status')
        
        # Icon logic
        icon = "✅" 
        if status == "MANUAL_REVIEW": icon = "⚠️"
        if status == "REJECTED": icon = "❌"
        
        # If it's an ATTACK case, getting REJECTED is actually a Success/Green outcome
        if "ATTACK" in description:
            if status == "REJECTED" or score < 50:
                icon = "(Attack Blocked)"
            else:
                icon = "(Attack Succeeded - Fail)"

        print(f"   VERDICT: {icon} {status} (Score: {score}/100)")
        
        # Show specific details if relevant
        details = result.get('details', {})
        print(f"   [Details] Flatness: {details.get('flatness_ratio')} | ELA Score: {details.get('ela_score')}")

        if result.get('flags'):
            print(f"   🚩 FLAGS:")
            for flag in result['flags']:
                print(f"      - {flag}")
        else:
            print("Clean Document")
            
        print(f"---------------------------------------------------------------\n")

if __name__ == "__main__":
    main()