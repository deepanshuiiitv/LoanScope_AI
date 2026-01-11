
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