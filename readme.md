# 🏦 LoanScope AI: Agentic Credit Risk & Fraud Assessment
A **Flask-based AI backend** for document validation, forensic verification, text extraction, and loan risk assessment.  
Designed for fintech / NBFC / banking workflows.

---

## 🚀 Features

### 📄 Document Processing (3 AI Agents)
- **Agent 1 – Validation**
  - Document type detection & validation
- **Agent 2 – Forensic Verification**
  - Tampering, AI-generated, edited document detection
- **Agent 3 – Text Extraction & Cross-Reference**
  - Extracts & cross-checks data using applicant context

### 💰 Loan Assessment
- Feature engineering
- Policy (hard rule) checks
- AI risk scoring (Gemini)
- Final decision engine

---

## 🗂️ Project Structure

```

project/
├── app.py
├── cleanup.py
├── loan_functions.py
├── sample_documents/
├── templates/
│   ├── index.html
│   └── document_upload.html
├── ai_services/
│   ├── agent_1_validation/
│   ├── agent_2_verification/
│   └── agent_3_text_extraction/
└── README.md

````

---

## 🔧 Setup & Run

### 1️⃣ Install dependencies
```bash
pip install flask langchain-core numpy google google-generativeai google-genai
````

### 2️⃣ Run the server

```bash
python app.py
```

Server starts at:

```
http://127.0.0.1:5000
```

---

## 🌐 Web Pages

### Home Page

```
GET /
```

### Document Upload UI

```
GET /upload
```

---

## 📌 APIs & How to Use Them

---

### 🔹 1. Document Processing API

**POST** `/document/process`

Runs **all 3 AI agents** on a document.

---

### ▶️ Option A: Upload File (Form-Data)

**Postman / Frontend**

* Method: `POST`
* URL:

  ```
  http://127.0.0.1:5000/document/process
  ```
* Body → `form-data`

| Key                    | Type | Example      |
| ---------------------- | ---- | ------------ |
| `file`                 | File | pan_card.jpg |
| `profession`           | Text | Salaried     |
| `description`          | Text | PAN Card     |
| `expected_type`        | Text | PAN_CARD     |
| `doc_type`             | Text | pan_card     |
| `declared_loan_amount` | Text | 4500000      |

---

### ▶️ Option B: JSON (File Already on Server)

```json
{
  "profession": "Salaried",
  "file_path": "sample_documents/my_pan_card.jpg",
  "description": "PAN Card",
  "expected_type": "PAN_CARD",
  "doc_type": "pan_card",
  "declared_loan_amount": 4500000
}
```

---

### ✅ Response

```json
{
  "agent_1_validation": {...},
  "agent_2_verification": {...},
  "agent_3_text_extraction": {...}
}
```

---

## 🔹 2. Loan Assessment API

**POST** `/loan/assess`

Evaluates loan eligibility using rules + AI.

---

### ▶️ Request (JSON)

```json
{
  "profession": "salaried",
  "age": 34,
  "pan_valid": true,
  "credit_score": 760,
  "loan_amount": 4500000,
  "property_value": 6000000,
  "net_monthly_salary": 85000,
  "salary_credits": [83000, 85000, 87000],
  "existing_emi": 18000,
  "proposed_emi": 22000
}
```

---

### ✅ Response

```json
{
  "decision": "APPROVE | REJECT | MANAGER_REVIEW",
  "risk_score": 0.72
}
```

---

## 🧹 Cleanup (Optional)

Temporary uploaded files can be cleared using:

```python
clear_sample_documents("sample_documents")
```

---

## 🧠 Design Principles

* Policy-first, AI-assisted
* Stateless APIs
* Modular agent architecture
* JSON-friendly 
* Production-safe file handling

---

## 🔮 Future Enhancements

* Async processing
* Frontend Support
* Batch document upload
* Swagger / OpenAPI docs
* Auth & rate limiting
* Database audit logs