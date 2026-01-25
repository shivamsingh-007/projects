# CyberSentryAI - Complete Setup Guide

## 🎯 Overview
This guide will help you set up and connect the backend models to the frontend for all three detection types:
- Text Message Scam Detection
- URL Phishing Detection  
- Image Scam Detection

## 📋 Prerequisites

### Required Python Packages
```bash
pip install flask flask-cors scikit-learn pandas numpy pillow opencv-python matplotlib
```

Or install all at once:
```bash
pip install flask flask-cors scikit-learn pandas numpy pillow opencv-python matplotlib --break-system-packages
```

## 📁 Project Structure
```
CyberSentryAI/
├── models/                      # Trained models directory
│   ├── text_scam_model.pkl
│   ├── url_phishing_model.pkl
│   └── image_scam_model.pkl
├── datasets/                    # Training datasets
│   ├── spam.csv
│   ├── PhiUSIIL_Phishing_URL_Dataset.csv
│   ├── scam_images/            # Scam image samples
│   └── legitimate_images/      # Legitimate image samples
├── text_app.py                 # Text detection backend (port 5001)
├── url_app.py                  # URL detection backend (port 5002)
├── image_app.py                # Image detection backend (port 5003)
├── train_text_model.py         # Train text model
├── train_url_model.py          # Train URL model
├── train_image_model.py        # Train image model
└── frontend.html               # Frontend interface

```

## 🚀 Setup Instructions

### Step 1: Create Required Directories
```bash
mkdir -p models datasets/scam_images datasets/legitimate_images
```

### Step 2: Train the Models

#### A. Text Model (if not already trained)
```bash
python train_text_model.py
```
This requires the `spam.csv` dataset in the `datasets/` folder.

#### B. URL Model (if not already trained)
```bash
python train_url_model.py
```
This requires the `PhiUSIIL_Phishing_URL_Dataset.csv` in the `datasets/` folder.

#### C. Image Model (NEW)
```bash
python train_image_model.py
```

**Note:** If you don't have image datasets, the script will create a synthetic dataset for demonstration. For better accuracy, collect real scam and legitimate images and place them in:
- `datasets/scam_images/` - phishing screenshots, fake QR codes, scam posters
- `datasets/legitimate_images/` - normal screenshots, genuine ads, regular images

### Step 3: Update Backend Files

#### Update text_app.py
Make sure it has CORS enabled and runs on port 5001:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
```

#### Update url_app.py  
Make sure it has CORS enabled and runs on port 5002:
```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

if __name__ == "__main__":
    app.run(debug=True, port=5002)
```

#### The image_app.py already has CORS enabled and runs on port 5003

### Step 4: Start the Backend Servers

Open **three separate terminals** and run:

**Terminal 1 - Text Detection:**
```bash
python text_app.py
```
Should start on http://localhost:5001

**Terminal 2 - URL Detection:**
```bash
python url_app.py
```
Should start on http://localhost:5002

**Terminal 3 - Image Detection:**
```bash
python image_app.py
```
Should start on http://localhost:5003

### Step 5: Open the Frontend

Simply open `frontend.html` in your web browser:
```bash
# On Linux/Mac
open frontend.html

# On Windows
start frontend.html

# Or just double-click the file
```

## 🧪 Testing the System

### Test Text Detection:
1. Click on "📱 Text Message" tab
2. Paste this scam message:
```
URGENT! Your bank account will be locked in 24 hours. Click here to verify: http://fake-bank-login.com
```
3. Click "Analyze Message"

### Test URL Detection:
1. Click on "🔗 URL/Link" tab
2. Enter this suspicious URL:
```
http://secure-login-verify@phishing.com/bank/update
```
3. Click "Check URL"

### Test Image Detection:
1. Click on "🖼️ Image" tab
2. Upload any image (screenshot, poster, etc.)
3. Click "Analyze Image"

## 🔧 Troubleshooting

### CORS Errors
If you see CORS errors in the browser console:
1. Make sure `flask-cors` is installed: `pip install flask-cors`
2. Add to each backend file:
```python
from flask_cors import CORS
CORS(app)
```

### Port Already in Use
If a port is already taken, change it in both:
1. Backend file: `app.run(debug=True, port=XXXX)`
2. Frontend file: Update `API_CONFIG` object

### Model Not Found
If you get "model not found" errors:
1. Make sure you've run the training scripts
2. Check that `models/` directory contains the .pkl files
3. Verify file paths match in the code

### Image Detection Not Working
1. Install required packages: `pip install pillow opencv-python`
2. Make sure the image is a valid format (jpg, png, jpeg, webp)
3. Check browser console for detailed error messages

## 📊 API Endpoints

### Text Detection API
- **URL:** `http://localhost:5001/detect-text`
- **Method:** POST
- **Body:** `{"text": "message content"}`

### URL Detection API
- **URL:** `http://localhost:5002/detect-url`
- **Method:** POST
- **Body:** `{"url": "https://example.com"}`

### Image Detection API
- **URL:** `http://localhost:5003/detect-image`
- **Method:** POST
- **Body:** FormData with 'image' file OR JSON with 'image_data' base64

## 🎨 Customization

### Change API URLs
Edit the `API_CONFIG` object in `frontend.html`:
```javascript
const API_CONFIG = {
    TEXT_API: 'http://localhost:5001/detect-text',
    URL_API: 'http://localhost:5002/detect-url',
    IMAGE_API: 'http://localhost:5003/detect-image'
};
```

### Improve Image Model
1. Collect real scam images and legitimate images
2. Place them in appropriate folders
3. Retrain: `python train_image_model.py`
4. Restart backend: `python image_app.py`

## 📈 Next Steps

1. **Improve Models:** Collect more training data for better accuracy
2. **Deploy:** Host on cloud platforms (Heroku, AWS, Azure)
3. **Add Features:** 
   - Email integration
   - Browser extension
   - Mobile app
   - Real-time alerts
4. **Enhance UI:** Add charts, statistics, history

## 🆘 Need Help?

Common issues and solutions:
- **Backend not starting:** Check if Python packages are installed
- **Frontend not connecting:** Verify backend URLs and CORS setup
- **Low accuracy:** Retrain models with more data
- **Image upload fails:** Check file size and format

## ✅ Quick Start Checklist

- [ ] Install all Python packages
- [ ] Create models and datasets directories
- [ ] Train all three models
- [ ] Update backend files with CORS
- [ ] Start all three backend servers
- [ ] Open frontend.html in browser
- [ ] Test all three detection types

You're all set! 🎉
