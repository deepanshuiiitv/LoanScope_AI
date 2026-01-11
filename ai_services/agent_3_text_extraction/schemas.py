
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
