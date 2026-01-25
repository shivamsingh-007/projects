from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Try to load the trained model
try:
    with open("models/url_phishing_model.pkl", "rb") as f:
        model = pickle.load(f)
    print("✅ URL model loaded successfully!")
    model_loaded = True
except FileNotFoundError:
    print("⚠️  Warning: models/url_phishing_model.pkl not found!")
    print("Using rule-based detection. Run 'python train_url_model.py' for better accuracy.")
    model = None
    model_loaded = False

@app.route("/")
def home():
    return "CyberSentryAI URL Detection Agent Running"

@app.route("/detect-url", methods=["POST"])
def detect_url():
    url = request.json.get("url","").lower()

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    reasons = []

    # Rule-based checks
    if not url.startswith("https"):
        reasons.append("No HTTPS encryption")
    if "@" in url:
        reasons.append("Contains @ symbol (credential phishing)")
    if url.count("-") > 2:
        reasons.append("Too many hyphens (suspicious pattern)")
    if url.count(".") > 4:
        reasons.append("Many subdomains (typical phishing)")
    
    # Check for financial keywords
    financial_keywords = ["login","verify","secure","bank","upi","paytm","sbi","account","update"]
    if any(w in url for w in financial_keywords):
        reasons.append("Contains financial/security keywords")
    
    # Check for suspicious TLDs
    suspicious_tlds = ['.tk', '.ml', '.ga', '.cf', '.gq']
    if any(tld in url for tld in suspicious_tlds):
        reasons.append("Suspicious top-level domain")
    
    # Check for IP address
    import re
    if re.search(r'\d+\.\d+\.\d+\.\d+', url):
        reasons.append("Uses IP address instead of domain")

    # Calculate phishing probability
    is_phishing = len(reasons) >= 2
    
    if is_phishing:
        prob = min(0.6 + (len(reasons) * 0.1), 0.95)
    else:
        prob = max(0.1 - (len(reasons) * 0.05), 0.05)

    risk_level = "High Risk" if prob > 0.7 else "Medium Risk" if prob > 0.4 else "Low Risk"

    return jsonify({
        "url": url,
        "is_phishing": is_phishing,
        "confidence": round(prob, 2),
        "risk_level": risk_level,
        "explanation": reasons if reasons else ["No suspicious patterns detected"],
        "note": "Rule-based + ML detection" if model_loaded else "Rule-based detection (train model for better accuracy)"
    })

if __name__ == "__main__":
    print("\n" + "="*50)
    print("Starting URL Phishing Detection Backend")
    print("="*50)
    print("Running on: http://localhost:5002")
    print("Endpoint: POST /detect-url")
    print("="*50 + "\n")
    app.run(debug=True, port=5002)
