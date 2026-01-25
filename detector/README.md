# 🛡️ CyberSentryAI - Complete Image Detection Integration

## 📌 What You've Received

I've created a complete image detection system that integrates with your existing text and URL detection backends. Here's everything you need:

### 📦 Files Included

#### **Backend Files** (Python/Flask)
1. **image_app.py** - Image detection Flask server (Port 5003)
2. **train_image_model.py** - Script to train the image detection model
3. **text_app_updated.py** - Updated text backend with CORS
4. **url_app_updated.py** - Updated URL backend with CORS

#### **Frontend Files**
5. **frontend.html** - Complete web interface with all 3 detection types

#### **Setup & Testing**
6. **SETUP_GUIDE.md** - Detailed setup instructions
7. **ARCHITECTURE.md** - System architecture and data flow diagrams
8. **requirements.txt** - Python dependencies
9. **test_backends.py** - Test script to verify all backends
10. **quick_start.sh** - Automated setup script

## 🚀 Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

Or if you need system packages flag:
```bash
pip install flask flask-cors scikit-learn pandas numpy pillow opencv-python matplotlib --break-system-packages
```

### Step 2: Train Models & Start Backends

**Option A - Manual (Recommended for first time)**

Open 3 separate terminal windows:

```bash
# Terminal 1 - Text Detection
python text_app_updated.py

# Terminal 2 - URL Detection  
python url_app_updated.py

# Terminal 3 - Image Detection
python image_app.py
```

**Option B - Use Existing Files**

If you want to keep using your original files, just add CORS:
```python
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Add this line
```

### Step 3: Open Frontend
```bash
# Just double-click or:
open frontend.html
```

## 🧪 Test the System

### Test Image Detection:
1. Open `frontend.html` in your browser
2. Click the "🖼️ Image" tab
3. Upload any screenshot, poster, or image
4. Click "Analyze Image"
5. See the results!

### Run Automated Tests:
```bash
python test_backends.py
```

## 📋 How It Works

### Image Detection Features

The image detection model analyzes:
- **Color Patterns** - Suspicious red/urgent colors
- **Text Density** - Dense text typical of scams
- **Brightness** - Extreme brightness to grab attention
- **Dimensions** - Unusual aspect ratios
- **Color Variance** - High variance for urgency

### API Endpoint

**URL:** `http://localhost:5003/detect-image`
**Method:** POST
**Content-Type:** multipart/form-data

**Request (FormData):**
```javascript
const formData = new FormData();
formData.append('image', fileInput.files[0]);
```

**Response:**
```json
{
  "is_scam": true,
  "confidence": 0.85,
  "risk_level": "High Risk",
  "explanation": [
    "High red color intensity (urgency indicator)",
    "Dense text content (typical of scam messages)"
  ],
  "features_detected": {
    "width": 800,
    "height": 600,
    "red_intensity": 180.5,
    ...
  }
}
```

## 🎯 Integration Points

### Frontend → Backend Communication

```javascript
// Text Detection
fetch('http://localhost:5001/detect-text', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({text: "message"})
})

// URL Detection
fetch('http://localhost:5002/detect-url', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({url: "https://example.com"})
})

// Image Detection
const formData = new FormData();
formData.append('image', file);
fetch('http://localhost:5003/detect-image', {
  method: 'POST',
  body: formData
})
```

## 🔧 Customization

### Change Backend Ports

Edit in backend file:
```python
app.run(debug=True, port=5003)  # Change port here
```

Edit in frontend.html:
```javascript
const API_CONFIG = {
    IMAGE_API: 'http://localhost:5003/detect-image'  // Update URL
};
```

### Improve Model Accuracy

1. Collect real scam images and place in `datasets/scam_images/`
2. Collect legitimate images and place in `datasets/legitimate_images/`
3. Retrain model: `python train_image_model.py`
4. Restart backend: `python image_app.py`

## 📁 Project Structure

```
CyberSentryAI/
├── models/
│   ├── text_scam_model.pkl
│   ├── url_phishing_model.pkl
│   └── image_scam_model.pkl
├── datasets/
│   ├── spam.csv
│   ├── PhiUSIIL_Phishing_URL_Dataset.csv
│   ├── scam_images/
│   └── legitimate_images/
├── text_app_updated.py (or your text_app.py)
├── url_app_updated.py (or your url_app.py)
├── image_app.py ⭐ NEW
├── train_image_model.py ⭐ NEW
├── frontend.html ⭐ NEW
└── requirements.txt
```

## ⚠️ Common Issues & Solutions

### Issue: CORS Error in Browser
**Solution:** Make sure flask-cors is installed and enabled:
```python
from flask_cors import CORS
CORS(app)
```

### Issue: Model Not Found
**Solution:** Train the model first:
```bash
python train_image_model.py
```

### Issue: Cannot Connect to Backend
**Solution:** 
1. Check backend is running: `python image_app.py`
2. Verify port is 5003
3. Check console for errors

### Issue: Image Upload Fails
**Solution:**
1. Use supported formats: jpg, png, jpeg, webp
2. Keep file size reasonable (< 10MB)
3. Check browser console for errors

## 🔒 Security Notes

- Currently set up for **local development only**
- CORS is enabled for all origins (change for production)
- No authentication (add for production)
- Debug mode enabled (disable for production)

## 🚀 Next Steps

1. ✅ Test with sample images
2. ✅ Collect real scam/legitimate images for training
3. ✅ Retrain model with real data
4. ✅ Deploy to cloud (Heroku, AWS, Azure)
5. ✅ Add user authentication
6. ✅ Create mobile app version
7. ✅ Add email integration

## 📞 Support

If you encounter issues:

1. **Check SETUP_GUIDE.md** - Detailed setup instructions
2. **Check ARCHITECTURE.md** - System architecture
3. **Run test_backends.py** - Verify all backends are running
4. **Check browser console** - Look for JavaScript errors
5. **Check terminal output** - Look for Python errors

## 📝 License & Credits

- Flask: BSD License
- scikit-learn: BSD License
- OpenCV: Apache 2.0 License
- PIL: HPND License

---

**Created for CyberSentryAI Project**
*Protecting users from scams with AI-powered detection*

🛡️ Stay Safe Online!
