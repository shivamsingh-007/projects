from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
from PIL import Image
import io
import base64
import cv2

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend connection

# Load image model (you'll need to train this first)
try:
    with open("models/image_scam_model.pkl", "rb") as f:
        image_model = pickle.load(f)
    model_loaded = True
except:
    model_loaded = False
    print("Warning: Image model not found. Using rule-based detection.")

@app.route("/")
def home():
    return "CyberSentryAI Image Detection Agent Running"

@app.route("/detect-image", methods=["POST"])
def detect_image():
    try:
        # Handle both base64 and file upload
        if 'image' in request.files:
            # File upload
            file = request.files['image']
            image_bytes = file.read()
        elif 'image_data' in request.json:
            # Base64 encoded image
            image_data = request.json['image_data']
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            image_bytes = base64.b64decode(image_data)
        else:
            return jsonify({"error": "No image provided"}), 400

        # Open image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Feature extraction for rule-based detection
        features = extract_image_features(image)
        
        if model_loaded:
            # Use ML model if available
            prediction = image_model.predict([features])[0]
            confidence = image_model.predict_proba([features])[0][1]
        else:
            # Rule-based detection
            prediction, confidence = rule_based_detection(features)
        
        is_scam = bool(prediction)
        risk_level = "High Risk" if confidence > 0.7 else "Medium Risk" if confidence > 0.4 else "Low Risk"
        
        # Generate explanation
        explanation = generate_explanation(features, is_scam)
        
        return jsonify({
            "is_scam": is_scam,
            "confidence": round(float(confidence), 3),
            "risk_level": risk_level,
            "explanation": explanation,
            "features_detected": features
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_image_features(image):
    """Extract features from image for scam detection"""
    features = {}
    
    # Convert to numpy array
    img_array = np.array(image)
    
    # Image dimensions
    features['width'] = image.width
    features['height'] = image.height
    features['aspect_ratio'] = image.width / image.height
    
    # Color analysis
    mean_color = img_array.mean(axis=(0, 1))
    features['red_intensity'] = float(mean_color[0])
    features['green_intensity'] = float(mean_color[1])
    features['blue_intensity'] = float(mean_color[2])
    
    # Brightness
    features['brightness'] = float(img_array.mean())
    
    # Text density estimation (using edge detection as proxy)
    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    features['text_density'] = float(edges.sum() / (image.width * image.height))
    
    # Color variance (high variance might indicate fake urgency colors)
    features['color_variance'] = float(np.var(img_array))
    
    return features

def rule_based_detection(features):
    """Simple rule-based detection when ML model is not available"""
    score = 0
    
    # Check for common scam image characteristics
    if features['red_intensity'] > 150:  # Aggressive red colors
        score += 0.2
    
    if features['text_density'] > 0.3:  # Dense text (urgency messages)
        score += 0.3
    
    if features['brightness'] < 50 or features['brightness'] > 200:  # Extreme brightness
        score += 0.1
    
    if features['color_variance'] > 5000:  # High color variance
        score += 0.2
    
    # Aspect ratio check (unusual dimensions)
    if features['aspect_ratio'] < 0.5 or features['aspect_ratio'] > 2.5:
        score += 0.2
    
    confidence = min(score, 0.95)
    prediction = 1 if confidence > 0.5 else 0
    
    return prediction, confidence

def generate_explanation(features, is_scam):
    """Generate human-readable explanation"""
    reasons = []
    
    if features['red_intensity'] > 150:
        reasons.append("High red color intensity (urgency indicator)")
    
    if features['text_density'] > 0.3:
        reasons.append("Dense text content (typical of scam messages)")
    
    if features['brightness'] < 50:
        reasons.append("Very dark image (suspicious)")
    elif features['brightness'] > 200:
        reasons.append("Very bright image (attention-grabbing)")
    
    if features['color_variance'] > 5000:
        reasons.append("High color variance (designed to catch attention)")
    
    if features['aspect_ratio'] < 0.5 or features['aspect_ratio'] > 2.5:
        reasons.append("Unusual image dimensions")
    
    if not reasons:
        if is_scam:
            reasons.append("ML model detected scam patterns")
        else:
            reasons.append("No suspicious patterns detected")
    
    return reasons

if __name__ == "__main__":
    app.run(debug=True, port=5003)
