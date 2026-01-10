from .tools import ForensicTools

class ForensicAgent:
    def __init__(self):
        self.tools = ForensicTools()

    # UPDATED: Now accepts 'doc_type' string (optional)
    def analyze(self, file_path: str, doc_type: str = "unknown") -> dict:
        print(f"Forensic Agent: Scanning {file_path} (Type: {doc_type})...")
        
        integrity_score = 100
        flags = []
        
        # 1. Metadata Check
        meta = self.tools.analyze_metadata(file_path)
        if "error" in meta: return {"status": "ERROR", "message": meta["error"]}
        
        # 2. Digital Flatness Check
        flatness = self.tools.check_digital_flatness(file_path)
        
        # --- CONTEXT-AWARE LOGIC ---
        # Define which docs MUST be physical (Identity, Farmer docs)
        # These should NEVER look "perfectly digital"
        physical_docs = [
            "pan_card", "driving_license", "passport", "voter_id", 
            "mandi_receipt", "7_12_extract", "agreement"
        ]
        
        # Define docs that ARE often digital (Bank statements, ITR)
        # These are allowed to look "perfect"
        digital_native_docs = [
            "bank_statement", "salary_slip", "form_16", 
            "itr_v", "computation_of_income", "aadhaar_card" # e-Aadhaar is common
        ]

        # LOGIC: The "Laundering" Trap
        if meta["source_type"] == "social_media_or_screenshot":
            
            # CASE A: It's a Physical Doc (e.g. PAN) but looks Digital -> FAKE
            if any(x in doc_type for x in physical_docs) and flatness.get("is_suspicious_digital"):
                integrity_score -= 30
                flags.append(f"Suspicious: '{doc_type}' should be a scan, but looks like a digital graphic.")
            
            # CASE B: It's a Digital Doc (e.g. Bank Stmt) -> PASS (Ignore Flatness)
            elif any(x in doc_type for x in digital_native_docs) and flatness.get("is_suspicious_digital"):
                # We do NOT penalize digital docs for being flat.
                # But we still deduct a tiny bit for missing metadata.
                integrity_score -= 5
                flags.append("Source: Social Media/Screenshot (Allowed for Digital Docs)")
            
            # CASE C: Unknown Type -> Standard Rules
            elif flatness.get("is_suspicious_digital"):
                 integrity_score -= 20
                 flags.append("Suspicious: 'Laundered' Digital File")

        # 3. ELA Check
        ela = self.tools.perform_ela(file_path, meta["source_type"])
        
        # Stricter ELA threshold for Digital Docs (since they should be clean)
        threshold = 40
        if any(x in doc_type for x in digital_native_docs):
            threshold = 60 # Digital docs naturally have high contrast edges
            
        if ela.get("visual_tamper_score", 0) > threshold:
            integrity_score -= ela["visual_tamper_score"]
            flags.append("Pixel Irregularities Detected (Possible Edit)")

        # 4. Final Verdict
        integrity_score = max(0, integrity_score)
        
        # Handle "Critical Risk" flags from Metadata (Photoshop)
        if meta.get("risk_flags"):
            integrity_score -= 50
            flags.extend(meta["risk_flags"])

        status = "PASSED"
        if integrity_score < 75: status = "MANUAL_REVIEW"
        if integrity_score < 40: status = "REJECTED"

        return {
            "status": status,
            "integrity_score": integrity_score,
            "flags": flags
        }