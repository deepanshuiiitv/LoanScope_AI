# from thefuzz import fuzz
# import re

# class CrossCheckLogic:
    
#     # --- IDENTITY LOGIC (From My Code) ---
#     @staticmethod
#     def verify_name(name_1: str, name_2: str) -> dict:
#         if not name_1 or not name_2:
#             return {"match": False, "score": 0, "reason": "Missing Name Data"}
            
#         # Token Sort Ratio handles "Kumar Rahul" vs "Rahul Kumar"
#         score = fuzz.token_sort_ratio(name_1, name_2)
        
#         if score > 85:
#             return {"match": True, "score": score, "reason": "High Similarity"}
#         elif score > 70:
#             return {"match": True, "score": score, "reason": "Minor Mismatch (Acceptable)"}
#         else:
#             return {"match": False, "score": score, "reason": "Significant Name Mismatch"}

#     # --- FINANCIAL LOGIC (Adapted from YOUR Code) ---
#     @staticmethod
#     def clean_financial_value(val: float, income: float, field_type: str) -> float:
#         """
#         Sanitizes values based on logic.
#         Fixes OCR artifacts like '25000' reading as '825000'.
#         """
#         if income == 0 or val == 0: return val
        
#         # EMI shouldn't be > 50% of Income
#         threshold = 0.50 if field_type == "emi" else 3.0
        
#         # If Value is suspiciously high
#         if val > (income * threshold):
#             val_str = str(int(val))
#             # Check for common OCR artifact prefixes
#             if val_str[0] in ['2', '3', '4', '8', '7']:
#                 try:
#                     stripped_val = float(val_str[1:])
#                     return stripped_val
#                 except: pass
#         return val

#     @staticmethod
#     def extract_financials(text: str) -> dict:
#         """
#         Simple heuristic extraction without BERT (Heavy).
#         """
#         # Find currency patterns
#         data = {"monthly_income": 0.0, "amounts": []}
        
#         # Regex for Income/Salary
#         inc_match = re.search(r"(?:Income|Salary|Earnings|Net Pay).*?([\d,]+\.?\d*)", text, re.IGNORECASE)
#         if inc_match:
#             try:
#                 clean = inc_match.group(1).replace(",", "")
#                 data["monthly_income"] = float(clean)
#             except: pass
            
#         return data


class BusinessLogic:
    
    @staticmethod
    def calculate_aggregates(extracted_list: list, profession: str) -> dict:
        """
        Takes raw data extracted from all files and calculates the final fields.
        extracted_list = [{'doc_type': 'salary_slip', 'data': {...}}, ...]
        """
        output = {
            "net_monthly_salary": 0.0,
            "avg_net_profit_3y": 0.0,
            "annual_agri_income": 0.0,
            "salary_credits": 0
        }
        
        # 1. Salaried Logic
        if profession == "Salaried":
            salaries = []
            for item in extracted_list:
                if item['doc_type'] == 'salary_slip':
                    val = item['data'].get('net_salary', 0)
                    if val > 0: salaries.append(val)
                elif item['doc_type'] == 'bank_statement':
                    # Heuristic: Count how many times a "Salary-like" amount appears
                    # (In a real app, we'd process the transaction rows)
                    salary_hits = extracted_list.count(
                        lambda x: "salary" in x.get("data", {}).get("text", "").lower()
                    )
                    output["salary_credits"] = salary_hits
                    # Mocking 6 valid credits found
            
            if salaries:
                # Average of found slips
                output["net_monthly_salary"] = sum(salaries) / len(salaries)

        # 2. Self-Employed Logic
        elif profession == "Self-Employed":
            profits = []
            for item in extracted_list:
                if item['doc_type'] in ['itr_v', 'computation_of_income']:
                    val = item['data'].get('income', 0)
                    if val > 0: profits.append(val)
                elif item['doc_type'] == 'business_registration':
                     output["business_age_years"] = item['data'].get('business_age', 0)
            
            if profits:
                output["avg_net_profit_3y"] = sum(profits) / len(profits)

        # 3. Farmer Logic
        elif profession == "Farmer":
            agri_income = 0.0
            for item in extracted_list:
                if item['doc_type'] == 'mandi_receipt':
                    agri_income += item['data'].get('agri_income', 0)
                elif item['doc_type'] == 'income_certificate_agri':
                    # Certificate usually has the annual total
                    val = item['data'].get('agri_income', 0)
                    if val > agri_income: agri_income = val # Take max
            
            output["annual_agri_income"] = agri_income

        return output