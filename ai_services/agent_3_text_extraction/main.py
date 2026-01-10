# from .agent import CrossRefAgent

# def main():
#     agent = CrossRefAgent()
    
#     # Mock User Input (What they filled in the form)
#     user_data = {
#         "declared_name": "Kavyansh Khandelwal",
#         "declared_income": 50000.0,
#         "pan_number": "ABCDE1234F" # Replace with real regex pattern for test
#     }
    
#     # Test Cases
#     files = [
#         ("sample_documents/my_pan_card_2.jpg", "pan_card"),
#         ("sample_documents/sbi_statement.pdf", "bank_statement") 
#     ]
    
#     print("⚖️ Starting Cross-Reference Logic...\n")
    
#     for f_path, d_type in files:
#         result = agent.execute(f_path, d_type, user_data)
#         print(f"📄 File: {f_path}")
#         print(f"   Status: {result['status']}")
#         print(f"   Extracted: {result['extracted_data'].get('pan_number') or 'Text Data Found'}")
#         print(f"   Flags: {result['flags']}")
#         print("-" * 40)

# if __name__ == "__main__":
#     main()

from .agent import CrossRefAgent

def main():
    agent = CrossRefAgent()
    
    # Mocking a Self-Employed Applicant
    context = {
        "profession": "Salaried",
        "declared_loan_amount": 1000000
    }
    
    files = [
        # ("sample_documents/gst_cert.jpg", "business_registration"),
        # ("sample_documents/itr_v_2024.pdf", "itr_v"),
        ("sample_documents/my_pan_card_3.jpg", "pan_card"),
        ("sample_documents/salary_slip_nov.png", "salary_slip"),
        ("sample_documents/sbi_statement.jpg", "bank_statement"),
    ]
    
    result = agent.execute(files, context)
    import json
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()