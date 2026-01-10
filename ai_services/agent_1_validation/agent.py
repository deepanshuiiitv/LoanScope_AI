# from google import genai
# from google.genai import types
# from .config import API_KEY
# from .schemas import ValidationResult, DocCategory
# from .utils import load_file_content
# import pydantic

# print("🔥 LOADED agent.py — model =", __name__)


# class ValidationAgent:
#     def __init__(self):
#         # NEW SDK: We initialize a Client, not a GenerativeModel
#         self.client = genai.Client(api_key=API_KEY)
#         self.model_name = "models/gemini-2.5-flash"
#         print("🔥 USING MODEL:", self.model_name)


#     def validate(self, file_path: str, expected_type: DocCategory = None) -> dict:
#         print(f"🤖 Agent Validation: Analyzing {file_path}...")
        
#         try:
#             # 1. Load File
#             file_blob = load_file_content(file_path)
            
#             # 2. Prepare Content
#             # The new SDK handles bytes simpler using types.Part
#             file_part = types.Part.from_bytes(
#                 data=file_blob["data"],
#                 mime_type=file_blob["mime_type"]
#             )

#             prompt_text = """
#             You are a Senior Loan Underwriter. Analyze this document file.
#             Task: Classify this document into the allowed categories and check for validity.
#             Guidelines:
#             - Analyze the FIRST page for identity headers.
#             - Check for 'Income Tax Department' (PAN/ITR), 'Unique Identification Authority' (Aadhaar).
#             - Verify readability.
#             - If irrelevant (food, selfie), mark detected_type as UNKNOWN.
#             """

#             # 3. Call Model (New Syntax)
#             response = self.client.models.generate_content(
#                 model=self.model_name,
#                 contents=[file_part, prompt_text],
#                 config=types.GenerateContentConfig(
#                     response_mime_type="application/json",
#                     response_schema=ValidationResult
#                 )
#             )

#             # 4. Automatic Parsing (The new SDK does this for you!)
#             # response.parsed is already a ValidationResult object
#             validated_data: ValidationResult = response.parsed

#             if not validated_data:
#                 return {"error": "AI returned empty response or failed to parse JSON."}

#             return self._apply_business_logic(validated_data, expected_type)

#         except Exception as e:
#             return {"error": f"AI processing failed: {str(e)}"}

#     def _apply_business_logic(self, data: ValidationResult, expected_type: DocCategory):
#         # Convert Pydantic model to dict
#         response = data.model_dump()
#         response["status"] = "APPROVED"

#         # Logic 1: Wrong Type
#         if expected_type and data.detected_type != expected_type:
#             response["status"] = "REJECTED"
#             response["rejection_reason"] = f"Uploaded {data.detected_type.value}, but requested {expected_type.value}."
#             return response

#         # Logic 2: Unreadable
#         if not data.is_readable:
#             response["status"] = "REJECTED"
#             response["rejection_reason"] = "Document is unclear. Please upload a high-quality scan."
#             return response

#         # Logic 3: Low Confidence
#         if data.confidence_score < 0.70:
#             response["status"] = "MANUAL_REVIEW"
#             response["rejection_reason"] = "AI confidence low. Human review required."

#         return response


import json
from google import genai
from google.genai import types
from .config import API_KEY
from .schemas import ValidationResult, DocCategory
from .utils import load_file_content


class ValidationAgent:
    def __init__(self):
        # Gemini client
        self.client = genai.Client(api_key=API_KEY)
        self.model_name = "models/gemini-2.5-flash"

    def validate(self, file_path: str, expected_type: DocCategory = None) -> dict:
        print(f"Agent Validation: Analyzing {file_path}...")

        try:
            # 1. Load file bytes
            file_blob = load_file_content(file_path)

            file_part = types.Part.from_bytes(
                data=file_blob["data"],
                mime_type=file_blob["mime_type"]
            )

            # 2. Prompt (STRICT output rules)
            prompt_text = """
You are a Senior Loan Underwriter for an Indian Bank.

TASK:
- Identify the document type
- Check readability
- Return a structured JSON response ONLY

DOCUMENT TYPES (keywords):
- PAN: Income Tax Department, Permanent Account Number
- Aadhaar: Unique Identification Authority of India, Mera Aadhaar
- Voter ID: Election Commission of India
- Driving License: Driving Licence, DL No
- Utility Bill: Electricity Bill, Consumer No, Discom
- Rent Agreement: Leave and License, Lessor, Lessee
- Salary Slip: Earnings, Deductions, Net Pay
- Form 16: Certificate under Section 203
- Bank Statement: Account Statement, IFSC
- ITR-V: Income Tax Return Acknowledgement
- Land Record: 7/12, Satbara, Survey No
- Mandi Receipt: Krishi Upaj Mandi, J-Form

VALIDATION RULES:
- If text is blurry or unreadable → is_readable=false
- If irrelevant (selfie, food, scenery) → detected_type=unknown

OUTPUT FORMAT (STRICT):
Return ONLY valid JSON with:
- detected_type: one of these exact values:
  pan_card, aadhaar_card, voter_id, driving_license,
  utility_bill, rent_agreement, salary_slip, form_16,
  bank_statement, itr_v, land_record, crop_sale_receipt,
  kisan_credit_card_stmt, unknown
- confidence_score: number between 0.0 and 1.0
- is_readable: true or false
- visible_entities: list of strings
- document_date: string or null
"""

            # 3. Call Gemini
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[file_part, prompt_text],
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ValidationResult
                )
            )

            # 4. Parse response safely
            if response.parsed:
                validated_data = response.parsed
            else:
                raw_text = self._extract_raw_json(response)
                if not raw_text:
                    return {"error": "AI returned no JSON output"}

                raw = json.loads(raw_text)
                raw["detected_type"] = self._normalize_doc_type(
                    raw.get("detected_type")
                )
                validated_data = ValidationResult(**raw)

            # 5. Apply business rules
            return self._apply_business_logic(validated_data, expected_type)

        except Exception as e:
            return {
                "status": "ERROR",
                "detected_type": None,
                "confidence_score": None,
                "rejection_reason": f"AI processing failed: {str(e)}"
            }


    # ------------------------------------------------------------------
    # Business Logic
    # ------------------------------------------------------------------

    def _apply_business_logic(self, data: ValidationResult, expected_type: DocCategory):
        response = data.model_dump()
        response["detected_type"] = data.detected_type.value
        response["status"] = "APPROVED"

        if expected_type and data.detected_type != expected_type:
            response["status"] = "REJECTED"
            response["rejection_reason"] = (
                f"Uploaded {data.detected_type.value}, "
                f"but requested {expected_type.value}."
            )
            return response

        if not data.is_readable:
            response["status"] = "REJECTED"
            response["rejection_reason"] = (
                "Document is unreadable. Please upload a clearer scan."
            )
            return response

        if data.confidence_score < 0.65:
            response["status"] = "MANUAL_REVIEW"
            response["rejection_reason"] = (
                "AI confidence low. Human review required."
            )

        return response


    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _extract_raw_json(self, response):
        """
        Safely extract raw JSON text from google-genai response
        """
        try:
            parts = response.candidates[0].content.parts
            for part in parts:
                if hasattr(part, "text") and part.text:
                    return part.text
        except Exception:
            pass
        return None

    def _normalize_doc_type(self, value: str) -> DocCategory:
        if not value:
            return DocCategory.UNKNOWN

        value = value.lower().strip()

        mapping = {
            "pan": DocCategory.PAN_CARD,
            "pan card": DocCategory.PAN_CARD,
            "pan_card": DocCategory.PAN_CARD,

            "aadhaar": DocCategory.AADHAAR_CARD,
            "aadhaar card": DocCategory.AADHAAR_CARD,
            "aadhaar_card": DocCategory.AADHAAR_CARD,

            "voter id": DocCategory.VOTER_ID,
            "driving license": DocCategory.DRIVING_LICENSE,
            "dl": DocCategory.DRIVING_LICENSE,

            "salary slip": DocCategory.SALARY_SLIP,
            "salary_slip": DocCategory.SALARY_SLIP,

            "electricity bill": DocCategory.UTILITY_BILL,
            "utility bill": DocCategory.UTILITY_BILL,

            "form 16": DocCategory.FORM_16,
            "itr v": DocCategory.ITR_V,
            "itr_v": DocCategory.ITR_V,

            "7/12": DocCategory.LAND_RECORD,
            "satbara": DocCategory.LAND_RECORD,

            "mandi receipt": DocCategory.CROP_SALE_RECEIPT,
        }

        return mapping.get(value, DocCategory.UNKNOWN)
