
from .agent import CrossRefAgent

def main(profession: str):
    agent = CrossRefAgent()
    
    context = {
        "profession": profession,
        "declared_loan_amount": 1000000
    }
    
    files = [
        ("sample_documents/my_pan_card_3.jpg", "pan_card"),
        ("sample_documents/salary_slip_nov.png", "salary_slip"),
        ("sample_documents/sbi_statement.jpg", "bank_statement"),
    ]
    
    return agent.execute(files, context)

if __name__ == "__main__":
    main()