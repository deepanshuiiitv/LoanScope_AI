from flask import Flask, request, jsonify, render_template
from langchain_core.runnables import RunnableSequence, RunnableLambda
from loan_functions import (
    feature_engineering,
    hard_rule_tool,
    ai_risk_tool,
    decision_tool
)
import os
from ai_services.agent_1_validation.main import main
from ai_services.agent_2_verification.main import main as main1
from ai_services.agent_3_text_extraction.main import main as main2

from cleanup import clear_sample_documents 
from werkzeug.utils import secure_filename


app = Flask(__name__)

pipeline = RunnableSequence(
    RunnableLambda(feature_engineering),
    RunnableLambda(hard_rule_tool),
    RunnableLambda(ai_risk_tool),
    RunnableLambda(decision_tool)
)

UPLOAD_DIR = "sample_documents"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["GET"])
def document_upload():
    return render_template("document_upload.html")

@app.route("/document/process", methods=["POST"])
def validate_from_frontend():
    try:
        data = request.get_json(force=True)
        profession = data.get("profession")

        if not profession:
            return jsonify({"error": "profession is required"}), 400
        
        # # ✅ file from form-data
        # file = request.files.get("file")
        # if not file:
        #     return jsonify({"error": "file is required"}), 400

        # filename = secure_filename(file.filename)
        # file.save(os.path.join(UPLOAD_DIR, filename))

        r = main()
        r2 = main1()
        r3 = main2(profession)

        return jsonify({
            "agent_1_validation": r,
            "agent_2_verification": r2,
            "agent_3_text_extraction": r3
        })

    except Exception:
        import traceback
        return jsonify({
            "status": "ERROR",
            "trace": traceback.format_exc()
        }), 500


@app.route("/loan/assess", methods=["POST"])
def assess_loan():
    data = request.get_json(force=True)
    result = pipeline.invoke(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)