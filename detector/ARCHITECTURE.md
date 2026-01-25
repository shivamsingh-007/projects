# CyberSentryAI Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (HTML/JS)                       │
│                      frontend.html                           │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Text Message │  │  URL Check   │  │Image Upload  │     │
│  │     Tab      │  │     Tab      │  │     Tab      │     │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘     │
│         │                  │                  │              │
└─────────┼──────────────────┼──────────────────┼──────────────┘
          │                  │                  │
          │ POST             │ POST             │ POST
          │ /detect-text     │ /detect-url      │ /detect-image
          ▼                  ▼                  ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  Text Backend   │ │  URL Backend    │ │ Image Backend   │
│   Port: 5001    │ │   Port: 5002    │ │   Port: 5003    │
│                 │ │                 │ │                 │
│ text_app.py     │ │ url_app.py      │ │ image_app.py    │
│                 │ │                 │ │                 │
│ Uses:           │ │ Uses:           │ │ Uses:           │
│ - Flask         │ │ - Flask         │ │ - Flask         │
│ - CORS          │ │ - CORS          │ │ - CORS          │
│ - ML Model      │ │ - Rule-based    │ │ - Rule-based    │
│                 │ │ - ML Model      │ │ - ML Model      │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │ Loads             │ Loads             │ Loads
         ▼                   ▼                   ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│ text_scam_model │ │url_phishing_model│ │image_scam_model │
│     .pkl        │ │     .pkl        │ │     .pkl        │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         ▲                   ▲                   ▲
         │                   │                   │
         │ Created by        │ Created by        │ Created by
         │                   │                   │
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│train_text_model │ │train_url_model  │ │train_image_model│
│     .py         │ │     .py         │ │     .py         │
└─────────────────┘ └─────────────────┘ └─────────────────┘
         ▲                   ▲                   ▲
         │                   │                   │
         │ Uses              │ Uses              │ Uses
         │                   │                   │
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│  spam.csv       │ │ PhiUSIIL        │ │  Image Files    │
│                 │ │ Dataset.csv     │ │  in folders     │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

## Data Flow

### 1. Text Message Detection Flow
```
User Input (Message Text)
    ↓
Frontend sends POST to http://localhost:5001/detect-text
    ↓
Backend extracts text features using TF-IDF
    ↓
ML Model (SVM) predicts scam probability
    ↓
Response: {is_scam, confidence, risk_level, explanation}
    ↓
Frontend displays colored result box
```

### 2. URL Detection Flow
```
User Input (URL)
    ↓
Frontend sends POST to http://localhost:5002/detect-url
    ↓
Backend analyzes URL patterns:
  - HTTPS check
  - @ symbol
  - Hyphens count
  - Suspicious keywords
  - IP address detection
    ↓
Rule-based + ML scoring
    ↓
Response: {is_phishing, confidence, risk_level, explanation[]}
    ↓
Frontend displays colored result box with warning signs
```

### 3. Image Detection Flow
```
User uploads image file
    ↓
Frontend converts to FormData
    ↓
Frontend sends POST to http://localhost:5003/detect-image
    ↓
Backend processes image:
  - Opens with PIL
  - Extracts features (colors, brightness, text density)
  - Analyzes patterns
    ↓
Rule-based + ML scoring
    ↓
Response: {is_scam, confidence, risk_level, explanation[]}
    ↓
Frontend displays colored result box with indicators
```

## Component Details

### Frontend (frontend.html)
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Features**:
  - 3 tabs for different detection types
  - File upload for images
  - Real-time API calls
  - Color-coded results (green=safe, yellow=warning, red=danger)
  - Loading indicators
  - Error handling

### Backend Servers
- **Technology**: Flask (Python)
- **Key Libraries**:
  - flask-cors: Enable cross-origin requests
  - scikit-learn: ML models
  - PIL/OpenCV: Image processing
- **Ports**:
  - 5001: Text detection
  - 5002: URL detection
  - 5003: Image detection

### Machine Learning Models
- **Text**: LinearSVC with TF-IDF vectorization
- **URL**: Random Forest Classifier (500 trees)
- **Image**: Random Forest Classifier (200 trees)

## Security Features

1. **CORS Protection**: Only allows requests from specified origins
2. **Input Validation**: Checks for empty/invalid inputs
3. **Error Handling**: Graceful degradation if models not loaded
4. **File Type Validation**: Image uploads restricted to safe formats

## Deployment Considerations

### Local Development (Current Setup)
- All servers run on localhost
- No authentication required
- Debug mode enabled

### Production Deployment (Future)
- Use production WSGI server (Gunicorn, uWSGI)
- Enable HTTPS
- Add rate limiting
- Implement user authentication
- Use environment variables for configuration
- Set up monitoring and logging
- Deploy on cloud (AWS, Heroku, Azure)

## Scalability

Current setup handles:
- Single user testing
- Small-scale demonstrations

For production:
- Use load balancer
- Add caching layer (Redis)
- Database for logging detections
- Horizontal scaling with multiple instances
- Message queue for async processing

## File Relationships

```
frontend.html
    ├─ Calls → text_app.py (port 5001)
    ├─ Calls → url_app.py (port 5002)
    └─ Calls → image_app.py (port 5003)

text_app.py
    └─ Loads → models/text_scam_model.pkl
        └─ Created by → train_text_model.py
            └─ Uses → datasets/spam.csv

url_app.py
    └─ Loads → models/url_phishing_model.pkl
        └─ Created by → train_url_model.py
            └─ Uses → datasets/PhiUSIIL_Phishing_URL_Dataset.csv

image_app.py
    └─ Loads → models/image_scam_model.pkl
        └─ Created by → train_image_model.py
            └─ Uses → datasets/scam_images/ & datasets/legitimate_images/
```
