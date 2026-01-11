

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

    results = []

    for description, file_path in test_cases:
        if not os.path.exists(file_path):
            results.append({
                "test": description,
                "file_path": file_path,
                "status": "SKIPPED",
                "reason": "File not found"
            })
            continue

        result = agent.analyze(file_path)

        score = result.get("integrity_score", 0)
        status = result.get("status")

        attack_outcome = None
        if "ATTACK" in description:
            attack_outcome = (
                "BLOCKED" if status == "REJECTED" or score < 50 else "FAILED"
            )

        results.append({
            "test": description,
            "file_path": file_path,
            "status": status,
            "integrity_score": score,
            "attack_outcome": attack_outcome,
            "details": result.get("details"),
            "flags": result.get("flags", [])
        })

    return results

if __name__ == "__main__":
    main()