from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Load model
try:
    with open("models/text_scam_model.pkl", "rb") as f:
        model, vectorizer = pickle.load(f)
    print("✅ Text model loaded successfully!")
except FileNotFoundError:
    print("❌ Error: models/text_scam_model.pkl not found!")
    print("Please run 'python train_text_model.py' first")
    model = None
    vectorizer = None

@app.route("/")
def home():
    return "CyberSentryAI Text Detection Agent Running"

@app.route("/detect-text", methods=["POST"])
def detect_text():
    if model is None or vectorizer is None:
        return jsonify({
            "error": "Model not loaded. Please train the model first."
        }), 500
    
    data = request.json
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    pred = prob > 0.5

    risk = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"

    return jsonify({
        "text": text,
        "is_scam": bool(pred),
        "confidence": round(prob, 3),
        "risk_level": risk,
        "explanation": "Message shows scam patterns like urgency, financial threat or impersonation"
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting Text Scam Detection Backend")
    print("="*50)
    print("Running on: http://localhost:5001")
    print("Endpoint: POST /detect-text")
    print("="*50 + "\n")
    app.run(debug=True, port=5001)
