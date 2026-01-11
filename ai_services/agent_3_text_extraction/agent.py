

from google import genai
from google.genai import types
from .config import API_KEY
from .schemas import ExtractedLoanData
import json
import os

class CrossRefAgent:
    def __init__(self):
        self.client = genai.Client(api_key=API_KEY)
        self.model = "models/gemini-2.5-flash"

    def execute(self, files: list, user_context: dict) -> dict:
        print(f"⚖️ Agent 3 (Gemini): Extracting data for {user_context['profession']}...")

        final_data = ExtractedLoanData(
            profession=user_context.get("profession", "Unknown"),
            loan_amount_requested=user_context.get("declared_loan_amount", 0)
        )

        for file_path, doc_type in files:
            if not os.path.exists(file_path):
                print(f"⚠️ File not found: {file_path}")
                continue

            print(f"\n[DEBUG] Gemini processing: {doc_type} | {file_path}")

            with open(file_path, "rb") as f:
                file_bytes = f.read()

            file_part = types.Part.from_bytes(
                data=file_bytes,
                mime_type=self._guess_mime(file_path)
            )

            prompt = """
            You are a senior loan underwriter AI.Analyze the attached document.
            Document type hint: """ + doc_type + """
            Your task is to extract ONLY the fields that are clearly visible
            in this document. If a field is not present or not clearly identifiable,
            return null for that field. DO NOT guess or hallucinate.
            --------------------
            FIELDS TO EXTRACT
            --------------------
            1. age:
            - If Date of Birth (DOB) is visible (PAN or Aadhaar),
            calculate age in completed years as of today.
            - If DOB is not visible, return null.
            2. pan_number:
            - Extract PAN number if visible.
            - Correct for OCR confusion (O↔0, I↔1).
            - If not visible, return null.
            3. is_pan_valid:
            - true if a valid PAN number structure is visible.
            - false otherwise.
            4. net_monthly_salary:
            - Extract NET PAY from salary slip.
            - Ignore gross salary, dates, employee IDs.
            - If not visible, return null.
            5. salary_credits:
            - ONLY from bank statements.
            - Identify salary credit transactions (monthly recurring credits).
            - Return an array of the last up to 6 salary credit amounts.
            - Example: [87300, 87300, 86000]
            - If no salary credits are visible, return null.
            6. existing_emi:
            - ONLY from bank statements.
            - Identify EMI debit transactions (loan EMI, home loan, personal loan).
            - Return the monthly EMI amount.
            - If multiple EMIs exist, return the total monthly EMI.
            - If no EMI is visible, return null.
            7. property_value:
            - ONLY from valuation reports or property documents.
            - Extract stated property value.
            - If not present, return null.
            --------------------
            STRICT OUTPUT FORMAT
            --------------------
            Return ONLY valid JSON with exactly these keys:
            {
            "age": number | null,
            "pan_number": string | null,
            "is_pan_valid": boolean,
            "net_monthly_salary": number | null,
            "salary_credits": array | null,
            "existing_emi": number | null,
            "property_value": number | null
            }
            """

            response = self.client.models.generate_content(
                model=self.model,
                contents=[file_part, prompt],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )

            data = json.loads(response.text)

            # ---- MERGE RESULTS SAFELY ----
            for k, v in data.items():
                if v not in [None, 0, "", []]:
                    setattr(final_data, k, v)

        # ---- POST VALIDATION ----
        if final_data.pan_number:
            final_data.is_pan_valid = True

        return final_data.model_dump()

    def _guess_mime(self, path):
        ext = path.lower()
        if ext.endswith(".pdf"):
            return "application/pdf"
        if ext.endswith(".png"):
            return "image/png"
        if ext.endswith(".jpg") or ext.endswith(".jpeg"):
            return "image/jpeg"
        return "application/octet-stream"
