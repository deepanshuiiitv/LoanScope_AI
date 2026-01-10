# from pydantic import BaseModel, Field
# from typing import Optional, List

# class ExtractedLoanData(BaseModel):
#     # --- COMMON FIELDS ---
#     profession: str = Field(..., description="Salaried, Self-Employed, or Farmer")
#     age: Optional[int] = None
#     pan_number: Optional[str] = None
#     is_pan_valid: bool = False
    
#     # Financials (Mapped based on profession)
#     net_monthly_salary: Optional[float] = 0.0
#     avg_net_profit_3y: Optional[float] = 0.0
#     annual_agri_income: Optional[float] = 0.0
    
#     # Stability Checks
#     salary_credits_count: int = 0  # Number of valid salary credits found
#     business_age_years: float = 0.0
#     kcc_overdue_amount: float = 0.0
    
#     # Liability & Credit
#     credit_score: Optional[int] = None
#     existing_emi: float = 0.0
#     dpd_30_plus: bool = False # Did we find any late payments?
    
#     # Property / Loan Info
#     loan_amount_requested: float = 0.0
#     property_value: float = 0.0
    
#     # Audit Trail
#     missing_fields: List[str] = Field(default_factory=list)
#     flags: List[str] = Field(default_factory=list)

from pydantic import BaseModel
from typing import Optional, List

class ExtractedLoanData(BaseModel):
    profession: str
    age: Optional[int] = None
    pan_number: Optional[str] = None
    is_pan_valid: bool = False

    net_monthly_salary: Optional[float] = None
    salary_credits: Optional[List[float]] = None
    existing_emi: Optional[float] = None

    loan_amount_requested: Optional[float] = None
    property_value: Optional[float] = None

    avg_net_profit_3y: float = 0.0
    annual_agri_income: float = 0.0
    business_age_years: float = 0.0

    missing_fields: List[str] = []
    flags: List[str] = []
