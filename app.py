from flask import Flask, request, jsonify
from langchain_core.runnables import RunnableSequence, RunnableLambda
from loan_functions import (
    feature_engineering,
    hard_rule_tool,
    ai_risk_tool,
    decision_tool
)


app = Flask(__name__)

pipeline = RunnableSequence(
    RunnableLambda(feature_engineering),
    RunnableLambda(hard_rule_tool),
    RunnableLambda(ai_risk_tool),
    RunnableLambda(decision_tool)
)

@app.route("/loan/assess", methods=["POST"])
def assess_loan():
    data = request.get_json(force=True)
    result = pipeline.invoke(data)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)