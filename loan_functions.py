import numpy as np
import re
from google import genai
import os


# -------------------------
# FEATURE ENGINEERING
# -------------------------
def feature_engineering(data):
    p = data["profession"]
    features = {}

    features["ltv"] = data["loan_amount"] / data["property_value"]

    if p == "salaried":
        total_emi = data["existing_emi"] + data["proposed_emi"]
        features["net_income"] = data["net_monthly_salary"]
        features["foir"] = total_emi / data["net_monthly_salary"]

        arr = np.array(data["salary_credits"])
        features["income_stability"] = max(0, 1 - (np.std(arr) / np.mean(arr)))

    elif p == "self_employed":
        features["net_income"] = data["avg_net_profit_3y"] / 12
        total_emi = data["existing_emi"] + data["proposed_emi"]
        features["foir"] = total_emi / features["net_income"]
        features["business_age"] = data["business_age_years"]
        features["income_stability"] = min(1, data["business_age_years"] / 5)

    elif p == "farmer":
        features["net_income"] = data["annual_agri_income"] / 12
        total_emi = data["existing_emi"] + data["proposed_emi"]
        features["foir"] = total_emi / features["net_income"]
        features["income_stability"] = 0.6
        features["kcc_overdue"] = data["kcc_overdue"]

    features["credit_score"] = data["credit_score"]
    data["features"] = features
    return data

# -------------------------
# HARD RULE ENGINE
# -------------------------
def hard_rule_tool(data):
    f = data["features"]
    p = data["profession"]

    if not data["pan_valid"]:
        return {"decision": "REJECT", "reason": "PAN_INVALID"}

    if not data["legal_clearance"]:
        return {"decision": "REJECT", "reason": "LEGAL_NOT_CLEAR"}

    if data["credit_score"] is not None and data["credit_score"] < 650:
        return {"decision": "REJECT", "reason": "LOW_CREDIT_SCORE"}

    if data["age"] < 21 or data["age"] > 65:
        return {"decision": "REJECT", "reason": "AGE_NOT_ELIGIBLE"}

    if p == "salaried" and f["foir"] > 0.6:
        return {"decision": "REJECT", "reason": "FOIR_SALARIED"}

    if p == "self_employed" and f["foir"] > 0.5:
        return {"decision": "REJECT", "reason": "FOIR_BUSINESS"}

    if p == "farmer" and f["foir"] > 0.4:
        return {"decision": "REJECT", "reason": "FOIR_FARMER"}

    if f["ltv"] > 0.9:
        return {"decision": "REJECT", "reason": "LTV_EXCEEDED"}

    if p == "farmer" and data["kcc_overdue"]:
        return {"decision": "REJECT", "reason": "KCC_DEFAULT"}

    data["hard_rule"] = {"decision": "PASS"}
    return data

# -------------------------
# AI RISK ENGINE
# -------------------------
def ai_risk_tool(data):
    API_KEY = os.getenv("API_KEY")
    client = genai.Client(api_key=API_KEY)
    if data.get("hard_rule", {}).get("decision") == "REJECT":
        return data

    prompt = f"""
Respond ONLY in this format:

RISK_SCORE: <0-1>
REASON: <short>
CUSTOMER_ACTION: <short>

Profession: {data["profession"]}
Features: {data["features"]}
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    text = response.text.strip()

    score = float(re.search(r"RISK_SCORE\s*:\s*([0-1]\.?\d*)", text).group(1))
    reason = re.search(r"REASON\s*:\s*(.+)", text).group(1)
    action = re.search(r"CUSTOMER_ACTION\s*:\s*(.+)", text).group(1)

    data["risk_score"] = score
    data["ai_reason"] = reason
    data["customer_action"] = action
    return data

# -------------------------
# FINAL DECISION
# -------------------------
def decision_tool(data):
    score = data["risk_score"]

    if score >= 0.75:
        return {"decision": "APPROVE", "risk_score": score}

    if score <= 0.45:
        return {"decision": "REJECT", "reason": data["ai_reason"],"risk_score": score}

    return {
        "decision": "MANAGER_REVIEW",
        "risk_score": score,
        "reason": data["ai_reason"],
        "features": data["features"]
    }