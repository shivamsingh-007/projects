#!/bin/bash

echo "=========================================="
echo "CyberSentryAI Quick Start Setup"
echo "=========================================="
echo ""

# Create directories
echo "📁 Creating directories..."
mkdir -p models
mkdir -p datasets/scam_images
mkdir -p datasets/legitimate_images

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed!"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Train models if they don't exist
echo ""
echo "🤖 Checking models..."

if [ ! -f "models/text_scam_model.pkl" ]; then
    echo "Training text model..."
    python3 train_text_model.py
fi

if [ ! -f "models/url_phishing_model.pkl" ]; then
    echo "Training URL model..."
    python3 train_url_model.py
fi

if [ ! -f "models/image_scam_model.pkl" ]; then
    echo "Training image model..."
    python3 train_image_model.py
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To start the system, run these commands in separate terminals:"
echo ""
echo "Terminal 1: python3 text_app.py"
echo "Terminal 2: python3 url_app.py"
echo "Terminal 3: python3 image_app.py"
echo ""
echo "Then open frontend.html in your browser"
echo ""
echo "Or run: ./start_backends.sh (if available)"
echo ""
